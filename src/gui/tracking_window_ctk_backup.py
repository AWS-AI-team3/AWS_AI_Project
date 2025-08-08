"""
Tracking window for gesture control
"""

import customtkinter as ctk
import tkinter as tk
import cv2
import threading
import time
from PIL import Image, ImageTk
from config.settings import *

class TrackingWindow:
    def __init__(self, gesture_recognizer, mouse_controller, stop_callback):
        self.gesture_recognizer = gesture_recognizer
        self.mouse_controller = mouse_controller
        self.stop_callback = stop_callback
        
        self.window = ctk.CTkToplevel()
        self.window.title("제스처 트래킹")
        self.window.geometry("800x700")
        self.window.attributes('-topmost', True)
        
        self.is_running = False
        self.show_camera = True
        self.show_skeleton = True
        self.is_recording = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up tracking window UI"""
        # Main container
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Ad frame (for free users)
        ad_frame = ctk.CTkFrame(main_frame)
        ad_frame.pack(fill="x", pady=(0, 10))
        
        ad_label = ctk.CTkLabel(
            ad_frame,
            text="🎯 프리미엄으로 업그레이드하여 광고를 제거하세요!",
            font=ctk.CTkFont(size=12)
        )
        ad_label.pack(side="left", padx=10, pady=5)
        
        ad_close_btn = ctk.CTkButton(
            ad_frame,
            text="✕",
            width=30,
            height=30,
            command=lambda: ad_frame.pack_forget()
        )
        ad_close_btn.pack(side="right", padx=10, pady=5)
        
        # Camera frame
        self.camera_frame = ctk.CTkFrame(main_frame)
        self.camera_frame.pack(expand=True, fill="both", pady=(0, 10))
        
        self.camera_label = ctk.CTkLabel(
            self.camera_frame,
            text="카메라 시작 중...",
            font=ctk.CTkFont(size=16)
        )
        self.camera_label.pack(expand=True, padx=20, pady=20)
        
        # Control panel
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(fill="x")
        
        # Control buttons
        button_frame = ctk.CTkFrame(control_frame)
        button_frame.pack(pady=10)
        
        # Camera toggle
        self.camera_toggle = ctk.CTkSwitch(
            button_frame,
            text="카메라 표시",
            command=self.toggle_camera
        )
        self.camera_toggle.pack(side="left", padx=10)
        self.camera_toggle.select()  # Default on
        
        # Recording button
        self.record_btn = ctk.CTkButton(
            button_frame,
            text="🎤 녹음 시작",
            width=100,
            command=self.toggle_recording
        )
        self.record_btn.pack(side="left", padx=10)
        
        # Stop tracking button
        stop_btn = ctk.CTkButton(
            button_frame,
            text="트래킹 종료",
            width=100,
            fg_color="red",
            hover_color="darkred",
            command=self.stop
        )
        stop_btn.pack(side="left", padx=10)
        
        # Status frame
        status_frame = ctk.CTkFrame(control_frame)
        status_frame.pack(fill="x", pady=(10, 0))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="상태: 준비됨",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        self.gesture_label = ctk.CTkLabel(
            status_frame,
            text="제스처: 없음",
            font=ctk.CTkFont(size=12)
        )
        self.gesture_label.pack(side="right", padx=10, pady=5)
        
    def start(self):
        """Start gesture tracking"""
        self.is_running = True
        self.tracking_thread = threading.Thread(target=self.tracking_loop, daemon=True)
        self.tracking_thread.start()
        
    def tracking_loop(self):
        """Main tracking loop"""
        cap = cv2.VideoCapture(CAMERA_INDEX)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
        
        frame_count = 0
        fps_start_time = time.time()
        
        while self.is_running:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Process frame for gestures
            processed_frame, gesture_data = self.gesture_recognizer.process_frame(frame)
            
            # Update gesture status
            if gesture_data:
                gesture_type = gesture_data.get('type', 'unknown')
                self.update_gesture_status(gesture_type)
                
                # Get mouse position from landmarks
                mouse_pos = None
                if 'landmarks' in gesture_data:
                    landmarks = gesture_data['landmarks']
                    # Use thumb position method if available, otherwise fallback
                    if hasattr(self.gesture_recognizer, 'get_thumb_position'):
                        mouse_pos = self.gesture_recognizer.get_thumb_position(landmarks)
                    else:
                        mouse_pos = self.gesture_recognizer.get_mouse_position(
                            landmarks, (CAMERA_HEIGHT, CAMERA_WIDTH)
                        )
                
                # Process gesture for mouse control
                self.mouse_controller.process_gesture(gesture_data, mouse_pos)
            else:
                self.update_gesture_status("없음")
            
            # Update camera display
            if self.show_camera:
                self.update_camera_display(processed_frame)
            
            # Calculate FPS
            frame_count += 1
            if frame_count % 30 == 0:
                fps = 30 / (time.time() - fps_start_time)
                self.update_status(f"상태: 실행 중 ({fps:.1f} FPS)")
                fps_start_time = time.time()
        
        cap.release()
        
    def update_camera_display(self, frame):
        """Update camera display"""
        try:
            # Convert to RGB and resize
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (640, 480))
            
            # Convert to PhotoImage
            image = Image.fromarray(frame_resized)
            photo = ImageTk.PhotoImage(image)
            
            # Update label
            self.camera_label.configure(image=photo, text="")
            self.camera_label.image = photo  # Keep reference
        except Exception as e:
            print(f"Camera display error: {e}")
    
    def update_status(self, status):
        """Update status label"""
        try:
            self.status_label.configure(text=status)
        except:
            pass
    
    def update_gesture_status(self, gesture):
        """Update gesture status label"""
        try:
            gesture_text = {
                "index_finger_point": "검지 포인팅",
                "index_finger_tap": "좌클릭",
                "middle_finger_tap": "우클릭",
                "thumb_up": "스크롤 업",
                "thumb_down": "스크롤 다운",
                "peace_sign": "피스 사인",
                "fist": "주먹",
                "open_hand": "손바닥",
                "unknown": "알 수 없음",
                "없음": "없음"
            }.get(gesture, gesture)
            
            self.gesture_label.configure(text=f"제스처: {gesture_text}")
        except:
            pass
    
    def toggle_camera(self):
        """Toggle camera display"""
        self.show_camera = self.camera_toggle.get()
        if not self.show_camera:
            self.camera_label.configure(image="", text="카메라 숨김")
    
    def toggle_recording(self):
        """Toggle voice recording"""
        self.is_recording = not self.is_recording
        
        if self.is_recording:
            self.record_btn.configure(text="🔴 녹음 중")
            self.update_status("상태: 음성 녹음 중")
        else:
            self.record_btn.configure(text="🎤 녹음 시작")
            self.update_status("상태: 실행 중")
    
    
    def stop(self):
        """Stop tracking and close window"""
        self.is_running = False
        self.mouse_controller.set_mouse_enabled(False)
        
        if hasattr(self, 'tracking_thread'):
            self.tracking_thread.join(timeout=1.0)
        
        self.window.destroy()
        self.stop_callback()