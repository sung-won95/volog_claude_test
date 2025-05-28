#!/usr/bin/env python3
"""
AI 보컬 코치 설치 스크립트
운영체제와 환경에 맞는 의존성을 자동으로 설치합니다.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, check=True):
    """명령어 실행"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=check,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_python_version():
    """Python 버전 확인"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 이상이 필요합니다.")
        print(f"   현재 버전: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python 버전: {version.major}.{version.minor}.{version.micro}")
    return True

def check_pip():
    """pip 설치 확인"""
    success, stdout, stderr = run_command("pip --version", check=False)
    if success:
        print(f"✅ pip 확인됨: {stdout.strip()}")
        return True
    else:
        print("❌ pip가 설치되지 않았습니다.")
        return False

def detect_os():
    """운영체제 감지"""
    system = platform.system().lower()
    print(f"🖥️  운영체제: {platform.system()} {platform.release()}")
    return system

def install_system_dependencies(os_type):
    """시스템 의존성 설치"""
    print("\n📦 시스템 의존성 확인 중...")
    
    if os_type == "linux":
        # Ubuntu/Debian 계열
        if os.path.exists("/etc/apt"):
            print("🐧 Ubuntu/Debian 감지")
            commands = [
                "sudo apt-get update",
                "sudo apt-get install -y python3-dev",
                "sudo apt-get install -y libasound2-dev",  # sounddevice용
                "sudo apt-get install -y libportaudio2",   # sounddevice용 
                "sudo apt-get install -y libsndfile1",     # soundfile용
                "sudo apt-get install -y ffmpeg"           # 오디오 처리용
            ]
        # RedHat/CentOS 계열
        elif os.path.exists("/etc/yum.conf") or os.path.exists("/etc/dnf"):
            print("🎩 RedHat/Fedora 감지")
            commands = [
                "sudo yum install -y python3-devel",
                "sudo yum install -y alsa-lib-devel",
                "sudo yum install -y portaudio-devel", 
                "sudo yum install -y libsndfile-devel",
                "sudo yum install -y ffmpeg"
            ]
        else:
            print("⚠️  알 수 없는 Linux 배포판")
            return True
            
        for cmd in commands:
            print(f"   실행 중: {cmd}")
            success, stdout, stderr = run_command(cmd, check=False)
            if not success:
                print(f"   ⚠️  명령어 실패 (계속 진행): {cmd}")
    
    elif os_type == "darwin":  # macOS
        print("🍎 macOS 감지")
        # Homebrew 확인
        success, _, _ = run_command("brew --version", check=False)
        if success:
            commands = [
                "brew install portaudio",
                "brew install libsndfile", 
                "brew install ffmpeg"
            ]
            for cmd in commands:
                print(f"   실행 중: {cmd}")
                run_command(cmd, check=False)
        else:
            print("   ⚠️  Homebrew가 설치되지 않았습니다.")
            print("   💡 Homebrew 설치: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
    
    elif os_type == "windows":
        print("🪟 Windows 감지")
        print("   💡 Windows에서는 pip로 모든 의존성을 설치합니다.")
    
    return True

def choose_installation_type():
    """설치 유형 선택"""
    print("\n🎯 설치 유형을 선택하세요:")
    print("1. 최소 설치 (웹 기능만)")
    print("2. 완전 설치 (모든 기능)")
    print("3. 개발자 설치 (개발 도구 포함)")
    print("4. 프로덕션 설치 (서버 배포용)")
    
    while True:
        choice = input("선택 (1-4): ").strip()
        if choice == "1":
            return "requirements-minimal.txt"
        elif choice == "2":
            return "requirements.txt"
        elif choice == "3":
            return "requirements-dev.txt"
        elif choice == "4":
            return "requirements-prod.txt"
        else:
            print("1, 2, 3, 4 중 하나를 선택하세요.")

def install_python_packages(requirements_file):
    """Python 패키지 설치"""
    print(f"\n📥 Python 패키지 설치 중: {requirements_file}")
    
    # pip 업그레이드
    print("   pip 업그레이드 중...")
    run_command("pip install --upgrade pip", check=False)
    
    # 패키지 설치
    cmd = f"pip install -r {requirements_file}"
    print(f"   실행 중: {cmd}")
    
    success, stdout, stderr = run_command(cmd, check=False)
    
    if success:
        print("✅ Python 패키지 설치 완료!")
        return True
    else:
        print("❌ Python 패키지 설치 실패:")
        print(stderr)
        return False

def create_env_file():
    """환경 설정 파일 생성"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("\n⚙️  환경 설정 파일 생성 중...")
        try:
            with open(env_example, 'r') as src:
                content = src.read()
            with open(env_file, 'w') as dst:
                dst.write(content)
            print("✅ .env 파일이 생성되었습니다.")
        except Exception as e:
            print(f"⚠️  .env 파일 생성 실패: {e}")

def test_installation():
    """설치 테스트"""
    print("\n🧪 설치 테스트 중...")
    
    test_imports = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("numpy", "NumPy"),
        ("librosa", "Librosa"),
        ("matplotlib", "Matplotlib")
    ]
    
    failed_imports = []
    
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name}")
            failed_imports.append(name)
    
    if failed_imports:
        print(f"\n⚠️  일부 패키지 가져오기 실패: {', '.join(failed_imports)}")
        return False
    else:
        print("\n🎉 모든 패키지가 성공적으로 설치되었습니다!")
        return True

def show_next_steps():
    """다음 단계 안내"""
    print("\n🚀 설치 완료! 다음 단계:")
    print("\n웹 애플리케이션 시작:")
    print("   python start_web.py")
    print("   또는")
    print("   python -m uvicorn app:app --reload")
    
    print("\n콘솔 버전 시작:")
    print("   python main.py")
    
    print("\n📖 사용 가이드:")
    print("   - WEB_GUIDE.md: 웹 버전 사용법")
    print("   - REALTIME_GUIDE.md: 실시간 기능 사용법")
    print("   - README.md: 전체 프로젝트 정보")

def main():
    """메인 실행 함수"""
    print("🎤 AI 보컬 코치 설치 스크립트")
    print("=" * 50)
    
    # Python 버전 확인
    if not check_python_version():
        return 1
    
    # pip 확인
    if not check_pip():
        return 1
    
    # 운영체제 감지
    os_type = detect_os()
    
    # 시스템 의존성 설치
    install_system_dependencies(os_type)
    
    # 설치 유형 선택
    requirements_file = choose_installation_type()
    
    # 가상환경 권장
    if not os.environ.get('VIRTUAL_ENV'):
        print("\n⚠️  가상환경 사용을 권장합니다:")
        print("   python -m venv venv")
        print("   source venv/bin/activate  # Linux/Mac")
        print("   venv\\Scripts\\activate     # Windows")
        
        if input("\n계속 설치하시겠습니까? (y/N): ").lower() != 'y':
            return 0
    
    # Python 패키지 설치
    if not install_python_packages(requirements_file):
        return 1
    
    # 환경 설정 파일 생성
    create_env_file()
    
    # 설치 테스트
    if not test_installation():
        print("\n⚠️  일부 패키지에 문제가 있을 수 있습니다.")
        print("   수동으로 다시 설치해보세요:")
        print(f"   pip install -r {requirements_file}")
    
    # 다음 단계 안내
    show_next_steps()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
