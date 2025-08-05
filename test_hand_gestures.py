#!/usr/bin/env python3
"""
Simple hand gesture recognition test script
Tests MediaPipe hand tracking and gesture recognition without GUI dependencies
"""

import cv2
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from gesture.gesture_recognizer import GestureRecognizer
from gesture.mouse_controller import MouseController

def main():
    """Main test function"""
    print("=== Hand Gesture Recognition Test ===")
    print("Controls:")
    print("- Hold up different fingers to test gesture recognition")
    print("- Point with index finger to test mouse cursor movement")
    print("- Make a fist to test drag gestures")
    print("- Show thumbs up/down for scroll testing")
    print("- Press 'q' to quit")
    print("- Press 'm' to toggle mouse control on/off")
    print()
    
    # Initialize components
    try:
        gesture_recognizer = GestureRecognizer()
        mouse_controller = MouseController()
        print("OK - Gesture recognizer and mouse controller initialized")
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
    
    mouse_enabled = True
    frame_count = 0
    
    print("\n=== Starting gesture recognition (press 'q' to quit) ===\n")
    
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
                
                # Display gesture information
                if gesture_data:
                    gesture_type = gesture_data.get('type', 'unknown')
                    confidence = gesture_data.get('confidence', 0.0)
                    
                    # Draw gesture info on frame
                    cv2.putText(processed_frame, f"Gesture: {gesture_type}", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(processed_frame, f"Confidence: {confidence:.2f}", 
                               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # Print gesture info to console (every 30 frames to reduce spam)
                    if frame_count % 30 == 0:
                        print(f"Detected: {gesture_type} (confidence: {confidence:.2f})")
                    
                    # Test mouse control if enabled
                    if mouse_enabled and gesture_data:
                        landmarks = gesture_data.get('landmarks')
                        if landmarks is not None:
                            # Get mouse position from index finger
                            mouse_pos = gesture_recognizer.get_mouse_position(landmarks, frame.shape[:2])
                            
                            # Process gesture for mouse control
                            if gesture_type == "index_finger_point" and mouse_pos:
                                mouse_controller.process_gesture(gesture_data, mouse_pos)
                            else:
                                mouse_controller.process_gesture(gesture_data)
                            
                            # Test click detection
                            click_gesture = gesture_recognizer.detect_click_gesture(landmarks)
                            if click_gesture == "tap":
                                print("CLICK - Click gesture detected!")
                                mouse_controller.left_click()
                
                # Show mouse control status
                mouse_status = "ON" if mouse_enabled else "OFF"
                cv2.putText(processed_frame, f"Mouse Control: {mouse_status}", 
                           (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                           (0, 255, 0) if mouse_enabled else (0, 0, 255), 2)
                
                # Show instructions
                cv2.putText(processed_frame, "Press 'q' to quit, 'm' to toggle mouse", 
                           (10, processed_frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Display frame
                cv2.imshow('Hand Gesture Test', processed_frame)
                
            except Exception as e:
                print(f"Error processing frame: {e}")
                cv2.imshow('Hand Gesture Test', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\nQuitting...")
                break
            elif key == ord('m'):
                mouse_enabled = not mouse_enabled
                mouse_controller.set_mouse_enabled(mouse_enabled)
                status = "enabled" if mouse_enabled else "disabled"
                print(f"Mouse control {status}")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        # Cleanup
        try:
            cap.release()
            cv2.destroyAllWindows()
            gesture_recognizer.cleanup()
            print("OK - Cleanup completed")
        except Exception as e:
            print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    main()