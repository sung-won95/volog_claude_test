"""
실시간 음성 녹음 및 분석 모듈
실제 마이크 입력을 받아 실시간으로 피드백을 제공하는 기능
"""

import numpy as np
import sounddevice as sd
import threading
import time
import queue
from typing import Optional, Dict, Any, Callable, List
import librosa
from collections import deque

class RealtimeRecorder:
    """실시간 음성 녹음 및 분석 클래스"""
    
    def __init__(self, sample_rate: int = 22050, channels: int = 1, 
                 buffer_size: int = 2048):
        """초기화"""
        self.sample_rate = sample_rate
        self.channels = channels
        self.buffer_size = buffer_size
        
        # 녹음 상태
        self.is_recording = False
        self.is_analyzing = False
        
        # 버퍼
        self.audio_buffer = deque(maxlen=self.sample_rate * 10)  # 최대 10초 저장
        self.analysis_queue = queue.Queue()
        
        # 분석 설정
        self.analysis_window = 1.0  # 1초 단위로 분석
        self.min_freq = 80.0
        self.max_freq = 800.0
        
        # 콜백 함수들
        self.pitch_callback = None
        self.volume_callback = None
        self.feedback_callback = None
        
        # 분석 스레드
        self.analysis_thread = None
        
    def start_recording(self, target_melody: Optional[Dict[str, Any]] = None,
                       pitch_callback: Optional[Callable] = None,
                       volume_callback: Optional[Callable] = None,
                       feedback_callback: Optional[Callable] = None) -> bool:
        """실시간 녹음 시작"""
        try:
            # 콜백 함수 설정
            self.pitch_callback = pitch_callback
            self.volume_callback = volume_callback
            self.feedback_callback = feedback_callback
            self.target_melody = target_melody
            
            # 마이크 사용 가능성 확인
            if not self._check_microphone():
                print("❌ 마이크를 찾을 수 없습니다. 데모 모드로 전환합니다.")
                return False
            
            # 버퍼 초기화
            self.audio_buffer.clear()
            
            # 녹음 시작
            print("🎤 실시간 녹음 시작...")
            self.is_recording = True
            self.is_analyzing = True
            
            # 분석 스레드 시작
            self.analysis_thread = threading.Thread(target=self._analysis_worker)
            self.analysis_thread.daemon = True
            self.analysis_thread.start()
            
            # 오디오 스트림 시작
            self.stream = sd.InputStream(
                callback=self._audio_callback,
                channels=self.channels,
                samplerate=self.sample_rate,
                blocksize=self.buffer_size,
                dtype=np.float32
            )
            self.stream.start()
            
            return True
            
        except Exception as e:
            print(f"❌ 녹음 시작 실패: {e}")
            self.is_recording = False
            self.is_analyzing = False
            return False
    
    def stop_recording(self) -> Dict[str, Any]:
        """녹음 중지 및 전체 오디오 반환"""
        try:
            if self.is_recording:
                self.is_recording = False
                self.is_analyzing = False
                
                # 스트림 중지
                if hasattr(self, 'stream'):
                    self.stream.stop()
                    self.stream.close()
                
                # 분석 스레드 종료 대기
                if self.analysis_thread and self.analysis_thread.is_alive():
                    self.analysis_thread.join(timeout=2.0)
                
                # 전체 오디오 데이터 반환
                if len(self.audio_buffer) > 0:
                    full_audio = np.array(list(self.audio_buffer))
                    return {
                        'audio': full_audio,
                        'sr': self.sample_rate,
                        'duration': len(full_audio) / self.sample_rate,
                        'channels': self.channels,
                        'timestamp': time.time()
                    }
                else:
                    return None
                    
        except Exception as e:
            print(f"❌ 녹음 중지 실패: {e}")
            return None
    
    def _check_microphone(self) -> bool:
        """마이크 사용 가능성 확인"""
        try:
            devices = sd.query_devices()
            input_devices = [d for d in devices if d['max_input_channels'] > 0]
            
            if len(input_devices) == 0:
                return False
            
            # 기본 입력 장치 테스트
            test_duration = 0.1
            try:
                test_audio = sd.rec(
                    int(test_duration * self.sample_rate), 
                    samplerate=self.sample_rate, 
                    channels=self.channels,
                    dtype=np.float32
                )
                sd.wait()
                return True
            except:
                return False
                
        except Exception:
            return False
    
    def _audio_callback(self, indata, frames, time, status):
        """오디오 입력 콜백"""
        if status:
            print(f"오디오 상태: {status}")
        
        if self.is_recording:
            # 모노 변환
            if indata.shape[1] > 1:
                audio_mono = np.mean(indata, axis=1)
            else:
                audio_mono = indata[:, 0]
            
            # 버퍼에 추가
            self.audio_buffer.extend(audio_mono)
            
            # 분석을 위해 큐에 추가
            if len(audio_mono) > 0:
                self.analysis_queue.put(audio_mono.copy())
    
    def _analysis_worker(self):
        """실시간 분석 워커 스레드"""
        analysis_buffer = deque(maxlen=int(self.sample_rate * self.analysis_window))
        
        while self.is_analyzing:
            try:
                # 큐에서 오디오 데이터 가져오기
                try:
                    audio_chunk = self.analysis_queue.get(timeout=0.1)
                    analysis_buffer.extend(audio_chunk)
                except queue.Empty:
                    continue
                
                # 충분한 데이터가 있으면 분석 수행
                if len(analysis_buffer) >= int(self.sample_rate * self.analysis_window):
                    audio_data = np.array(list(analysis_buffer))
                    
                    # 실시간 분석
                    analysis_result = self._analyze_realtime(audio_data)
                    
                    # 콜백 호출
                    self._call_callbacks(analysis_result)
                    
                    # 버퍼 일부 제거 (중복 방지)
                    remove_count = len(audio_chunk)
                    for _ in range(min(remove_count, len(analysis_buffer))):
                        analysis_buffer.popleft()
                
            except Exception as e:
                print(f"실시간 분석 오류: {e}")
                time.sleep(0.1)
    
    def _analyze_realtime(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """실시간 오디오 분석"""
        try:
            result = {}
            
            # 1. 음정 분석
            pitch_info = self._extract_pitch_realtime(audio_data)
            result['pitch'] = pitch_info
            
            # 2. 음량 분석
            volume_info = self._analyze_volume_realtime(audio_data)
            result['volume'] = volume_info
            
            # 3. 안정성 분석
            stability_info = self._analyze_stability_realtime(audio_data)
            result['stability'] = stability_info
            
            # 4. 목표 멜로디와 비교 (있는 경우)
            if self.target_melody:
                comparison = self._compare_with_target(pitch_info, self.target_melody)
                result['comparison'] = comparison
            
            return result
            
        except Exception as e:
            return {'error': f'실시간 분석 실패: {e}'}
    
    def _extract_pitch_realtime(self, audio: np.ndarray) -> Dict[str, Any]:
        """실시간 음정 추출"""
        try:
            # 스펙트로그램 계산
            stft = librosa.stft(audio, n_fft=1024, hop_length=256)
            pitches, magnitudes = librosa.piptrack(
                S=np.abs(stft), sr=self.sample_rate, 
                fmin=self.min_freq, fmax=self.max_freq, threshold=0.1
            )
            
            # 주요 피치 추출
            pitch_values = []
            confidence_values = []
            
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                confidence = magnitudes[index, t]
                
                if pitch > 0:
                    pitch_values.append(pitch)
                    confidence_values.append(confidence)
            
            if len(pitch_values) > 0:
                avg_pitch = np.mean(pitch_values)
                pitch_stability = 1.0 - (np.std(pitch_values) / (avg_pitch + 1e-8))
                avg_confidence = np.mean(confidence_values)
            else:
                avg_pitch = 0.0
                pitch_stability = 0.0
                avg_confidence = 0.0
            
            return {
                'frequency': avg_pitch,
                'stability': max(0.0, pitch_stability),
                'confidence': avg_confidence,
                'note': self._frequency_to_note(avg_pitch) if avg_pitch > 0 else None
            }
            
        except Exception as e:
            return {'error': f'음정 추출 실패: {e}'}
    
    def _analyze_volume_realtime(self, audio: np.ndarray) -> Dict[str, Any]:
        """실시간 음량 분석"""
        try:
            # RMS 계산
            rms = np.sqrt(np.mean(audio**2))
            
            # dB 변환
            db = 20 * np.log10(rms + 1e-8)
            
            # 정규화된 볼륨 (0-1)
            normalized_volume = max(0.0, min(1.0, (db + 60) / 60))
            
            return {
                'rms': rms,
                'db': db,
                'normalized': normalized_volume,
                'level': self._get_volume_level(normalized_volume)
            }
            
        except Exception as e:
            return {'error': f'음량 분석 실패: {e}'}
    
    def _analyze_stability_realtime(self, audio: np.ndarray) -> Dict[str, Any]:
        """실시간 안정성 분석"""
        try:
            # 에너지 변화율 계산
            frame_size = len(audio) // 10
            energy_frames = []
            
            for i in range(0, len(audio) - frame_size, frame_size):
                frame = audio[i:i + frame_size]
                energy = np.sum(frame**2)
                energy_frames.append(energy)
            
            if len(energy_frames) > 1:
                energy_stability = 1.0 - (np.std(energy_frames) / (np.mean(energy_frames) + 1e-8))
            else:
                energy_stability = 0.5
            
            return {
                'energy_stability': max(0.0, energy_stability),
                'overall_stability': max(0.0, energy_stability)
            }
            
        except Exception as e:
            return {'error': f'안정성 분석 실패: {e}'}
    
    def _compare_with_target(self, pitch_info: Dict[str, Any], 
                           target_melody: Dict[str, Any]) -> Dict[str, Any]:
        """목표 멜로디와 비교"""
        try:
            current_freq = pitch_info.get('frequency', 0)
            
            if current_freq <= 0:
                return {'accuracy': 0.0, 'message': '음성이 감지되지 않습니다'}
            
            # 목표 주파수 중에서 가장 가까운 값 찾기
            target_freqs = target_melody.get('frequencies', [])
            if len(target_freqs) == 0:
                return {'accuracy': 0.5, 'message': '목표 멜로디가 없습니다'}
            
            # 현재 시점에서 예상되는 목표 주파수 계산
            # (실제로는 시간 동기화가 필요하지만, 여기서는 평균값 사용)
            target_freq = np.mean(target_freqs[target_freqs > 0])
            
            if target_freq <= 0:
                return {'accuracy': 0.5, 'message': '유효한 목표 음정이 없습니다'}
            
            # 센트 단위로 오차 계산
            cent_error = 1200 * np.log2(current_freq / target_freq)
            accuracy = max(0.0, 1.0 - abs(cent_error) / 100.0)
            
            # 피드백 메시지 생성
            if abs(cent_error) <= 20:
                message = "🎯 정확합니다!"
            elif cent_error > 20:
                message = f"📈 너무 높습니다 ({cent_error:.0f}센트)"
            else:
                message = f"📉 너무 낮습니다 ({abs(cent_error):.0f}센트)"
            
            return {
                'accuracy': accuracy,
                'cent_error': cent_error,
                'message': message,
                'target_freq': target_freq,
                'current_freq': current_freq
            }
            
        except Exception as e:
            return {'error': f'비교 분석 실패: {e}'}
    
    def _frequency_to_note(self, frequency: float) -> str:
        """주파수를 음표로 변환"""
        try:
            if frequency <= 0:
                return "None"
            
            # A4 = 440Hz 기준
            A4 = 440.0
            note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            
            # 반음 계산
            semitones_from_A4 = 12 * np.log2(frequency / A4)
            note_index = int(round(semitones_from_A4)) % 12
            octave = 4 + int(round(semitones_from_A4)) // 12
            
            return f"{note_names[note_index]}{octave}"
            
        except Exception:
            return "Unknown"
    
    def _get_volume_level(self, normalized_volume: float) -> str:
        """정규화된 볼륨을 레벨로 변환"""
        if normalized_volume < 0.1:
            return "매우 작음"
        elif normalized_volume < 0.3:
            return "작음"
        elif normalized_volume < 0.7:
            return "적당"
        elif normalized_volume < 0.9:
            return "큼"
        else:
            return "매우 큼"
    
    def _call_callbacks(self, analysis_result: Dict[str, Any]):
        """콜백 함수들 호출"""
        try:
            if self.pitch_callback and 'pitch' in analysis_result:
                self.pitch_callback(analysis_result['pitch'])
            
            if self.volume_callback and 'volume' in analysis_result:
                self.volume_callback(analysis_result['volume'])
            
            if self.feedback_callback:
                self.feedback_callback(analysis_result)
                
        except Exception as e:
            print(f"콜백 호출 오류: {e}")
    
    def list_audio_devices(self):
        """사용 가능한 오디오 장치 목록"""
        try:
            print("\n🎤 사용 가능한 오디오 장치:")
            devices = sd.query_devices()
            
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    print(f"  {i}: {device['name']} (입력 채널: {device['max_input_channels']})")
            
            return devices
            
        except Exception as e:
            print(f"장치 목록 조회 실패: {e}")
            return []
    
    def set_input_device(self, device_id: int):
        """입력 장치 설정"""
        try:
            sd.default.device[0] = device_id
            print(f"입력 장치가 {device_id}번으로 설정되었습니다.")
        except Exception as e:
            print(f"장치 설정 실패: {e}")
