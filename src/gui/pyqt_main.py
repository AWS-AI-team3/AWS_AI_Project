"""
PyQt6-based main window for gesture control
Enhanced version with modern UI styling
"""

import sys
import platform
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QWidget, QFrame, QMessageBox, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor

# Windows DPI 인식 설정 (한 번만 실행)
_DPI_INITIALIZED = False

def setup_dpi_awareness():
    global _DPI_INITIALIZED
    if not _DPI_INITIALIZED and platform.system() == "Windows":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
        os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
        os.environ.setdefault("QT_SCALE_FACTOR", "1")
        _DPI_INITIALIZED = True

from src.gesture.simple_overlay import SimpleHandOverlay
from config.settings import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT


class PyQtMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.hand_overlay = None
        self.current_user = {'name': 'User', 'email': 'user@example.com'}  # Simplified user info
        self.is_authenticated = False
        self.setup_dark_theme()
        self.init_ui()
        
    def setup_dark_theme(self):
        """Set up modern dark theme from external stylesheet"""
        try:
            style_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'styles', 'dark_theme.qss')
            style_path = os.path.abspath(style_path)
            if os.path.exists(style_path):
                with open(style_path, 'r', encoding='utf-8') as f:
                    self.setStyleSheet(f.read())
            else:
                # Fallback to inline styles
                self.setStyleSheet("""
                    QMainWindow { background-color: #2b2b2b; color: #ffffff; }
                    QWidget { background-color: #2b2b2b; color: #ffffff; }
                    QPushButton { background-color: #404040; border: 2px solid #606060; 
                                border-radius: 8px; padding: 12px 24px; font-size: 14px; 
                                font-weight: bold; color: #ffffff; }
                    QPushButton:hover { background-color: #505050; border-color: #707070; }
                    QLabel { color: #ffffff; background: transparent; }
                    QFrame { background-color: #353535; border-radius: 10px; padding: 20px; }
                """)
        except Exception:
            # Minimal fallback
            self.setStyleSheet("QMainWindow { background-color: #2b2b2b; color: #ffffff; }")
        
    def init_ui(self):
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Show login page initially
        self.show_login_page()
    
    def show_login_page(self):
        """Display login page"""
        self.clear_current_layout()
        
        # Create new central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)
        
        # Title
        title = QLabel(APP_NAME)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(32)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Spacing
        layout.addStretch()
        
        # Login button
        auth_button = QPushButton("시작하기")
        auth_button.setFixedSize(220, 60)
        auth_button.clicked.connect(self.on_login)
        
        # Center the button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(auth_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        layout.addStretch()
    
    def show_main_page(self):
        """Display main page after login"""
        self.clear_current_layout()
        
        # Create new central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # User info frame
        user_frame = QFrame()
        user_layout = QVBoxLayout(user_frame)
        
        welcome_label = QLabel(f"환영합니다, {self.current_user['name']}님!")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_font = QFont()
        welcome_font.setPointSize(18)
        welcome_label.setFont(welcome_font)
        user_layout.addWidget(welcome_label)
        
        layout.addWidget(user_frame)
        
        # Spacing
        layout.addStretch()
        
        # Main tracking button
        self.start_button = QPushButton("🖐 손 제스처 추적 시작")
        self.start_button.setFixedSize(250, 70)
        self.start_button.clicked.connect(self.start_tracking)
        
        self.stop_button = QPushButton("⏹ 추적 중지")
        self.stop_button.setFixedSize(250, 70)
        self.stop_button.clicked.connect(self.stop_tracking)
        self.stop_button.hide()
        
        # Center main buttons
        main_button_layout = QHBoxLayout()
        main_button_layout.addStretch()
        main_button_layout.addWidget(self.start_button)
        main_button_layout.addWidget(self.stop_button)
        main_button_layout.addStretch()
        layout.addLayout(main_button_layout)
        
        # Control buttons frame
        control_frame = QFrame()
        control_layout = QHBoxLayout(control_frame)
        control_layout.setSpacing(15)
        
        # Help button
        help_button = QPushButton("도움말")
        help_button.setFixedSize(120, 45)
        help_button.clicked.connect(self.show_help)
        control_layout.addWidget(help_button)
        
        # Settings button  
        settings_button = QPushButton("설정")
        settings_button.setFixedSize(120, 45)
        settings_button.clicked.connect(self.show_settings)
        control_layout.addWidget(settings_button)
        
        # Logout button
        logout_button = QPushButton("종료")
        logout_button.setFixedSize(120, 45)
        logout_button.clicked.connect(self.logout)
        control_layout.addWidget(logout_button)
        
        # Center control buttons
        control_button_layout = QHBoxLayout()
        control_button_layout.addStretch()
        control_button_layout.addWidget(control_frame)
        control_button_layout.addStretch()
        layout.addLayout(control_button_layout)
        
        layout.addStretch()
    
    def clear_current_layout(self):
        """Clear current layout"""
        # Since we create a new central widget each time, 
        # just delete the old central widget if it exists
        old_widget = self.centralWidget()
        if old_widget:
            old_widget.deleteLater()
            QApplication.processEvents()
        
    def on_login(self):
        """Handle login button click"""
        self.is_authenticated = True
        self.show_main_page()
        
    def show_help(self):
        """Show help dialog"""
        help_text = """제스처 가이드:

🖐 검지손가락: 마우스 커서 이동
👆 엄지+검지 터치: 좌클릭  
🖖 엄지+중지 터치: 우클릭
📜 엄지+검지+중지 터치: 스크롤 모드
⬆️ 스크롤 중 위로 이동: 위로 스크롤
⬇️ 스크롤 중 아래로 이동: 아래로 스크롤
✊ 엄지+검지 꾹 누르기: 드래그 시작/끝

💡 팁: 자연스럽게 손동작을 하세요!"""
        
        msg = QMessageBox()
        msg.setWindowTitle("제스처 도움말")
        msg.setText(help_text)
        msg.setStyleSheet(self.styleSheet())
        msg.exec()
        
    def show_settings(self):
        """Show settings (placeholder)"""
        msg = QMessageBox()
        msg.setWindowTitle("설정")
        msg.setText("설정 기능은 추후 업데이트 예정입니다.")
        msg.setStyleSheet(self.styleSheet())
        msg.exec()
        
    def logout(self):
        """Return to login page"""
        if self.hand_overlay:
            self.hand_overlay.stop_tracking()
        self.is_authenticated = False
        self.show_login_page()
        
    def start_tracking(self):
        """Start hand tracking with overlay"""
        if self.hand_overlay is None:
            self.hand_overlay = SimpleHandOverlay()
            # Set callback for remote tracking stop
            self.hand_overlay.set_tracking_stop_callback(self.on_remote_tracking_stopped)
        
        self.hand_overlay.start_tracking()
        self.start_button.hide()
        self.stop_button.show()
        
    def stop_tracking(self):
        """Stop hand tracking"""
        if self.hand_overlay:
            self.hand_overlay.stop_tracking()
        
        self.stop_button.hide()
        self.start_button.show()
        
    def on_remote_tracking_stopped(self):
        """Handle tracking stopped from remote control"""
        # Update button states to match the stop_tracking method
        self.stop_button.hide()
        self.start_button.show()
        
    def closeEvent(self, event):
        """Handle window close event"""
        if self.hand_overlay:
            self.hand_overlay.stop_tracking()
        event.accept()


def main():
    setup_dpi_awareness()
    app = QApplication(sys.argv)
    window = PyQtMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()