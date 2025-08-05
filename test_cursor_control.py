#!/usr/bin/env python3
"""
Hand cursor control test - Index finger as cursor, pinch to click
Shows cursor on desktop, not camera window
"""

import cv2
import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from gesture.gesture_recognizer import GestureRecognizer
from gesture.mouse_controller import MouseController
from gesture.cursor_overlay import SimpleCursorOverlay

def main():
    """Main test function"""
    print("=== Hand Cursor Control Test ===")
    print("Controls:")
    print("- Point with INDEX FINGER to move cursor")
    print("- PINCH (thumb + index) to LEFT CLICK") 
    print("- Cursor will appear on your DESKTOP, not camera window")
    print("- Press 'q' in camera window to quit")
    print("- Press SPACE to toggle cursor overlay on/off")
    print()
    
    # Initialize components
    try:
        gesture_recognizer = GestureRecognizer()
        mouse_controller = MouseController()
        cursor_overlay = SimpleCursorOverlay()
        print("OK - All components initialized")
    except Exception as e:
        print(f"ERROR - Error initializing components: {e}")
        return
    
    # Initialize camera
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("ERROR - Could not open camera")
            return
        print("OK - Camera initialized")
    except Exception as e:
        print(f"ERROR - Error initializing camera: {e}")
        return
    
    # Start cursor overlay
    cursor_overlay.start()
    
    frame_count = 0
    last_click_time = 0
    cursor_active = True
    
    print("\n=== Hand cursor active! Look at your desktop ===")
    print("Move your index finger to control the cursor")
    print("Pinch thumb and index finger together to click")
    print()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("ERROR - Error reading from camera")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            frame_count += 1
            
            # Process frame for gestures
            try:
                processed_frame, gesture_data = gesture_recognizer.process_frame(frame)
                
                if gesture_data and cursor_active:
                    gesture_type = gesture_data.get('type', 'unknown')
                    landmarks = gesture_data.get('landmarks')
                    
                    # Get normalized cursor position from index finger
                    if landmarks is not None:
                        cursor_pos = gesture_recognizer.get_mouse_position(landmarks, frame.shape[:2])
                        
                        if cursor_pos:
                            # Convert normalized coordinates to screen coordinates
                            import pyautogui
                            screen_width, screen_height = pyautogui.size()
                            screen_x = int(cursor_pos[0] * screen_width)
                            screen_y = int(cursor_pos[1] * screen_height)
                            
                            # Update cursor position on desktop
                            cursor_overlay.update_position(screen_x, screen_y)
                            mouse_controller.move_mouse(cursor_pos)
                    
                    # Handle pinch click
                    if gesture_type == "pinch_click":
                        current_time = time.time()
                        if current_time - last_click_time > 0.5:  # Prevent rapid clicking
                            cursor_overlay.set_clicking(True)
                            mouse_controller.left_click()
                            last_click_time = current_time
                            print(f"PINCH CLICK detected at {screen_x}, {screen_y}")
                    else:
                        cursor_overlay.set_clicking(False)
                    
                    # Display gesture info on camera window
                    if frame_count % 30 == 0:  # Every 30 frames to reduce spam
                        print(f"Gesture: {gesture_type}")
                
                # Draw status on camera frame
                status_text = "CURSOR ACTIVE" if cursor_active else "CURSOR DISABLED"
                status_color = (0, 255, 0) if cursor_active else (0, 0, 255)
                cv2.putText(processed_frame, status_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
                
                cv2.putText(processed_frame, "Point index finger to move cursor", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(processed_frame, "Pinch thumb+index to click", (10, 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(processed_frame, "Press SPACE to toggle, 'q' to quit", (10, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Display camera window (small, just for feedback)
                small_frame = cv2.resize(processed_frame, (640, 480))
                cv2.imshow('Hand Tracking (Camera View)', small_frame)
                
            except Exception as e:
                print(f"Error processing frame: {e}")
                cv2.imshow('Hand Tracking (Camera View)', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\nQuitting...")
                break
            elif key == ord(' '):  # Space bar
                cursor_active = not cursor_active
                status = "enabled" if cursor_active else "disabled"
                print(f"Cursor control {status}")
                if cursor_active:
                    cursor_overlay.start()
                else:
                    cursor_overlay.stop()
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        # Cleanup
        try:
            cursor_overlay.stop()
            cap.release()
            cv2.destroyAllWindows()
            gesture_recognizer.cleanup()
            print("OK - Cleanup completed")
        except Exception as e:
            print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    main()