"""
Main GUI application window using CustomTkinter
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import cv2
from PIL import Image, ImageTk
import sys
import os

from src.auth.google_auth import GoogleAuthenticator  
from src.face.face_recognition_system import FaceRecognitionSystem
from src.gesture.thumb_gesture_recognizer import ThumbGestureRecognizer
from src.gesture.mouse_controller import MouseController
from src.gui.tracking_window import TrackingWindow
from src.gui.settings_window import SettingsWindow
from config.settings import *

class GestureControlApp:
    def __init__(self):
        # Set appearance mode and color theme
        ctk.set_appearance_mode(THEME)
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title(APP_NAME)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        # Initialize components
        self.auth = GoogleAuthenticator()
        self.face_system = FaceRecognitionSystem()
        self.gesture_recognizer = ThumbGestureRecognizer()
        self.mouse_controller = MouseController()
        
        # Application state
        self.current_user = None
        self.is_tracking = False
        
        # Initialize UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the main UI"""
        self.current_frame = None
        self.show_login_page()
        
    def show_login_page(self):
        """Display login page"""
        self.clear_frame()
        
        self.current_frame = ctk.CTkFrame(self.root)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            self.current_frame, 
            text="Gesture Control",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(pady=(50, 30))
        
        # Google OAuth login button
        login_btn = ctk.CTkButton(
            self.current_frame,
            text="Google 로그인",
            font=ctk.CTkFont(size=16),
            height=50,
            width=200,
            command=self.handle_google_login
        )
        login_btn.pack(pady=20)
        
    def handle_google_login(self):
        """Handle Google OAuth login"""
        try:
            user_info = self.auth.authenticate()
            if user_info:
                self.current_user = user_info
                # Check if user exists in face recognition system
                if self.face_system.user_exists(user_info['email']):
                    self.show_face_auth_page()
                else:
                    self.show_face_registration_page()
            else:
                messagebox.showerror("오류", "로그인에 실패했습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"인증 중 오류가 발생했습니다: {str(e)}")
    
    def show_face_registration_page(self):
        """Display face registration page"""
        self.clear_frame()
        
        self.current_frame = ctk.CTkFrame(self.root)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            self.current_frame,
            text="얼굴 인식 등록",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Camera frame
        self.camera_frame = ctk.CTkFrame(self.current_frame)
        self.camera_frame.pack(pady=20)
        
        self.camera_label = ctk.CTkLabel(self.camera_frame, text="카메라 준비 중...")
        self.camera_label.pack(padx=20, pady=20)
        
        # Capture button  
        capture_btn = ctk.CTkButton(
            self.current_frame,
            text="촬영",
            font=ctk.CTkFont(size=16),
            height=40,
            width=150,
            command=self.capture_face_for_registration
        )
        capture_btn.pack(pady=20)
        
        # Start camera for registration
        self.start_camera_preview()
        
    def show_face_auth_page(self):
        """Display face authentication page"""
        self.clear_frame()
        
        self.current_frame = ctk.CTkFrame(self.root)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            self.current_frame,
            text="얼굴 인증",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Camera frame
        self.camera_frame = ctk.CTkFrame(self.current_frame)
        self.camera_frame.pack(pady=20)
        
        self.camera_label = ctk.CTkLabel(self.camera_frame, text="카메라 준비 중...")
        self.camera_label.pack(padx=20, pady=20)
        
        # Auth button
        auth_btn = ctk.CTkButton(
            self.current_frame,
            text="인증",
            font=ctk.CTkFont(size=16),
            height=40,
            width=150,
            command=self.authenticate_face
        )
        auth_btn.pack(pady=20)
        
        # Start camera for authentication
        self.start_camera_preview()
    
    def show_main_page(self):
        """Display main page"""
        self.clear_frame()
        
        self.current_frame = ctk.CTkFrame(self.root)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # User info
        user_frame = ctk.CTkFrame(self.current_frame)
        user_frame.pack(fill="x", pady=(20, 10))
        
        user_label = ctk.CTkLabel(
            user_frame,
            text=f"환영합니다, {self.current_user.get('name', 'User')}님",
            font=ctk.CTkFont(size=18)
        )
        user_label.pack(pady=20)
        
        # Main buttons
        button_frame = ctk.CTkFrame(self.current_frame)
        button_frame.pack(expand=True, fill="both", pady=20)
        
        # Tracking button
        tracking_btn = ctk.CTkButton(
            button_frame,
            text="트래킹 시작",
            font=ctk.CTkFont(size=20, weight="bold"),
            height=60,
            width=200,
            command=self.start_tracking
        )
        tracking_btn.pack(pady=20)
        
        # Control buttons frame
        control_frame = ctk.CTkFrame(button_frame)
        control_frame.pack(pady=20)
        
        # Settings button
        settings_btn = ctk.CTkButton(
            control_frame,
            text="설정",
            font=ctk.CTkFont(size=16),
            height=40,
            width=120,
            command=self.show_settings
        )
        settings_btn.pack(side="left", padx=10)
        
        # Help button  
        help_btn = ctk.CTkButton(
            control_frame,
            text="도움말",
            font=ctk.CTkFont(size=16),
            height=40,
            width=120,
            command=self.show_help
        )
        help_btn.pack(side="left", padx=10)
        
        # Logout button
        logout_btn = ctk.CTkButton(
            control_frame,
            text="로그아웃",
            font=ctk.CTkFont(size=16),
            height=40,
            width=120,
            command=self.logout
        )
        logout_btn.pack(side="left", padx=10)
    
    def start_camera_preview(self):
        """Start camera preview for face operations"""
        def camera_thread():
            cap = cv2.VideoCapture(CAMERA_INDEX)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            
            while hasattr(self, 'camera_label') and self.camera_label.winfo_exists():
                ret, frame = cap.read()
                if ret:
                    # Convert to RGB and resize for display
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_resized = cv2.resize(frame_rgb, (400, 300))
                    
                    # Convert to PhotoImage
                    image = Image.fromarray(frame_resized)
                    photo = ImageTk.PhotoImage(image)
                    
                    # Update label
                    try:
                        self.camera_label.configure(image=photo, text="")
                        self.camera_label.image = photo  # Keep a reference
                        self.current_camera_frame = frame
                    except:
                        break
                else:
                    break
            
            cap.release()
        
        self.camera_thread = threading.Thread(target=camera_thread, daemon=True)
        self.camera_thread.start()
    
    def capture_face_for_registration(self):
        """Capture and register face"""
        if hasattr(self, 'current_camera_frame'):
            success = self.face_system.register_face(
                self.current_camera_frame, 
                self.current_user['email']
            )
            
            if success:
                messagebox.showinfo("성공", "얼굴이 성공적으로 등록되었습니다.")
                self.show_main_page()
            else:
                messagebox.showerror("실패", "얼굴 등록에 실패했습니다. 다시 시도해주세요.")
    
    def authenticate_face(self):
        """Authenticate using face recognition"""
        if hasattr(self, 'current_camera_frame'):
            success = self.face_system.authenticate_face(
                self.current_camera_frame,
                self.current_user['email']
            )
            
            if success:
                messagebox.showinfo("성공", "얼굴 인증이 완료되었습니다.")
                self.show_main_page()
            else:
                messagebox.showerror("실패", "얼굴 인증에 실패했습니다.")
    
    def start_tracking(self):
        """Start gesture tracking"""
        self.tracking_window = TrackingWindow(
            self.gesture_recognizer,
            self.mouse_controller,
            self.stop_tracking_callback
        )
        self.tracking_window.start()
        self.is_tracking = True
        
        # Hide main window
        self.root.withdraw()
    
    def stop_tracking_callback(self):
        """Callback when tracking stops"""
        self.is_tracking = False
        self.root.deiconify()  # Show main window again
    
    def show_settings(self):
        """Show settings window"""
        settings_window = SettingsWindow(self.root)
    
    def show_help(self):
        """Show help modal"""
        help_window = ctk.CTkToplevel(self.root)
        help_window.title("도움말")
        help_window.geometry("600x400")
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Help content
        help_text = """제스처 가이드:

• 검지손가락 포인팅: 마우스 커서 이동
• 검지손가락 탭: 좌클릭
• 중지손가락 탭: 우클릭  
• 엄지손가락 위: 스크롤 업
• 엄지손가락 아래: 스크롤 다운
• 주먹: 드래그 시작
• 손바닥 펴기: 드래그 종료
• 브이(✌️): 음성 시작
• 주먹: 음성 종료"""
        
        help_label = ctk.CTkLabel(
            help_window,
            text=help_text,
            font=ctk.CTkFont(size=14),
            justify="left"
        )
        help_label.pack(padx=20, pady=20)
        
        close_btn = ctk.CTkButton(
            help_window,
            text="닫기",
            command=help_window.destroy
        )
        close_btn.pack(pady=20)
    
    def logout(self):
        """Logout and return to login page"""
        self.current_user = None
        if self.is_tracking:
            self.tracking_window.stop()
        self.show_login_page()
    
    def clear_frame(self):
        """Clear current frame"""
        if self.current_frame:
            self.current_frame.destroy()
    
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing"""
        if hasattr(self, 'tracking_window') and self.is_tracking:
            self.tracking_window.stop()
        
        self.gesture_recognizer.cleanup()
        self.root.destroy()