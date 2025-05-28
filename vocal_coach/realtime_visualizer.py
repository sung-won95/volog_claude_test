"""
실시간 시각화 모듈
실시간 음성 분석 결과를 시각적으로 표시하는 기능
"""

import matplotlib.pyplot as plt
import numpy as np
from collections import deque
from typing import Dict, Any, Optional
import threading
import time

class RealtimeVisualizer:
    """실시간 시각화 클래스"""
    
    def __init__(self, max_points: int = 100):
        """초기화"""
        self.max_points = max_points
        
        # 데이터 버퍼
        self.pitch_data = deque(maxlen=max_points)
        self.volume_data = deque(maxlen=max_points)
        self.accuracy_data = deque(maxlen=max_points)
        self.time_data = deque(maxlen=max_points)
        
        # 목표 데이터
        self.target_pitch = None
        
        # 시각화 상태
        self.is_running = False
        self.fig = None
        self.axes = None
        self.lines = {}
        
        # 스레드
        self.update_thread = None
        self.start_time = time.time()
    
    def start_visualization(self, target_melody: Optional[Dict[str, Any]] = None):
        """시각화 시작"""
        try:
            # 목표 멜로디 설정
            if target_melody and 'frequencies' in target_melody:
                target_freqs = target_melody['frequencies']
                self.target_pitch = np.mean(target_freqs[target_freqs > 0])
            
            # 시각화 시작
            self.is_running = True
            self.start_time = time.time()
            
            print("📊 실시간 시각화가 시작되었습니다.")
            return True
            
        except Exception as e:
            print(f"❌ 시각화 시작 실패: {e}")
            return False
    
    def stop_visualization(self):
        """시각화 중지"""
        self.is_running = False
        print("📊 실시간 시각화를 중지했습니다.")
    
    def update_data(self, analysis_result: Dict[str, Any]):
        """분석 결과로 데이터 업데이트"""
        try:
            current_time = time.time() - self.start_time
            self.time_data.append(current_time)
            
            # 피치 데이터
            pitch_info = analysis_result.get('pitch', {})
            pitch_freq = pitch_info.get('frequency', 0)  
            self.pitch_data.append(pitch_freq if pitch_freq > 0 else None)
            
            # 볼륨 데이터
            volume_info = analysis_result.get('volume', {})
            volume_level = volume_info.get('normalized', 0)
            self.volume_data.append(volume_level)
            
            # 정확도 데이터
            comparison_info = analysis_result.get('comparison', {})
            accuracy = comparison_info.get('accuracy', 0)
            self.accuracy_data.append(accuracy)
            
        except Exception as e:
            print(f"데이터 업데이트 오류: {e}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """세션 통계 정보 반환"""
        try:
            stats = {
                'duration': 0,
                'avg_pitch': 0,
                'avg_volume': 0,
                'avg_accuracy': 0,
                'data_points': len(self.time_data)
            }
            
            if self.time_data:
                stats['duration'] = list(self.time_data)[-1] if self.time_data else 0
            
            # 피치 통계
            valid_pitches = [p for p in self.pitch_data if p is not None and p > 0]
            if valid_pitches:
                stats['avg_pitch'] = np.mean(valid_pitches)
            
            # 볼륨 통계
            if self.volume_data:
                volumes = list(self.volume_data)
                stats['avg_volume'] = np.mean(volumes)
            
            # 정확도 통계
            if self.accuracy_data:
                accuracies = list(self.accuracy_data)
                stats['avg_accuracy'] = np.mean(accuracies)
            
            return stats
            
        except Exception as e:
            return {'error': f'통계 계산 실패: {e}'}
    
    def reset_data(self):
        """데이터 버퍼 초기화"""
        self.pitch_data.clear()
        self.volume_data.clear()
        self.accuracy_data.clear()
        self.time_data.clear()
        self.start_time = time.time()
        print("📊 시각화 데이터가 초기화되었습니다.")
