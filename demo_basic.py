#!/usr/bin/env python3
"""
AI 보컬 코치 - 기본 데모 (패키지 설치 없이 실행 가능)
외부 라이브러리 최소 의존성으로 핵심 개념 체험
"""

import random
import time
import sys

def simulate_audio_analysis():
    """오디오 분석 시뮬레이션"""
    print("🎵 가상 노래 분석 중...")
    
    # 가상 노래 정보
    song_info = {
        'title': '데모 노래',
        'duration': 30.0,
        'tempo': 120,
        'key': 'C Major',
        'sections': [
            {'name': '인트로', 'start': 0, 'end': 8, 'difficulty': 'easy'},
            {'name': '1절', 'start': 8, 'end': 16, 'difficulty': 'medium'},
            {'name': '후렴', 'start': 16, 'end': 24, 'difficulty': 'hard'},
            {'name': '아웃트로', 'start': 24, 'end': 30, 'difficulty': 'easy'}
        ]
    }
    
    # 분석 진행 시뮬레이션
    tasks = ['멜로디 추출', '박자 감지', '구간 분할', '난이도 계산']
    for task in tasks:
        print(f"  - {task}...")
        time.sleep(0.5)
    
    print("✅ 분석 완료!")
    return song_info

def simulate_voice_recording(duration):
    """음성 녹음 시뮬레이션"""
    print(f"\n🎤 {duration}초 녹음 시뮬레이션")
    
    # 카운트다운
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(0.5)
    
    print("  🔴 녹음 시작!")
    
    # 진행률 바
    steps = 20
    for i in range(steps + 1):
        progress = i / steps
        bar_length = 30
        filled = int(bar_length * progress)
        bar = '█' * filled + '░' * (bar_length - filled)
        elapsed = duration * progress
        
        print(f"\r  [{bar}] {progress*100:.1f}% ({elapsed:.1f}s/{duration:.1f}s)", end='')
        time.sleep(duration / steps)
    
    print("\n  🔴 녹음 완료!")

def analyze_performance():
    """성능 분석 시뮬레이션"""
    print("\n🔍 음성 분석 중...")
    time.sleep(1)
    
    # 랜덤 점수 생성 (현실적인 범위)
    scores = {
        '음정': random.uniform(60, 90),
        '호흡': random.uniform(55, 85), 
        '발음': random.uniform(50, 80),
        '성대 접촉': random.uniform(60, 85)
    }
    
    return scores

def generate_feedback(scores):
    """피드백 생성"""
    feedback_templates = {
        '음정': {
            'excellent': "음정이 매우 정확합니다! 완벽해요!",
            'good': "음정이 대체로 정확합니다. 조금만 더 연습하면 완벽해질 거예요!",
            'average': "음정이 약간 불안정합니다. 목표 음을 다시 들어보고 연습해보세요.",
            'poor': "음정 연습이 더 필요해 보입니다. 피아노와 함께 연습해보세요."
        },
        '호흡': {
            'excellent': "호흡이 매우 안정적입니다! 프로 수준이에요!",
            'good': "호흡이 안정적입니다. 좋은 호흡 지지력을 보여주고 있어요!",
            'average': "호흡이 약간 불안정합니다. 복식호흡을 연습해보세요.",
            'poor': "호흡 연습이 필요합니다. 긴 'ㅅ' 소리로 호흡 조절을 연습해보세요."
        },
        '발음': {
            'excellent': "발음이 매우 명확합니다! 훌륭해요!",
            'good': "발음이 명확합니다. 좋은 딕션을 보여주고 있어요!",
            'average': "발음을 더 명확하게 해보세요. 입 모양에 신경써보세요.",
            'poor': "발음 연습이 필요합니다. 거울을 보며 입 모양을 확인해보세요."
        },
        '성대 접촉': {
            'excellent': "음을 부드럽고 안정적으로 시작합니다! 완벽해요!",
            'good': "음의 시작이 안정적입니다. 좋은 성대 사용법이에요!",
            'average': "음의 시작이 약간 불안정합니다. 더 부드럽게 시작해보세요.",
            'poor': "성대 접촉 연습이 필요합니다. 'ㅎ' 소리로 부드럽게 시작하는 연습을 해보세요."
        }
    }
    
    feedbacks = []
    recommendations = []
    
    for category, score in scores.items():
        if score >= 85:
            level = 'excellent'
        elif score >= 75:
            level = 'good' 
        elif score >= 60:
            level = 'average'
        else:
            level = 'poor'
        
        feedbacks.append(feedback_templates[category][level])
        
        if score < 70:
            if category == '음정':
                recommendations.append("스케일 연습으로 음정 감각 기르기")
            elif category == '호흡':
                recommendations.append("복식호흡과 립 트릴 연습하기")
            elif category == '발음':
                recommendations.append("거울 보며 입 모양 연습하기")
            elif category == '성대 접촉':
                recommendations.append("부드러운 음의 시작 연습하기")
    
    return feedbacks, recommendations

