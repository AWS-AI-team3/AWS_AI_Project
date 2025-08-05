"""
Dummy Google OAuth authentication system - placeholder
"""

from typing import Optional, Dict

class GoogleAuthenticator:
    """Placeholder Google OAuth authenticator"""
    
    def __init__(self):
        """Initialize dummy authenticator"""
        print("Google authentication system initialized (placeholder mode)")
        self.credentials = None
        self.user_info = None
    
    def authenticate(self) -> Optional[Dict]:
        """Placeholder for Google OAuth authentication"""
        print("Google authentication not implemented yet")
        # Return dummy user info for testing
        return {
            'id': 'dummy_user_123',
            'email': 'test@example.com',
            'name': 'Test User',
            'picture': None,
            'verified_email': True
        }
    
    def get_user_info(self) -> Optional[Dict]:
        """Placeholder for getting user info"""
        return {
            'id': 'dummy_user_123',
            'email': 'test@example.com',
            'name': 'Test User',
            'picture': None,
            'verified_email': True
        }
    
    def logout(self):
        """Placeholder for logout"""
        print("Google logout not implemented yet")
        self.credentials = None
        self.user_info = None
    
    def is_authenticated(self) -> bool:
        """Placeholder for authentication check"""
        return True  # Always return True for testing