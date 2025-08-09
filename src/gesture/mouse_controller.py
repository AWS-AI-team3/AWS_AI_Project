"""
Mouse control functionality using detected gestures
"""

import pyautogui
import time
from typing import Optional, Tuple
from config.settings import *
# Import specific settings if needed  
try:
    from config.settings import (CLICK_HOLD_TIME, SCROLL_SENSITIVITY, MOUSE_SENSITIVITY, 
                                DOUBLE_CLICK_THRESHOLD, PINCH_THRESHOLD, SCROLL_ANGLE_THRESHOLD)
except ImportError:
    CLICK_HOLD_TIME = 0.1
    SCROLL_SENSITIVITY = 10
    MOUSE_SENSITIVITY = 1.2
    DOUBLE_CLICK_THRESHOLD = 0.4
    PINCH_THRESHOLD = 0.04
    SCROLL_ANGLE_THRESHOLD = 0.15

class MouseController:
    def __init__(self):
        # Configure pyautogui for maximum responsiveness
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.001  # Minimal delay for faster response
        
        self.screen_width, self.screen_height = pyautogui.size()
        self.mouse_enabled = True
        self.last_click_time = 0
        
        # Gesture mapping to actions
        self.gesture_actions = {
            "cursor_point": self.move_mouse,
            "thumb_index_pinch": self.handle_left_click_or_drag,
            "thumb_middle_pinch": self.right_click,
            "fist": self.drag_start,
            "open_hand": self.drag_end
        }
        
        self.dragging = False
        self.pinch_dragging = False  # For thumb-index pinch drag
        self.pinch_start_time = 0
        self.last_double_click_time = 0
        self.click_count = 0
        self.last_gesture_time = 0
        
    def process_gesture(self, gesture_data: dict, mouse_pos: Optional[Tuple[int, int]] = None):
        """Process gesture and execute corresponding mouse action"""
        if not self.mouse_enabled or not gesture_data:
            # End any ongoing pinch drag if no gesture detected
            if self.pinch_dragging:
                self.end_pinch_drag()
            return
            
        gesture_type = gesture_data.get('type')
        
        # Handle thumb-index-middle scroll gestures
        if gesture_type.startswith("thumb_index_middle_scroll:"):
            scroll_speed = float(gesture_type.split(":")[1])
            self.handle_thumb_index_middle_scroll(scroll_speed)
            return
        elif gesture_type == "thumb_index_middle_scroll_start":
            # Initialize scroll - no action needed, just acknowledgment
            return
        elif gesture_type == "thumb_index_middle_scroll_hold":
            # Holding pinch position - no scroll action
            return
        
        # End pinch drag if different gesture detected
        if gesture_type != "thumb_index_pinch" and self.pinch_dragging:
            self.end_pinch_drag()
        
        if gesture_type in self.gesture_actions:
            action = self.gesture_actions[gesture_type]
            
            if gesture_type == "cursor_point":
                # Cursor movement is now handled in hand_overlay.py
                pass
            elif gesture_type in ["thumb_index_pinch", "thumb_middle_pinch"]:
                if mouse_pos:
                    action(mouse_pos)
                else:
                    action()
            else:
                action()
    
    def move_mouse(self, position: Tuple[float, float]):
        """Move mouse cursor to specified position with smoothing"""
        if not self.mouse_enabled or position is None:
            return
            
        # Direct mapping from normalized hand coordinates to screen coordinates
        # position comes as (x, y) where x, y are normalized [0, 1]
        screen_x = int(position[0] * self.screen_width)
        screen_y = int(position[1] * self.screen_height)
        
        # Ensure coordinates are within screen bounds
        screen_x = max(0, min(screen_x, self.screen_width - 1))
        screen_y = max(0, min(screen_y, self.screen_height - 1))
        
        
        # Use moveTo with duration=0 for immediate response
        pyautogui.moveTo(screen_x, screen_y, duration=0)
    
    def handle_left_click_or_drag(self, mouse_pos: Optional[Tuple[int, int]] = None):
        """Handle thumb-index pinch: click or drag"""
        if not self.mouse_enabled:
            return
            
        current_time = time.time()
        
        if not self.pinch_dragging:
            # Check for double-click first
            if current_time - self.last_click_time < DOUBLE_CLICK_THRESHOLD:
                self.double_click()
                return
            
            # First time detecting pinch - start potential drag
            self.pinch_start_time = current_time
            self.pinch_dragging = True
            pyautogui.mouseDown()
            self.last_click_time = current_time
        else:
            # Continue dragging - mouse position is already updated in hand_overlay.py
            pass
                
    def end_pinch_drag(self):
        """End pinch drag operation"""
        if self.pinch_dragging:
            current_time = time.time()
            drag_duration = current_time - self.pinch_start_time
            
            pyautogui.mouseUp()
            
            # If drag duration was very short, treat as click
            if drag_duration < 0.15:  # Less than 150ms = click
                # mouseUp already happened, so this was effectively a click
                pass
            
            self.pinch_dragging = False
            self.pinch_start_time = 0
            
    def left_click(self):
        """Simple left mouse click"""
        if not self.mouse_enabled:
            return
            
        current_time = time.time()
        if current_time - self.last_click_time > CLICK_HOLD_TIME:
            pyautogui.click()
            self.last_click_time = current_time
    
    def right_click(self, mouse_pos: Optional[Tuple[int, int]] = None):
        """Perform right mouse click"""
        if not self.mouse_enabled:
            return
            
        current_time = time.time()
        if current_time - self.last_click_time > CLICK_HOLD_TIME:
            pyautogui.rightClick()
            self.last_click_time = current_time
    
    def handle_thumb_index_middle_scroll(self, scroll_speed: float):
        """Handle thumb-index-middle triple pinch scroll based on Y-axis movement"""
        if not self.mouse_enabled:
            return
            
        # Convert scroll speed to scroll units with higher sensitivity
        # Positive scroll_speed = moved down = scroll down (negative scroll units)
        # Negative scroll_speed = moved up = scroll up (positive scroll units)
        scroll_units = int(-scroll_speed * SCROLL_SENSITIVITY * 2)  # Doubled sensitivity
        
        # Lower threshold for more responsive scrolling
        if abs(scroll_units) >= 1:
            pyautogui.scroll(scroll_units)
    
    def scroll_up(self):
        """Scroll up"""
        if not self.mouse_enabled:
            return
        pyautogui.scroll(1)
    
    def scroll_down(self):
        """Scroll down"""  
        if not self.mouse_enabled:
            return
        pyautogui.scroll(-1)
    
    def drag_start(self):
        """Start dragging"""
        if not self.mouse_enabled or self.dragging:
            return
        pyautogui.mouseDown()
        self.dragging = True
    
    def drag_end(self):
        """End dragging"""
        if not self.mouse_enabled or not self.dragging:
            return
        pyautogui.mouseUp()
        self.dragging = False
    
    def middle_click(self):
        """Perform middle mouse click"""
        if not self.mouse_enabled:
            return
        pyautogui.middleClick()
    
    def set_mouse_enabled(self, enabled: bool):
        """Enable or disable mouse control"""
        self.mouse_enabled = enabled
        
        if not enabled:
            if self.dragging:
                self.drag_end()
            if self.pinch_dragging:
                self.end_pinch_drag()
    
    def get_current_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        return pyautogui.position()