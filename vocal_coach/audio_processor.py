"""
오디오 처리 모듈
오디오 파일 로드, 전처리, 포맷 변환 등의 기능 제공
"""

import numpy as np
import librosa
import soundfile as sf
from typing import Optional, Dict, Any
import os

class AudioProcessor:
    """오디오 처리 클래스"""
    
    def __init__(self, target_sr: int = 22050):
        """
        초기화
        
        Args:
            target_sr: 목표 샘플링 레이트
        """
        self.target_sr = target_sr
        
    def load_audio(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        오디오 파일 로드
        
        Args:
            file_path: 오디오 파일 경로
            
        Returns:
            오디오 데이터 딕셔너리 또는 None
        """
        try:
            if not os.path.exists(file_path):
                print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
                return None
            
            # librosa로 오디오 로드
            audio, sr = librosa.load(file_path, sr=self.target_sr, mono=True)
            
            # 정규화
            audio = self._normalize_audio(audio)
            
            # 메타데이터 수집
            duration = len(audio) / sr
            filename = os.path.basename(file_path)
            
            audio_data = {
                'audio': audio,
                'sr': sr,
                'duration': duration,
                'filename': filename,
                'original_path': file_path
            }
            
            print(f"✅ 오디오 로드 성공: {filename} ({duration:.1f}초, {sr}Hz)")
            return audio_data
            
        except Exception as e:
            print(f"❌ 오디오 로드 실패: {e}")
            return None
    
    def _normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """
        오디오 정규화
        
        Args:
            audio: 입력 오디오
            
        Returns:
            정규화된 오디오
        """
        # RMS 기반 정규화
        rms = np.sqrt(np.mean(audio**2))
        if rms > 0:
            target_rms = 0.1  # 목표 RMS 레벨
            audio = audio * (target_rms / rms)
        
        # 클리핑 방지
        audio = np.clip(audio, -1.0, 1.0)
        
        return audio
    
    def extract_vocal(self, audio_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """
        음원 분리를 통한 보컬 추출 (기본 구현)
        
        Args:
            audio_data: 오디오 데이터
            
        Returns:
            보컬 오디오 또는 None
        """
        try:
            audio = audio_data['audio']
            sr = audio_data['sr']
            
            # 간단한 보컬 추출 (중앙 채널 강조)
            # 실제로는 Spleeter나 demucs 같은 도구를 사용하는 것이 좋음
            
            # 스테레오가 아닌 경우 그대로 반환
            if len(audio.shape) == 1:
                return audio
            
            # 중앙 채널 추출 (간단한 보컬 분리)
            if len(audio.shape) == 2:
                # Mid-Side 변환
                mid = (audio[0] + audio[1]) / 2
                side = (audio[0] - audio[1]) / 2
                
                # 보컬은 주로 중앙에 위치
                vocal_estimate = mid + 0.3 * side
                return vocal_estimate
            
            return audio
            
        except Exception as e:
            print(f"❌ 보컬 추출 실패: {e}")
            return None
    
    def preprocess_for_analysis(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        분석용 오디오 전처리
        
        Args:
            audio: 입력 오디오
            sr: 샘플링 레이트
            
        Returns:
            전처리된 데이터
        """
        try:
            # 윈도우 함수 적용
            windowed_audio = audio * np.hanning(len(audio))
            
            # 스펙트로그램 계산
            stft = librosa.stft(windowed_audio, n_fft=2048, hop_length=512)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # 멜 스펙트로그램
            mel_spec = librosa.feature.melspectrogram(
                y=windowed_audio, sr=sr, n_mels=128
            )
            
            # MFCC 특징
            mfcc = librosa.feature.mfcc(
                y=windowed_audio, sr=sr, n_mfcc=13
            )
            
            return {
                'audio': windowed_audio,
                'stft_magnitude': magnitude,
                'stft_phase': phase,
                'mel_spectrogram': mel_spec,
                'mfcc': mfcc,
                'sr': sr
            }
            
        except Exception as e:
            print(f"❌ 전처리 실패: {e}")
            return {'audio': audio, 'sr': sr}
    
    def save_audio(self, audio: np.ndarray, sr: int, output_path: str) -> bool:
        """
        오디오 저장
        
        Args:
            audio: 오디오 데이터
            sr: 샘플링 레이트
            output_path: 출력 파일 경로
            
        Returns:
            성공 여부
        """
        try:
            sf.write(output_path, audio, sr)
            print(f"✅ 오디오 저장 완료: {output_path}")
            return True
        except Exception as e:
            print(f"❌ 오디오 저장 실패: {e}")
            return False
    
    def apply_effects(self, audio: np.ndarray, sr: int, effects: Dict[str, Any]) -> np.ndarray:
        """
        오디오 이펙트 적용
        
        Args:
            audio: 입력 오디오
            sr: 샘플링 레이트
            effects: 이펙트 설정
            
        Returns:
            이펙트가 적용된 오디오
        """
        processed_audio = audio.copy()
        
        try:
            # 음량 조절
            if 'volume' in effects:
                processed_audio *= effects['volume']
            
            # 피치 시프트
            if 'pitch_shift' in effects:
                processed_audio = librosa.effects.pitch_shift(
                    processed_audio, sr=sr, n_steps=effects['pitch_shift']
                )
            
            # 시간 스트레칭
            if 'time_stretch' in effects:
                processed_audio = librosa.effects.time_stretch(
                    processed_audio, rate=effects['time_stretch']
                )
            
            # 노이즈 게이트
            if 'noise_gate' in effects:
                threshold = effects['noise_gate']
                processed_audio = np.where(
                    np.abs(processed_audio) < threshold, 
                    processed_audio * 0.1, 
                    processed_audio
                )
            
            return processed_audio
            
        except Exception as e:
            print(f"❌ 이펙트 적용 실패: {e}")
            return audio
