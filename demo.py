#!/usr/bin/env python3
"""
AI 보컬 코치 데모 스크립트
주요 기능들을 간단히 테스트해볼 수 있습니다.
"""

import sys
import numpy as np
from vocal_coach.ai_vocal_coach import AIVocalCoach

def demo_analysis():
    """분석 기능 데모"""
    print("🎵 AI 보컬 코치 - 분석 기능 데모")
    print("=" * 50)
    
    # AI 보컬 코치 인스턴스 생성
    coach = AIVocalCoach()
    coach.demo_mode = True
    
    # 데모 데이터 생성
    print("📊 데모 데이터 생성 중...")
    coach._generate_demo_data()
    
    # 분석 결과 표시
    coach.show_analysis_summary()
    
    return coach

def demo_practice_session(coach):
    """연습 세션 데모"""
    print("\n🎯 연습 세션 데모")
    print("=" * 50)
    
    # 연습 구간 표시
    coach.show_practice_sections()
    
    # 첫 번째 구간으로 자동 연습
    if coach.practice_sections:
        section = coach.practice_sections[0]
        print(f"\n🎤 자동 연습: {section['name']}")
        
        # 가상 녹음 데이터 생성
        from vocal_coach.voice_recorder import VoiceRecorder
        recorder = VoiceRecorder()
        recorded_audio = recorder.record_section(section['duration'], countdown=1)
        
        if recorded_audio:
            # 음성 분석
            from vocal_coach.voice_analyzer import VoiceAnalyzer
            analyzer = VoiceAnalyzer()
            analysis_result = analyzer.analyze_voice(recorded_audio, section['melody'])
            
            # 피드백 생성
            from vocal_coach.feedback_engine import FeedbackEngine
            feedback_engine = FeedbackEngine()
            feedback = feedback_engine.generate_feedback(analysis_result, section)
            
            # 결과 표시
            print("\n📋 분석 결과:")
            scores = analysis_result.get('scores', {})
            for category, score in scores.items():
                category_korean = {
                    'pitch': '음정',
                    'breath': '호흡', 
                    'pronunciation': '발음',
                    'vocal_onset': '성대 접촉'
                }.get(category, category)
                print(f"  {category_korean}: {score*100:.1f}점")
            
            print(f"\n💬 종합 피드백:")
            print(f"  {feedback['overall_feedback']}")
            
            print(f"\n🎉 격려 메시지:")
            print(f"  {feedback['encouragement']}")
            
            if feedback['recommendations']:
                print(f"\n💡 추천 연습:")
                for i, rec in enumerate(feedback['recommendations'][:3], 1):
                    print(f"  {i}. {rec}")

def demo_visualization():
    """시각화 데모"""
    print("\n📊 시각화 기능 데모")
    print("=" * 50)
    
    try:
        import matplotlib.pyplot as plt
        
        # 간단한 멜로디 시각화
        time = np.linspace(0, 5, 100)
        freq1 = 261.63 * (1 + 0.1 * np.sin(2 * np.pi * 0.5 * time))  # 목표
        freq2 = 261.63 * (1 + 0.08 * np.sin(2 * np.pi * 0.6 * time) + 0.02 * np.random.randn(100))  # 사용자
        
        plt.figure(figsize=(10, 6))
        plt.subplot(2, 1, 1)
        plt.plot(time, freq1, 'b-', label='목표 멜로디', linewidth=2)
        plt.plot(time, freq2, 'r-', label='사용자 음성', linewidth=2, alpha=0.8)
        plt.ylabel('주파수 (Hz)')
        plt.title('멜로디 비교')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.subplot(2, 1, 2)
        scores = [0.75, 0.68, 0.82, 0.71]
        categories = ['음정', '호흡', '발음', '성대 접촉']
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        bars = plt.bar(categories, [s*100 for s in scores], color=colors, alpha=0.7)
        plt.ylabel('점수')
        plt.title('카테고리별 점수')
        plt.ylim(0, 100)
        
        for bar, score in zip(bars, scores):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'{score*100:.1f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.show()
        
        print("✅ 시각화 완료! 그래프를 확인하세요.")
        
    except ImportError:
        print("❌ matplotlib이 설치되지 않아 시각화를 건너뜁니다.")
    except Exception as e:
        print(f"❌ 시각화 오류: {e}")

def main():
    """메인 데모 함수"""
    print("🎪 AI 보컬 코치 프로토타입 데모")
    print("=" * 60)
    print("이 데모는 AI 보컬 코치의 주요 기능들을 보여줍니다.")
    print("실제 마이크 입력 없이도 모든 기능을 체험할 수 있습니다.")
    print("=" * 60)
    
    try:
        # 1. 분석 기능 데모
        coach = demo_analysis()
        
        # 2. 연습 세션 데모
        demo_practice_session(coach)
        
        # 3. 시각화 데모
        demo_visualization()
        
        print("\n" + "=" * 60)
        print("🎊 데모 완료!")
        print("실제 사용을 위해서는 'python main.py'를 실행하세요.")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n👋 데모를 중단합니다.")
    except Exception as e:
        print(f"\n❌ 데모 실행 중 오류: {e}")
        print("의존성이 모두 설치되었는지 확인해주세요.")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()
