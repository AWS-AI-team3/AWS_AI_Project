"""
Thumb-based gesture recognition system using MediaPipe
"""

import cv2
import mediapipe as mp
import numpy as np
import time
from typing import Optional, Tuple, List, Dict


class ThumbGestureRecognizer:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # For double-click detection
        self.last_click_time = 0
        self.double_click_threshold = 0.5  # seconds
        self.click_cooldown = 0.1  # prevent multiple clicks
        self.last_gesture_time = 0
        
        # For tracking thumb-index state
        self.previous_thumb_index_distance = None
        self.touch_threshold = 0.06  # Distance threshold for touch detection
        self.was_touching = False
        
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Optional[Dict]]:
        """Process video frame and detect thumb-based gestures"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        gesture_data = None
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Extract gesture data
                gesture_data = self._extract_thumb_gesture(hand_landmarks)
                
        return frame, gesture_data
    
    def _extract_thumb_gesture(self, landmarks) -> Dict:
        """Extract thumb-based gestures from hand landmarks"""
        # Get landmark positions
        positions = []
        for lm in landmarks.landmark:
            positions.append([lm.x, lm.y, lm.z])
        
        positions = np.array(positions)
        
        # Detect specific gestures
        gesture_type = self._classify_thumb_gesture(positions)
        
        return {
            'type': gesture_type,
            'landmarks': positions,
            'confidence': 0.8
        }
    
    def _classify_thumb_gesture(self, positions: np.ndarray) -> str:
        """Classify thumb-based gestures"""
        current_time = time.time()
        
        # Landmark indices
        THUMB_TIP = 4
        THUMB_MCP = 2
        INDEX_TIP = 8
        INDEX_MCP = 5
        WRIST = 0
        
        # Get positions
        thumb_tip = positions[THUMB_TIP]
        index_tip = positions[INDEX_TIP]
        thumb_mcp = positions[THUMB_MCP]
        index_mcp = positions[INDEX_MCP]
        wrist = positions[WRIST]
        
        # Calculate distance between thumb tip and index tip
        thumb_index_distance = np.sqrt(np.sum((thumb_tip - index_tip) ** 2))
        
        # Check if thumb and index are touching
        is_touching = thumb_index_distance < self.touch_threshold
        
        # Detect touch events (transition from not touching to touching)
        if is_touching and not self.was_touching:
            # Just started touching
            if current_time - self.last_gesture_time > self.click_cooldown:
                self.last_gesture_time = current_time
                
                # Check for double-click
                if current_time - self.last_click_time < self.double_click_threshold:
                    self.last_click_time = 0  # Reset to prevent triple-click
                    self.was_touching = is_touching
                    return "thumb_index_double_click"
                else:
                    self.last_click_time = current_time
                    self.was_touching = is_touching
                    return "thumb_index_click"
        
        self.was_touching = is_touching
        
        # Default cursor control using thumb position
        # Check if thumb is extended (higher than MCP joint)
        thumb_extended = thumb_tip[1] < thumb_mcp[1]
        
        if thumb_extended:
            return "thumb_cursor"
        
        return "idle"
    
    def get_thumb_position(self, landmarks: np.ndarray) -> Tuple[float, float]:
        """Get normalized thumb position for cursor control"""
        if landmarks is None:
            return None
            
        # Use thumb tip (landmark 4)
        thumb_tip = landmarks[4]
        
        # Return normalized coordinates
        # Use direct coordinates (frame is already flipped in hand_overlay.py)
        norm_x = thumb_tip[0]  # Direct x coordinate
        norm_y = thumb_tip[1]
        
        return norm_x, norm_y
    
    def cleanup(self):
        """Clean up resources"""
        if self.hands:
            self.hands.close()