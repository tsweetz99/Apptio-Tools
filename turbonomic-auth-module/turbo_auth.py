#!/usr/bin/env python3
"""
Turbonomic Authentication Module
Provides flexible authentication methods for Turbonomic API access.
"""

import requests
import getpass
import os
import time
from typing import Optional, Tuple
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TurbonomicAuth:
    """Handle authentication and session management for Turbonomic API."""
    
    def __init__(self, url: str):
        """
        Initialize authentication handler.
        
        Args:
            url: Turbonomic instance URL
        """
        self.url = url.rstrip('/')
        self.session = requests.Session()
        self.session.verify = False  # For self-signed certificates
        self.jsessionid = None
        self.session_expiry = None
        self.session_timeout = 1800  # 30 minutes in seconds
        
    def authenticate_with_credentials(self, username: str, password: str) -> str:
        """
        Authenticate with username/password and return JSESSIONID.
        
        Args:
            username: Turbonomic username
            password: Turbonomic password
            
        Returns:
            JSESSIONID string
            
        Raises:
            Exception: If authentication fails
        """
        # Add hateoas=true query parameter as shown in Postman collection
        auth_url = f"{self.url}/api/v3/login?hateoas=true"
        
        try:
            # Use form-encoded data (application/x-www-form-urlencoded)
            response = self.session.post(
                auth_url,
                data={'username': username, 'password': password},
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                verify=False
            )
            
            if response.status_code == 200:
                jsessionid = response.cookies.get('JSESSIONID')
                if jsessionid:
                    self.jsessionid = jsessionid
                    # Set expiry to 1 minute before actual timeout for safety
                    self.session_expiry = time.time() + self.session_timeout - 60
                    print(f"✓ Authenticated as {username}")
                    return jsessionid
                else:
                    raise Exception("No JSESSIONID in response")
            else:
                # Provide more helpful error message
                error_msg = f"Authentication failed: {response.status_code}"
                if response.text:
                    error_msg += f"\nResponse: {response.text}"
                error_msg += f"\n\nPlease verify:"
                error_msg += f"\n  - Username is correct: {username}"
                error_msg += f"\n  - Password is correct"
                error_msg += f"\n  - Account is not locked"
                error_msg += f"\n  - Turbonomic URL is accessible: {self.url}"
                raise Exception(error_msg)
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection error: {e}\n\nPlease verify Turbonomic URL is accessible: {self.url}")
    
    def validate_jsessionid(self, jsessionid: str) -> bool:
        """
        Validate existing JSESSIONID.
        
        Args:
            jsessionid: JSESSIONID to validate
            
        Returns:
            True if valid, False otherwise
        """
        test_url = f"{self.url}/api/v3/markets"
        self.session.cookies.set('JSESSIONID', jsessionid)
        
        try:
            response = self.session.get(test_url, verify=False)
            if response.status_code == 200:
                self.jsessionid = jsessionid
                self.session_expiry = time.time() + self.session_timeout - 60
                return True
            return False
        except:
            return False
    
    def get_session(self) -> str:
        """
        Get valid session, refreshing if needed.
        
        Returns:
            Valid JSESSIONID
        """
        if not self.jsessionid or (self.session_expiry and time.time() >= self.session_expiry):
            raise Exception("Session expired. Please re-authenticate.")
        
        return self.jsessionid


def get_credentials_from_env() -> dict:
    """
    Load credentials from environment variables.
    
    Returns:
        Dictionary with url, username, password, jsessionid
    """
    return {
        'url': os.getenv('TURBO_URL'),
        'username': os.getenv('TURBO_USERNAME'),
        'password': os.getenv('TURBO_PASSWORD'),
        'jsessionid': os.getenv('TURBO_JSESSIONID')
    }


def setup_authentication(url: Optional[str] = None, 
                        username: Optional[str] = None,
                        password: Optional[str] = None,
                        jsessionid: Optional[str] = None) -> Tuple[str, str]:
    """
    Setup authentication using multiple methods in priority order:
    1. Provided JSESSIONID (backward compatibility)
    2. Provided username/password
    3. Environment variables
    4. Interactive prompt
    
    Args:
        url: Turbonomic instance URL
        username: Username for authentication
        password: Password for authentication
        jsessionid: Existing JSESSIONID
        
    Returns:
        Tuple of (url, jsessionid)
        
    Raises:
        Exception: If authentication fails or no method provided
    """
    # Get URL from environment if not provided
    if not url:
        url = os.getenv('TURBO_URL')
        if not url:
            raise Exception("URL required (use --url or set TURBO_URL environment variable)")
    
    # Method 1: Direct JSESSIONID (backward compatibility)
    if jsessionid:
        print("Using provided JSESSIONID...")
        auth = TurbonomicAuth(url)
        if auth.validate_jsessionid(jsessionid):
            return url, jsessionid
        else:
            print("Warning: Provided JSESSIONID is invalid, trying other methods...")
    
    # Method 2: Provided username/password
    if username and password:
        print(f"Authenticating as {username}...")
        auth = TurbonomicAuth(url)
        jsessionid = auth.authenticate_with_credentials(username, password)
        return url, jsessionid
    
    # Method 3: Environment variables
    env_creds = get_credentials_from_env()
    
    if env_creds['jsessionid']:
        print("Using JSESSIONID from environment...")
        url = env_creds['url'] or url
        auth = TurbonomicAuth(url)
        if auth.validate_jsessionid(env_creds['jsessionid']):
            return url, env_creds['jsessionid']
        else:
            print("Warning: Environment JSESSIONID is invalid, trying other methods...")
    
    if env_creds['username'] and env_creds['password']:
        print("Authenticating with credentials from environment...")
        url = env_creds['url'] or url
        auth = TurbonomicAuth(url)
        jsessionid = auth.authenticate_with_credentials(
            env_creds['username'],
            env_creds['password']
        )
        return url, jsessionid
    
    # Method 4: Interactive username/password
    if username:
        password = getpass.getpass(f"Password for {username}: ")
        auth = TurbonomicAuth(url)
        jsessionid = auth.authenticate_with_credentials(username, password)
        return url, jsessionid
    
    # No authentication method provided
    raise Exception(
        "No authentication method provided. Use one of:\n"
        "  --jsessionid <ID>\n"
        "  --username <user> (will prompt for password)\n"
        "  --username <user> --password <pass>\n"
        "  Environment variables: TURBO_USERNAME + TURBO_PASSWORD\n"
        "  Environment variable: TURBO_JSESSIONID"
    )


if __name__ == '__main__':
    # Test authentication
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python3 turbo_auth.py <url> <username>")
        sys.exit(1)
    
    try:
        url, jsessionid = setup_authentication(
            url=sys.argv[1],
            username=sys.argv[2]
        )
        print(f"\n✓ Authentication successful!")
        print(f"URL: {url}")
        print(f"JSESSIONID: {jsessionid[:20]}...")
    except Exception as e:
        print(f"\n✗ Authentication failed: {e}")
        sys.exit(1)

# Made with Bob
