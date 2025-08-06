"""
Alternative macOS overlay using Cocoa/AppKit for true system-wide visibility
"""

import threading
import time
import cv2
import numpy as np
from typing import Optional, List
from src.gesture.thumb_gesture_recognizer import ThumbGestureRecognizer
import pyautogui

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer, QObject, pyqtSignal
    import AppKit
    import Cocoa
    HAS_COCOA = True
except ImportError:
    HAS_COCOA = False
    print("Cocoa/AppKit not available - falling back to basic overlay")


class MacOSNativeOverlay(QObject):
    """Native macOS overlay using Cocoa for system-wide visibility"""
    
    def __init__(self):
        super().__init__()
        self.gesture_recognizer = ThumbGestureRecognizer()
        self.cap = None
        self.is_tracking = False
        self.overlay_window = None
        
        # Timer for updating
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)
        
        if HAS_COCOA:
            self.setup_cocoa_overlay()
        else:
            print("Cocoa not available - hand tracking will work but overlay may not be visible")
            
    def setup_cocoa_overlay(self):
        """Setup native Cocoa overlay window"""
        try:
            # Create NSWindow with special properties for overlay
            screen_rect = AppKit.NSScreen.mainScreen().frame()
            
            # Create window with transparent background
            self.overlay_window = AppKit.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                screen_rect,
                AppKit.NSWindowStyleMaskBorderless,
                AppKit.NSBackingStoreBuffered,
                False
            )
            
            # Set window properties for system-wide overlay
            self.overlay_window.setLevel_(AppKit.NSModalPanelWindowLevel + 1000)  # Very high level
            self.overlay_window.setBackgroundColor_(AppKit.NSColor.clearColor())
            self.overlay_window.setOpaque_(False)
            self.overlay_window.setIgnoresMouseEvents_(True)
            self.overlay_window.setCollectionBehavior_(
                AppKit.NSWindowCollectionBehaviorCanJoinAllSpaces |
                AppKit.NSWindowCollectionBehaviorStationary |
                AppKit.NSWindowCollectionBehaviorIgnoresCycle
            )
            
            # Create custom view for drawing
            self.overlay_view = HandSkeletonView.alloc().init()
            self.overlay_window.setContentView_(self.overlay_view)
            
            print("✅ Native Cocoa overlay created successfully")
            
        except Exception as e:
            print(f"❌ Failed to create Cocoa overlay: {e}")
            self.overlay_window = None
            
    def start_tracking(self):
        """Start hand tracking with native overlay"""
        if self.is_tracking:
            return
            
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.is_tracking = True
        
        if self.overlay_window and HAS_COCOA:
            self.overlay_window.makeKeyAndOrderFront_(None)
            print("🎯 Native overlay shown - should be visible above all apps")
        
        self.timer.start(33)  # ~30 FPS
        
    def stop_tracking(self):
        """Stop hand tracking"""
        self.is_tracking = False
        self.timer.stop()
        
        if self.cap:
            self.cap.release()
            self.cap = None
            
        if self.overlay_window and HAS_COCOA:
            self.overlay_window.orderOut_(None)
            
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
            landmarks = gesture_data['landmarks'].tolist()
            
            # Update native overlay
            if self.overlay_view and HAS_COCOA:
                self.overlay_view.updateLandmarks_(landmarks)
                self.overlay_window.contentView().setNeedsDisplay_(True)
            
            # Handle gestures
            self.handle_gesture(gesture_data)
            
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


# Native Cocoa view for drawing hand skeleton
if HAS_COCOA:
    import objc
    
    class HandSkeletonView(AppKit.NSView):
        """Custom NSView for drawing hand skeleton"""
        
        def init(self):
            self = objc.super(HandSkeletonView, self).init()
            if self is None:
                return None
            self.landmarks = None
            return self
            
        def updateLandmarks_(self, landmarks):
            """Update landmarks for drawing"""
            self.landmarks = landmarks
            
        def drawRect_(self, rect):
            """Draw hand skeleton"""
            if not self.landmarks:
                return
                
            # Get screen dimensions
            screen_rect = self.window().frame()
            screen_width = screen_rect.size.width
            screen_height = screen_rect.size.height
            
            # Convert landmarks to screen coordinates
            screen_landmarks = []
            for point in self.landmarks:
                x = point[0] * screen_width
                y = (1.0 - point[1]) * screen_height  # Flip Y coordinate
                screen_landmarks.append((x, y))
            
            # Set up drawing context
            context = AppKit.NSGraphicsContext.currentContext().CGContext()
            
            # Set line properties
            Cocoa.CGContextSetLineWidth(context, 3.0)
            Cocoa.CGContextSetRGBStrokeColor(context, 0.0, 1.0, 0.0, 0.8)  # Green with alpha
            
            # Draw hand connections
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
                    
                    Cocoa.CGContextBeginPath(context)
                    Cocoa.CGContextMoveToPoint(context, start_point[0], start_point[1])
                    Cocoa.CGContextAddLineToPoint(context, end_point[0], end_point[1])
                    Cocoa.CGContextStrokePath(context)
            
            # Draw landmark points
            Cocoa.CGContextSetRGBFillColor(context, 1.0, 0.0, 0.0, 0.8)  # Red with alpha
            for x, y in screen_landmarks:
                rect = Cocoa.CGRectMake(x-3, y-3, 6, 6)
                Cocoa.CGContextFillEllipseInRect(context, rect)
else:
    # Dummy class if Cocoa is not available
    class HandSkeletonView:
        pass


def create_macos_overlay():
    """Factory function to create appropriate overlay for macOS"""
    if HAS_COCOA:
        print("🍎 Using native macOS Cocoa overlay")
        return MacOSNativeOverlay()
    else:
        print("⚠️  Cocoa not available - install pyobjc-framework-Cocoa")
        return None