"""
멜로디 분석 모듈
오디오에서 멜로디 라인 추출 및 분석 기능 제공
"""

import numpy as np
import librosa
from typing import Dict, Any, Optional, Tuple
from scipy.signal import medfilt
import matplotlib.pyplot as plt

class MelodyAnalyzer:
    """멜로디 분석 클래스"""
    
    def __init__(self):
        """초기화"""
        self.min_freq = 80.0    # 최소 주파수 (Hz)
        self.max_freq = 800.0   # 최대 주파수 (Hz)
        self.frame_length = 2048
        self.hop_length = 512
        
    def extract_melody(self, audio_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        오디오에서 멜로디 추출
        
        Args:
            audio_data: 오디오 데이터
            
        Returns:
            멜로디 데이터 또는 None
        """
        try:
            audio = audio_data['audio']
            sr = audio_data['sr']
            
            print("🎼 멜로디 추출 중...")
            
            # 1. 기본 주파수(F0) 추출
            f0_times, f0_values = self._extract_f0(audio, sr)
            
            # 2. 노이즈 제거 및 스무딩
            f0_values = self._smooth_f0(f0_values)
            
            # 3. 신뢰도 계산
            confidence = self._calculate_confidence(audio, sr, f0_times, f0_values)
            
            # 4. 음표 단위 분할
            notes = self._segment_notes(f0_times, f0_values, confidence)
            
            melody_data = {
                'times': f0_times,
                'frequencies': f0_values,
                'confidence': confidence,
                'notes': notes,
                'sr': sr
            }
            
            print(f"✅ 멜로디 추출 완료 ({len(f0_times)}개 프레임)")
            return melody_data
            
        except Exception as e:
            print(f"❌ 멜로디 추출 실패: {e}")
            return None
    
    def _extract_f0(self, audio: np.ndarray, sr: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        기본 주파수(F0) 추출 - librosa의 piptrack 사용
        
        Args:
            audio: 오디오 신호
            sr: 샘플링 레이트
            
        Returns:
            시간 배열, 주파수 배열
        """
        # STFT 계산
        stft = librosa.stft(audio, n_fft=self.frame_length, hop_length=self.hop_length)
        
        # Pitch tracking
        pitches, magnitudes = librosa.piptrack(
            S=np.abs(stft),
            sr=sr,
            fmin=self.min_freq,
            fmax=self.max_freq,
            threshold=0.1
        )
        
        # 시간 축 생성
        times = librosa.frames_to_time(
            np.arange(pitches.shape[1]), 
            sr=sr, 
            hop_length=self.hop_length
        )
        
        # 각 시간 프레임에서 가장 강한 피치 선택
        f0_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            
            # 유효한 피치가 있는 경우에만 추가
            if pitch > 0:
                f0_values.append(pitch)
            else:
                # 이전 값으로 보간하거나 0으로 설정
                if len(f0_values) > 0:
                    f0_values.append(f0_values[-1])
                else:
                    f0_values.append(0.0)
        
        return times, np.array(f0_values)
    
    def _smooth_f0(self, f0_values: np.ndarray, window_size: int = 5) -> np.ndarray:
        """
        F0 값 스무딩
        
        Args:
            f0_values: 원본 F0 값들
            window_size: 필터 윈도우 크기
            
        Returns:
            스무딩된 F0 값들
        """
        # 0이 아닌 값들만 필터링
        valid_mask = f0_values > 0
        
        if np.sum(valid_mask) < 3:
            return f0_values
        
        # 메디안 필터 적용
        smoothed = f0_values.copy()
        valid_f0 = f0_values[valid_mask]
        
        if len(valid_f0) > window_size:
            smoothed_valid = medfilt(valid_f0, kernel_size=window_size)
            smoothed[valid_mask] = smoothed_valid
        
        return smoothed
    
    def _calculate_confidence(self, audio: np.ndarray, sr: int, 
                            times: np.ndarray, f0_values: np.ndarray) -> np.ndarray:
        """
        멜로디 신뢰도 계산
        
        Args:
            audio: 오디오 신호
            sr: 샘플링 레이트
            times: 시간 배열
            f0_values: 주파수 배열
            
        Returns:
            신뢰도 배열
        """
        confidence = np.zeros_like(f0_values)
        
        # 스펙트로그램 계산
        stft = librosa.stft(audio, n_fft=self.frame_length, hop_length=self.hop_length)
        magnitude = np.abs(stft)
        
        for i, (time, freq) in enumerate(zip(times, f0_values)):
            if freq > 0:
                # 해당 주파수에서의 에너지 계산
                freq_bin = int(freq * self.frame_length / sr)
                frame_idx = min(i, magnitude.shape[1] - 1)
                
                if freq_bin < magnitude.shape[0]:
                    # 기본 주파수와 하모닉의 에너지 비율로 신뢰도 계산
                    fundamental_energy = magnitude[freq_bin, frame_idx]
                    
                    # 주변 주파수 빈들의 평균 에너지
                    window = 3
                    start_bin = max(0, freq_bin - window)
                    end_bin = min(magnitude.shape[0], freq_bin + window + 1)
                    local_energy = np.mean(magnitude[start_bin:end_bin, frame_idx])
                    
                    # 전체 프레임의 평균 에너지
                    total_energy = np.mean(magnitude[:, frame_idx])
                    
                    if total_energy > 0:
                        confidence[i] = min(1.0, local_energy / (total_energy + 1e-8))
                    else:
                        confidence[i] = 0.0
                else:
                    confidence[i] = 0.0
            else:
                confidence[i] = 0.0
        
        return confidence
    
    def _segment_notes(self, times: np.ndarray, f0_values: np.ndarray, 
                      confidence: np.ndarray, min_note_duration: float = 0.1) -> list:
        """
        연속된 F0를 음표 단위로 분할
        
        Args:
            times: 시간 배열
            f0_values: 주파수 배열
            confidence: 신뢰도 배열
            min_note_duration: 최소 음표 길이 (초)
            
        Returns:
            음표 리스트
        """
        notes = []
        
        if len(f0_values) == 0:
            return notes
        
        # 신뢰할 수 있는 구간만 추출
        valid_mask = (f0_values > 0) & (confidence > 0.3)
        
        if not np.any(valid_mask):
            return notes
        
        # 연속된 구간 찾기
        segments = []
        start_idx = None
        
        for i, is_valid in enumerate(valid_mask):
            if is_valid and start_idx is None:
                start_idx = i
            elif not is_valid and start_idx is not None:
                segments.append((start_idx, i - 1))
                start_idx = None
        
        # 마지막 구간 처리
        if start_idx is not None:
            segments.append((start_idx, len(valid_mask) - 1))
        
        # 각 구간을 음표로 변환
        for start_idx, end_idx in segments:
            if start_idx >= len(times) or end_idx >= len(times):
                continue
                
            duration = times[end_idx] - times[start_idx]
            
            if duration >= min_note_duration:
                segment_f0 = f0_values[start_idx:end_idx + 1]
                segment_conf = confidence[start_idx:end_idx + 1]
                
                # 가중 평균으로 대표 주파수 계산
                weights = segment_conf
                if np.sum(weights) > 0:
                    avg_freq = np.average(segment_f0, weights=weights)
                else:
                    avg_freq = np.mean(segment_f0)
                
                note = {
                    'start_time': times[start_idx],
                    'end_time': times[end_idx],
                    'duration': duration,
                    'frequency': avg_freq,
                    'midi_note': self._freq_to_midi(avg_freq),
                    'confidence': np.mean(segment_conf)
                }
                
                notes.append(note)
        
        return notes
    
    def _freq_to_midi(self, frequency: float) -> int:
        """
        주파수를 MIDI 노트 번호로 변환
        
        Args:
            frequency: 주파수 (Hz)
            
        Returns:
            MIDI 노트 번호
        """
        if frequency <= 0:
            return 0
        
        # A4 = 440Hz = MIDI 69
        midi_note = 69 + 12 * np.log2(frequency / 440.0)
        return int(round(midi_note))
    
    def _midi_to_freq(self, midi_note: int) -> float:
        """
        MIDI 노트 번호를 주파수로 변환
        
        Args:
            midi_note: MIDI 노트 번호
            
        Returns:
            주파수 (Hz)
        """
        return 440.0 * (2 ** ((midi_note - 69) / 12.0))
    
    def analyze_melody_features(self, melody_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        멜로디 특징 분석
        
        Args:
            melody_data: 멜로디 데이터
            
        Returns:
            분석된 특징들
        """
        try:
            f0_values = melody_data['frequencies']
            confidence = melody_data['confidence']
            notes = melody_data.get('notes', [])
            
            # 기본 통계
            valid_f0 = f0_values[f0_values > 0]
            
            if len(valid_f0) == 0:
                return {'error': '유효한 멜로디 데이터가 없습니다'}
            
            features = {
                'pitch_range': {
                    'min_freq': float(np.min(valid_f0)),
                    'max_freq': float(np.max(valid_f0)),
                    'range_semitones': self._freq_to_midi(np.max(valid_f0)) - 
                                     self._freq_to_midi(np.min(valid_f0))
                },
                'pitch_statistics': {
                    'mean_freq': float(np.mean(valid_f0)),
                    'median_freq': float(np.median(valid_f0)),
                    'std_freq': float(np.std(valid_f0))
                },
                'stability': {
                    'mean_confidence': float(np.mean(confidence)),
                    'pitch_stability': self._calculate_pitch_stability(valid_f0)
                },
                'note_count': len(notes),
                'coverage': len(valid_f0) / len(f0_values) if len(f0_values) > 0 else 0
            }
            
            return features
            
        except Exception as e:
            return {'error': f'특징 분석 실패: {e}'}
    
    def _calculate_pitch_stability(self, f0_values: np.ndarray) -> float:
        """
        피치 안정성 계산 (작을수록 안정)
        
        Args:
            f0_values: 주파수 값들
            
        Returns:
            안정성 지수
        """
        if len(f0_values) < 2:
            return 0.0
        
        # 연속된 값들 간의 변화율 계산
        diff = np.diff(f0_values)
        relative_diff = np.abs(diff) / (f0_values[:-1] + 1e-8)
        
        # 평균 변화율 (백분율)
        stability = np.mean(relative_diff) * 100
        
        return float(stability)
    
    def visualize_melody(self, melody_data: Dict[str, Any], title: str = "멜로디 분석") -> None:
        """
        멜로디 시각화
        
        Args:
            melody_data: 멜로디 데이터
            title: 그래프 제목
        """
        try:
            times = melody_data['times']
            frequencies = melody_data['frequencies']
            confidence = melody_data['confidence']
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            
            # 상단: 주파수 곡선
            valid_mask = frequencies > 0
            ax1.plot(times[valid_mask], frequencies[valid_mask], 'b-', linewidth=1.5, alpha=0.8)
            ax1.set_ylabel('주파수 (Hz)')
            ax1.set_title(title)
            ax1.grid(True, alpha=0.3)
            
            # 음표 표시
            notes = melody_data.get('notes', [])
            for note in notes:
                ax1.axhspan(note['frequency'] * 0.98, note['frequency'] * 1.02, 
                           xmin=(note['start_time'] - times[0]) / (times[-1] - times[0]),
                           xmax=(note['end_time'] - times[0]) / (times[-1] - times[0]),
                           alpha=0.3, color='red')
            
            # 하단: 신뢰도
            ax2.fill_between(times, confidence, alpha=0.6, color='green')
            ax2.set_xlabel('시간 (초)')
            ax2.set_ylabel('신뢰도')
            ax2.set_ylim(0, 1)
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print(f"❌ 멜로디 시각화 실패: {e}")
