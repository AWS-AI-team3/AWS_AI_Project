"""
Google OAuth placeholder module
This module provides stub implementation for migration purposes
"""

class GoogleAuthenticator:
    """Placeholder Google OAuth authenticator"""
    
    def __init__(self):
        self.authenticated = False
        
    def authenticate(self):
        """Stub authentication method"""
        return {
            'email': 'user@example.com',
            'name': 'Test User',
            'id': '123456789'
        }
        
    def is_authenticated(self):
        """Check if user is authenticated"""
        return self.authenticated
        
    def logout(self):
        """Logout user"""
        self.authenticated = False