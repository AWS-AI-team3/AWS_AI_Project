"""
Simple floating window overlay for hand skeleton
"""

import cv2
import numpy as np
import threading
import time
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPainter, QPen, QColor
from typing import Optional, List
import pyautogui

from src.gesture.thumb_gesture_recognizer import ThumbGestureRecognizer


class FloatingSkeletonWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.hand_landmarks = None
        self.setup_window()
        
    def setup_window(self):
        """Setup floating window"""
        self.setWindowTitle("Hand Skeleton")
        self.setGeometry(50, 50, 400, 300)  # Small floating window
        
        # Make window stay on top but not interfere with other apps
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.FramelessWindowHint
        )
        
        # Semi-transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 100);")
        
    def update_landmarks(self, landmarks: Optional[List[List[float]]]):
        """Update hand landmarks and trigger repaint"""
        self.hand_landmarks = landmarks
        self.update()
        
    def paintEvent(self, event):
        """Draw hand skeleton"""
        if not self.hand_landmarks:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Scale landmarks to window size
        window_width = self.width()
        window_height = self.height()
        
        screen_landmarks = []
        for point in self.hand_landmarks:
            # Scale and flip landmarks to fit window
            x = int((1.0 - point[0]) * window_width)  # Flip X for mirror
            y = int(point[1] * window_height)
            screen_landmarks.append((x, y))
        
        # Draw hand connections
        pen = QPen(QColor(0, 255, 0, 200))  # Green
        pen.setWidth(2)
        painter.setPen(pen)
        
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
            if start_idx < len(screen_landmarks) and end_idx < len(screen_landmarks):
                start_point = screen_landmarks[start_idx]
                end_point = screen_landmarks[end_idx]
                painter.drawLine(start_point[0], start_point[1], 
                               end_point[0], end_point[1])
        
        # Draw landmarks as dots
        dot_pen = QPen(QColor(255, 0, 0, 200))  # Red dots
        dot_pen.setWidth(4)
        painter.setPen(dot_pen)
        
        for x, y in screen_landmarks:
            painter.drawPoint(x, y)
            
    def mousePressEvent(self, event):
        """Allow dragging the window"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            
    def mouseMoveEvent(self, event):
        """Handle window dragging"""
        if hasattr(self, 'drag_position') and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)


class SimpleHandOverlay:
    def __init__(self):
        self.gesture_recognizer = ThumbGestureRecognizer()
        self.skeleton_window = FloatingSkeletonWindow()
        self.cap = None
        self.is_tracking = False
        
        # Timer for updating
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)
        
    def start_tracking(self):
        """Start hand tracking"""
        if self.is_tracking:
            return
            
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.is_tracking = True
        self.skeleton_window.show()
        self.timer.start(33)  # ~30 FPS
        
        print("✅ Hand tracking started with floating skeleton window")
        
    def stop_tracking(self):
        """Stop hand tracking"""
        self.is_tracking = False
        self.timer.stop()
        
        if self.cap:
            self.cap.release()
            self.cap = None
            
        self.skeleton_window.hide()
        
    def process_frame(self):
        """Process camera frame and update display"""
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
            # Update floating window with landmarks
            landmarks = gesture_data['landmarks'].tolist()
            self.skeleton_window.update_landmarks(landmarks)
            
            # Handle gestures for cursor control
            self.handle_gesture(gesture_data)
        else:
            # Clear skeleton if no hand detected
            self.skeleton_window.update_landmarks(None)
            
    def handle_gesture(self, gesture_data):
        """Handle detected gestures"""
        gesture_type = gesture_data['type']
        landmarks = gesture_data['landmarks']
        
        if gesture_type == "thumb_cursor":
            # Move cursor based on thumb position
            thumb_pos = self.gesture_recognizer.get_thumb_position(landmarks)
            if thumb_pos:
                screen_x = int(thumb_pos[0] * pyautogui.size()[0])
                screen_y = int(thumb_pos[1] * pyautogui.size()[1])
                pyautogui.moveTo(screen_x, screen_y, duration=0.02)
            
        elif gesture_type == "thumb_index_click":
            pyautogui.click()
            
        elif gesture_type == "thumb_index_double_click":
            pyautogui.doubleClick()