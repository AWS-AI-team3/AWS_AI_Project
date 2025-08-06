"""
MediaPipe-based gesture recognition system
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, Tuple, List, Dict
from config.settings import *
# Import specific settings if needed
try:
    from config.settings import PINCH_THRESHOLD, SCROLL_ANGLE_THRESHOLD
except ImportError:
    PINCH_THRESHOLD = 0.04
    SCROLL_ANGLE_THRESHOLD = 0.15

class GestureRecognizer:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_NUM_HANDS,
            min_detection_confidence=HAND_DETECTION_CONFIDENCE,
            min_tracking_confidence=HAND_TRACKING_CONFIDENCE,
            model_complexity=1  # Higher complexity for better accuracy
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
        THUMB_IP = 3
        INDEX_TIP = 8
        INDEX_PIP = 6
        MIDDLE_TIP = 12
        MIDDLE_PIP = 10
        RING_TIP = 16
        RING_PIP = 14
        PINKY_TIP = 20
        PINKY_PIP = 18
        
        thumb_pos = positions[THUMB_TIP]
        index_pos = positions[INDEX_TIP]
        middle_pos = positions[MIDDLE_TIP]
        
        # Check for thumb-index pinch (left click) - more sensitive
        thumb_index_dist = np.sqrt(np.sum((thumb_pos - index_pos) ** 2))
        if thumb_index_dist < PINCH_THRESHOLD:
            return "thumb_index_pinch"
        
        # Check for thumb-middle pinch (right click) - more sensitive
        thumb_middle_dist = np.sqrt(np.sum((thumb_pos - middle_pos) ** 2))
        if thumb_middle_dist < PINCH_THRESHOLD:
            return "thumb_middle_pinch"
        
        # Get finger states (extended or not)
        thumb_up = positions[THUMB_TIP][1] < positions[THUMB_IP][1]
        index_up = positions[INDEX_TIP][1] < positions[INDEX_PIP][1]
        middle_up = positions[MIDDLE_TIP][1] < positions[MIDDLE_PIP][1]
        ring_up = positions[RING_TIP][1] < positions[RING_PIP][1]
        pinky_up = positions[PINKY_TIP][1] < positions[PINKY_PIP][1]
        
        fingers_up = [thumb_up, index_up, middle_up, ring_up, pinky_up]
        total_fingers = sum(fingers_up)
        
        # Check for horizontal thumb scroll position - more sensitive
        if total_fingers == 1 and thumb_up:
            # Calculate thumb angle for scroll detection
            thumb_angle = self._get_thumb_angle(positions)
            if abs(thumb_angle) > SCROLL_ANGLE_THRESHOLD:  # Only trigger if significant angle
                return f"thumb_scroll:{thumb_angle}"
        
        # Gesture classification logic
        if total_fingers == 0:
            return "fist"
        elif total_fingers == 5:
            return "open_hand"
        else:
            return "cursor_point"
    
    def get_mouse_position(self, landmarks: np.ndarray, frame_shape: Tuple[int, int]) -> Tuple[float, float]:
        """Convert thumb tip position to normalized coordinates [0, 1]"""
        if landmarks is None:
            return None
            
        # Use thumb tip (landmark 4) instead of index finger
        thumb_tip = landmarks[4]
        
        # Return normalized coordinates (MediaPipe already provides normalized coords)
        norm_x = thumb_tip[0]
        norm_y = thumb_tip[1]
        
        return norm_x, norm_y
    
    def _get_thumb_angle(self, positions: np.ndarray) -> float:
        """Calculate thumb angle for scroll detection with speed control based on vertical angle"""
        THUMB_TIP = 4
        THUMB_IP = 3
        THUMB_MCP = 2
        
        # Get thumb joint positions
        tip = positions[THUMB_TIP]
        ip = positions[THUMB_IP] 
        mcp = positions[THUMB_MCP]
        
        # Calculate thumb direction vector
        thumb_vector = tip - mcp
        
        # Calculate vertical and horizontal components
        vertical_component = thumb_vector[1]  # Y displacement
        horizontal_component = abs(thumb_vector[0])  # Absolute X displacement
        
        # Calculate the angle from horizontal (0 = horizontal, 1 = vertical)
        vector_magnitude = np.sqrt(thumb_vector[0]**2 + thumb_vector[1]**2)
        if vector_magnitude < 0.01:  # Avoid division by zero
            return 0.0
            
        # Calculate vertical ratio (how vertical the thumb is)
        vertical_ratio = abs(vertical_component) / vector_magnitude
        
        # Speed factor: reduces as thumb becomes more horizontal
        # When vertical_ratio is close to 1 (vertical thumb), speed_factor is 1
        # When vertical_ratio is close to 0 (horizontal thumb), speed_factor approaches 0
        speed_factor = vertical_ratio ** 2  # Square for more gradual speed reduction
        
        # Base scroll direction and strength
        base_strength = vertical_component * 8  # Scale factor for sensitivity
        
        # Apply speed factor
        final_scroll_strength = base_strength * speed_factor
        
        # Normalize and clip to reasonable range
        normalized_angle = np.clip(final_scroll_strength, -1.0, 1.0)
        
        return normalized_angle
    
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