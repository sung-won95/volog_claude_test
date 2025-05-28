"""
박자 감지 모듈
오디오에서 박자, 템포, 박자표 감지 기능 제공
"""

import numpy as np
import librosa
from typing import Dict, Any, Optional, Tuple, List

class BeatDetector:
    """박자 감지 클래스"""
    
    def __init__(self):
        """초기화"""
        self.min_tempo = 60.0   # 최소 템포 (BPM)
        self.max_tempo = 200.0  # 최대 템포 (BPM)
        
    def detect_beats(self, audio_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """박자 및 템포 감지"""
        try:
            audio = audio_data['audio']
            sr = audio_data['sr']
            
            print("🥁 박자 분석 중...")
            
            # 1. 템포 감지
            tempo = self._detect_tempo(audio, sr)
            
            # 2. 박자 위치 감지
            beat_times = self._detect_beat_positions(audio, sr, tempo)
            
            # 3. 박자표 추정
            time_signature = self._estimate_time_signature(beat_times, tempo)
            
            # 4. 마디 구분
            measure_positions = self._detect_measures(beat_times, time_signature)
            
            # 5. 다운비트 감지
            downbeats = self._detect_downbeats(audio, sr, beat_times, time_signature)
            
            beat_data = {
                'tempo': tempo,
                'beat_times': beat_times,
                'time_signature': time_signature,
                'beats_per_measure': time_signature[0],
                'measure_positions': measure_positions,
                'downbeats': downbeats,
                'beat_intervals': np.diff(beat_times) if len(beat_times) > 1 else [],
                'tempo_stability': self._calculate_tempo_stability(beat_times)
            }
            
            print(f"✅ 박자 분석 완료 (템포: {tempo:.1f} BPM, 박자표: {time_signature})")
            return beat_data
            
        except Exception as e:
            print(f"❌ 박자 감지 실패: {e}")
            return None
    
    def _detect_tempo(self, audio: np.ndarray, sr: int) -> float:
        """템포 감지"""
        tempo, _ = librosa.beat.beat_track(y=audio, sr=sr, start_bpm=120.0, tightness=100)
        tempo = np.clip(tempo, self.min_tempo, self.max_tempo)
        return float(tempo)
    
    def _detect_beat_positions(self, audio: np.ndarray, sr: int, tempo: float) -> np.ndarray:
        """박자 위치 감지"""
        _, beat_frames = librosa.beat.beat_track(y=audio, sr=sr, bpm=tempo, units='frames')
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        return beat_times
    
    def _estimate_time_signature(self, beat_times: np.ndarray, tempo: float) -> Tuple[int, int]:
        """박자표 추정"""
        if len(beat_times) < 8:
            return (4, 4)
        
        intervals = np.diff(beat_times)
        interval_std = np.std(intervals)
        avg_interval = np.mean(intervals)
        
        if interval_std < avg_interval * 0.1:
            beat_period = 60.0 / tempo
            if abs(avg_interval - beat_period * 3/4) < 0.1:
                return (3, 4)
            else:
                return (4, 4)
        else:
            return (4, 4)
    
    def _detect_measures(self, beat_times: np.ndarray, time_signature: Tuple[int, int]) -> List[float]:
        """마디 위치 감지"""
        beats_per_measure = time_signature[0]
        measure_positions = []
        
        if len(beat_times) > 0:
            measure_positions.append(beat_times[0])
        
        for i in range(beats_per_measure, len(beat_times), beats_per_measure):
            if i < len(beat_times):
                measure_positions.append(beat_times[i])
        
        return measure_positions
    
    def _detect_downbeats(self, audio: np.ndarray, sr: int, 
                         beat_times: np.ndarray, time_signature: Tuple[int, int]) -> List[float]:
        """다운비트 감지"""
        beats_per_measure = time_signature[0]
        downbeats = []
        
        for i in range(0, len(beat_times), beats_per_measure):
            if i < len(beat_times):
                downbeats.append(beat_times[i])
        
        return downbeats
    
    def _calculate_tempo_stability(self, beat_times: np.ndarray) -> float:
        """템포 안정성 계산"""
        if len(beat_times) < 3:
            return 0.0
        
        intervals = np.diff(beat_times)
        if len(intervals) == 0:
            return 0.0
        
        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        if mean_interval > 0:
            cv = std_interval / mean_interval
            stability = max(0.0, 1.0 - cv * 10)
            return min(1.0, stability)
        else:
            return 0.0
