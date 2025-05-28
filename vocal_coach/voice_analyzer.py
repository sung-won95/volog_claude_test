"""
음성 분석 모듈
사용자 음성의 음정, 호흡, 발음, 성대 접촉 분석 기능 제공
"""

import numpy as np
import librosa
from typing import Dict, Any, Optional, Tuple, List

class VoiceAnalyzer:
    """음성 분석 클래스"""
    
    def __init__(self):
        """초기화"""
        self.min_freq = 80.0
        self.max_freq = 800.0
        self.frame_length = 2048
        self.hop_length = 512
        
    def analyze_voice(self, recorded_audio: Dict[str, Any], 
                     target_melody: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 음성 종합 분석"""
        try:
            audio = recorded_audio['audio']
            sr = recorded_audio['sr']
            
            print("🔍 음성 분석 중...")
            
            # 1. 음정 분석
            pitch_analysis = self._analyze_pitch(audio, sr, target_melody)
            
            # 2. 호흡 분석
            breath_analysis = self._analyze_breath_support(audio, sr)
            
            # 3. 발음 분석
            pronunciation_analysis = self._analyze_pronunciation(audio, sr)
            
            # 4. 성대 접촉 분석
            vocal_onset_analysis = self._analyze_vocal_onset(audio, sr)
            
            # 5. 종합 점수 계산
            scores = self._calculate_scores(
                pitch_analysis, breath_analysis, 
                pronunciation_analysis, vocal_onset_analysis
            )
            
            analysis_result = {
                'pitch_analysis': pitch_analysis,
                'breath_analysis': breath_analysis,
                'pronunciation_analysis': pronunciation_analysis,
                'vocal_onset_analysis': vocal_onset_analysis,
                'scores': scores,
                'overall_score': np.mean(list(scores.values()))
            }
            
            print("✅ 음성 분석 완료!")
            return analysis_result
            
        except Exception as e:
            print(f"❌ 음성 분석 실패: {e}")
            return {'error': f'음성 분석 실패: {e}'}
    
    def _analyze_pitch(self, audio: np.ndarray, sr: int, 
                      target_melody: Dict[str, Any]) -> Dict[str, Any]:
        """음정 분석"""
        try:
            # F0 추출
            f0_times, f0_values = self._extract_f0(audio, sr)
            
            # 목표 멜로디와 비교
            target_times = target_melody.get('times', np.array([]))
            target_freqs = target_melody.get('frequencies', np.array([]))
            
            if len(target_times) == 0 or len(target_freqs) == 0:
                return {
                    'times': f0_times,
                    'frequencies': f0_values,
                    'accuracy': 0.7,  # 데모용 기본값
                    'stability': self._calculate_pitch_stability(f0_values),
                    'intonation_errors': []
                }
            
            # 시간 정렬 및 비교
            aligned_user, aligned_target = self._align_melodies(
                f0_times, f0_values, target_times, target_freqs
            )
            
            # 음정 정확도 계산
            accuracy = self._calculate_pitch_accuracy(aligned_user, aligned_target)
            
            # 음정 안정성 계산
            stability = self._calculate_pitch_stability(f0_values)
            
            return {
                'times': f0_times,
                'frequencies': f0_values,
                'target_frequencies': aligned_target,
                'accuracy': accuracy,
                'stability': stability,
                'intonation_errors': []
            }
            
        except Exception as e:
            print(f"❌ 음정 분석 실패: {e}")
            return {'error': f'음정 분석 실패: {e}'}
    
    def _extract_f0(self, audio: np.ndarray, sr: int) -> Tuple[np.ndarray, np.ndarray]:
        """F0 추출"""
        stft = librosa.stft(audio, n_fft=self.frame_length, hop_length=self.hop_length)
        pitches, magnitudes = librosa.piptrack(
            S=np.abs(stft), sr=sr, fmin=self.min_freq, fmax=self.max_freq, threshold=0.1
        )
        
        times = librosa.frames_to_time(
            np.arange(pitches.shape[1]), sr=sr, hop_length=self.hop_length
        )
        
        f0_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            f0_values.append(pitch if pitch > 0 else 0.0)
        
        return times, np.array(f0_values)
    
    def _align_melodies(self, user_times: np.ndarray, user_freqs: np.ndarray,
                       target_times: np.ndarray, target_freqs: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """멜로디 시간 정렬"""
        min_time = max(user_times[0], target_times[0])
        max_time = min(user_times[-1], target_times[-1])
        
        if max_time <= min_time:
            return np.array([]), np.array([])
        
        common_times = np.linspace(min_time, max_time, 100)
        aligned_user = np.interp(common_times, user_times, user_freqs)
        aligned_target = np.interp(common_times, target_times, target_freqs)
        
        return aligned_user, aligned_target
    
    def _calculate_pitch_accuracy(self, user_freqs: np.ndarray, target_freqs: np.ndarray) -> float:
        """음정 정확도 계산"""
        if len(user_freqs) == 0 or len(target_freqs) == 0:
            return 0.7  # 데모용 기본값
        
        valid_mask = (user_freqs > 0) & (target_freqs > 0)
        if not np.any(valid_mask):
            return 0.7
        
        user_valid = user_freqs[valid_mask]
        target_valid = target_freqs[valid_mask]
        
        # 센트 단위로 오차 계산
        cent_errors = 1200 * np.log2(user_valid / (target_valid + 1e-8))
        accurate_count = np.sum(np.abs(cent_errors) <= 50)
        accuracy = accurate_count / len(cent_errors)
        
        return float(max(0.5, accuracy))
    
    def _calculate_pitch_stability(self, f0_values: np.ndarray) -> float:
        """음정 안정성 계산"""
        valid_f0 = f0_values[f0_values > 0]
        
        if len(valid_f0) < 2:
            return 0.7
        
        diff = np.diff(valid_f0)
        relative_diff = np.abs(diff) / (valid_f0[:-1] + 1e-8)
        jitter = np.mean(relative_diff)
        
        stability = max(0.3, 1.0 - jitter * 50)
        return float(stability)
    
    def _analyze_breath_support(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """호흡 지지 분석"""
        try:
            volume_consistency = self._analyze_volume_consistency(audio, sr)
            sustainability = self._analyze_sustainability(audio, sr)
            
            return {
                'volume_consistency': volume_consistency,
                'sustainability': sustainability,
                'overall_support': (volume_consistency + sustainability) / 2
            }
            
        except Exception as e:
            return {'error': f'호흡 분석 실패: {e}'}
    
    def _analyze_volume_consistency(self, audio: np.ndarray, sr: int) -> float:
        """음량 일관성 분석"""
        frame_length = int(sr * 0.1)
        hop_length = int(frame_length / 2)
        
        rms_values = []
        for i in range(0, len(audio) - frame_length, hop_length):
            frame = audio[i:i + frame_length]
            rms = np.sqrt(np.mean(frame**2))
            rms_values.append(rms)
        
        if len(rms_values) == 0:
            return 0.6
        
        rms_values = np.array(rms_values)
        mean_rms = np.mean(rms_values)
        std_rms = np.std(rms_values)
        
        if mean_rms > 0:
            cv = std_rms / mean_rms
            consistency = max(0.3, 1.0 - cv)
        else:
            consistency = 0.6
        
        return float(consistency)
    
    def _analyze_sustainability(self, audio: np.ndarray, sr: int) -> float:
        """지속성 분석"""
        frame_length = int(sr * 0.05)
        hop_length = int(frame_length / 2)
        
        energy_frames = []
        for i in range(0, len(audio) - frame_length, hop_length):
            frame = audio[i:i + frame_length]
            energy = np.sum(frame**2)
            energy_frames.append(energy)
        
        if len(energy_frames) == 0:
            return 0.6
        
        energy_frames = np.array(energy_frames)
        energy_threshold = np.mean(energy_frames) * 0.1
        voice_active = energy_frames > energy_threshold
        
        sustainability = np.sum(voice_active) / len(voice_active) if len(voice_active) > 0 else 0.6
        return float(max(0.4, sustainability))
    
    def _analyze_pronunciation(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """발음 분석"""
        try:
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
            
            mfcc_variation = np.std(mfcc, axis=1).mean()
            spectral_clarity = np.mean(spectral_centroids)
            
            clarity_score = max(0.4, min(0.9, 0.6 + mfcc_variation * 0.01))
            
            return {
                'clarity_score': clarity_score,
                'articulation_quality': 'good' if clarity_score > 0.7 else 'needs_improvement'
            }
            
        except Exception as e:
            return {'error': f'발음 분석 실패: {e}'}
    
    def _analyze_vocal_onset(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """성대 접촉 분석"""
        try:
            onset_frames = librosa.onset.onset_detect(y=audio, sr=sr, units='frames')
            
            if len(onset_frames) == 0:
                return {
                    'onset_type': 'normal',
                    'onset_quality': 0.6
                }
            
            onset_quality = 0.6
            
            if len(onset_frames) > 0:
                onset_frame = onset_frames[0]
                onset_time = librosa.frames_to_time(onset_frame, sr=sr)
                
                start_sample = max(0, int((onset_time - 0.05) * sr))
                end_sample = min(len(audio), int((onset_time + 0.05) * sr))
                
                if end_sample > start_sample:
                    onset_segment = audio[start_sample:end_sample]
                    
                    energy_profile = np.abs(onset_segment)
                    if len(energy_profile) > 0:
                        energy_gradient = np.gradient(energy_profile)
                        max_gradient = np.max(energy_gradient)
                        
                        onset_quality = max(0.3, min(0.9, 0.7 - max_gradient * 500))
            
            return {
                'onset_type': 'normal',
                'onset_quality': onset_quality,
                'onset_count': len(onset_frames)
            }
            
        except Exception as e:
            return {'error': f'성대 접촉 분석 실패: {e}'}
    
    def _calculate_scores(self, pitch_analysis: Dict[str, Any], 
                         breath_analysis: Dict[str, Any],
                         pronunciation_analysis: Dict[str, Any], 
                         vocal_onset_analysis: Dict[str, Any]) -> Dict[str, float]:
        """종합 점수 계산"""
        scores = {}
        
        # 음정 점수
        if 'error' not in pitch_analysis:
            pitch_score = (
                pitch_analysis.get('accuracy', 0.6) * 0.6 +
                pitch_analysis.get('stability', 0.6) * 0.4
            )
            scores['pitch'] = max(0.3, min(1.0, pitch_score))
        else:
            scores['pitch'] = 0.5
        
        # 호흡 점수
        if 'error' not in breath_analysis:
            scores['breath'] = breath_analysis.get('overall_support', 0.6)
        else:
            scores['breath'] = 0.5
        
        # 발음 점수
        if 'error' not in pronunciation_analysis:
            scores['pronunciation'] = pronunciation_analysis.get('clarity_score', 0.6)
        else:
            scores['pronunciation'] = 0.5
        
        # 성대 접촉 점수
        if 'error' not in vocal_onset_analysis:
            scores['vocal_onset'] = vocal_onset_analysis.get('onset_quality', 0.6)
        else:
            scores['vocal_onset'] = 0.5
        
        return scores