def get_score_emoji(score):
    """점수에 따른 이모지"""
    if score >= 90:
        return "🌟"
    elif score >= 80:
        return "🎉"
    elif score >= 70:
        return "👏"
    elif score >= 60:
        return "👍"
    elif score >= 50:
        return "🤔"
    else:
        return "💪"

def show_results(scores, feedbacks, recommendations):
    """결과 표시"""
    print("\n" + "=" * 50)
    print("📊 연습 결과")
    print("=" * 50)
    
    # 점수 표시
    print("\n🎯 점수:")
    for category, score in scores.items():
        emoji = get_score_emoji(score)
        print(f"  {emoji} {category}: {score:.1f}점")
    
    # 총점
    total_score = sum(scores.values()) / len(scores)
    total_emoji = get_score_emoji(total_score)
    print(f"\n{total_emoji} 종합 점수: {total_score:.1f}점")
    
    # 피드백
    print(f"\n💡 피드백:")
    for i, feedback in enumerate(feedbacks, 1):
        print(f"  {i}. {feedback}")
    
    # 추천 연습
    if recommendations:
        print(f"\n🏃‍♂️ 추천 연습:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    # 격려 메시지
    if total_score >= 80:
        print(f"\n🎊 정말 훌륭합니다! 계속 이런 식으로 연습하세요!")
    elif total_score >= 70:
        print(f"\n🎉 잘하고 계세요! 조금만 더 연습하면 완벽해질 거예요!")
    elif total_score >= 60:
        print(f"\n👍 좋은 시작이에요! 꾸준히 연습하시면 더욱 늘 거예요!")
    else:
        print(f"\n💪 괜찮아요! 연습이 곧 실력이에요. 천천히 해보세요!")

def main_demo():
    """메인 데모 함수"""
    print("🎪 AI 보컬 코치 - 기본 데모")
    print("=" * 60)
    print("⚠️  이 데모는 패키지 설치 없이 핵심 개념을 체험할 수 있습니다.")
    print("💡 실제 기능을 사용하려면 main.py를 실행하세요.")
    print("=" * 60)
    
    try:
        # 1. 노래 분석 시뮬레이션
        song_info = simulate_audio_analysis()
        
        print(f"\n📋 분석된 노래 정보:")
        print(f"  제목: {song_info['title']}")
        print(f"  길이: {song_info['duration']}초")
        print(f"  템포: {song_info['tempo']} BPM")
        print(f"  조성: {song_info['key']}")
        
        print(f"\n📏 연습 구간:")
        for i, section in enumerate(song_info['sections'], 1):
            difficulty_emoji = {'easy': '🟢', 'medium': '🟡', 'hard': '🔴'}[section['difficulty']]
            print(f"  {i}. {section['name']} ({section['start']}-{section['end']}초) {difficulty_emoji}")
        
        # 2. 구간 선택
        print(f"\n🎯 연습할 구간을 선택하세요:")
        while True:
            try:
                choice = input(f"구간 선택 (1-{len(song_info['sections'])}): ").strip()
                section_idx = int(choice) - 1
                if 0 <= section_idx < len(song_info['sections']):
                    break
                else:
                    print(f"1부터 {len(song_info['sections'])} 사이의 숫자를 입력하세요.")
            except ValueError:
                print("숫자를 입력하세요.")
        
        selected_section = song_info['sections'][section_idx]
        duration = selected_section['end'] - selected_section['start']
        
        print(f"\n✅ 선택된 구간: {selected_section['name']}")
        print(f"⏱️  길이: {duration}초")
        print(f"📈 난이도: {selected_section['difficulty']}")
        
        # 3. 연습 시작
        input("\n🎤 준비되면 Enter를 눌러 연습을 시작하세요...")
        
        # 4. 녹음 시뮬레이션
        simulate_voice_recording(duration)
        
        # 5. 분석
        scores = analyze_performance()
        
        # 6. 피드백 생성
        feedbacks, recommendations = generate_feedback(scores)
        
        # 7. 결과 표시
        show_results(scores, feedbacks, recommendations)
        
        # 8. 다음 단계 안내
        print(f"\n" + "=" * 60)
        print(f"🚀 다음 단계:")
        print(f"1. pip install -r requirements_minimal.txt")
        print(f"2. python main.py")
        print(f"3. 실제 노래 파일로 연습하기!")
        print(f"=" * 60)
        
    except KeyboardInterrupt:
        print(f"\n\n👋 데모를 중단합니다.")
    except Exception as e:
        print(f"\n❌ 데모 실행 중 오류: {e}")

if __name__ == "__main__":
    main_demo()
