#!/usr/bin/env python3
"""
AI 보컬 코치 프로토타입 - 메인 실행 파일
"""

import os
import sys
from vocal_coach.ai_vocal_coach import AIVocalCoach

def select_song_file():
    """노래 파일 선택"""
    import glob
    
    # sample_songs 폴더의 오디오 파일 찾기
    audio_extensions = ['*.wav', '*.mp3', '*.flac', '*.m4a', '*.ogg']
    audio_files = []
    
    for ext in audio_extensions:
        audio_files.extend(glob.glob(f"sample_songs/{ext}"))
    
    if not audio_files:
        print("❌ sample_songs 폴더에 오디오 파일이 없습니다.")
        print("💡 다음 형식의 파일을 sample_songs 폴더에 넣어주세요:")
        print("   - WAV, MP3, FLAC, M4A, OGG")
        return None
    
    print("🎵 사용 가능한 노래 파일:")
    for i, file in enumerate(audio_files, 1):
        filename = os.path.basename(file)
        print(f"  {i}. {filename}")
    
    print(f"  {len(audio_files) + 1}. 데모 모드 (가상 노래)")
    
    while True:
        try:
            choice = input(f"\n선택하세요 (1-{len(audio_files) + 1}): ").strip()
            choice_idx = int(choice) - 1
            
            if choice_idx == len(audio_files):  # 데모 모드
                return "demo"
            elif 0 <= choice_idx < len(audio_files):
                return audio_files[choice_idx]
            else:
                print(f"1부터 {len(audio_files) + 1} 사이의 숫자를 입력하세요.")
        except ValueError:
            print("숫자를 입력하세요.")

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("AI 보컬 코치 프로토타입 v1.0")
    print("=" * 60)
    
    # AI 보컬 코치 인스턴스 생성
    coach = AIVocalCoach()
    
    # 노래 파일 선택
    selected_file = select_song_file()
    
    if selected_file is None:
        return 1
    
    print(f"\n🎵 노래 로딩 중...")
    
    try:
        if selected_file == "demo":
            print("   (데모용 가상 노래 로드)")
            coach.demo_mode = True
            coach._generate_demo_data()
        else:
            print(f"   파일: {os.path.basename(selected_file)}")
            success = coach.load_song(selected_file)
            if not success:
                print("❌ 노래 로드에 실패했습니다. 데모 모드로 전환합니다.")
                coach.demo_mode = True
                coach._generate_demo_data()
        
        print("✅ 노래 분석 완료!")
        print("📏 연습 구간 준비 완료")
        
        # 메뉴 표시
        while True:
            print("\n" + "=" * 40)
            print("선택하세요:")
            print("1. 연습 구간 목록 보기")
            print("2. 특정 구간 연습하기")
            print("3. 실시간 연습 모드 (NEW!)")
            print("4. 실시간 설정")
            print("5. 커스텀 구간 만들기")
            print("6. 전체 분석 결과 보기")
            print("7. 종료")
            print("=" * 40)
            
            choice = input("입력 (1-7): ").strip()
            
            if choice == "1":
                coach.show_practice_sections()
            elif choice == "2":
                coach.practice_section()
            elif choice == "3":
                coach.realtime_practice_mode()
            elif choice == "4":
                coach.configure_realtime_settings()
            elif choice == "5":
                coach.create_custom_section()
            elif choice == "6":
                coach.show_analysis_summary()
            elif choice == "7":
                print("프로그램을 종료합니다.")
                break
            else:
                print("잘못된 입력입니다. (1-7 중 선택)")
                
    except Exception as e:
        print(f"오류 발생: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
