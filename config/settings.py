"""
Application settings and configuration
"""

import os
from typing import Dict, Any

# Application settings
APP_NAME = "Gesture Control"
APP_VERSION = "1.0.0"

# Google OAuth settings
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
REDIRECT_URI = 'http://localhost:8080/callback'

# MediaPipe settings
MEDIAPIPE_CONFIDENCE = 0.7
HAND_DETECTION_CONFIDENCE = 0.5
HAND_TRACKING_CONFIDENCE = 0.5
MAX_NUM_HANDS = 2

# Face recognition settings
FACE_RECOGNITION_TOLERANCE = 0.6
FACE_DETECTION_MODEL = 'hog'  # or 'cnn' for better accuracy

# Camera settings
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# Mouse control settings
MOUSE_SENSITIVITY = 1.0
SCROLL_SENSITIVITY = 2
CLICK_HOLD_TIME = 0.5

# UI settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
THEME = "dark"

# Gesture definitions
GESTURE_MAPPING = {
    "left_click": "index_finger_tap",
    "right_click": "middle_finger_tap", 
    "scroll_up": "thumb_up",
    "scroll_down": "thumb_down",
    "mouse_move": "index_finger_point",
    "start_voice": "peace_sign",
    "stop_voice": "fist",
    "stop_tracking": "stop_gesture"
}

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
GIFS_DIR = os.path.join(ASSETS_DIR, "gifs")
USER_DATA_DIR = os.path.join(BASE_DIR, "user_data")

# Ensure directories exist
for directory in [ASSETS_DIR, IMAGES_DIR, GIFS_DIR, USER_DATA_DIR]:
    os.makedirs(directory, exist_ok=True)