"""
비즈니스 로직 서비스
"""

import os
import uuid
import shutil
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional
from fastapi import HTTPException, UploadFile

from vocal_coach.ai_vocal_coach import AIVocalCoach
from vocal_coach.audio_processor import AudioProcessor
from web.config import get_settings

settings = get_settings()

class SessionManager:
    """세션 관리 클래스"""
    
    def __init__(self):
        self.coaches: Dict[str, AIVocalCoach] = {}
        self.audio_processor = AudioProcessor()
    
    def create_session(self) -> str:
        """새 세션 생성"""
        session_id = str(uuid.uuid4())
        return session_id
    
    def get_coach(self, session_id: str) -> AIVocalCoach:
        """세션의 코치 인스턴스 반환"""
        if session_id not in self.coaches:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        return self.coaches[session_id]
    
    def delete_session(self, session_id: str):
        """세션 삭제"""
        # 코치 인스턴스 삭제
        if session_id in self.coaches:
            del self.coaches[session_id]
        
        # 관련 파일들 삭제
        self._cleanup_session_files(session_id)
    
    def _cleanup_session_files(self, session_id: str):
        """세션 관련 파일들 정리"""
        # 업로드된 파일 삭제
        for ext in settings.ALLOWED_AUDIO_EXTENSIONS:
            file_path = f"{settings.UPLOAD_DIR}/{session_id}{ext}"
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # 녹음 파일들 삭제
        recording_pattern = f"{settings.RECORDING_DIR}/{session_id}_*.wav"
        import glob
        for file_path in glob.glob(recording_pattern):
            if os.path.exists(file_path):
                os.remove(file_path)

# 전역 세션 매니저 인스턴스
session_manager = SessionManager()

class FileService:
    """파일 처리 서비스"""
    
    @staticmethod
    def validate_audio_file(file: UploadFile) -> bool:
        """오디오 파일 유효성 검사"""
        file_extension = Path(file.filename).suffix.lower()
        return file_extension in settings.ALLOWED_AUDIO_EXTENSIONS
    
    @staticmethod
    def save_uploaded_file(file: UploadFile, session_id: str) -> str:
        """업로드된 파일 저장"""
        file_extension = Path(file.filename).suffix.lower()
        upload_path = f"{settings.UPLOAD_DIR}/{session_id}{file_extension}"
        
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return upload_path
    
    @staticmethod
    def find_uploaded_file(session_id: str) -> Optional[str]:
        """업로드된 파일 찾기"""
        for ext in settings.ALLOWED_AUDIO_EXTENSIONS:
            file_path = f"{settings.UPLOAD_DIR}/{session_id}{ext}"
            if os.path.exists(file_path):
                return file_path
        return None
    
    @staticmethod
    def save_recording(recording: UploadFile, session_id: str, section_id: int) -> str:
        """녹음 파일 저장"""
        recording_path = f"{settings.RECORDING_DIR}/{session_id}_{section_id}.wav"
        
        with open(recording_path, "wb") as buffer:
            shutil.copyfileobj(recording.file, buffer)
        
        return recording_path

class AnalysisService:
    """분석 서비스"""
    
    @staticmethod
    def analyze_song(session_id: str) -> List[Dict[str, Any]]:
        """노래 분석 및 구간 생성"""
        # 업로드된 파일 찾기
        file_path = FileService.find_uploaded_file(session_id)
        if not file_path:
            raise HTTPException(status_code=404, detail="업로드된 파일을 찾을 수 없습니다.")
        
        # AI 보컬 코치 인스턴스 생성
        coach = AIVocalCoach()
        
        # 노래 로드 및 분석
        success = coach.load_song(file_path)
        if not success:
            raise HTTPException(status_code=500, detail="노래 분석에 실패했습니다.")
        
        # 세션에 코치 저장
        session_manager.coaches[session_id] = coach
        
        # 연습 구간 정보 변환
        sections = []
        for section in coach.practice_sections:
            sections.append({
                "id": section['id'],
                "name": section['name'],
                "start_time": float(section['start_time']),
                "end_time": float(section['end_time']),
                "duration": float(section['duration']),
                "difficulty": section.get('difficulty', 'medium')
            })
        
        return sections
    
    @staticmethod
    def analyze_recording(session_id: str, section_id: int, recording_path: str) -> Dict[str, Any]:
        """녹음 분석"""
        coach = session_manager.get_coach(session_id)
        
        # 해당 구간 찾기
        selected_section = None
        for section in coach.practice_sections:
            if section['id'] == section_id:
                selected_section = section
                break
        
        if not selected_section:
            raise HTTPException(status_code=404, detail="선택된 구간을 찾을 수 없습니다.")
        
        # 오디오 로드
        recorded_audio = session_manager.audio_processor.load_audio(recording_path)
        if recorded_audio is None:
            raise HTTPException(status_code=500, detail="녹음 파일을 처리할 수 없습니다.")
        
        # 음성 분석
        analysis_result = coach.voice_analyzer.analyze_voice(
            recorded_audio, selected_section['melody']
        )
        
        # 피드백 생성
        feedback = coach.feedback_engine.generate_feedback(
            analysis_result, selected_section
        )
        
        # 응답 데이터 준비
        response_data = {
            "analysis": {
                "scores": analysis_result.get('scores', {}),
                "overall_score": analysis_result.get('overall_score', 0)
            },
            "feedback": {
                "feedbacks": feedback.get('feedbacks', []),
                "recommendations": feedback.get('recommendations', [])
            },
            "section": {
                "name": selected_section['name'],
                "duration": selected_section['duration']
            }
        }
        
        # NumPy 타입을 Python 기본 타입으로 변환
        return AnalysisService._convert_numpy_types(response_data)
    
    @staticmethod
    def _convert_numpy_types(obj):
        """NumPy 타입을 Python 기본 타입으로 변환"""
        if isinstance(obj, dict):
            return {key: AnalysisService._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [AnalysisService._convert_numpy_types(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        else:
            return obj
