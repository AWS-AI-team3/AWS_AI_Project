"""
Dummy Face recognition system - placeholder for future implementation
"""

import cv2
import numpy as np
from typing import Optional, List, Tuple

class FaceRecognitionSystem:
    """Placeholder face recognition system"""
    
    def __init__(self):
        """Initialize dummy face recognition system"""
        print("Face recognition system initialized (placeholder mode)")
        self.enabled = False
    
    def register_face(self, image: np.ndarray, user_id: str) -> bool:
        """Placeholder for face registration"""
        print(f"Face registration not implemented yet for user: {user_id}")
        return True  # Always return True for now
    
    def authenticate_face(self, image: np.ndarray, user_id: str) -> bool:
        """Placeholder for face authentication"""
        print(f"Face authentication not implemented yet for user: {user_id}")
        return True  # Always return True for now
    
    def user_exists(self, user_id: str) -> bool:
        """Placeholder for user existence check"""
        return False
    
    def remove_user_faces(self, user_id: str) -> bool:
        """Placeholder for removing user faces"""
        print(f"Face removal not implemented yet for user: {user_id}")
        return True
    
    def get_face_count(self, user_id: str) -> int:
        """Placeholder for getting face count"""
        return 0
    
    def detect_faces_in_frame(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Placeholder for face detection in frame"""
        return []  # Return empty list - no faces detected
    
    def draw_face_boxes(self, frame: np.ndarray, face_locations: List[Tuple[int, int, int, int]]) -> np.ndarray:
        """Placeholder for drawing face boxes"""
        return frame  # Return frame unchanged
    
    def get_user_list(self) -> List[str]:
        """Placeholder for getting user list"""
        return []
    
    def validate_image_quality(self, image: np.ndarray) -> Tuple[bool, str]:
        """Placeholder for image quality validation"""
        return True, "Image validation not implemented"