"""
Face recognition system placeholder module
This module provides stub implementation for migration purposes
"""

class FaceRecognitionSystem:
    """Placeholder face recognition system"""
    
    def __init__(self):
        self.registered_users = set()
        
    def user_exists(self, user_email: str) -> bool:
        """Check if user exists in the system"""
        # For migration, always return False to skip face auth
        return False
        
    def register_face(self, image, user_email: str) -> bool:
        """Register user's face"""
        self.registered_users.add(user_email)
        return True
        
    def authenticate_face(self, image, user_email: str) -> bool:
        """Authenticate user via face recognition"""
        return user_email in self.registered_users
        
    def cleanup(self):
        """Clean up resources"""
        pass