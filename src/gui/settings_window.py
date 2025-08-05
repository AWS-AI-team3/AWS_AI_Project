"""
Settings window for gesture customization
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from config.settings import *

class SettingsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = ctk.CTkToplevel(parent)
        self.window.title("설정")
        self.window.geometry("700x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Settings data
        self.settings = {
            "show_cursor": True,
            "show_skeleton": True,
            "gesture_mappings": GESTURE_MAPPING.copy(),
            "enabled_features": {
                "left_click": True,
                "right_click": True,
                "scroll": True,
                "voice_start": True,
                "voice_stop": True,
                "tracking_stop": True
            }
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up settings UI"""
        # Main container
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Back button
        back_btn = ctk.CTkButton(
            header_frame,
            text="← 뒤로",
            width=80,
            command=self.close_window
        )
        back_btn.pack(side="left", padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="설정",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=(20, 0), pady=10)
        
        # Scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(main_frame)
        self.scroll_frame.pack(fill="both", expand=True)
        
        # Display settings
        self.create_display_settings()
        
        # Gesture settings
        self.create_gesture_settings()
        
        # Save button
        save_btn = ctk.CTkButton(
            main_frame,
            text="설정 저장",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            command=self.save_settings
        )
        save_btn.pack(pady=20)
        
    def create_display_settings(self):
        """Create display settings section"""
        # Display settings section
        display_frame = ctk.CTkFrame(self.scroll_frame)
        display_frame.pack(fill="x", pady=(0, 20))
        
        display_title = ctk.CTkLabel(
            display_frame,
            text="화면 표시 설정",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        display_title.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Mouse cursor toggle
        cursor_frame = ctk.CTkFrame(display_frame)
        cursor_frame.pack(fill="x", padx=20, pady=5)
        
        cursor_label = ctk.CTkLabel(cursor_frame, text="마우스 커서 표시")
        cursor_label.pack(side="left", padx=10, pady=10)
        
        self.cursor_toggle = ctk.CTkSwitch(
            cursor_frame,
            text="",
            command=self.toggle_cursor
        )
        self.cursor_toggle.pack(side="right", padx=10, pady=10)
        if self.settings["show_cursor"]:
            self.cursor_toggle.select()
        
        # Skeleton toggle
        skeleton_frame = ctk.CTkFrame(display_frame)
        skeleton_frame.pack(fill="x", padx=20, pady=(5, 20))
        
        skeleton_label = ctk.CTkLabel(skeleton_frame, text="스켈레톤 표시")
        skeleton_label.pack(side="left", padx=10, pady=10)
        
        self.skeleton_toggle = ctk.CTkSwitch(
            skeleton_frame,
            text="",
            command=self.toggle_skeleton
        )
        self.skeleton_toggle.pack(side="right", padx=10, pady=10)
        if self.settings["show_skeleton"]:
            self.skeleton_toggle.select()
            
    def create_gesture_settings(self):
        """Create gesture settings section"""
        # Gesture settings section
        gesture_frame = ctk.CTkFrame(self.scroll_frame)
        gesture_frame.pack(fill="x")
        
        gesture_title = ctk.CTkLabel(
            gesture_frame,
            text="제스처 기능 설정",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        gesture_title.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Feature list
        features = [
            ("left_click", "좌클릭", ["index_finger_tap", "thumb_tap"]),
            ("right_click", "우클릭", ["middle_finger_tap", "pinky_tap"]),
            ("scroll", "휠 스크롤", ["thumb_up_down", "two_finger_scroll"]),
            ("voice_start", "음성 시작", ["peace_sign", "ok_sign"]),
            ("voice_stop", "음성 종료", ["fist", "stop_gesture"]),
            ("tracking_stop", "트래킹 종료", ["stop_gesture", "timeout"])
        ]
        
        self.feature_widgets = {}
        
        for feature_id, feature_name, gesture_options in features:
            self.create_feature_setting(
                gesture_frame, feature_id, feature_name, gesture_options
            )
    
    def create_feature_setting(self, parent, feature_id, feature_name, gesture_options):
        """Create individual feature setting"""
        feature_frame = ctk.CTkFrame(parent)
        feature_frame.pack(fill="x", padx=20, pady=5)
        
        # Feature info frame
        info_frame = ctk.CTkFrame(feature_frame)
        info_frame.pack(fill="x", padx=10, pady=10)
        
        # Feature name
        name_label = ctk.CTkLabel(
            info_frame,
            text=feature_name,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        name_label.pack(side="left", padx=10)
        
        # Enable toggle
        toggle = ctk.CTkSwitch(
            info_frame,
            text="활성화",
            command=lambda: self.toggle_feature(feature_id)
        )
        toggle.pack(side="right", padx=10)
        
        if self.settings["enabled_features"][feature_id]:
            toggle.select()
        
        # Dropdown button
        dropdown_btn = ctk.CTkButton(
            info_frame,
            text="제스처 선택 ▼",
            width=120,
            command=lambda: self.toggle_dropdown(feature_id)
        )
        dropdown_btn.pack(side="right", padx=(0, 10))
        
        # Dropdown frame (initially hidden)
        dropdown_frame = ctk.CTkFrame(feature_frame)
        
        # Gesture options
        gesture_var = tk.StringVar()
        current_gesture = self.get_current_gesture(feature_id)
        gesture_var.set(current_gesture)
        
        for gesture in gesture_options:
            radio = ctk.CTkRadioButton(
                dropdown_frame,
                text=self.get_gesture_display_name(gesture),
                variable=gesture_var,
                value=gesture,
                command=lambda g=gesture, fid=feature_id: self.set_gesture(fid, g)
            )
            radio.pack(anchor="w", padx=20, pady=5)
        
        self.feature_widgets[feature_id] = {
            "toggle": toggle,
            "dropdown_btn": dropdown_btn,
            "dropdown_frame": dropdown_frame,
            "gesture_var": gesture_var,
            "visible": False
        }
    
    def get_current_gesture(self, feature_id):
        """Get current gesture for feature"""
        mapping = {
            "left_click": self.settings["gesture_mappings"]["left_click"],
            "right_click": self.settings["gesture_mappings"]["right_click"],
            "scroll": "thumb_up_down",
            "voice_start": self.settings["gesture_mappings"]["start_voice"],
            "voice_stop": self.settings["gesture_mappings"]["stop_voice"],
            "tracking_stop": "stop_gesture"
        }
        return mapping.get(feature_id, "index_finger_tap")
    
    def get_gesture_display_name(self, gesture):
        """Get display name for gesture"""
        names = {
            "index_finger_tap": "검지 탭",
            "thumb_tap": "엄지 탭",
            "middle_finger_tap": "중지 탭",
            "pinky_tap": "새끼손가락 탭",
            "thumb_up_down": "엄지 위/아래",
            "two_finger_scroll": "두 손가락 스크롤",
            "peace_sign": "피스 사인 (✌️)",
            "ok_sign": "OK 사인 (👌)",
            "fist": "주먹",
            "stop_gesture": "정지 제스처",
            "timeout": "타임아웃"
        }
        return names.get(gesture, gesture)
    
    def toggle_dropdown(self, feature_id):
        """Toggle dropdown visibility"""
        widget = self.feature_widgets[feature_id]
        
        if widget["visible"]:
            widget["dropdown_frame"].pack_forget()
            widget["dropdown_btn"].configure(text="제스처 선택 ▼")
            widget["visible"] = False
        else:
            widget["dropdown_frame"].pack(fill="x", padx=20, pady=(0, 10))
            widget["dropdown_btn"].configure(text="제스처 선택 ▲")
            widget["visible"] = True
    
    def toggle_feature(self, feature_id):
        """Toggle feature enable/disable"""
        toggle = self.feature_widgets[feature_id]["toggle"]
        self.settings["enabled_features"][feature_id] = toggle.get()
    
    def toggle_cursor(self):
        """Toggle cursor display"""
        self.settings["show_cursor"] = self.cursor_toggle.get()
    
    def toggle_skeleton(self):
        """Toggle skeleton display"""
        self.settings["show_skeleton"] = self.skeleton_toggle.get()
    
    def set_gesture(self, feature_id, gesture):
        """Set gesture for feature"""
        # Check for conflicts
        current_mappings = {}
        for fid, widgets in self.feature_widgets.items():
            if fid != feature_id:
                current_mappings[fid] = widgets["gesture_var"].get()
        
        if gesture in current_mappings.values():
            messagebox.showwarning(
                "제스처 충돌",
                f"'{self.get_gesture_display_name(gesture)}' 제스처가 이미 다른 기능에 할당되어 있습니다."
            )
            return
        
        # Update mapping
        mapping_keys = {
            "left_click": "left_click",
            "right_click": "right_click", 
            "voice_start": "start_voice",
            "voice_stop": "stop_voice"
        }
        
        if feature_id in mapping_keys:
            self.settings["gesture_mappings"][mapping_keys[feature_id]] = gesture
    
    def save_settings(self):
        """Save settings"""
        try:
            # Here you would typically save to a config file
            messagebox.showinfo("저장 완료", "설정이 저장되었습니다.")
            self.close_window()
        except Exception as e:
            messagebox.showerror("저장 실패", f"설정 저장 중 오류가 발생했습니다: {str(e)}")
    
    def close_window(self):
        """Close settings window"""
        self.window.destroy()