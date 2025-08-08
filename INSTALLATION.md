# 🚀 설치 가이드

## 📦 uv를 이용한 모듈러 설치 (권장)

### 👤 **일반 사용자용 설치**
제스처 제어 앱의 모든 기능을 사용하고 싶은 경우:

```bash
# uv 가상환경 생성 및 활성화
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 사용자용 설치 (모든 앱 기능 포함)
uv pip install -e .
```

**포함된 기능:**
- ✅ 손 추적 및 제스처 인식 (MediaPipe)
- ✅ 마우스/키보드 제어 (PyAutoGUI)
- ✅ PyQt6 오버레이 시스템
- ✅ 카메라 피드, 리모컨, 광고창 등 모든 GUI

### 🛠️ **개발자용 설치** 
코드 개발 및 기여를 위한 경우:

```bash
# uv 가상환경 생성 및 활성화
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

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
```bash
python src/gui/pyqt_main.py
```

### 심플 버전
```bash  
python main.py
```

## 📋 시스템 요구사항

- **Python**: 3.8.1 이상
- **OS**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **카메라**: USB 웹캠 또는 내장 카메라
- **메모리**: 최소 4GB RAM (8GB 권장)

## 🔧 문제 해결

### MediaPipe 설치 실패 시
```bash
# pip 업그레이드 후 재시도
uv pip install --upgrade pip
uv pip install mediapipe
```

### PyQt6 설치 실패 시
```bash  
# 시스템별 의존성 설치
# Ubuntu/Debian
sudo apt-get install python3-pyqt6

# macOS  
brew install pyqt6

# Windows - 일반적으로 자동 설치됨
```

### 권한 오류 시
```bash
# Windows에서 관리자 권한으로 실행하거나
# 사용자 레벨 설치 사용
uv pip install --user -e .
```

## 📊 용량 정보

- **사용자용**: ~300MB
- **개발자용**: ~350MB  

## 🆘 지원

문제가 발생하면 [GitHub Issues](https://github.com/AWS-AI-team3/AWS_AI_Project/issues)에 보고해주세요.