"""
Hand skeleton overlay that appears above all applications
"""

import cv2
import numpy as np
import threading
import time
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor
import mediapipe as mp
from typing import Optional, List, Tuple
import pyautogui

# Disable PyAutoGUI failsafe for smooth operation
pyautogui.FAILSAFE = False

from src.gesture.gesture_recognizer import GestureRecognizer
from src.gesture.mouse_controller import MouseController


class HandOverlayWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.hand_landmarks = None
        self.screen_width = QApplication.primaryScreen().size().width()
        self.screen_height = QApplication.primaryScreen().size().height()
        
        # Make widget transparent and always on top
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        # Set to full screen
        self.setGeometry(0, 0, self.screen_width, self.screen_height)
        
    def update_landmarks(self, landmarks: Optional[List[List[float]]]):
        """Update hand landmarks and trigger repaint"""
        self.hand_landmarks = landmarks
        self.update()
        
    def paintEvent(self, event):
        """Draw hand skeleton on overlay"""
        if not self.hand_landmarks:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Set up pen for drawing
        pen = QPen(QColor(0, 255, 0, 200))  # Green with transparency
        pen.setWidth(3)
        painter.setPen(pen)
        
        # Convert normalized landmarks to screen coordinates
        screen_landmarks = []
        for point in self.hand_landmarks:
            x = int(point[0] * self.screen_width)
            y = int(point[1] * self.screen_height)
            screen_landmarks.append((x, y))
        
        # Draw hand connections
        self.draw_hand_connections(painter, screen_landmarks)
        
        # Draw landmarks as dots
        dot_pen = QPen(QColor(255, 0, 0, 200))  # Red dots
        dot_pen.setWidth(6)
        painter.setPen(dot_pen)
        
        for x, y in screen_landmarks:
            painter.drawPoint(x, y)
    
    def draw_hand_connections(self, painter, landmarks):
        """Draw hand skeleton connections"""
        # MediaPipe hand connections
        connections = [
            # Thumb
            (0, 1), (1, 2), (2, 3), (3, 4),
            # Index finger
            (0, 5), (5, 6), (6, 7), (7, 8),
            # Middle finger
            (0, 9), (9, 10), (10, 11), (11, 12),
            # Ring finger
            (0, 13), (13, 14), (14, 15), (15, 16),
            # Pinky
            (0, 17), (17, 18), (18, 19), (19, 20),
            # Palm connections
            (5, 9), (9, 13), (13, 17)
        ]
        
        for start_idx, end_idx in connections:
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                start_point = landmarks[start_idx]
                end_point = landmarks[end_idx]
                painter.drawLine(start_point[0], start_point[1], 
                               end_point[0], end_point[1])


class HandOverlay:
    def __init__(self):
        self.gesture_recognizer = GestureRecognizer()
        self.mouse_controller = MouseController()
        self.overlay_widget = HandOverlayWidget()
        self.cap = None
        self.is_tracking = False
        self.tracking_thread = None
        
        # Timer for updating overlay
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)
        
    def start_tracking(self):
        """Start hand tracking"""
        if self.is_tracking:
            return
            
        self.cap = cv2.VideoCapture(0)
        # Set high resolution for better accuracy
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        
        self.is_tracking = True
        self.overlay_widget.show()
        self.timer.start(16)  # ~60 FPS for better responsiveness
        
    def stop_tracking(self):
        """Stop hand tracking"""
        self.is_tracking = False
        self.timer.stop()
        
        if self.cap:
            self.cap.release()
            self.cap = None
            
        self.overlay_widget.hide()
        
    def process_frame(self):
        """Process camera frame and update overlay"""
        if not self.is_tracking or not self.cap:
            return
            
        ret, frame = self.cap.read()
        if not ret:
            return
            
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Process frame with gesture recognizer
        processed_frame, gesture_data = self.gesture_recognizer.process_frame(frame)
        
        if gesture_data and gesture_data['landmarks'] is not None:
            # Update overlay with landmarks
            landmarks = gesture_data['landmarks'].tolist()
            self.overlay_widget.update_landmarks(landmarks)
            
            # Get mouse position from thumb
            mouse_pos = self.gesture_recognizer.get_mouse_position(gesture_data['landmarks'], frame.shape[:2])
            
            # Debug: Print gesture and mouse position
            print(f"Gesture: {gesture_data['type']}, Mouse pos: {mouse_pos}")
            
            # Process gesture with mouse controller
            self.mouse_controller.process_gesture(gesture_data, mouse_pos)
        else:
            # Clear overlay if no hand detected
            self.overlay_widget.update_landmarks(None)
            # End any ongoing gestures
            self.mouse_controller.process_gesture(None, None)
            
    def handle_gesture(self, gesture_data):
        """Handle detected gestures (deprecated - now handled by mouse_controller)"""
        pass  # Now handled by mouse_controller.process_gesture()