"""
AI 보컬 코치 메인 클래스
노래 분석, 연습 구간 관리, 피드백 생성 기능 제공
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Optional
import time

from .audio_processor import AudioProcessor
from .melody_analyzer import MelodyAnalyzer
from .beat_detector import BeatDetector
from .section_divider import SectionDivider
from .voice_recorder import VoiceRecorder
from .voice_analyzer import VoiceAnalyzer
from .feedback_engine import FeedbackEngine
from .section_selector import SectionSelector

class AIVocalCoach:
    """AI 보컬 코치 메인 클래스"""
    
    def __init__(self):
        """초기화"""
        # 각 모듈 인스턴스 생성
        self.audio_processor = AudioProcessor()
        self.melody_analyzer = MelodyAnalyzer()
        self.beat_detector = BeatDetector()
        self.section_divider = SectionDivider()
        self.voice_recorder = VoiceRecorder()
        self.voice_analyzer = VoiceAnalyzer()
        self.feedback_engine = FeedbackEngine()
        self.section_selector = SectionSelector()
        
        # 노래 데이터
        self.song_data = None
        self.melody_data = None
        self.beat_data = None
        self.practice_sections = []
        
        # 데모 모드
        self.demo_mode = False
        
    def load_song(self, song_path: str) -> bool:
        """
        노래 파일 로드 및 초기 분석
        
        Args:
            song_path: 노래 파일 경로
            
        Returns:
            성공 여부
        """
        try:
            print(f"🎵 노래 로드 중: {song_path}")
            
            # 1. 오디오 파일 로드
            self.song_data = self.audio_processor.load_audio(song_path)
            if self.song_data is None:
                return False
            
            # 2. 멜로디 추출
            print("🎼 멜로디 분석 중...")
            self.melody_data = self.melody_analyzer.extract_melody(self.song_data)
            
            # 3. 박자 및 템포 감지
            print("🥁 박자 분석 중...")
            self.beat_data = self.beat_detector.detect_beats(self.song_data)
            
            # 4. 연습 구간 분할
            print("📏 구간 분할 중...")
            self.practice_sections = self.section_divider.divide_sections(
                self.song_data, self.beat_data, self.melody_data
            )
            
            print(f"✅ 분석 완료! {len(self.practice_sections)}개 연습 구간 생성")
            return True
            
        except Exception as e:
            print(f"❌ 노래 로드 실패: {e}")
            return False
    
    def _generate_demo_data(self):
        """데모용 가상 데이터 생성"""
        print("🎪 데모 모드 - 가상 데이터 생성 중...")
        
        # 가상 노래 데이터
        duration = 30.0  # 30초
        sample_rate = 22050
        
        self.song_data = {
            'audio': np.random.randn(int(duration * sample_rate)) * 0.1,
            'sr': sample_rate,
            'duration': duration,
            'filename': 'demo_song.wav'
        }
        
        # 가상 멜로디 데이터 (C4-C5 범위의 간단한 멜로디)
        time_frames = np.linspace(0, duration, 100)
        base_freq = 261.63  # C4
        melody_pattern = [1.0, 1.125, 1.25, 1.33, 1.5, 1.33, 1.25, 1.125]  # C-D-E-F-G-F-E-D
        
        pitch_values = []
        for i, t in enumerate(time_frames):
            pattern_idx = int((i / len(time_frames)) * len(melody_pattern))
            pattern_idx = min(pattern_idx, len(melody_pattern) - 1)
            freq = base_freq * melody_pattern[pattern_idx]
            pitch_values.append(freq)
        
        self.melody_data = {
            'times': time_frames,
            'frequencies': np.array(pitch_values),
            'confidence': np.ones_like(time_frames) * 0.8
        }
        
        # 가상 박자 데이터 (120 BPM)
        bpm = 120
        beat_interval = 60.0 / bpm
        beat_times = np.arange(0, duration, beat_interval)
        
        self.beat_data = {
            'tempo': bpm,
            'beat_times': beat_times,
            'time_signature': (4, 4),
            'beats_per_measure': 4
        }
        
        # 가상 연습 구간 생성 (4마디씩)
        measures_per_section = 4
        beats_per_measure = 4
        beats_per_section = measures_per_section * beats_per_measure
        
        self.practice_sections = []
        section_idx = 0
        
        for i in range(0, len(beat_times), beats_per_section):
            if i + beats_per_section <= len(beat_times):
                start_time = beat_times[i]
                end_time = beat_times[i + beats_per_section - 1] + beat_interval
                
                # 해당 구간의 멜로디 데이터 추출
                mask = (time_frames >= start_time) & (time_frames < end_time)
                section_melody = {
                    'times': time_frames[mask] - start_time,  # 상대 시간으로 변환
                    'frequencies': np.array(pitch_values)[mask],
                    'confidence': np.ones(np.sum(mask)) * 0.8
                }
                
                section = {
                    'id': section_idx,
                    'name': f"구간 {section_idx + 1} (마디 {i//beats_per_measure + 1}-{(i + beats_per_section)//beats_per_measure})",
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': end_time - start_time,
                    'melody': section_melody,
                    'difficulty': 'easy' if section_idx < 2 else 'medium'
                }
                
                self.practice_sections.append(section)
                section_idx += 1
        
        print(f"✅ 데모 데이터 생성 완료! {len(self.practice_sections)}개 연습 구간")
    
    def show_practice_sections(self):
        """연습 구간 목록 표시"""
        if not self.practice_sections:
            print("❌ 연습 구간이 없습니다. 먼저 노래를 로드하세요.")
            return
        
        print(f"\n📋 연습 구간 목록 ({len(self.practice_sections)}개):")
        print("-" * 60)
        
        for section in self.practice_sections:
            duration = section['duration']
            difficulty = section.get('difficulty', 'medium')
            difficulty_emoji = {'easy': '🟢', 'medium': '🟡', 'hard': '🔴'}.get(difficulty, '🟡')
            
            print(f"{section['id'] + 1:2d}. {section['name']}")
            print(f"    시간: {section['start_time']:.1f}s - {section['end_time']:.1f}s ({duration:.1f}초)")
            print(f"    난이도: {difficulty_emoji} {difficulty}")
            print()
    
    def practice_section(self):
        """특정 구간 연습하기"""
        if not self.practice_sections:
            print("❌ 연습 구간이 없습니다.")
            return
        
        # 구간 선택
        self.show_practice_sections()
        
        while True:
            try:
                choice = input(f"연습할 구간 선택 (1-{len(self.practice_sections)}): ").strip()
                section_idx = int(choice) - 1
                
                if 0 <= section_idx < len(self.practice_sections):
                    break
                else:
                    print(f"1부터 {len(self.practice_sections)} 사이의 숫자를 입력하세요.")
            except ValueError:
                print("숫자를 입력하세요.")
        
        selected_section = self.practice_sections[section_idx]
        
        print(f"\n🎯 선택된 구간: {selected_section['name']}")
        print(f"⏱️  시간: {selected_section['duration']:.1f}초")
        
        # 목표 멜로디 시각화
        self._visualize_target_melody(selected_section)
        
        # 연습 진행
        input("\n🎤 준비되면 Enter를 눌러 녹음을 시작하세요...")
        
        # 녹음 실행
        print("🔴 녹음 시작!")
        recorded_audio = self.voice_recorder.record_section(selected_section['duration'])
        
        if recorded_audio is not None:
            print("🔍 음성 분석 중...")
            
            # 사용자 음성 분석
            analysis_result = self.voice_analyzer.analyze_voice(
                recorded_audio, selected_section['melody']
            )
            
            # 피드백 생성
            feedback = self.feedback_engine.generate_feedback(
                analysis_result, selected_section
            )
            
            # 결과 표시
            self._show_practice_result(analysis_result, feedback, selected_section)
        else:
            print("❌ 녹음에 실패했습니다.")
    
    def _visualize_target_melody(self, section: Dict):
        """목표 멜로디 시각화"""
        try:
            melody = section['melody']
            
            plt.figure(figsize=(12, 6))
            plt.plot(melody['times'], melody['frequencies'], 'b-', linewidth=2, label='목표 멜로디')
            plt.xlabel('시간 (초)')
            plt.ylabel('주파수 (Hz)')
            plt.title(f"{section['name']} - 목표 멜로디")
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print(f"멜로디 시각화 오류: {e}")
    
    def _show_practice_result(self, analysis: Dict, feedback: Dict, section: Dict):
        """연습 결과 표시"""
        print("\n" + "=" * 50)
        print(f"📊 {section['name']} 연습 결과")
        print("=" * 50)
        
        # 점수 표시
        scores = analysis.get('scores', {})
        
        print("\n🎯 점수:")
        for category, score in scores.items():
            score_percent = score * 100
            emoji = self._get_score_emoji(score)
            category_korean = {
                'pitch': '음정',
                'breath': '호흡',
                'pronunciation': '발음',
                'vocal_onset': '성대 접촉'
            }.get(category, category)
            
            print(f"  {emoji} {category_korean}: {score_percent:.1f}점")
        
        # 전체 점수
        total_score = np.mean(list(scores.values())) * 100
        total_emoji = self._get_score_emoji(np.mean(list(scores.values())))
        print(f"\n{total_emoji} 종합 점수: {total_score:.1f}점")
        
        # 피드백 표시
        print("\n💡 피드백:")
        feedbacks = feedback.get('feedbacks', [])
        
        if not feedbacks:
            print("  🎉 훌륭합니다! 모든 요소가 좋습니다.")
        else:
            for i, fb in enumerate(feedbacks, 1):
                print(f"  {i}. {fb}")
        
        # 추천 연습
        recommendations = feedback.get('recommendations', [])
        if recommendations:
            print("\n🏃‍♂️ 추천 연습:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        # 그래프 표시
        self._visualize_comparison(analysis, section)
    
    def _get_score_emoji(self, score: float) -> str:
        """점수에 따른 이모지 반환"""
        if score >= 0.9:
            return "🌟"
        elif score >= 0.8:
            return "🎉"
        elif score >= 0.7:
            return "👏"
        elif score >= 0.6:
            return "👍"
        elif score >= 0.5:
            return "🤔"
        else:
            return "💪"
    
    def _visualize_comparison(self, analysis: Dict, section: Dict):
        """목표 멜로디와 사용자 음성 비교 시각화"""
        try:
            target_melody = section['melody']
            user_melody = analysis.get('pitch_analysis', {})
            
            if 'frequencies' not in user_melody:
                print("시각화할 사용자 음성 데이터가 없습니다.")
                return
            
            plt.figure(figsize=(14, 8))
            
            # 상단: 주파수 비교
            plt.subplot(2, 1, 1)
            plt.plot(target_melody['times'], target_melody['frequencies'], 
                    'b-', linewidth=2, label='목표 멜로디', alpha=0.8)
            plt.plot(user_melody['times'], user_melody['frequencies'], 
                    'r-', linewidth=2, label='사용자 음성', alpha=0.8)
            plt.xlabel('시간 (초)')
            plt.ylabel('주파수 (Hz)')
            plt.title('멜로디 비교')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # 하단: 점수 막대 그래프
            plt.subplot(2, 1, 2)
            scores = analysis.get('scores', {})
            categories = list(scores.keys())
            values = [scores[cat] * 100 for cat in categories]
            
            category_names = {
                'pitch': '음정',
                'breath': '호흡',
                'pronunciation': '발음',
                'vocal_onset': '성대 접촉'
            }
            
            korean_categories = [category_names.get(cat, cat) for cat in categories]
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
            
            bars = plt.bar(korean_categories, values, color=colors[:len(values)], alpha=0.7)
            plt.ylabel('점수')
            plt.title('카테고리별 점수')
            plt.ylim(0, 100)
            
            # 막대 위에 점수 표시
            for bar, value in zip(bars, values):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                        f'{value:.1f}', ha='center', va='bottom')
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print(f"비교 시각화 오류: {e}")
    
    def create_custom_section(self):
        """커스텀 구간 생성하기"""
        if not self.song_data or not self.melody_data or not self.beat_data:
            print("❌ 노래 데이터가 없습니다. 먼저 노래를 로드하세요.")
            return
        
        print("\n🎨 커스텀 구간 만들기")
        print("=" * 50)
        
        # 구간 선택
        custom_section = self.section_selector.select_custom_section(
            self.song_data, self.melody_data, self.beat_data
        )
        
        if custom_section is None:
            print("구간 선택이 취소되었습니다.")
            return
        
        # 미리보기
        self.section_selector.preview_section(custom_section, self.song_data)
        
        # 확인
        confirm = input().strip().lower()
        if confirm in ['y', 'yes', '네', 'ㅇ']:
            # 기존 구간 목록에 추가
            custom_section['id'] = len(self.practice_sections)
            self.practice_sections.append(custom_section)
            
            print(f"✅ 커스텀 구간이 추가되었습니다!")
            print(f"   구간 번호: {len(self.practice_sections)}")
            print(f"   이제 '2. 특정 구간 연습하기'에서 선택할 수 있습니다.")
        else:
            print("커스텀 구간 생성을 취소했습니다.")
    
    def show_analysis_summary(self):
        """전체 분석 결과 요약 표시"""
        if not self.song_data:
            print("❌ 로드된 노래가 없습니다.")
            return
        
        print("\n" + "=" * 60)
        print("📈 전체 분석 결과 요약")
        print("=" * 60)
        
        # 노래 정보
        print(f"\n🎵 노래 정보:")
        if self.demo_mode:
            print(f"  파일명: 데모 노래")
        else:
            print(f"  파일명: {self.song_data.get('filename', '알 수 없음')}")
        print(f"  길이: {self.song_data.get('duration', 0):.1f}초")
        print(f"  샘플레이트: {self.song_data.get('sr', 0)}Hz")
        
        # 박자 정보
        if self.beat_data:
            print(f"\n🥁 박자 정보:")
            print(f"  템포: {self.beat_data.get('tempo', 0):.1f} BPM")
            print(f"  박자표: {self.beat_data.get('time_signature', (4, 4))}")
            print(f"  총 박자 수: {len(self.beat_data.get('beat_times', []))}")
        
        # 멜로디 정보
        if self.melody_data:
            freqs = self.melody_data.get('frequencies', [])
            if len(freqs) > 0:
                print(f"\n🎼 멜로디 정보:")
                print(f"  최저 음: {np.min(freqs):.1f}Hz")
                print(f"  최고 음: {np.max(freqs):.1f}Hz")
                print(f"  평균 음높이: {np.mean(freqs):.1f}Hz")
        
        # 연습 구간 정보
        print(f"\n📏 연습 구간:")
        print(f"  총 구간 수: {len(self.practice_sections)}")
        if self.practice_sections:
            avg_duration = np.mean([s['duration'] for s in self.practice_sections])
            print(f"  평균 구간 길이: {avg_duration:.1f}초")
        
        print("\n💡 시스템 상태: 준비 완료 ✅")
