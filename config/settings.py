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

# MediaPipe settings - Optimized for speed and accuracy
MEDIAPIPE_CONFIDENCE = 0.8
HAND_DETECTION_CONFIDENCE = 0.8  # Higher for better accuracy
HAND_TRACKING_CONFIDENCE = 0.7   # Higher for smoother tracking
MAX_NUM_HANDS = 1  # Focus on single hand for better performance

# Face recognition settings
FACE_RECOGNITION_TOLERANCE = 0.6
FACE_DETECTION_MODEL = 'hog'  # or 'cnn' for better accuracy

# Camera settings - Optimized for performance
CAMERA_INDEX = 0
CAMERA_WIDTH = 1280  # Higher resolution for better accuracy
CAMERA_HEIGHT = 720
CAMERA_FPS = 60  # Higher FPS for better responsiveness

# Mouse control settings - Optimized for responsiveness
MOUSE_SENSITIVITY = 1.2
SCROLL_SENSITIVITY = 3
CLICK_HOLD_TIME = 0.1  # Faster click response
DOUBLE_CLICK_THRESHOLD = 0.4  # Max time between clicks for double-click
PINCH_THRESHOLD = 0.04  # More sensitive pinch detection
SCROLL_ANGLE_THRESHOLD = 0.15  # More sensitive scroll detection

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