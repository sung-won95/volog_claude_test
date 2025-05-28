"""
FastAPI 기반 AI 보컬 코치 웹 애플리케이션 - 메인 엔트리포인트
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# 라우터 임포트
from web.routes import upload, analysis, recording, main
from web.config import get_settings

# 설정 로드
settings = get_settings()

# FastAPI 앱 생성
app = FastAPI(
    title="AI 보컬 코치",
    description="웹 기반 AI 보컬 코칭 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# 라우터 등록
app.include_router(main.router, tags=["메인"])
app.include_router(upload.router, prefix="/api", tags=["업로드"])
app.include_router(analysis.router, prefix="/api", tags=["분석"])
app.include_router(recording.router, prefix="/api", tags=["녹음"])

# 필요한 디렉토리 생성
os.makedirs("uploads", exist_ok=True)
os.makedirs("recordings", exist_ok=True)
os.makedirs("web/static", exist_ok=True)

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
