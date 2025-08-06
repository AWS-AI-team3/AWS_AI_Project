# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MediaPipe Gesture Control Desktop Application - A Python-based desktop application that uses MediaPipe for hand gesture recognition to control mouse functions and system interactions.

### Key Features
- Real-time hand gesture recognition using MediaPipe
- Mouse control via hand gestures (cursor movement, clicking)
- Cross-platform support (Windows/macOS)
- Modular architecture with optional authentication modules
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
├── auth/           # Authentication modules (Google OAuth - optional)
├── face/           # Face recognition modules (AWS Rekognition - optional)
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
- **CursorOverlay**: Desktop cursor visualization system
- **Optional Modules**:
  - **AWSFaceRecognitionModule**: AWS Rekognition-based face authentication
  - **GoogleAuthModule**: OAuth 2.0 authentication flow

### Current Gesture Mappings (Index Finger Based)
- Index finger pointing → Mouse cursor movement
- Thumb-index pinch → Left click
- Thumb up/down → Scroll up/down
- Fist → Drag start
- Open hand → Drag end
- Peace sign → Special gesture

### Data Flow
1. Camera captures video frames
2. MediaPipe processes frames for hand landmarks  
3. GestureRecognizer classifies gestures based on finger positions
4. MouseController executes corresponding mouse actions
5. CursorOverlay provides visual feedback on desktop

## Development Progress Log

### Phase 1: Initial Setup (Completed)
- ✅ Created project structure with uv package management
- ✅ Set up MediaPipe hand tracking system
- ✅ Implemented basic gesture recognition
- ✅ Created mouse control functionality

### Phase 2: Modular Architecture (Completed)
- ✅ Separated Google OAuth into optional module (src/auth/google_auth_module.py)
- ✅ Separated AWS Face Recognition into optional module (src/face/aws_face_recognition_module.py)
- ✅ Created placeholder systems for main app to work without optional modules
- ✅ Fixed uv dependency management issues (removed face_recognition lib conflicts)

### Phase 3: Gesture Control Implementation (Completed)
- ✅ Implemented index finger cursor control with normalized coordinates
- ✅ Added thumb-index pinch detection for left clicking
- ✅ Fixed coordinate mapping for proper mirror effect handling
- ✅ Created desktop cursor overlay system (SimpleCursorOverlay)
- ✅ Proper screen coordinate mapping from MediaPipe landmarks

### Phase 4: Documentation & Deployment (Completed)
- ✅ Created comprehensive README with Windows/macOS installation guides
- ✅ Added troubleshooting section for common issues
- ✅ Set up development workflow for team collaboration
- ✅ Deployed to GitHub with proper commit messages

### Current Implementation Details

#### Gesture Recognition Logic
- Uses MediaPipe landmark detection (21 points per hand)
- Pinch detection: Euclidean distance between thumb tip (4) and index tip (8)
- Pinch threshold: distance < 0.05 (normalized coordinates)
- Cursor tracking: Uses index finger tip (landmark 8) position

#### Coordinate System
- MediaPipe provides normalized coordinates [0,1]
- Direct mapping to screen coordinates without additional mirroring
- Frame is flipped horizontally for natural camera interaction

#### Mouse Control
- pyautogui handles actual mouse movement and clicking
- Gesture-to-action mapping in MouseController class
- Click debouncing: 0.5 second minimum between clicks

### Next Development Phase: Thumb Cursor Control
**Planned Changes:**
- Switch from index finger (landmark 8) to thumb tip (landmark 4) for cursor control
- Adjust gesture classification logic for thumb-based interaction
- Update coordinate mapping for thumb movement patterns
- Modify click detection to use different finger combinations

### Technical Notes
- Cross-platform compatibility maintained through proper path handling
- Optional modules prevent dependency issues for core functionality  
- uv package manager ensures consistent environments across team
- MediaPipe TensorFlow Lite backend provides efficient processing