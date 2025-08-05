"""
MediaPipe-based gesture recognition system
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, Tuple, List, Dict
from config.settings import *

class GestureRecognizer:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_NUM_HANDS,
            min_detection_confidence=HAND_DETECTION_CONFIDENCE,
            min_tracking_confidence=HAND_TRACKING_CONFIDENCE
        )
        
        self.previous_landmarks = None
        self.gesture_history = []
        
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Optional[Dict]]:
        """Process video frame and detect hand gestures"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        gesture_data = None
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand skeleton if enabled
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )
                
                # Extract gesture
                gesture_data = self._extract_gesture(hand_landmarks)
                
        return frame, gesture_data
    
    def _extract_gesture(self, landmarks) -> Dict:
        """Extract gesture type from hand landmarks"""
        # Get landmark positions
        positions = []
        for lm in landmarks.landmark:
            positions.append([lm.x, lm.y, lm.z])
        
        positions = np.array(positions)
        
        # Detect specific gestures
        gesture_type = self._classify_gesture(positions)
        
        return {
            'type': gesture_type,
            'landmarks': positions,
            'confidence': 0.8  # Placeholder
        }
    
    def _classify_gesture(self, positions: np.ndarray) -> str:
        """Classify gesture based on hand landmarks"""
        # Finger tip and pip indices
        THUMB_TIP = 4
        INDEX_TIP = 8
        INDEX_PIP = 6
        MIDDLE_TIP = 12
        MIDDLE_PIP = 10
        RING_TIP = 16
        RING_PIP = 14
        PINKY_TIP = 20
        PINKY_PIP = 18
        
        # Check for thumb-index pinch (click gesture)
        thumb_pos = positions[THUMB_TIP]
        index_pos = positions[INDEX_TIP]
        
        # Calculate distance between thumb tip and index tip
        distance = np.sqrt(np.sum((thumb_pos - index_pos) ** 2))
        
        # If thumb and index are close together, it's a pinch/click
        if distance < 0.05:  # Adjust threshold as needed
            return "pinch_click"
        
        # Get finger states (extended or not)
        thumb_up = positions[THUMB_TIP][1] < positions[THUMB_TIP - 1][1]
        index_up = positions[INDEX_TIP][1] < positions[INDEX_PIP][1]
        middle_up = positions[MIDDLE_TIP][1] < positions[MIDDLE_PIP][1]
        ring_up = positions[RING_TIP][1] < positions[RING_PIP][1]
        pinky_up = positions[PINKY_TIP][1] < positions[PINKY_PIP][1]
        
        fingers_up = [thumb_up, index_up, middle_up, ring_up, pinky_up]
        total_fingers = sum(fingers_up)
        
        # Gesture classification logic
        if total_fingers == 0:
            return "fist"
        elif total_fingers == 1 and index_up:
            return "cursor_point"  # Changed from index_finger_point
        elif total_fingers == 1 and thumb_up:
            return "thumb_up"
        elif total_fingers == 2 and index_up and middle_up:
            return "peace_sign"
        elif total_fingers == 5:
            return "open_hand"
        else:
            return "cursor_point" if index_up else "unknown"
    
    def get_mouse_position(self, landmarks: np.ndarray, frame_shape: Tuple[int, int]) -> Tuple[float, float]:
        """Convert index finger position to normalized coordinates [0, 1]"""
        if landmarks is None:
            return None
            
        # Use index finger tip (landmark 8)
        index_tip = landmarks[8]
        
        # Return normalized coordinates (MediaPipe already provides normalized coords)
        # MediaPipe coordinates are already mirrored when we flip the frame
        # So we use them directly without additional flipping
        norm_x = index_tip[0]  # Use direct x coordinate
        norm_y = index_tip[1]
        
        return norm_x, norm_y
    
    def detect_click_gesture(self, current_landmarks: np.ndarray) -> Optional[str]:
        """Detect click gestures based on finger movement"""
        if self.previous_landmarks is None:
            self.previous_landmarks = current_landmarks
            return None
            
        # Simple tap detection based on z-coordinate change
        INDEX_TIP = 8
        current_z = current_landmarks[INDEX_TIP][2]
        previous_z = self.previous_landmarks[INDEX_TIP][2]
        
        z_diff = current_z - previous_z
        
        # Threshold for tap detection
        if z_diff < -0.05:  # Forward movement (tap)
            self.previous_landmarks = current_landmarks
            return "tap"
            
        self.previous_landmarks = current_landmarks
        return None
    
    def cleanup(self):
        """Clean up resources"""
        if self.hands:
            self.hands.close()