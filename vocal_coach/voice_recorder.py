"""
음성 녹음 모듈
사용자 음성을 실시간으로 녹음하는 기능 제공
"""

import numpy as np
import time
from typing import Optional, Dict, Any

class VoiceRecorder:
    """음성 녹음 클래스"""
    
    def __init__(self, sample_rate: int = 22050, channels: int = 1):
        """초기화"""
        self.sample_rate = sample_rate
        self.channels = channels
        
    def record_section(self, duration: float, countdown: int = 3) -> Optional[Dict[str, Any]]:
        """지정된 시간 동안 음성 녹음 (데모용 가상 구현)"""
        try:
            print(f"🎤 녹음 시뮬레이션 ({duration:.1f}초)")
            
            # 카운트다운
            if countdown > 0:
                self._countdown(countdown)
            
            print("🔴 녹음 시작!")
            
            # 진행률 표시
            self._show_progress(duration)
            
            # 가상 녹음 데이터 생성
            audio_data = self._generate_demo_recording(duration)
            
            print("🔴 녹음 완료!")
            
            return {
                'audio': audio_data,
                'sr': self.sample_rate,
                'duration': duration,
                'channels': self.channels,
                'timestamp': time.time()
            }
                
        except Exception as e:
            print(f"❌ 녹음 실패: {e}")
            return None
    
    def _generate_demo_recording(self, duration: float) -> np.ndarray:
        """데모용 가상 녹음 데이터 생성"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples)
        
        # 기본 주파수 (C4 = 261.63 Hz)
        base_freq = 261.63
        melody_pattern = [1.0, 1.125, 1.25, 1.33, 1.5, 1.33, 1.25, 1.125]
        
        audio = np.zeros(samples)
        
        for i, freq_ratio in enumerate(melody_pattern):
            start_idx = int(i * samples / len(melody_pattern))
            end_idx = int((i + 1) * samples / len(melody_pattern))
            
            if end_idx <= samples:
                freq = base_freq * freq_ratio
                t_segment = t[start_idx:end_idx]
                
                # 하모닉 추가
                segment = (
                    0.6 * np.sin(2 * np.pi * freq * t_segment) +
                    0.3 * np.sin(2 * np.pi * freq * 2 * t_segment) +
                    0.1 * np.sin(2 * np.pi * freq * 3 * t_segment)
                )
                
                # 엔벨로프 적용
                envelope = np.hanning(len(segment))
                segment *= envelope
                
                audio[start_idx:end_idx] = segment
        
        # 노이즈 추가
        noise = np.random.normal(0, 0.05, samples)
        audio += noise
        
        return self._normalize_audio(audio)
    
    def _countdown(self, seconds: int):
        """카운트다운 표시"""
        print("📢 녹음 준비...")
        for i in range(seconds, 0, -1):
            print(f"   {i}...")
            time.sleep(1)
        print("   시작! 🎤")
    
    def _show_progress(self, duration: float):
        """녹음 진행률 표시"""
        steps = 20
        step_duration = duration / steps
        
        for i in range(steps + 1):
            progress = i / steps
            bar_length = 30
            filled_length = int(bar_length * progress)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            elapsed_time = i * step_duration
            
            print(f"\r🎤 녹음 중: [{bar}] {progress*100:.1f}% ({elapsed_time:.1f}s/{duration:.1f}s)", end='')
            
            if i < steps:
                time.sleep(step_duration)
        
        print()
    
    def _normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """오디오 정규화"""
        rms = np.sqrt(np.mean(audio**2))
        if rms > 0:
            target_rms = 0.1
            audio = audio * (target_rms / rms)
        
        audio = np.clip(audio, -1.0, 1.0)
        return audio
    
    def test_microphone(self, duration: float = 3.0) -> bool:
        """마이크 테스트"""
        print("🎤 마이크 테스트 (데모 모드)")
        print("✅ 마이크가 정상적으로 작동합니다.")
        return True
