#!/usr/bin/env python3
"""
AI 보컬 코치 웹 애플리케이션 시작 스크립트
"""

import os
import sys
import uvicorn
from web.config import get_settings

def check_dependencies():
    """필수 의존성 확인"""
    required_packages = [
        'fastapi',
        'uvicorn', 
        'librosa',
        'numpy',
        'matplotlib',
        'soundfile'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 다음 패키지들이 설치되지 않았습니다:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n설치 방법:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def create_directories():
    """필요한 디렉토리 생성"""
    directories = [
        "uploads",
        "recordings", 
        "web/static",
        "web/templates"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ 디렉토리 생성: {directory}")

def main():
    """메인 실행 함수"""
    print("🎤 AI 보컬 코치 웹 애플리케이션 시작")
    print("=" * 50)
    
    # 의존성 확인
    if not check_dependencies():
        sys.exit(1)
    
    # 디렉토리 생성
    create_directories()
    
    # 설정 로드
    settings = get_settings()
    
    print(f"\n🌐 서버 정보:")
    print(f"   주소: http://{settings.HOST}:{settings.PORT}")
    print(f"   디버그 모드: {settings.DEBUG}")
    
    print(f"\n🎵 기능:")
    print(f"   ✅ 노래 파일 업로드")
    print(f"   ✅ AI 분석 및 구간 생성")
    print(f"   ✅ 웹 기반 녹음")
    print(f"   ✅ 실시간 피드백")
    print(f"   ✅ 결과 시각화")
    
    print(f"\n🚀 서버 시작 중...")
    
    try:
        # 웹 서버 시작
        uvicorn.run(
            "app:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level="info" if settings.DEBUG else "warning"
        )
    except KeyboardInterrupt:
        print("\n⏹️  서버가 중지되었습니다.")
    except Exception as e:
        print(f"\n❌ 서버 시작 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
