"""
구간 분할 모듈
노래를 연습 가능한 마디 단위로 분할하는 기능 제공
"""

import numpy as np
from typing import Dict, Any, List, Optional

class SectionDivider:
    """구간 분할 클래스"""
    
    def __init__(self, measures_per_section: int = 4):
        """
        초기화
        
        Args:
            measures_per_section: 구간당 마디 수
        """
        self.measures_per_section = measures_per_section
        
    def divide_sections(self, song_data: Dict[str, Any], 
                       beat_data: Dict[str, Any], 
                       melody_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        노래를 연습 구간으로 분할
        
        Args:
            song_data: 노래 데이터
            beat_data: 박자 데이터
            melody_data: 멜로디 데이터
            
        Returns:
            연습 구간 리스트
        """
        try:
            sections = []
            
            # 박자 데이터에서 마디 정보 추출
            measure_positions = beat_data.get('measure_positions', [])
            beats_per_measure = beat_data.get('beats_per_measure', 4)
            beat_times = beat_data.get('beat_times', [])
            
            if len(measure_positions) < 2:
                # 박자 데이터가 부족한 경우 시간 기반으로 분할
                return self._divide_by_time(song_data, melody_data)
            
            # 마디 기반으로 구간 분할
            section_idx = 0
            
            for i in range(0, len(measure_positions), self.measures_per_section):
                end_measure_idx = min(i + self.measures_per_section, len(measure_positions))
                
                if i < len(measure_positions):
                    start_time = measure_positions[i]
                    
                    # 마지막 구간 처리
                    if end_measure_idx < len(measure_positions):
                        end_time = measure_positions[end_measure_idx]
                    else:
                        # 마지막 구간은 노래 끝까지
                        song_duration = song_data.get('duration', 30.0)
                        end_time = min(song_duration, start_time + 15.0)  # 최대 15초로 제한
                    
                    # 구간이 너무 짧으면 스킵
                    if end_time - start_time < 2.0:
                        continue
                    
                    # 해당 구간의 멜로디 추출
                    section_melody = self._extract_section_melody(
                        melody_data, start_time, end_time
                    )
                    
                    # 구간 난이도 계산
                    difficulty = self._calculate_difficulty(section_melody, start_time, end_time)
                    
                    # 마디 번호 계산
                    start_measure = i // self.measures_per_section * self.measures_per_section + 1
                    end_measure = min(start_measure + self.measures_per_section - 1, 
                                    len(measure_positions))
                    
                    section = {
                        'id': section_idx,
                        'name': f"구간 {section_idx + 1} (마디 {start_measure}-{end_measure})",
                        'start_time': start_time,
                        'end_time': end_time,
                        'duration': end_time - start_time,
                        'melody': section_melody,
                        'difficulty': difficulty,
                        'measure_range': (start_measure, end_measure),
                        'beats_in_section': self._get_beats_in_section(
                            beat_times, start_time, end_time
                        )
                    }
                    
                    sections.append(section)
                    section_idx += 1
            
            if not sections:
                # 마디 기반 분할이 실패한 경우 시간 기반으로 대체
                return self._divide_by_time(song_data, melody_data)
            
            return sections
            
        except Exception as e:
            print(f"❌ 구간 분할 실패: {e}")
            # 실패 시 시간 기반으로 대체
            return self._divide_by_time(song_data, melody_data)
    
    def _divide_by_time(self, song_data: Dict[str, Any], 
                       melody_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        시간 기반 구간 분할 (백업 방법)
        
        Args:
            song_data: 노래 데이터
            melody_data: 멜로디 데이터
            
        Returns:
            연습 구간 리스트
        """
        sections = []
        duration = song_data.get('duration', 30.0)
        section_length = 8.0  # 8초씩 분할
        
        section_idx = 0
        start_time = 0.0
        
        while start_time < duration:
            end_time = min(start_time + section_length, duration)
            
            # 구간이 너무 짧으면 스킵
            if end_time - start_time < 3.0:
                break
            
            # 해당 구간의 멜로디 추출
            section_melody = self._extract_section_melody(
                melody_data, start_time, end_time
            )
            
            # 구간 난이도 계산
            difficulty = self._calculate_difficulty(section_melody, start_time, end_time)
            
            section = {
                'id': section_idx,
                'name': f"구간 {section_idx + 1} ({start_time:.1f}s-{end_time:.1f}s)",
                'start_time': start_time,
                'end_time': end_time,
                'duration': end_time - start_time,
                'melody': section_melody,
                'difficulty': difficulty,
                'measure_range': None,
                'beats_in_section': []
            }
            
            sections.append(section)
            section_idx += 1
            start_time = end_time
        
        return sections
    
    def _extract_section_melody(self, melody_data: Dict[str, Any], 
                               start_time: float, end_time: float) -> Dict[str, Any]:
        """
        특정 구간의 멜로디 추출
        
        Args:
            melody_data: 전체 멜로디 데이터
            start_time: 시작 시간
            end_time: 끝 시간
            
        Returns:
            구간 멜로디 데이터
        """
        try:
            times = melody_data.get('times', np.array([]))
            frequencies = melody_data.get('frequencies', np.array([]))
            confidence = melody_data.get('confidence', np.array([]))
            
            if len(times) == 0:
                # 멜로디 데이터가 없는 경우 빈 데이터 반환
                return {
                    'times': np.array([]),
                    'frequencies': np.array([]),
                    'confidence': np.array([])
                }
            
            # 시간 범위에 해당하는 인덱스 찾기
            mask = (times >= start_time) & (times < end_time)
            
            if not np.any(mask):
                # 해당 구간에 멜로디가 없는 경우
                return {
                    'times': np.array([]),
                    'frequencies': np.array([]),
                    'confidence': np.array([])
                }
            
            # 상대 시간으로 변환 (구간 내에서 0부터 시작)
            section_times = times[mask] - start_time
            section_frequencies = frequencies[mask]
            section_confidence = confidence[mask] if len(confidence) > 0 else np.ones_like(section_times)
            
            return {
                'times': section_times,
                'frequencies': section_frequencies,
                'confidence': section_confidence
            }
            
        except Exception as e:
            print(f"❌ 구간 멜로디 추출 실패: {e}")
            return {
                'times': np.array([]),
                'frequencies': np.array([]),
                'confidence': np.array([])
            }
    
    def _calculate_difficulty(self, section_melody: Dict[str, Any], 
                            start_time: float, end_time: float) -> str:
        """
        구간 난이도 계산
        
        Args:
            section_melody: 구간 멜로디 데이터
            start_time: 시작 시간
            end_time: 끝 시간
            
        Returns:
            난이도 ('easy', 'medium', 'hard')
        """
        try:
            frequencies = section_melody.get('frequencies', np.array([]))
            
            if len(frequencies) == 0:
                return 'easy'
            
            # 유효한 주파수만 필터링
            valid_freqs = frequencies[frequencies > 0]
            
            if len(valid_freqs) == 0:
                return 'easy'
            
            # 난이도 요소들
            factors = {
                'range': 0,      # 음역대
                'variation': 0,  # 음높이 변화
                'stability': 0,  # 안정성
                'duration': 0    # 길이
            }
            
            # 1. 음역대 (반음 단위)
            freq_range = np.max(valid_freqs) / np.min(valid_freqs)
            semitone_range = 12 * np.log2(freq_range)
            
            if semitone_range > 12:  # 옥타브 이상
                factors['range'] = 2
            elif semitone_range > 7:  # 완전 5도 이상
                factors['range'] = 1
            else:
                factors['range'] = 0
            
            # 2. 음높이 변화 (변동성)
            if len(valid_freqs) > 1:
                freq_std = np.std(valid_freqs)
                freq_mean = np.mean(valid_freqs)
                variation_coeff = freq_std / freq_mean if freq_mean > 0 else 0
                
                if variation_coeff > 0.15:
                    factors['variation'] = 2
                elif variation_coeff > 0.08:
                    factors['variation'] = 1
                else:
                    factors['variation'] = 0
            
            # 3. 안정성 (신뢰도 기반)
            confidence = section_melody.get('confidence', np.array([]))
            if len(confidence) > 0:
                avg_confidence = np.mean(confidence)
                if avg_confidence < 0.5:
                    factors['stability'] = 2  # 불안정할수록 어려움
                elif avg_confidence < 0.7:
                    factors['stability'] = 1
                else:
                    factors['stability'] = 0
            
            # 4. 길이 (긴 구간일수록 어려움)
            duration = end_time - start_time
            if duration > 12:
                factors['duration'] = 2
            elif duration > 8:
                factors['duration'] = 1
            else:
                factors['duration'] = 0
            
            # 총 난이도 점수 계산
            total_score = sum(factors.values())
            
            if total_score >= 5:
                return 'hard'
            elif total_score >= 3:
                return 'medium'
            else:
                return 'easy'
            
        except Exception as e:
            print(f"❌ 난이도 계산 실패: {e}")
            return 'medium'
    
    def _get_beats_in_section(self, beat_times: List[float], 
                             start_time: float, end_time: float) -> List[float]:
        """
        구간 내의 박자들 추출
        
        Args:
            beat_times: 전체 박자 시간들
            start_time: 시작 시간
            end_time: 끝 시간
            
        Returns:
            구간 내 박자들 (상대 시간)
        """
        try:
            beat_times = np.array(beat_times)
            mask = (beat_times >= start_time) & (beat_times < end_time)
            section_beats = beat_times[mask] - start_time  # 상대 시간으로 변환
            return section_beats.tolist()
        except:
            return []
    
    def get_section_summary(self, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        구간 분할 결과 요약
        
        Args:
            sections: 구간 리스트
            
        Returns:
            요약 정보
        """
        if not sections:
            return {'total_sections': 0}
        
        durations = [s['duration'] for s in sections]
        difficulties = [s['difficulty'] for s in sections]
        
        difficulty_count = {
            'easy': difficulties.count('easy'),
            'medium': difficulties.count('medium'),
            'hard': difficulties.count('hard')
        }
        
        summary = {
            'total_sections': len(sections),
            'total_duration': sum(durations),
            'average_duration': np.mean(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'difficulty_distribution': difficulty_count,
            'measures_per_section': self.measures_per_section
        }
        
        return summary
