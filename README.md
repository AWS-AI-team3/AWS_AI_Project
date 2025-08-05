# MediaPipe Gesture Control Desktop Application

  A Python-based desktop application that uses MediaPipe for hand gesture recognition to control mouse functions. Control your computer using hand gestures captured through
  your webcam.

  ## 🚀 Features

  - **Hand Gesture Recognition**: Real-time hand tracking using MediaPipe
  - **Mouse Control**: Index finger cursor movement and thumb-index pinch clicking
  - **Cross-Platform**: Works on Windows and macOS
  - **Modular Architecture**: Optional AWS face recognition and Google authentication modules
  - **Modern GUI**: CustomTkinter-based user interface

  ## 🎮 How to Use

  1. **Cursor Control**: Point your index finger to move the mouse cursor
  2. **Left Click**: Pinch your thumb and index finger together
  3. **Camera View**: Small camera window shows hand tracking feedback
  4. **Desktop Control**: Cursor appears on your desktop, not in the camera window

  ## 📋 Prerequisites

  - Python 3.8 or higher
  - Webcam/Camera
  - Internet connection (for package installation)

  ## 🛠️ Installation

  ### Windows Users

  1. **Install uv package manager**:
     ```powershell
     # Using PowerShell (recommended)
     powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

     # Or using pip
     pip install uv

  2. Clone the repository:
  git clone https://github.com/ashcircle03/AWS_AI_Project.git
  cd AWS_AI_Project
  3. Create virtual environment and install dependencies:
  # Create virtual environment
  uv venv

  # Activate virtual environment
  .venv\Scripts\activate

  # Install dependencies
  uv pip install -e .
  4. Run the application:
  # Option 1: Using uv (recommended)
  uv run python main.py

  # Option 2: With activated venv
  python main.py

  macOS Users

  1. Install uv package manager:
  # Using Homebrew (recommended)
  brew install uv

  # Or using curl
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Or using pip
  pip install uv
  2. Clone the repository:
  git clone https://github.com/ashcircle03/AWS_AI_Project.git
  cd AWS_AI_Project
  3. Create virtual environment and install dependencies:
  # Create virtual environment
  uv venv

  # Activate virtual environment
  source .venv/bin/activate

  # Install dependencies
  uv pip install -e .
  4. Run the application:
  # Option 1: Using uv (recommended)
  uv run python main.py

  # Option 2: With activated venv
  python main.py

  Alternative Installation (Both Platforms)

  If you prefer using traditional pip:

  # Clone repository
  git clone https://github.com/ashcircle03/AWS_AI_Project.git
  cd AWS_AI_Project

  # Create virtual environment
  python -m venv .venv

  # Activate virtual environment
  # Windows:
  .venv\Scripts\activate
  # macOS/Linux:
  source .venv/bin/activate

  # Install dependencies
  pip install -r requirements.txt

  # Run application
  python main.py

  🔧 Development Setup

  For team members who want to contribute:

  1. Fork the repository on GitHub
  2. Clone your fork:
  git clone https://github.com/YOUR_USERNAME/AWS_AI_Project.git
  cd AWS_AI_Project
  3. Install with development dependencies:
  uv pip install -e ".[dev]"
  4. Available development tools:
  # Run tests
  uv run pytest tests/

  # Code formatting
  uv run black src/

  # Linting
  uv run flake8 src/

  # Type checking
  uv run mypy src/

  🖥️ System Requirements

  Windows

  - Windows 10 or higher
  - Camera access permission
  - Python 3.8+

  macOS

  - macOS 10.14 or higher
  - Camera access permission (System Preferences → Security & Privacy → Camera)
  - Accessibility permission for mouse control (System Preferences → Security & Privacy → Accessibility)
  - Python 3.8+

  📦 Project Structure

  AWS_AI_Project/
  ├── src/
  │   ├── auth/              # Authentication modules (optional)
  │   ├── face/              # Face recognition modules (optional)
  │   ├── gesture/           # Hand gesture recognition & mouse control
  │   ├── gui/               # User interface components
  │   └── utils/             # Utility functions
  ├── config/                # Configuration settings
  ├── assets/                # Images, GIFs, and other assets
  ├── tests/                 # Test files
  ├── main.py               # Main application entry point
  ├── pyproject.toml        # Project configuration and dependencies
  ├── requirements.txt      # Pip-compatible requirements
  └── README.md            # This file

  🔍 Troubleshooting

  Common Issues

  1. Camera not detected:
    - Check camera permissions in system settings
    - Try different camera indices (0, 1, 2) in the code
    - Restart the application
  2. Mouse control not working:
    - macOS: Enable accessibility permissions for Terminal/Python
    - Windows: Run as administrator if needed
    - Check if pyautogui is properly installed
  3. Package installation errors:
    - Update pip: pip install --upgrade pip
    - Try installing dependencies one by one
    - Check Python version compatibility
  4. Performance issues:
    - Close other camera applications
    - Reduce camera resolution in settings
    - Ensure good lighting conditions

  Getting Help

  - Issues: Report bugs on https://github.com/ashcircle03/AWS_AI_Project/issues
  - Discussions: Use https://github.com/ashcircle03/AWS_AI_Project/discussions for questions
  - Contributing: See CONTRIBUTING.md for contribution guidelines

  🚧 Optional Features

  AWS Face Recognition (Optional)

  To enable AWS face recognition, set up AWS credentials:
  # Install AWS CLI and configure
  aws configure

  # Or set environment variables
  export AWS_ACCESS_KEY_ID="your_access_key"
  export AWS_SECRET_ACCESS_KEY="your_secret_key"
  export AWS_DEFAULT_REGION="us-east-1"

  Google Authentication (Optional)

  To enable Google OAuth, set up Google Cloud credentials:
  export GOOGLE_CLIENT_ID="your_client_id"
  export GOOGLE_CLIENT_SECRET="your_client_secret"

  📄 License

  This project is licensed under the MIT License - see the LICENSE file for details.

  🤝 Contributing

  1. Fork the repository
  2. Create a feature branch (git checkout -b feature/amazing-feature)
  3. Commit your changes (git commit -m 'Add amazing feature')
  4. Push to the branch (git push origin feature/amazing-feature)
  5. Open a Pull Request

  👥 Team

  - Lead Developer: [Your Name]
  - Contributors: See https://github.com/ashcircle03/AWS_AI_Project/graphs/contributors

  ---
  Made with ❤️ using MediaPipe, OpenCV, and Python