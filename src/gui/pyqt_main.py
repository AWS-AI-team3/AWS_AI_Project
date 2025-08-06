"""
PyQt6-based main window for gesture control
"""

import sys
import platform
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QWidget, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# Windows DPI 인식 설정
if platform.system() == "Windows":
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_SCALE_FACTOR"] = "1"

from src.gesture.hand_overlay import HandOverlay


class PyQtMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.hand_overlay = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Gesture Control - PyQt")
        self.setGeometry(100, 100, 500, 400)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Gesture Control")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Spacing
        layout.addStretch()
        
        # Google Auth button (just UI, no actual authentication)
        auth_button = QPushButton("Google 로그인")
        auth_button.setFixedSize(200, 50)
        auth_button.clicked.connect(self.on_google_auth)
        
        # Center the button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(auth_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Control buttons (initially hidden)
        self.control_frame = QFrame()
        self.control_layout = QVBoxLayout(self.control_frame)
        
        # Start tracking button
        self.start_button = QPushButton("손 추적 시작")
        self.start_button.setFixedSize(200, 50)
        self.start_button.clicked.connect(self.start_tracking)
        
        # Stop tracking button
        self.stop_button = QPushButton("손 추적 중지")
        self.stop_button.setFixedSize(200, 50)
        self.stop_button.clicked.connect(self.stop_tracking)
        self.stop_button.hide()
        
        # Center control buttons
        control_button_layout = QHBoxLayout()
        control_button_layout.addStretch()
        control_button_layout.addWidget(self.start_button)
        control_button_layout.addWidget(self.stop_button)
        control_button_layout.addStretch()
        
        self.control_layout.addLayout(control_button_layout)
        
        layout.addWidget(self.control_frame)
        self.control_frame.hide()
        
        layout.addStretch()
        
    def on_google_auth(self):
        """Handle Google authentication button click"""
        # For now, just show the control buttons
        self.control_frame.show()
        self.sender().hide()
        
    def start_tracking(self):
        """Start hand tracking with overlay"""
        if self.hand_overlay is None:
            self.hand_overlay = HandOverlay()
        
        self.hand_overlay.start_tracking()
        self.start_button.hide()
        self.stop_button.show()
        
    def stop_tracking(self):
        """Stop hand tracking"""
        if self.hand_overlay:
            self.hand_overlay.stop_tracking()
        
        self.stop_button.hide()
        self.start_button.show()
        
    def closeEvent(self, event):
        """Handle window close event"""
        if self.hand_overlay:
            self.hand_overlay.stop_tracking()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = PyQtMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()