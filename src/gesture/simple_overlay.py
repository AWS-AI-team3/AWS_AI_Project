"""
Simple floating window overlay for hand skeleton
"""

import cv2
import numpy as np
import threading
import time
from PyQt6.QtWidgets import QWidget, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QObject
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QPixmap, QImage
from typing import Optional, List
try:
    import pyautogui
except ImportError:
    print("WARNING: pyautogui not installed, mouse control will be disabled")
    pyautogui = None

from src.gesture.thumb_gesture_recognizer import ThumbGestureRecognizer


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
        
        # Only draw fingertips: thumb(4), index(8), middle(12)
        fingertip_indices = [4, 8, 12]  # Thumb, Index, Middle fingertips
        
        dot_pen = QPen(QColor(255, 0, 0, 200))  # Red dots
        dot_pen.setWidth(8)  # Larger dots for fingertips
        painter.setPen(dot_pen)
        
        for i in fingertip_indices:
            if i < len(screen_landmarks):
                x, y = screen_landmarks[i]
                painter.drawPoint(x, y)
    
    def draw_hand_connections(self, painter, landmarks):
        """Draw hand skeleton connections - now disabled for fingertips only mode"""
        # No connections drawn - only showing fingertips
        pass


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


class AdOverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_window()
        self.setup_timer()
        
    def setup_window(self):
        """Setup ad overlay window at bottom-right"""
        self.setWindowTitle("Ad")
        self.setFixedSize(250, 150)
        
        # Position at bottom-right of screen
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 270, screen.height() - 200)
        
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.FramelessWindowHint
        )
        
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(50, 50, 50, 200);
                border: 2px solid #00ff00;
                border-radius: 10px;
            }
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        # Layout
        layout = QVBoxLayout()
        self.ad_label = QLabel("💡 Gesture Control Pro\n✨ Premium Features Available")
        self.ad_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.ad_label)
        self.setLayout(layout)
        
    def setup_timer(self):
        """Setup timer for periodic display"""
        self.show_timer = QTimer()
        self.show_timer.timeout.connect(self.show_ad)
        self.show_timer.start(10000)  # Show every 10 seconds
        
        self.hide_timer = QTimer()
        self.hide_timer.timeout.connect(self.hide)
        
    def show_ad(self):
        """Show ad for a brief period"""
        self.show()
        self.hide_timer.start(3000)  # Hide after 3 seconds
        
    def mousePressEvent(self, event):
        """Allow dragging the window"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            
    def mouseMoveEvent(self, event):
        """Handle window dragging"""
        if hasattr(self, 'drag_position') and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)


class CameraOverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.current_frame = None
        self.setup_window()
        
    def setup_window(self):
        """Setup camera overlay window at top-right"""
        self.setWindowTitle("Camera Feed")
        self.setFixedSize(320, 240)
        
        # Position at top-right of screen
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 340, 20)
        
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.FramelessWindowHint
        )
        
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 150);
                border: 2px solid #0099ff;
                border-radius: 8px;
            }
        """)
        
    def update_frame(self, frame):
        """Update camera frame"""
        if frame is not None:
            self.current_frame = frame
            self.update()
            
    def paintEvent(self, event):
        """Draw camera frame"""
        painter = QPainter(self)
        
        if self.current_frame is not None:
            try:
                # Convert OpenCV frame to Qt format
                height, width, channel = self.current_frame.shape
                bytes_per_line = 3 * width
                
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
                
                # Create QImage properly
                q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                
                # Convert to QPixmap and scale
                pixmap = QPixmap.fromImage(q_image).scaled(
                    self.size(), 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                
                # Draw the frame
                painter.drawPixmap(0, 0, pixmap)
            except Exception as e:
                # Draw error message if frame conversion fails
                painter.setPen(QPen(QColor(255, 0, 0), 2))
                painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"Frame Error: {str(e)}")
        else:
            # Draw placeholder when no camera frame
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.drawRect(10, 10, self.width()-20, self.height()-20)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Camera Feed")
        
    def mousePressEvent(self, event):
        """Allow dragging the window"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            
    def mouseMoveEvent(self, event):
        """Handle window dragging"""
        if hasattr(self, 'drag_position') and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)


class RemoteControlWindow(QWidget):
    record_start = pyqtSignal()
    record_stop = pyqtSignal()
    tracking_stop = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.setup_window()
        self.setup_ui()
        
    def setup_window(self):
        """Setup remote control window"""
        self.setWindowTitle("Remote Control")
        self.setFixedSize(200, 160)
        
        # Position at center-left of screen
        screen = QApplication.primaryScreen().geometry()
        self.move(50, screen.height() // 2 - 80)
        
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.FramelessWindowHint
        )
        
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(40, 40, 40, 220);
                border: 2px solid #ff6600;
                border-radius: 10px;
            }
            QPushButton {
                background-color: rgba(60, 60, 60, 200);
                color: white;
                border: 1px solid #888;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(80, 80, 80, 200);
            }
            QPushButton:pressed {
                background-color: rgba(100, 100, 100, 200);
            }
        """)
        
    def setup_ui(self):
        """Setup remote control UI"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Record buttons
        self.record_btn = QPushButton("🔴 녹음 시작")
        self.record_btn.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_btn)
        
        # Tracking stop button
        self.stop_tracking_btn = QPushButton("⏹️ 트래킹 종료")
        self.stop_tracking_btn.clicked.connect(self.tracking_stop.emit)
        layout.addWidget(self.stop_tracking_btn)
        
        self.setLayout(layout)
        
    def toggle_recording(self):
        """Toggle recording state"""
        if self.is_recording:
            self.record_btn.setText("🔴 녹음 시작")
            self.record_stop.emit()
            self.is_recording = False
        else:
            self.record_btn.setText("⏹️ 녹음 종료")
            self.record_start.emit()
            self.is_recording = True
            
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
        self.hand_overlay_widget = HandOverlayWidget()  # Full screen hand skeleton
        self.ad_window = AdOverlayWindow()
        self.camera_window = CameraOverlayWindow()
        self.remote_window = RemoteControlWindow()
        
        self.cap = None
        self.is_tracking = False
        self.is_recording = False
        
        # Callback for when tracking is stopped from remote
        self.tracking_stop_callback = None
        
        # Connect remote control signals
        self.remote_window.record_start.connect(self.start_recording)
        self.remote_window.record_stop.connect(self.stop_recording)
        self.remote_window.tracking_stop.connect(self.on_remote_tracking_stop)
        
        # Timer for updating
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)
        
        # Initially hide all overlay windows
        self.hand_overlay_widget.hide()
        self.camera_window.hide()
        self.remote_window.hide()
        self.ad_window.hide()
        
    def start_tracking(self):
        """Start hand tracking"""
        if self.is_tracking:
            return
            
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.is_tracking = True
        
        # Show all overlay windows when tracking starts
        self.camera_window.show()
        self.remote_window.show()
        # Ad window will show automatically via timer (every 10 seconds)
        
        # Show hand overlay last to ensure it's on top
        self.hand_overlay_widget.show()
        self.hand_overlay_widget.raise_()  # Bring to front
        
        self.timer.start(33)  # ~30 FPS
        
        print("✅ Hand tracking started with all overlay windows")
        
    def stop_tracking(self):
        """Stop hand tracking"""
        self.is_tracking = False
        self.timer.stop()
        
        if self.cap:
            self.cap.release()
            self.cap = None
            
        # Hide all overlay windows
        self.hand_overlay_widget.hide()
        self.camera_window.hide()
        self.remote_window.hide()
        self.ad_window.hide()
        
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
        
        # Update camera overlay with current frame
        self.camera_window.update_frame(frame)
        
        if gesture_data and gesture_data['landmarks'] is not None:
            # Update full screen overlay with landmarks
            landmarks = gesture_data['landmarks'].tolist()
            self.hand_overlay_widget.update_landmarks(landmarks)
            
            # Move cursor to thumb position (always follow thumb)
            thumb_pos = self.gesture_recognizer.get_thumb_position(gesture_data['landmarks'])
            if thumb_pos and pyautogui:
                screen_x = int(thumb_pos[0] * pyautogui.size()[0])
                screen_y = int(thumb_pos[1] * pyautogui.size()[1])
                pyautogui.moveTo(screen_x, screen_y, duration=0.01)
            
            # Handle gestures for cursor control
            self.handle_gesture(gesture_data)
        else:
            # Clear overlay if no hand detected
            self.hand_overlay_widget.update_landmarks(None)
            
    def handle_gesture(self, gesture_data):
        """Handle detected gestures"""
        gesture_type = gesture_data['type']
        landmarks = gesture_data['landmarks']
        
        if pyautogui is None:
            return
            
        # Thumb cursor movement is now handled in process_frame()
        # Only handle click gestures here
        if gesture_type == "thumb_index_click":
            pyautogui.click()
            
        elif gesture_type == "thumb_index_double_click":
            pyautogui.doubleClick()
            
    def start_recording(self):
        """Start recording functionality"""
        if not self.is_recording:
            self.is_recording = True
            print("🔴 녹음 시작됨")
            
    def stop_recording(self):
        """Stop recording functionality"""
        if self.is_recording:
            self.is_recording = False
            print("⏹️ 녹음 종료됨")
            
    def set_tracking_stop_callback(self, callback):
        """Set callback function to be called when remote tracking stop is pressed"""
        self.tracking_stop_callback = callback
        
    def on_remote_tracking_stop(self):
        """Handle tracking stop from remote control"""
        self.stop_tracking()
        # Call the callback if set (to update main GUI)
        if self.tracking_stop_callback:
            self.tracking_stop_callback()
