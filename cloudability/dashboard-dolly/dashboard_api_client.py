#!/usr/bin/env python3
"""
Dashboard API Client
Handles authentication and API requests for Cloudability dashboards.
"""

import requests
from requests.auth import HTTPBasicAuth
import json
from typing import Dict, List, Optional, Any
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DashboardAPIClient:
    """API client for Cloudability dashboard operations."""
    
    def __init__(self, api_key: Optional[str] = None, auth_type: str = "cloudability",
                 region: str = "", frontdoor_env: str = "", 
                 public_key: str = "", private_key: str = ""):
        """
        Initialize Dashboard API client.
        
        Args:
            api_key: Cloudability API key
            auth_type: Authentication type ("cloudability" or "frontdoor")
            region: Region ("", "au", "eu", "usgov")
            frontdoor_env: Frontdoor environment ID
            public_key: Frontdoor public key
            private_key: Frontdoor private key
        """
        self.auth_type = auth_type
        self.region = self._format_region(region)
        self.base_url = f"https://api{self.region}.cloudability.com/v3"
        self.session = requests.Session()
        self.session.verify = False
        
        if auth_type == "cloudability" and api_key:
            self.session.auth = HTTPBasicAuth(api_key, '')
        elif auth_type == "frontdoor":
            # Import apptio_lib for frontdoor auth
            try:
                from apptio_lib import apptio as fd
                opentoken = fd.get_auth(region=region, public=public_key, private=private_key)
                self.session.headers.update({
                    'apptio-opentoken': opentoken,
                    'apptio-current-environment': frontdoor_env,
                    'app-type': 'Flagship',
                })
            except ImportError:
                raise ImportError("apptio_lib is required for Frontdoor authentication")
    
    def _format_region(self, region: str) -> str:
        """Format region string for API URL."""
        if not region:
            return ""
        if region.startswith('.') or region.startswith('-'):
            return region
        if region == "usgov":
            return ".usgov"
        return f"-{region}"
    
    def test_connection(self) -> tuple[bool, str]:
        """
        Test the API connection.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            response = self.get('/internal/dashboards', params={'limit': 1})
            if isinstance(response, list) or (isinstance(response, dict) and 'result' in response):
                return True, "Connection successful"
            else:
                return False, f"Unexpected response: {response}"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """
        Make a GET request to the Cloudability API.
        
        Args:
            endpoint: API endpoint (e.g., '/internal/dashboards')
            params: Query parameters
            
        Returns:
            Response JSON
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status_code": getattr(e.response, 'status_code', None)}
    
    def post(self, endpoint: str, data: Dict) -> Any:
        """
        Make a POST request to the Cloudability API.
        
        Args:
            endpoint: API endpoint
            data: Request body data
            
        Returns:
            Response JSON or response object on error
        """
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = self.session.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                return e.response
            return {"error": str(e), "status_code": None}
    
    def get_organization_info(self) -> Optional[Dict]:
        """Get organization information."""
        try:
            response = self.get('/internal/organization/settings')
            if isinstance(response, dict) and 'name' in response:
                return response
            return None
        except:
            return None
    
    def get_dashboard_list(self, limit: int = 500) -> List[Dict]:
        """
        Get list of dashboards.
        
        Args:
            limit: Maximum number of dashboards to retrieve
            
        Returns:
            List of dashboard dictionaries
        """
        params = {
            'limit': limit,
            'skip_shared_dimension_filter_set_ids': 'true',
            'use_basic_user': 'true'
        }
        response = self.get('/internal/dashboards', params=params)
        
        if isinstance(response, list):
            return response
        elif isinstance(response, dict) and 'result' in response:
            return response['result']
        return []
    
    def get_dashboard(self, dashboard_id: int) -> Dict:
        """
        Get full dashboard details.
        
        Args:
            dashboard_id: Dashboard ID
            
        Returns:
            Dashboard dictionary
        """
        params = {
            'skip_shared_dimension_filter_set_ids': 'true',
            'use_basic_user': 'true'
        }
        return self.get(f'/internal/dashboards/{dashboard_id}', params=params)
    
    def create_dashboard(self, name: str) -> Dict:
        """
        Create a new dashboard.
        
        Args:
            name: Dashboard name
            
        Returns:
            Created dashboard dictionary
        """
        data = {'name': name}
        return self.post('/internal/dashboards', data=data)
    
    def create_widget(self, widget_data: Dict) -> Any:
        """
        Create a widget in a dashboard.
        
        Args:
            widget_data: Widget configuration
            
        Returns:
            Created widget response
        """
        return self.post('/internal/widgets', data=widget_data)

# Made with Bob
