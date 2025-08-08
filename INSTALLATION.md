# 🚀 Windows 설치 가이드

## 🎯 Windows 전용 uv 설치

### 👤 **일반 사용자용 설치**
제스처 제어 앱의 모든 기능을 사용하려면:

```cmd
# uv 가상환경 생성 및 활성화
uv venv
.venv\Scripts\activate

# 사용자용 설치 (모든 앱 기능 포함)
uv pip install -e .
```

**포함된 기능:**
- ✅ 손 추적 및 제스처 인식 (MediaPipe)
- ✅ 마우스/키보드 제어 (PyAutoGUI)
- ✅ PyQt6 오버레이 시스템
- ✅ 카메라 피드, 리모컨, 광고창 등 모든 GUI

### 🛠️ **개발자용 설치** 
코드 개발 및 기여를 위해:

```cmd
# uv 가상환경 생성 및 활성화
uv venv
.venv\Scripts\activate

# 개발자용 설치 (개발 도구 포함)
uv pip install -e ".[dev]"
```

**추가 포함 기능:**
- 📋 모든 사용자 기능
- 🧪 테스트 도구 (pytest, pytest-cov)
- 🎨 코드 포매팅 (black)
- 🔍 정적 분석 (flake8, mypy)
- ⚡ 사전 커밋 훅 (pre-commit)

## 🏃‍♂️ 실행 방법

### PyQt6 GUI 버전 (권장)
```cmd
python src\gui\pyqt_main.py
```

### 심플 버전
```cmd
python main.py
```

## 📋 Windows 시스템 요구사항

- **Python**: 3.8.1 이상
- **OS**: Windows 10 (1903 이상) 또는 Windows 11
- **카메라**: USB 웹캠 또는 내장 카메라
- **메모리**: 최소 4GB RAM (8GB 권장)
- **Visual C++ Redistributable**: 2015-2022 (MediaPipe 요구사항)

## 🔧 Windows 문제 해결

### MediaPipe 설치 실패 시
```cmd
# Visual C++ Redistributable 설치 후 재시도
# https://aka.ms/vs/17/release/vc_redist.x64.exe

# pip 업그레이드 후 재시도
uv pip install --upgrade pip
uv pip install mediapipe
```

### DPI 인식 경고 시
- Qt 애플리케이션에서 DPI 관련 경고가 나타날 수 있으나 기능에는 영향 없음
- Windows 디스플레이 설정에서 "배율 및 레이아웃" 100%로 설정 권장

### 관리자 권한 필요 시
```cmd
# 명령 프롬프트를 관리자 권한으로 실행하거나
# 사용자 레벨 설치 사용
uv pip install --user -e .
```

### 카메라 접근 권한
Windows 10/11에서 카메라 접근이 차단된 경우:
1. **설정** > **개인 정보 보호** > **카메라**
2. **데스크톱 앱이 카메라에 액세스하도록 허용** 켜기

## 📊 용량 정보

- **사용자용**: ~300MB
- **개발자용**: ~350MB  

## 🆘 지원

문제가 발생하면 [GitHub Issues](https://github.com/AWS-AI-team3/AWS_AI_Project/issues)에 보고해주세요.