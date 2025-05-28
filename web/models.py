"""
웹 애플리케이션 데이터 모델
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class UploadResponse(BaseModel):
    success: bool
    session_id: str
    filename: str
    message: str

class Section(BaseModel):
    id: int
    name: str
    start_time: float
    end_time: float
    duration: float
    difficulty: str

class AnalysisResponse(BaseModel):
    success: bool
    sections: List[Section]
    message: str

class ScoreData(BaseModel):
    pitch: Optional[float] = None
    breath: Optional[float] = None
    pronunciation: Optional[float] = None
    vocal_onset: Optional[float] = None

class AnalysisResult(BaseModel):
    scores: ScoreData
    overall_score: float

class FeedbackData(BaseModel):
    feedbacks: List[str]
    recommendations: List[str]

class SectionInfo(BaseModel):
    name: str
    duration: float

class RecordingResponse(BaseModel):
    success: bool
    analysis: AnalysisResult
    feedback: FeedbackData
    section: SectionInfo

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
