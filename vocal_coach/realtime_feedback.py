"""
실시간 피드백 엔진
실시간으로 음성을 분석하고 즉각적인 피드백을 제공하는 모듈
"""

import numpy as np
import time
from typing import Dict, Any, List, Optional
from collections import deque

class RealtimeFeedback:
    """실시간 피드백 클래스"""
    
    def __init__(self):
        """초기화"""
        # 피드백 히스토리
        self.pitch_history = deque(maxlen=30)
        self.volume_history = deque(maxlen=30)
        self.accuracy_history = deque(maxlen=30)
        
        # 피드백 상태
        self.current_feedback = {}
        self.last_feedback_time = time.time()
        self.feedback_interval = 0.5
        
        # 격려 메시지
        self.encouragement_messages = [
            "좋습니다! 계속해보세요! 💪",
            "훌륭해요! 🎉", 
            "잘하고 있어요! 👏",
            "점점 나아지고 있습니다! ✨"
        ]
    
    def process_realtime_analysis(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """실시간 분석 결과 처리"""
        try:
            current_time = time.time()
            
            # 히스토리 업데이트
            self._update_history(analysis_result)
            
            # 피드백 생성
            if current_time - self.last_feedback_time >= self.feedback_interval:
                feedback = self._generate_realtime_feedback(analysis_result)
                self.current_feedback = feedback
                self.last_feedback_time = current_time
                return feedback
            else:
                return self.current_feedback
                
        except Exception as e:
            return {'error': f'실시간 피드백 처리 실패: {e}'}
    
    def _update_history(self, analysis_result: Dict[str, Any]):
        """분석 히스토리 업데이트"""
        try:
            pitch_info = analysis_result.get('pitch', {})
            if 'frequency' in pitch_info:
                self.pitch_history.append({
                    'frequency': pitch_info['frequency'],
                    'stability': pitch_info.get('stability', 0),
                    'timestamp': time.time()
                })
            
            volume_info = analysis_result.get('volume', {})
            if 'normalized' in volume_info:
                self.volume_history.append({
                    'normalized': volume_info['normalized'],
                    'timestamp': time.time()
                })
            
            comparison_info = analysis_result.get('comparison', {})
            if 'accuracy' in comparison_info:
                self.accuracy_history.append({
                    'accuracy': comparison_info['accuracy'],
                    'timestamp': time.time()
                })
                
        except Exception as e:
            print(f"히스토리 업데이트 오류: {e}")
    
    def _generate_realtime_feedback(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """실시간 피드백 생성"""
        try:
            feedback = {
                'timestamp': time.time(),
                'messages': [],
                'suggestions': [],
                'scores': {}
            }
            
            # 음정 피드백
            pitch_info = analysis_result.get('pitch', {})
            comparison_info = analysis_result.get('comparison', {})
            
            if 'accuracy' in comparison_info:
                accuracy = comparison_info['accuracy']
                if accuracy >= 0.8:
                    feedback['messages'].append("🎯 좋은 음정입니다!")
                elif accuracy >= 0.6:
                    feedback['messages'].append("👍 괜찮은 음정이에요")
                else:
                    feedback['messages'].append("🎵 음정을 조금 더 맞춰보세요")
                
                feedback['scores']['pitch'] = accuracy
            
            # 음량 피드백
            volume_info = analysis_result.get('volume', {})
            if 'normalized' in volume_info:
                volume = volume_info['normalized']
                if volume < 0.2:
                    feedback['messages'].append("🔉 조금 더 크게 불러보세요")
                elif volume > 0.8:
                    feedback['messages'].append("🔊 조금 작게 불러보세요")
                else:
                    feedback['messages'].append("👍 좋은 음량이에요")
                
                feedback['scores']['volume'] = min(1.0, volume * 2)
            
            return feedback
            
        except Exception as e:
            return {'error': f'피드백 생성 실패: {e}'}
    
    def reset_session(self):
        """세션 초기화"""
        self.pitch_history.clear()
        self.volume_history.clear()
        self.accuracy_history.clear()
        self.current_feedback = {}
        print("✅ 피드백 세션이 초기화되었습니다.")
