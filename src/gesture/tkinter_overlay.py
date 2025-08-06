"""
Tkinter-based system overlay that works better on macOS
"""

import tkinter as tk
import threading
import time
import cv2
import platform
import subprocess
from typing import Optional, List
from src.gesture.thumb_gesture_recognizer import ThumbGestureRecognizer
import pyautogui


class TkinterSystemOverlay:
    """System-wide overlay using tkinter - works better on macOS"""
    
    def __init__(self):
        self.gesture_recognizer = ThumbGestureRecognizer()
        self.cap = None
        self.is_tracking = False
        self.root = None
        self.canvas = None
        self.landmarks = None
        
    def setup_overlay(self):
        """Setup tkinter overlay window"""
        self.root = tk.Tk()
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Configure window for system overlay
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.lift()  # Bring to front
        self.root.wm_attributes("-topmost", True)  # Keep on top
        self.root.wm_attributes("-disabled", True)  # Disable window interactions
        self.root.wm_attributes("-transparentcolor", "black")  # Make black transparent
        
        # macOS specific attributes
        if platform.system() == "Darwin":
            try:
                # Try to set macOS-specific window level
                self.root.wm_attributes("-alpha", 0.8)  # Semi-transparent
                # Force window to stay on top of all spaces
                subprocess.run([
                    "osascript", "-e", 
                    f'tell application "System Events" to set frontmost of process "Python" to true'
                ], capture_output=True)
            except:
                pass
        
        # Create transparent canvas
        self.canvas = tk.Canvas(
            self.root, 
            width=screen_width, 
            height=screen_height,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        print("✅ Tkinter system overlay created")
        
    def start_tracking(self):
        """Start hand tracking with overlay"""
        if self.is_tracking:
            return
            
        # Setup overlay window
        self.setup_overlay()
        
        # Setup camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.is_tracking = True
        
        # Start processing in separate thread
        self.processing_thread = threading.Thread(target=self.processing_loop, daemon=True)
        self.processing_thread.start()
        
        # Start tkinter main loop in separate thread  
        self.gui_thread = threading.Thread(target=self.gui_loop, daemon=True)
        self.gui_thread.start()
        
        print("🎯 Tkinter overlay started - should be visible above all apps")
        
    def stop_tracking(self):
        """Stop hand tracking"""
        self.is_tracking = False
        
        if self.cap:
            self.cap.release()
            self.cap = None
            
        if self.root:
            self.root.after(0, self.root.destroy)
            
    def gui_loop(self):
        """Run tkinter GUI loop"""
        if self.root:
            # Update overlay every 33ms (~30 FPS)
            self.root.after(33, self.update_overlay)
            self.root.mainloop()
            
    def processing_loop(self):
        """Process camera frames"""
        while self.is_tracking and self.cap:
            ret, frame = self.cap.read()
            if not ret:
                continue
                
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Process frame with gesture recognizer
            processed_frame, gesture_data = self.gesture_recognizer.process_frame(frame)
            
            if gesture_data and gesture_data['landmarks'] is not None:
                self.landmarks = gesture_data['landmarks'].tolist()
                
                # Handle gestures
                self.handle_gesture(gesture_data)
            else:
                self.landmarks = None
                
            time.sleep(0.033)  # ~30 FPS
            
    def update_overlay(self):
        """Update overlay display"""
        if not self.is_tracking or not self.canvas:
            return
            
        # Clear canvas
        self.canvas.delete("all")
        
        if self.landmarks:
            self.draw_hand_skeleton()
            
        # Keep window on top
        self.root.lift()
        
        # Schedule next update
        if self.is_tracking:
            self.root.after(33, self.update_overlay)
            
    def draw_hand_skeleton(self):
        """Draw hand skeleton on canvas"""
        if not self.landmarks or not self.canvas:
            return
            
        screen_width = self.canvas.winfo_width()
        screen_height = self.canvas.winfo_height()
        
        # Convert normalized landmarks to screen coordinates
        screen_landmarks = []
        for point in self.landmarks:
            x = int(point[0] * screen_width)
            y = int(point[1] * screen_height)
            screen_landmarks.append((x, y))
        
        # Hand connections
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
            # Palm
            (5, 9), (9, 13), (13, 17)
        ]
        
        # Draw connections
        for start_idx, end_idx in connections:
            if start_idx < len(screen_landmarks) and end_idx < len(screen_landmarks):
                start_point = screen_landmarks[start_idx]
                end_point = screen_landmarks[end_idx]
                
                self.canvas.create_line(
                    start_point[0], start_point[1],
                    end_point[0], end_point[1],
                    fill="lime", width=3
                )
        
        # Draw landmark points
        for x, y in screen_landmarks:
            self.canvas.create_oval(
                x-4, y-4, x+4, y+4,
                fill="red", outline="red"
            )
            
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


def create_tkinter_overlay():
    """Factory function to create tkinter overlay"""
    try:
        return TkinterSystemOverlay()
    except Exception as e:
        print(f"❌ Failed to create tkinter overlay: {e}")
        return None