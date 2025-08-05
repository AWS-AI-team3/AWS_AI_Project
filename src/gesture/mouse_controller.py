"""
Mouse control functionality using detected gestures
"""

import pyautogui
import time
from typing import Optional, Tuple
from config.settings import *

class MouseController:
    def __init__(self):
        # Configure pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01
        
        self.screen_width, self.screen_height = pyautogui.size()
        self.mouse_enabled = True
        self.last_click_time = 0
        
        # Gesture mapping to actions
        self.gesture_actions = {
            "cursor_point": self.move_mouse,
            "pinch_click": self.left_click,
            "thumb_up": self.scroll_up,
            "thumb_down": self.scroll_down,
            "fist": self.drag_start,
            "open_hand": self.drag_end
        }
        
        self.dragging = False
        
    def process_gesture(self, gesture_data: dict, mouse_pos: Optional[Tuple[int, int]] = None):
        """Process gesture and execute corresponding mouse action"""
        if not self.mouse_enabled or not gesture_data:
            return
            
        gesture_type = gesture_data.get('type')
        
        if gesture_type in self.gesture_actions:
            action = self.gesture_actions[gesture_type]
            
            if gesture_type == "cursor_point" and mouse_pos:
                action(mouse_pos)
            else:
                action()
    
    def move_mouse(self, position: Tuple[int, int]):
        """Move mouse cursor to specified position"""
        if not self.mouse_enabled:
            return
            
        # Direct mapping from normalized hand coordinates to screen coordinates
        # position comes as (x, y) where x, y are normalized [0, 1]
        screen_x = int(position[0] * self.screen_width)
        screen_y = int(position[1] * self.screen_height)
        
        # Ensure coordinates are within screen bounds
        screen_x = max(0, min(screen_x, self.screen_width - 1))
        screen_y = max(0, min(screen_y, self.screen_height - 1))
        
        pyautogui.moveTo(screen_x, screen_y)
    
    def left_click(self):
        """Perform left mouse click"""
        if not self.mouse_enabled:
            return
            
        current_time = time.time()
        if current_time - self.last_click_time > CLICK_HOLD_TIME:
            pyautogui.click()
            self.last_click_time = current_time
    
    def right_click(self):
        """Perform right mouse click"""
        if not self.mouse_enabled:
            return
            
        current_time = time.time()
        if current_time - self.last_click_time > CLICK_HOLD_TIME:
            pyautogui.rightClick()
            self.last_click_time = current_time
    
    def scroll_up(self):
        """Scroll up"""
        if not self.mouse_enabled:
            return
        pyautogui.scroll(SCROLL_SENSITIVITY)
    
    def scroll_down(self):
        """Scroll down"""  
        if not self.mouse_enabled:
            return
        pyautogui.scroll(-SCROLL_SENSITIVITY)
    
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
    
    def double_click(self):
        """Perform double click"""
        if not self.mouse_enabled:
            return
        pyautogui.doubleClick()
    
    def middle_click(self):
        """Perform middle mouse click"""
        if not self.mouse_enabled:
            return
        pyautogui.middleClick()
    
    def set_mouse_enabled(self, enabled: bool):
        """Enable or disable mouse control"""
        self.mouse_enabled = enabled
        
        if not enabled and self.dragging:
            self.drag_end()
    
    def get_current_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        return pyautogui.position()