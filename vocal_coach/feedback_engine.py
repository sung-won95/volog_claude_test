"""
피드백 엔진 모듈
분석 결과를 바탕으로 교육학적 피드백을 생성하는 기능 제공
"""

import numpy as np
from typing import Dict, Any, List
import random

class FeedbackEngine:
    """피드백 생성 엔진 클래스"""
    
    def __init__(self):
        """초기화"""
        pass
        
    def generate_feedback(self, analysis_result: Dict[str, Any], 
                         section_info: Dict[str, Any]) -> Dict[str, Any]:
        """분석 결과를 바탕으로 피드백 생성"""
        try:
            scores = analysis_result.get('scores', {})
            
            feedbacks = []
            recommendations = []
            
            # 1. 음정 피드백
            pitch_feedback = self._generate_pitch_feedback(
                scores.get('pitch', 0.5),
                analysis_result.get('pitch_analysis', {})
            )
            if pitch_feedback:
                feedbacks.extend(pitch_feedback['feedbacks'])
                recommendations.extend(pitch_feedback['recommendations'])
            
            # 2. 호흡 피드백
            breath_feedback = self._generate_breath_feedback(
                scores.get('breath', 0.5),
                analysis_result.get('breath_analysis', {})
            )
            if breath_feedback:
                feedbacks.extend(breath_feedback['feedbacks'])
                recommendations.extend(breath_feedback['recommendations'])
            
            # 3. 발음 피드백
            pronunciation_feedback = self._generate_pronunciation_feedback(
                scores.get('pronunciation', 0.5),
                analysis_result.get('pronunciation_analysis', {})
            )
            if pronunciation_feedback:
                feedbacks.extend(pronunciation_feedback['feedbacks'])
                recommendations.extend(pronunciation_feedback['recommendations'])
            
            # 4. 성대 접촉 피드백
            vocal_onset_feedback = self._generate_vocal_onset_feedback(
                scores.get('vocal_onset', 0.5),
                analysis_result.get('vocal_onset_analysis', {})
            )
            if vocal_onset_feedback:
                feedbacks.extend(vocal_onset_feedback['feedbacks'])
                recommendations.extend(vocal_onset_feedback['recommendations'])
            
            # 5. 종합 피드백
            overall_feedback = self._generate_overall_feedback(scores, section_info)
            
            feedback_result = {
                'feedbacks': feedbacks,
                'recommendations': recommendations,
                'overall_feedback': overall_feedback,
                'encouragement': self._generate_encouragement(scores),
                'next_steps': self._generate_next_steps(scores, section_info)
            }
            
            return feedback_result
            
        except Exception as e:
            return {
                'feedbacks': [f"피드백 생성 중 오류가 발생했습니다: {e}"],
                'recommendations': ["다시 시도해 보세요."],
                'overall_feedback': "분석을 완료했습니다.",
                'encouragement': "계속 연습하시면 더 좋아질 거예요!",
                'next_steps': ["다음 구간으로 이동하세요."]
            }
    
    def _generate_pitch_feedback(self, pitch_score: float, 
                                pitch_analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """음정 피드백 생성"""
        feedbacks = []
        recommendations = []
        
        accuracy = pitch_analysis.get('accuracy', 0.5)
        stability = pitch_analysis.get('stability', 0.5)
        
        # 음정 정확도 피드백
        if accuracy < 0.6:
            feedbacks.append("음정이 목표와 많이 다릅니다. 목표 멜로디를 다시 들어보고 천천히 따라해보세요.")
            recommendations.append("피아노나 앱으로 목표 음을 먼저 확인한 후 연습하기")
        elif accuracy < 0.8:
            feedbacks.append("음정이 대체로 정확하지만 일부 구간에서 벗어납니다.")
            recommendations.append("어려운 구간을 반복 연습하기")
        else:
            feedbacks.append("음정이 매우 정확합니다! 훌륭해요.")
        
        # 음정 안정성 피드백
        if stability < 0.6:
            feedbacks.append("음정이 흔들리는 경향이 있습니다. 더 안정적으로 유지해보세요.")
            recommendations.append("긴 음표를 연습하여 음정 안정성 향상하기")
            recommendations.append("립 트릴(lip trill) 연습으로 호흡과 음정 안정성 기르기")
        elif stability < 0.8:
            feedbacks.append("음정 안정성이 괜찮지만 조금 더 안정적으로 할 수 있어요.")
        else:
            feedbacks.append("음정이 매우 안정적입니다!")
        
        return {'feedbacks': feedbacks, 'recommendations': recommendations}
    
    def _generate_breath_feedback(self, breath_score: float, 
                                 breath_analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """호흡 피드백 생성"""
        feedbacks = []
        recommendations = []
        
        volume_consistency = breath_analysis.get('volume_consistency', 0.5)
        sustainability = breath_analysis.get('sustainability', 0.5)
        
        # 음량 일관성 피드백
        if volume_consistency < 0.6:
            feedbacks.append("음량이 일정하지 않습니다. 호흡을 더 꾸준히 유지해보세요.")
            recommendations.append("복식호흡 연습하기")
            recommendations.append("긴 'ㅅ' 소리로 호흡 조절 연습하기")
        elif volume_consistency < 0.8:
            feedbacks.append("음량이 대체로 일정하지만 약간의 변화가 있습니다.")
        else:
            feedbacks.append("음량이 매우 일정합니다! 좋은 호흡 조절이에요.")
        
        # 지속성 피드백
        if sustainability < 0.6:
            feedbacks.append("음을 끝까지 유지하는 데 어려움이 있습니다.")
            recommendations.append("호흡량을 늘리는 연습하기")
            recommendations.append("짧은 구간부터 시작해서 점차 길게 연습하기")
        elif sustainability < 0.8:
            feedbacks.append("음의 지속성이 괜찮습니다.")
        else:
            feedbacks.append("음을 끝까지 잘 유지합니다!")
        
        return {'feedbacks': feedbacks, 'recommendations': recommendations}
    
    def _generate_pronunciation_feedback(self, pronunciation_score: float,
                                       pronunciation_analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """발음 피드백 생성"""
        feedbacks = []
        recommendations = []
        
        clarity_score = pronunciation_analysis.get('clarity_score', 0.5)
        
        if clarity_score < 0.6:
            feedbacks.append("발음이 명확하지 않습니다. 입 모양과 혀의 위치를 더 정확히 해보세요.")
            recommendations.append("거울을 보며 입 모양 연습하기")
            recommendations.append("자음과 모음을 과장되게 발음하는 연습하기")
        elif clarity_score < 0.8:
            feedbacks.append("발음이 대체로 명확하지만 더 선명하게 할 수 있어요.")
            recommendations.append("딕션 연습하기")
        else:
            feedbacks.append("발음이 매우 명확합니다!")
        
        return {'feedbacks': feedbacks, 'recommendations': recommendations}
    
    def _generate_vocal_onset_feedback(self, vocal_onset_score: float,
                                     vocal_onset_analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """성대 접촉 피드백 생성"""
        feedbacks = []
        recommendations = []
        
        onset_type = vocal_onset_analysis.get('onset_type', 'normal')
        onset_quality = vocal_onset_analysis.get('onset_quality', 0.5)
        
        if onset_quality < 0.5:
            if onset_type == 'hard':
                feedbacks.append("음을 너무 강하게 시작하고 있습니다. 더 부드럽게 시작해보세요.")
                recommendations.append("'ㅎ' 소리를 살짝 넣어서 부드럽게 시작하는 연습하기")
            elif onset_type == 'breathy':
                feedbacks.append("목소리에 바람 소리가 많이 섞여 있습니다. 성대를 더 명확하게 붙여보세요.")
                recommendations.append("'아!' 소리를 끊어서 내는 연습하기")
            else:
                feedbacks.append("음의 시작이 불안정합니다.")
                recommendations.append("천천히 부드럽게 음을 시작하는 연습하기")
        elif onset_quality < 0.7:
            feedbacks.append("음의 시작이 괜찮지만 더 부드럽게 할 수 있어요.")
        else:
            feedbacks.append("음을 부드럽고 안정적으로 시작합니다!")
        
        return {'feedbacks': feedbacks, 'recommendations': recommendations}
    
    def _generate_overall_feedback(self, scores: Dict[str, float], 
                                 section_info: Dict[str, Any]) -> str:
        """종합 피드백 생성"""
        overall_score = np.mean(list(scores.values()))
        section_name = section_info.get('name', '이 구간')
        
        if overall_score >= 0.8:
            return f"{section_name}을 훌륭하게 소화했습니다! 모든 요소가 우수합니다."
        elif overall_score >= 0.7:
            return f"{section_name}을 잘 부르셨습니다. 몇 가지 개선점만 보완하면 완벽해요."
        elif overall_score >= 0.6:
            return f"{section_name}을 무난하게 부르셨습니다. 조금 더 연습하면 훨씬 나아질 거예요."
        elif overall_score >= 0.5:
            return f"{section_name}에서 아직 개선할 점들이 있습니다. 천천히 연습해보세요."
        else:
            return f"{section_name}이 조금 어려우신 것 같아요. 기본기부터 차근차근 연습해보시죠."
    
    def _generate_encouragement(self, scores: Dict[str, float]) -> str:
        """격려 메시지 생성"""
        overall_score = np.mean(list(scores.values()))
        
        encouragements = {
            'excellent': [
                "정말 훌륭합니다! 계속 이런 식으로 연습하세요!",
                "완벽한 연주였어요! 재능이 보입니다!",
                "프로 수준이에요! 자신감을 가지세요!"
            ],
            'good': [
                "잘하고 계세요! 조금만 더 연습하면 완벽해질 거예요!",
                "좋은 실력이에요! 꾸준히 하시면 더욱 늘 거예요!",
                "발전이 눈에 보입니다! 계속 화이팅!"
            ],
            'average': [
                "좋은 시작이에요! 포기하지 말고 계속 연습해보세요!",
                "연습할수록 늘 거예요! 꾸준히 하는 게 중요해요!",
                "기본기가 쌓이고 있어요! 조금씩 발전하고 있습니다!"
            ],
            'needs_improvement': [
                "괜찮아요! 모든 사람은 처음엔 어려워해요. 천천히 해보세요!",
                "연습이 곧 실력이에요! 조급해하지 마세요!",
                "지금은 기초를 다지는 시간이에요. 차근차근 해보세요!"
            ]
        }
        
        if overall_score >= 0.8:
            category = 'excellent'
        elif overall_score >= 0.7:
            category = 'good'
        elif overall_score >= 0.5:
            category = 'average'
        else:
            category = 'needs_improvement'
        
        return random.choice(encouragements[category])
    
    def _generate_next_steps(self, scores: Dict[str, float],
                           section_info: Dict[str, Any]) -> List[str]:
        """다음 단계 제안"""
        next_steps = []
        overall_score = np.mean(list(scores.values()))
        
        if overall_score >= 0.8:
            next_steps.append("이 구간을 마스터했습니다! 다음 구간으로 넘어가세요.")
            next_steps.append("더 어려운 구간에 도전해보세요.")
        elif overall_score >= 0.7:
            next_steps.append("거의 완성되었습니다! 한두 번 더 연습 후 다음 구간으로 넘어가세요.")
        elif overall_score >= 0.6:
            next_steps.append("기본은 잘 되어 있어요. 세부사항을 더 연습해보세요.")
        else:
            next_steps.append("이 구간을 더 연습하세요.")
            next_steps.append("기본기 연습을 병행하세요.")
        
        return next_steps
