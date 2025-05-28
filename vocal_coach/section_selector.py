"""
구간 선택 모듈
사용자가 원하는 특정 구간을 선택하고 커스터마이징하는 기능 제공
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple

class SectionSelector:
    """구간 선택 및 커스터마이징 클래스"""
    
    def __init__(self):
        """초기화"""
        pass
    
    def select_custom_section(self, song_data: Dict[str, Any], 
                            melody_data: Dict[str, Any],
                            beat_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        사용자 정의 구간 선택
        
        Args:
            song_data: 노래 데이터
            melody_data: 멜로디 데이터  
            beat_data: 박자 데이터
            
        Returns:
            선택된 구간 정보
        """
        try:
            total_duration = song_data.get('duration', 30.0)
            
            print(f"\n🎯 커스텀 구간 선택")
            print(f"전체 노래 길이: {total_duration:.1f}초")
            print("-" * 40)
            
            # 선택 방법 제시
            print("구간 선택 방법:")
            print("1. 시간으로 선택 (예: 30초-45초)")
            print("2. 마디로 선택 (예: 1마디-4마디)")  
            print("3. 자동 분할된 구간에서 선택")
            
            while True:
                try:
                    method = input("\n선택 방법 (1-3): ").strip()
                    
                    if method == "1":
                        return self._select_by_time(song_data, melody_data, beat_data)
                    elif method == "2":
                        return self._select_by_measures(song_data, melody_data, beat_data)
                    elif method == "3":
                        return self._select_from_auto_sections(song_data, melody_data, beat_data)
                    else:
                        print("1, 2, 3 중 하나를 선택하세요.")
                        
                except KeyboardInterrupt:
                    print("\n선택을 취소합니다.")
                    return None
                    
        except Exception as e:
            print(f"❌ 구간 선택 실패: {e}")
            return None
    
    def _select_by_time(self, song_data: Dict[str, Any], 
                       melody_data: Dict[str, Any],
                       beat_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """시간 기반 구간 선택"""
        total_duration = song_data.get('duration', 30.0)
        
        print(f"\n⏰ 시간 기반 구간 선택")
        print(f"전체 길이: 0초 ~ {total_duration:.1f}초")
        
        try:
            # 시작 시간 입력
            while True:
                start_input = input("시작 시간 (초): ").strip()
                try:
                    start_time = float(start_input)
                    if 0 <= start_time < total_duration:
                        break
                    else:
                        print(f"0 ~ {total_duration:.1f} 범위의 시간을 입력하세요.")
                except ValueError:
                    print("숫자를 입력하세요.")
            
            # 끝 시간 입력
            while True:
                end_input = input(f"끝 시간 (초, {start_time}초 이후): ").strip()
                try:
                    end_time = float(end_input)
                    if start_time < end_time <= total_duration:
                        break
                    else:
                        print(f"{start_time} ~ {total_duration:.1f} 범위의 시간을 입력하세요.")
                except ValueError:
                    print("숫자를 입력하세요.")
            
            # 구간 생성
            section = self._create_custom_section(
                start_time, end_time, song_data, melody_data, beat_data, 
                f"커스텀 구간 ({start_time:.1f}s-{end_time:.1f}s)"
            )
            
            return section
            
        except KeyboardInterrupt:
            return None
    
    def _select_by_measures(self, song_data: Dict[str, Any],
                           melody_data: Dict[str, Any], 
                           beat_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """마디 기반 구간 선택"""
        measure_positions = beat_data.get('measure_positions', [])
        beats_per_measure = beat_data.get('beats_per_measure', 4)
        
        if len(measure_positions) < 2:
            print("❌ 마디 정보가 부족합니다. 시간 기반 선택을 사용하세요.")
            return self._select_by_time(song_data, melody_data, beat_data)
        
        total_measures = len(measure_positions)
        
        print(f"\n🎼 마디 기반 구간 선택")
        print(f"총 마디 수: {total_measures}마디 ({beats_per_measure}/4 박자)")
        
        # 마디별 시간 정보 표시
        print("\n마디별 시간:")
        for i, pos in enumerate(measure_positions[:10]):  # 처음 10마디만 표시
            print(f"  {i+1}마디: {pos:.1f}초")
        if len(measure_positions) > 10:
            print(f"  ... (총 {len(measure_positions)}마디)")
        
        try:
            # 시작 마디 입력
            while True:
                start_input = input(f"\n시작 마디 (1-{total_measures}): ").strip()
                try:
                    start_measure = int(start_input)
                    if 1 <= start_measure <= total_measures:
                        break
                    else:
                        print(f"1 ~ {total_measures} 범위의 마디를 입력하세요.")
                except ValueError:
                    print("숫자를 입력하세요.")
            
            # 끝 마디 입력
            while True:
                end_input = input(f"끝 마디 ({start_measure}-{total_measures}): ").strip()
                try:
                    end_measure = int(end_input)
                    if start_measure <= end_measure <= total_measures:
                        break
                    else:
                        print(f"{start_measure} ~ {total_measures} 범위의 마디를 입력하세요.")
                except ValueError:
                    print("숫자를 입력하세요.")
            
            # 마디를 시간으로 변환
            start_time = measure_positions[start_measure - 1]
            
            if end_measure < len(measure_positions):
                end_time = measure_positions[end_measure]
            else:
                # 마지막 마디인 경우 추정
                tempo = beat_data.get('tempo', 120)
                measure_duration = (60.0 / tempo) * beats_per_measure
                end_time = start_time + (end_measure - start_measure + 1) * measure_duration
                end_time = min(end_time, song_data.get('duration', 30.0))
            
            # 구간 생성
            section = self._create_custom_section(
                start_time, end_time, song_data, melody_data, beat_data,
                f"마디 {start_measure}-{end_measure}"
            )
            
            return section
            
        except KeyboardInterrupt:
            return None
    
    def _select_from_auto_sections(self, song_data: Dict[str, Any],
                                  melody_data: Dict[str, Any],
                                  beat_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """자동 분할 구간에서 선택"""
        from .section_divider import SectionDivider
        
        divider = SectionDivider()
        auto_sections = divider.divide_sections(song_data, beat_data, melody_data)
        
        if not auto_sections:
            print("❌ 자동 분할된 구간이 없습니다.")
            return None
        
        print(f"\n📋 자동 분할된 구간 목록:")
        print("-" * 50)
        
        for section in auto_sections:
            duration = section['duration']
            difficulty = section.get('difficulty', 'medium')
            difficulty_emoji = {'easy': '🟢', 'medium': '🟡', 'hard': '🔴'}.get(difficulty, '🟡')
            
            print(f"{section['id'] + 1:2d}. {section['name']}")
            print(f"    시간: {section['start_time']:.1f}s - {section['end_time']:.1f}s ({duration:.1f}초)")
            print(f"    난이도: {difficulty_emoji} {difficulty}")
            print()
        
        try:
            while True:
                choice = input(f"선택할 구간 (1-{len(auto_sections)}): ").strip()
                try:
                    section_idx = int(choice) - 1
                    if 0 <= section_idx < len(auto_sections):
                        selected_section = auto_sections[section_idx]
                        print(f"✅ 선택됨: {selected_section['name']}")
                        return selected_section
                    else:
                        print(f"1부터 {len(auto_sections)} 사이의 숫자를 입력하세요.")
                except ValueError:
                    print("숫자를 입력하세요.")
                    
        except KeyboardInterrupt:
            return None
    
    def _create_custom_section(self, start_time: float, end_time: float,
                              song_data: Dict[str, Any], melody_data: Dict[str, Any],
                              beat_data: Dict[str, Any], name: str) -> Dict[str, Any]:
        """커스텀 구간 생성"""
        duration = end_time - start_time
        
        # 해당 구간의 멜로디 추출
        section_melody = self._extract_section_melody(melody_data, start_time, end_time)
        
        # 난이도 계산
        difficulty = self._calculate_difficulty(section_melody, duration)
        
        # 박자 정보 추출
        beats_in_section = self._get_beats_in_section(
            beat_data.get('beat_times', []), start_time, end_time
        )
        
        section = {
            'id': 0,
            'name': name,
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration,
            'melody': section_melody,
            'difficulty': difficulty,
            'measure_range': None,
            'beats_in_section': beats_in_section,
            'custom': True
        }
        
        print(f"\n✅ 구간 생성 완료:")
        print(f"   이름: {name}")
        print(f"   시간: {start_time:.1f}s - {end_time:.1f}s ({duration:.1f}초)")
        print(f"   난이도: {difficulty}")
        
        return section
    
    def _extract_section_melody(self, melody_data: Dict[str, Any], 
                               start_time: float, end_time: float) -> Dict[str, Any]:
        """구간 멜로디 추출"""
        try:
            times = melody_data.get('times', np.array([]))
            frequencies = melody_data.get('frequencies', np.array([]))
            confidence = melody_data.get('confidence', np.array([]))
            
            if len(times) == 0:
                return {
                    'times': np.array([]),
                    'frequencies': np.array([]),
                    'confidence': np.array([])
                }
            
            # 시간 범위 마스킹
            mask = (times >= start_time) & (times < end_time)
            
            if not np.any(mask):
                return {
                    'times': np.array([]),
                    'frequencies': np.array([]),
                    'confidence': np.array([])
                }
            
            # 상대 시간으로 변환
            section_times = times[mask] - start_time
            section_frequencies = frequencies[mask]
            section_confidence = confidence[mask] if len(confidence) > 0 else np.ones_like(section_times)
            
            return {
                'times': section_times,
                'frequencies': section_frequencies,
                'confidence': section_confidence
            }
            
        except Exception as e:
            print(f"❌ 멜로디 추출 실패: {e}")
            return {
                'times': np.array([]),
                'frequencies': np.array([]),
                'confidence': np.array([])
            }
    
    def _calculate_difficulty(self, section_melody: Dict[str, Any], duration: float) -> str:
        """구간 난이도 계산"""
        try:
            frequencies = section_melody.get('frequencies', np.array([]))
            
            if len(frequencies) == 0:
                return 'easy'
            
            valid_freqs = frequencies[frequencies > 0]
            
            if len(valid_freqs) == 0:
                return 'easy'
            
            # 난이도 요소들
            score = 0
            
            # 1. 음역대 (반음 단위)
            if len(valid_freqs) > 1:
                freq_range = np.max(valid_freqs) / np.min(valid_freqs)
                semitone_range = 12 * np.log2(freq_range)
                
                if semitone_range > 12:  # 옥타브 이상
                    score += 2
                elif semitone_range > 7:  # 완전 5도 이상
                    score += 1
            
            # 2. 길이
            if duration > 15:
                score += 2
            elif duration > 10:
                score += 1
            
            # 3. 변동성
            if len(valid_freqs) > 1:
                variation = np.std(valid_freqs) / np.mean(valid_freqs)
                if variation > 0.15:
                    score += 2
                elif variation > 0.08:
                    score += 1
            
            # 총점에 따른 난이도
            if score >= 4:
                return 'hard'
            elif score >= 2:
                return 'medium'
            else:
                return 'easy'
                
        except Exception as e:
            return 'medium'
    
    def _get_beats_in_section(self, beat_times: List[float], 
                             start_time: float, end_time: float) -> List[float]:
        """구간 내 박자 추출"""
        try:
            beat_times = np.array(beat_times)
            mask = (beat_times >= start_time) & (beat_times < end_time)
            section_beats = beat_times[mask] - start_time  # 상대 시간
            return section_beats.tolist()
        except:
            return []
    
    def preview_section(self, section: Dict[str, Any], song_data: Dict[str, Any]) -> None:
        """구간 미리보기"""
        print(f"\n🔍 구간 미리보기: {section['name']}")
        print("-" * 40)
        print(f"시간: {section['start_time']:.1f}s - {section['end_time']:.1f}s")
        print(f"길이: {section['duration']:.1f}초")
        print(f"난이도: {section['difficulty']}")
        
        melody = section['melody']
        if len(melody.get('frequencies', [])) > 0:
            freqs = melody['frequencies']
            valid_freqs = freqs[freqs > 0]
            
            if len(valid_freqs) > 0:
                print(f"음역: {np.min(valid_freqs):.1f}Hz - {np.max(valid_freqs):.1f}Hz")
                print(f"평균 음높이: {np.mean(valid_freqs):.1f}Hz")
        
        beats = section.get('beats_in_section', [])
        if beats:
            print(f"박자 수: {len(beats)}개")
        
        print("\n💡 이 구간으로 연습하시겠습니까? (y/n)")
