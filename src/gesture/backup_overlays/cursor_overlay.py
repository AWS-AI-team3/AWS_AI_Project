"""
Desktop cursor overlay for hand gesture tracking
Shows a visual cursor on the desktop that follows hand movements
"""

import tkinter as tk
from typing import Tuple, Optional
import threading
import time

class CursorOverlay:
    """Desktop cursor overlay that shows hand position"""
    
    def __init__(self, cursor_size: int = 20):
        self.cursor_size = cursor_size
        self.overlay_window = None
        self.running = False
        self.current_pos = (0, 0)
        self.is_clicking = False
        self.update_thread = None
        
    def start(self):
        """Start the cursor overlay"""
        if self.running:
            return
            
        self.running = True
        
        # Create overlay window in separate thread
        self.update_thread = threading.Thread(target=self._create_overlay, daemon=True)
        self.update_thread.start()
    
    def stop(self):
        """Stop the cursor overlay"""
        self.running = False
        if self.overlay_window:
            try:
                self.overlay_window.quit()
                self.overlay_window.destroy()
            except:
                pass
    
    def update_position(self, x: int, y: int):
        """Update cursor position"""
        self.current_pos = (x, y)
    
    def set_clicking(self, clicking: bool):
        """Set clicking state (changes cursor appearance)"""
        self.is_clicking = clicking
    
    def _create_overlay(self):
        """Create the overlay window"""
        try:
            # Create transparent overlay window
            self.overlay_window = tk.Tk()
            self.overlay_window.title("Hand Cursor")
            
            # Make window transparent and always on top
            self.overlay_window.attributes('-transparentcolor', 'black')
            self.overlay_window.attributes('-topmost', True)
            self.overlay_window.attributes('-toolwindow', True)
            
            # Remove window decorations
            self.overlay_window.overrideredirect(True)
            
            # Set window size
            self.overlay_window.geometry(f"{self.cursor_size}x{self.cursor_size}+0+0")
            
            # Create canvas for cursor
            canvas = tk.Canvas(
                self.overlay_window,
                width=self.cursor_size,
                height=self.cursor_size,
                bg='black',
                highlightthickness=0
            )
            canvas.pack()
            
            # Start update loop
            self._update_overlay(canvas)
            
            # Start tkinter main loop
            self.overlay_window.mainloop()
            
        except Exception as e:
            print(f"Error creating overlay: {e}")
    
    def _update_overlay(self, canvas):
        """Update overlay appearance and position"""
        if not self.running:
            return
        
        try:
            # Clear canvas
            canvas.delete("all")
            
            # Choose cursor color based on state
            cursor_color = "red" if self.is_clicking else "lime"
            outline_color = "white"
            
            # Draw cursor (circle with crosshair)
            center = self.cursor_size // 2
            radius = center - 2
            
            # Draw outer circle
            canvas.create_oval(
                2, 2, self.cursor_size - 2, self.cursor_size - 2,
                outline=outline_color, width=2, fill=""
            )
            
            # Draw inner circle
            canvas.create_oval(
                center - 3, center - 3, center + 3, center + 3,
                fill=cursor_color, outline=outline_color
            )
            
            # Draw crosshair
            canvas.create_line(
                center - 8, center, center + 8, center,
                fill=outline_color, width=1
            )
            canvas.create_line(
                center, center - 8, center, center + 8,
                fill=outline_color, width=1
            )
            
            # Update window position
            x, y = self.current_pos
            # Offset so cursor center is at the position
            x -= self.cursor_size // 2
            y -= self.cursor_size // 2
            
            self.overlay_window.geometry(f"{self.cursor_size}x{self.cursor_size}+{x}+{y}")
            
            # Schedule next update
            self.overlay_window.after(16, lambda: self._update_overlay(canvas))  # ~60 FPS
            
        except Exception as e:
            if self.running:  # Only print error if we're supposed to be running
                print(f"Error updating overlay: {e}")

class SimpleCursorOverlay:
    """Simplified cursor overlay using just mouse tracking"""
    
    def __init__(self):
        self.active = False
        self.click_indicator_time = 0
        
    def start(self):
        """Start the cursor overlay (simplified - just tracks mouse)"""
        self.active = True
        print("Cursor overlay started (following system mouse)")
    
    def stop(self):
        """Stop the cursor overlay"""
        self.active = False
        print("Cursor overlay stopped")
    
    def update_position(self, x: int, y: int):
        """Update cursor position (moves system mouse)"""
        if self.active:
            import pyautogui
            pyautogui.moveTo(x, y)
    
    def set_clicking(self, clicking: bool):
        """Set clicking state"""
        if clicking:
            current_time = time.time()
            # Prevent rapid clicking
            if current_time - self.click_indicator_time > 0.5:
                print("CLICK!")
                self.click_indicator_time = current_time