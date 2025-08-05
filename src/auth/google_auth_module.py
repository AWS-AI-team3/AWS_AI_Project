"""
Google OAuth authentication module - Optional component
This module can be imported and used when Google OAuth is needed
"""

import os
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading
import time
from typing import Optional, Dict

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    import requests
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False

class AuthHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback"""
    
    def do_GET(self):
        """Handle GET request for OAuth callback"""
        if self.path.startswith('/callback'):
            # Parse the authorization code from the callback URL
            query_components = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
            
            if 'code' in query_components:
                self.server.auth_code = query_components['code']
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'''
                <html>
                <body>
                <h1>Authentication successful!</h1>
                <p>You can close this window and return to the application.</p>
                <script>window.close();</script>
                </body>
                </html>
                ''')
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Authentication failed!</h1></body></html>')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress log messages"""
        pass

class GoogleAuthModule:
    """Google OAuth authentication module - Optional component"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str = "http://localhost:8080/callback"):
        if not GOOGLE_AUTH_AVAILABLE:
            raise ImportError("Google auth dependencies not available. Install with: pip install google-auth google-auth-oauthlib")
        
        self.credentials = None
        self.user_info = None
        
        # OAuth 2.0 client configuration
        self.client_config = {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        }
        
        self.redirect_uri = redirect_uri
        
        # OAuth scopes
        self.scopes = [
            'openid',
            'email',
            'profile'
        ]
    
    def authenticate(self) -> Optional[Dict]:
        """Perform Google OAuth authentication"""
        try:
            # Check if we have valid stored credentials
            if self.load_stored_credentials():
                if self.credentials.valid:
                    return self.get_user_info()
                elif self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                    self.save_credentials()
                    return self.get_user_info()
            
            # Start OAuth flow
            return self.start_oauth_flow()
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    def start_oauth_flow(self) -> Optional[Dict]:
        """Start OAuth authentication flow"""
        try:
            # Create flow
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.scopes
            )
            flow.redirect_uri = self.redirect_uri
            
            # Start local server for callback
            server = HTTPServer(('localhost', 8080), AuthHandler)
            server.timeout = 60  # 60 seconds timeout
            server.auth_code = None
            
            # Start server in background thread
            server_thread = threading.Thread(target=server.handle_request, daemon=True)
            server_thread.start()
            
            # Get authorization URL
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            # Open browser for authentication
            webbrowser.open(auth_url)
            
            # Wait for callback
            server_thread.join(timeout=60)
            
            if hasattr(server, 'auth_code') and server.auth_code:
                # Exchange authorization code for tokens
                flow.fetch_token(code=server.auth_code)
                self.credentials = flow.credentials
                
                # Save credentials
                self.save_credentials()
                
                # Get user info
                return self.get_user_info()
            else:
                print("Authentication timed out or failed")
                return None
                
        except Exception as e:
            print(f"OAuth flow error: {e}")
            return None
    
    def get_user_info(self) -> Optional[Dict]:
        """Get user information from Google API"""
        try:
            if not self.credentials or not self.credentials.valid:
                return None
            
            # Get user info from Google API
            headers = {'Authorization': f'Bearer {self.credentials.token}'}
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers=headers
            )
            
            if response.status_code == 200:
                user_info = response.json()
                self.user_info = {
                    'id': user_info.get('id'),
                    'email': user_info.get('email'),
                    'name': user_info.get('name'),
                    'picture': user_info.get('picture'),
                    'verified_email': user_info.get('verified_email', False)
                }
                return self.user_info
            
        except Exception as e:
            print(f"Error getting user info: {e}")
        
        return None
    
    def load_stored_credentials(self) -> bool:
        """Load stored credentials from file"""
        try:
            creds_file = os.path.join('user_data', 'credentials.json')
            
            if os.path.exists(creds_file):
                self.credentials = Credentials.from_authorized_user_file(creds_file, self.scopes)
                return True
        except Exception as e:
            print(f"Error loading credentials: {e}")
        
        return False
    
    def save_credentials(self):
        """Save credentials to file"""
        try:
            creds_file = os.path.join('user_data', 'credentials.json')
            os.makedirs(os.path.dirname(creds_file), exist_ok=True)
            
            with open(creds_file, 'w') as f:
                f.write(self.credentials.to_json())
                
        except Exception as e:
            print(f"Error saving credentials: {e}")
    
    def logout(self):
        """Logout and clear credentials"""
        try:
            # Revoke token
            if self.credentials and self.credentials.token:
                requests.post(
                    'https://oauth2.googleapis.com/revoke',
                    params={'token': self.credentials.token},
                    headers={'content-type': 'application/x-www-form-urlencoded'}
                )
            
            # Clear stored credentials
            creds_file = os.path.join('user_data', 'credentials.json')
            if os.path.exists(creds_file):
                os.remove(creds_file)
            
            self.credentials = None
            self.user_info = None
            
        except Exception as e:
            print(f"Error during logout: {e}")
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.credentials is not None and self.credentials.valid

def get_google_auth_module(client_id: str, client_secret: str, redirect_uri: str = "http://localhost:8080/callback"):
    """
    Factory function to get Google auth module if available
    
    Returns:
        GoogleAuthModule instance or None if dependencies not available
    """
    try:
        return GoogleAuthModule(client_id, client_secret, redirect_uri)
    except ImportError as e:
        print(f"Google authentication not available: {e}")
        return None