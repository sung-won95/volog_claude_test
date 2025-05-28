"""
웹 애플리케이션 설정
"""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS 설정
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # 파일 업로드 설정
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_AUDIO_EXTENSIONS: List[str] = [".mp3", ".wav", ".flac", ".m4a", ".ogg"]
    
    # 디렉토리 설정
    UPLOAD_DIR: str = "uploads"
    RECORDING_DIR: str = "recordings"
    STATIC_DIR: str = "web/static"
    
    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    """설정 인스턴스 반환"""
    return Settings()
