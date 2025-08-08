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
        self.click_cooldown = 0.15  # prevent multiple clicks (더 긴 쿨다운: 0.1 → 0.15)
        self.last_gesture_time = 0
        
        # For gesture debouncing (연속 제스처 방지)
        self.gesture_debounce_time = 0.2  # 제스처 간 최소 간격
        self.last_any_gesture_time = 0
        
        # For tracking thumb-index state
        self.previous_thumb_index_distance = None
        self.touch_threshold = 0.04  # Distance threshold for touch detection (더 둔감하게: 0.06 → 0.04)
        self.was_touching = False
        
        # For 3-finger scroll (thumb + index + middle)
        self.thumb_index_middle_scroll_start_pos = None
        self.is_thumb_index_middle_scrolling = False
        self.triple_pinch_threshold = 0.08  # Threshold for 3-finger pinch (더 둔감하게: 0.12 → 0.08)
        
        # For drag detection (thumb + index pinch hold)
        self.is_dragging = False
        self.drag_start_time = 0
        
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
        
        # Apply gesture debouncing to prevent over-sensitive detection
        if current_time - self.last_any_gesture_time < self.gesture_debounce_time:
            return "no_gesture"
        
        # Landmark indices
        THUMB_TIP = 4
        INDEX_TIP = 8
        MIDDLE_TIP = 12
        
        # Get positions
        thumb_tip = positions[THUMB_TIP]
        index_tip = positions[INDEX_TIP]
        middle_tip = positions[MIDDLE_TIP]
        
        # Calculate distances
        thumb_index_distance = np.sqrt(np.sum((thumb_tip - index_tip) ** 2))
        thumb_middle_distance = np.sqrt(np.sum((thumb_tip - middle_tip) ** 2))
        index_middle_distance = np.sqrt(np.sum((index_tip - middle_tip) ** 2))
        
        # Check for 3-finger pinch (scroll gesture)
        if (thumb_index_distance < self.triple_pinch_threshold and 
            thumb_middle_distance < self.triple_pinch_threshold and 
            index_middle_distance < self.triple_pinch_threshold):
            return self._handle_thumb_index_middle_scroll(positions)
        
        # Reset scroll state if not in triple pinch
        if self.is_thumb_index_middle_scrolling:
            self.is_thumb_index_middle_scrolling = False
            self.thumb_index_middle_scroll_start_pos = None
        
        # Check for thumb-middle pinch (right click)
        if thumb_middle_distance < self.touch_threshold:
            if current_time - self.last_gesture_time > self.click_cooldown:
                self.last_gesture_time = current_time
                self.last_any_gesture_time = current_time  # Update debounce timer
                return "thumb_middle_pinch"
        
        # Check for thumb-index pinch
        is_touching = thumb_index_distance < self.touch_threshold
        
        if is_touching:
            if not self.was_touching:
                # Just started pinch
                if current_time - self.last_gesture_time > self.click_cooldown:
                    self.last_gesture_time = current_time
                    self.drag_start_time = current_time
                    
                    # Check for double-click
                    if current_time - self.last_click_time < self.double_click_threshold:
                        self.last_click_time = 0
                        self.was_touching = is_touching
                        self.last_any_gesture_time = current_time  # Update debounce timer
                        return "thumb_index_double_click"
                    else:
                        self.last_click_time = current_time
                        self.was_touching = is_touching
                        self.is_dragging = True
                        self.last_any_gesture_time = current_time  # Update debounce timer
                        return "thumb_index_pinch_start"
            else:
                # Continuing pinch - check if it's drag
                if self.is_dragging and current_time - self.drag_start_time > 0.15:
                    return "thumb_index_drag"
                else:
                    return "thumb_index_pinch_hold"
        else:
            # Released pinch
            if self.was_touching and self.is_dragging:
                drag_duration = current_time - self.drag_start_time
                self.is_dragging = False
                self.was_touching = False
                
                if drag_duration < 0.15:  # Short duration = click
                    self.last_any_gesture_time = current_time  # Update debounce timer
                    return "thumb_index_click"
                else:  # Long duration = drag end
                    self.last_any_gesture_time = current_time  # Update debounce timer
                    return "thumb_index_drag_end"
        
        self.was_touching = is_touching
        
        # Default cursor control
        return "thumb_cursor"
    
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
            
            # Calculate scroll speed based on Y displacement with reduced sensitivity
            # Positive y_displacement = moved down = scroll down
            # Negative y_displacement = moved up = scroll up
            scroll_speed = y_displacement * 30  # Reduced sensitivity (50 → 30)
            
            # Apply minimum threshold to avoid micro-scrolls (더 높은 임계값)
            if abs(scroll_speed) > 0.4:
                return f"thumb_index_middle_scroll:{scroll_speed}"
            else:
                return "thumb_index_middle_scroll_hold"
    
    def cleanup(self):
        """Clean up resources"""
        if self.hands:
            self.hands.close()