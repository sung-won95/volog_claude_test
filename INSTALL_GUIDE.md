# 설치 가이드

## 🚀 빠른 설치 (추천)

### 방법 1: 최소 설치 (데모 모드만)
```bash
# 최소한의 패키지만 설치 (가장 안전)
pip install -r requirements_minimal.txt
```

이 방법으로 설치하면:
- ✅ 데모 모드 완전 지원
- ✅ 노래 파일 분석 가능
- ✅ 가상 녹음 및 피드백
- ❌ 실제 마이크 녹음 불가

### 방법 2: 전체 설치 (실제 녹음 포함)
```bash
# 전체 기능 설치
pip install -r requirements_full.txt
```

이 방법으로 설치하면:
- ✅ 모든 기능 지원
- ✅ 실제 마이크 녹음 가능
- ✅ 고급 시각화
- ⚠️ 일부 시스템에서 호환성 문제 가능

## 🔧 문제 해결

### Python 버전 호환성 문제

에러가 발생하면 다음 순서로 시도하세요:

#### 1단계: Python 버전 확인
```bash
python --version
# 또는
python3 --version
```

#### 2단계: pip 업그레이드
```bash
python -m pip install --upgrade pip
```

#### 3단계: 개별 패키지 설치
```bash
# 하나씩 설치해서 어떤 패키지에서 문제가 발생하는지 확인
pip install numpy
pip install scipy  
pip install matplotlib
pip install librosa
pip install soundfile
```

#### 4단계: 버전 다운그레이드
```bash
# 더 오래된 안정 버전 사용
pip install numpy==1.21.0
pip install scipy==1.7.0
pip install matplotlib==3.5.0
pip install librosa==0.9.0
pip install soundfile==0.10.0
```

### 특정 에러별 해결책

#### TensorFlow 관련 에러
```bash
# TensorFlow는 선택사항이므로 무시하고 진행
# requirements.txt에서 tensorflow 라인을 완전히 제거
```

#### sounddevice 설치 실패
```bash
# Windows의 경우
pip install sounddevice --only-binary=all

# macOS의 경우  
brew install portaudio
pip install sounddevice

# Linux의 경우
sudo apt-get install portaudio19-dev
pip install sounddevice
```

#### librosa 설치 실패
```bash
# ffmpeg 먼저 설치
# Windows: https://ffmpeg.org/download.html
# macOS: brew install ffmpeg  
# Linux: sudo apt-get install ffmpeg

pip install librosa
```

## 🏃‍♂️ 설치 없이 바로 실행

만약 패키지 설치가 계속 실패한다면, 코어 기능만으로도 체험 가능합니다:

### 1. 기본 Python 라이브러리만 사용
```bash
# 아무것도 설치하지 않고 실행
python demo_basic.py  # 기본 기능만 체험
```

### 2. 온라인 환경에서 실행
- Google Colab
- Jupyter Notebook
- Replit

## 📦 설치 확인

설치가 완료되면 다음 명령어로 확인:

```bash
python -c "
import numpy as np
import matplotlib.pyplot as plt
import librosa
print('✅ 기본 패키지 설치 완료!')
print(f'NumPy: {np.__version__}')
print(f'Librosa: {librosa.__version__}')
"
```

실제 녹음 기능 확인:
```bash
python -c "
try:
    import sounddevice as sd
    print('✅ 실시간 녹음 기능 사용 가능')
    print('🎤 마이크 테스트를 진행할 수 있습니다')
except ImportError:
    print('⚠️ 실시간 녹음 불가 (데모 모드만 사용)')
"
```

## 🎯 추천 설치 순서

1. **첫 시도**: `pip install -r requirements_minimal.txt`
2. **성공시**: 프로그램 실행해서 데모 모드 체험
3. **만족시**: `pip install sounddevice`로 녹음 기능 추가
4. **필요시**: 나머지 선택적 패키지들 개별 설치

이 순서로 하면 대부분의 호환성 문제를 피할 수 있습니다!
