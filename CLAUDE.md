# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MediaPipe Gesture Control Desktop Application - A Python-based desktop application that uses MediaPipe for hand gesture recognition to control mouse functions and system interactions.

### Key Features
- Google OAuth authentication
- Face recognition for user verification
- Real-time hand gesture recognition using MediaPipe
- Mouse control via hand gestures (click, scroll, move)
- Voice control integration
- Customizable gesture mappings
- Modern GUI using CustomTkinter

## Development Setup

### Installation with uv
```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .

# Or install with dev dependencies
uv pip install -e ".[dev]"
```

### Alternative: Install from requirements.txt
```bash
uv pip install -r requirements.txt
```

### Environment Variables
Set up Google OAuth credentials:
```bash
export GOOGLE_CLIENT_ID="your_client_id"
export GOOGLE_CLIENT_SECRET="your_client_secret"
```

### Running the Application
```bash
# With uv
uv run python main.py

# Or after activating venv
python main.py
```

### Testing
```bash
uv run pytest tests/
```

## Architecture

### Project Structure
```
src/
├── auth/           # Google OAuth authentication
├── face/           # Face recognition system
├── gesture/        # MediaPipe gesture recognition & mouse control
├── gui/           # CustomTkinter GUI components
└── utils/         # Utility functions

config/            # Application settings and configuration
assets/           # Images, GIFs, and other assets
user_data/        # User-specific data storage
```

### Core Components
- **GestureRecognizer**: MediaPipe-based hand tracking and gesture classification
- **MouseController**: Converts gestures to mouse actions using pyautogui
- **FaceRecognitionSystem**: User authentication via face recognition
- **GoogleAuthenticator**: OAuth 2.0 authentication flow
- **Main GUI**: CustomTkinter-based user interface with multiple windows

### Gesture Mappings
- Index finger pointing → Mouse cursor movement
- Index finger tap → Left click
- Middle finger tap → Right click
- Thumb up/down → Scroll up/down
- Fist → Drag start
- Open hand → Drag end
- Peace sign → Voice control start
- Stop gesture → End tracking

### Data Flow
1. User authenticates via Google OAuth
2. Face recognition verifies user identity
3. Camera captures video frames
4. MediaPipe processes frames for hand landmarks
5. Gesture classifier determines gesture type
6. Mouse controller executes corresponding actions
7. Settings allow gesture customization