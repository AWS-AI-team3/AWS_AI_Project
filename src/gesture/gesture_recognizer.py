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
            model_complexity=0  # Lower complexity for better performance
        )
        
        self.thumb_index_middle_scroll_start_pos = None
        self.is_thumb_index_middle_scrolling = False
        
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Optional[Dict]]:
        """Process video frame and detect hand gestures"""
        # Use in-place color conversion to reduce memory allocation
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb.flags.writeable = False  # Improve performance
        results = self.hands.process(frame_rgb)
        frame_rgb.flags.writeable = True
        
        gesture_data = None
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand skeleton if enabled
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )
                
                # Extract gesture
                gesture_data = self._extract_gesture(hand_landmarks)
        else:
            # No hands detected - reset scroll state
            if self.is_thumb_index_middle_scrolling:
                self.is_thumb_index_middle_scrolling = False
                self.thumb_index_middle_scroll_start_pos = None
                
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
        
        # Check for thumb-index-middle triple pinch (scroll gesture)
        # All three fingers (thumb, index, middle) must be close together
        thumb_index_dist = np.sqrt(np.sum((thumb_pos - index_pos) ** 2))
        thumb_middle_dist = np.sqrt(np.sum((thumb_pos - middle_pos) ** 2))
        index_middle_dist = np.sqrt(np.sum((index_pos - middle_pos) ** 2))
        
        # Triple pinch condition: all distances must be below threshold
        triple_pinch_threshold = PINCH_THRESHOLD * 2  # Slightly larger threshold for 3-finger pinch
        if (thumb_index_dist < triple_pinch_threshold and 
            thumb_middle_dist < triple_pinch_threshold and 
            index_middle_dist < triple_pinch_threshold):
            return self._handle_thumb_index_middle_scroll(positions)
        
        # Get finger states (extended or not)
        thumb_up = positions[THUMB_TIP][1] < positions[THUMB_IP][1]
        index_up = positions[INDEX_TIP][1] < positions[INDEX_PIP][1]
        middle_up = positions[MIDDLE_TIP][1] < positions[MIDDLE_PIP][1]
        ring_up = positions[RING_TIP][1] < positions[RING_PIP][1]
        pinky_up = positions[PINKY_TIP][1] < positions[PINKY_PIP][1]
        
        fingers_up = [thumb_up, index_up, middle_up, ring_up, pinky_up]
        total_fingers = sum(fingers_up)
        
        # Old thumb-only scroll gesture removed - replaced with thumb-ring pinch scroll
        
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
    
    def _handle_thumb_index_middle_scroll(self, positions: np.ndarray) -> str:
        """Handle thumb-index-middle triple pinch scroll gesture based on Y-axis movement"""
        THUMB_TIP = 4
        INDEX_TIP = 8
        MIDDLE_TIP = 12
        
        # Get current triple pinch center position (average of 3 fingertips)
        thumb_pos = positions[THUMB_TIP]
        index_pos = positions[INDEX_TIP]
        middle_pos = positions[MIDDLE_TIP]
        current_pinch_pos = (thumb_pos + index_pos + middle_pos) / 3  # Center point of 3-finger pinch
        
        if not self.is_thumb_index_middle_scrolling:
            # First time detecting triple pinch - initialize scroll tracking
            self.thumb_index_middle_scroll_start_pos = current_pinch_pos
            self.is_thumb_index_middle_scrolling = True
            return "thumb_index_middle_scroll_start"
        else:
            # Calculate Y-axis movement from initial pinch position
            y_displacement = current_pinch_pos[1] - self.thumb_index_middle_scroll_start_pos[1]
            
            # Calculate scroll speed based on Y displacement with higher sensitivity
            # Positive y_displacement = moved down = scroll down
            # Negative y_displacement = moved up = scroll up
            scroll_speed = y_displacement * 50  # Increased sensitivity from 20 to 50
            
            # Apply minimum threshold to avoid micro-scrolls (reduced for higher sensitivity)
            if abs(scroll_speed) > 0.2:
                return f"thumb_index_middle_scroll:{scroll_speed}"
            else:
                return "thumb_index_middle_scroll_hold"
    
    
    def cleanup(self):
        """Clean up resources"""
        if self.hands:
            self.hands.close()