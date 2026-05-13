#!/usr/bin/env python3
"""
Example usage of the Turbonomic Authentication Module
Demonstrates how to integrate the auth module into your own scripts.
"""

import requests
from turbo_auth import setup_authentication, TurbonomicAuth


def example_1_basic_authentication():
    """Example 1: Basic authentication with username/password"""
    print("\n=== Example 1: Basic Authentication ===")
    
    try:
        url, jsessionid = setup_authentication(
            url="https://your-turbonomic-instance.com",
            username="your-username",
            password="your-password"
        )
        print(f"✓ Authenticated successfully!")
        print(f"  URL: {url}")
        print(f"  JSESSIONID: {jsessionid[:20]}...")
        
    except Exception as e:
        print(f"✗ Authentication failed: {e}")


def example_2_environment_variables():
    """Example 2: Authentication using environment variables"""
    print("\n=== Example 2: Environment Variables ===")
    print("Set these environment variables:")
    print("  export TURBO_URL='https://your-turbonomic-instance.com'")
    print("  export TURBO_USERNAME='your-username'")
    print("  export TURBO_PASSWORD='your-password'")
    
    try:
        url, jsessionid = setup_authentication()
        print(f"✓ Authenticated using environment variables!")
        print(f"  URL: {url}")
        print(f"  JSESSIONID: {jsessionid[:20]}...")
        
    except Exception as e:
        print(f"✗ Authentication failed: {e}")


def example_3_interactive_prompt():
    """Example 3: Interactive password prompt"""
    print("\n=== Example 3: Interactive Password Prompt ===")
    
    try:
        url, jsessionid = setup_authentication(
            url="https://your-turbonomic-instance.com",
            username="your-username"
            # Password will be prompted interactively
        )
        print(f"✓ Authenticated successfully!")
        print(f"  URL: {url}")
        print(f"  JSESSIONID: {jsessionid[:20]}...")
        
    except Exception as e:
        print(f"✗ Authentication failed: {e}")


def example_4_using_auth_class():
    """Example 4: Using TurbonomicAuth class directly"""
    print("\n=== Example 4: Using TurbonomicAuth Class ===")
    
    try:
        # Initialize auth handler
        auth = TurbonomicAuth("https://your-turbonomic-instance.com")
        
        # Authenticate
        jsessionid = auth.authenticate_with_credentials(
            "your-username",
            "your-password"
        )
        
        print(f"✓ Authenticated successfully!")
        print(f"  JSESSIONID: {jsessionid[:20]}...")
        
        # Validate session
        is_valid = auth.validate_jsessionid(jsessionid)
        print(f"  Session valid: {is_valid}")
        
        # Get current session
        current_session = auth.get_session()
        print(f"  Current session: {current_session[:20]}...")
        
    except Exception as e:
        print(f"✗ Authentication failed: {e}")


def example_5_making_api_calls():
    """Example 5: Making API calls after authentication"""
    print("\n=== Example 5: Making API Calls ===")
    
    try:
        # Authenticate
        url, jsessionid = setup_authentication(
            url="https://your-turbonomic-instance.com",
            username="your-username",
            password="your-password"
        )
        
        # Create session for API calls
        session = requests.Session()
        session.cookies.set('JSESSIONID', jsessionid)
        session.verify = False  # For self-signed certificates
        
        # Example: Get markets
        response = session.get(f"{url}/api/v3/markets")
        if response.status_code == 200:
            markets = response.json()
            print(f"✓ API call successful!")
            print(f"  Retrieved {len(markets)} markets")
        else:
            print(f"✗ API call failed: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error: {e}")


def example_6_realized_savings_report():
    """Example 6: Fetching realized savings data"""
    print("\n=== Example 6: Realized Savings Report ===")
    
    try:
        # Authenticate
        url, jsessionid = setup_authentication(
            url="https://your-turbonomic-instance.com",
            username="your-username",
            password="your-password"
        )
        
        # Create session
        session = requests.Session()
        session.cookies.set('JSESSIONID', jsessionid)
        session.verify = False
        
        # Fetch succeeded actions (realized savings)
        api_url = f"{url}/api/v3/actions"
        params = {
            'state': 'SUCCEEDED',
            'actionType': 'RESIZE',
            'startDate': '2024-01-01',  # Adjust as needed
            'endDate': '2024-12-31'
        }
        
        response = session.get(api_url, params=params)
        if response.status_code == 200:
            actions = response.json()
            print(f"✓ Retrieved {len(actions)} realized savings actions")
            
            # Calculate total savings
            total_savings = sum(
                action.get('stats', {}).get('costSavings', 0) 
                for action in actions
            )
            print(f"  Total realized savings: ${total_savings:,.2f}")
        else:
            print(f"✗ API call failed: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    """Run all examples"""
    print("=" * 60)
    print("Turbonomic Authentication Module - Usage Examples")
    print("=" * 60)
    
    # Uncomment the examples you want to run:
    
    # example_1_basic_authentication()
    # example_2_environment_variables()
    # example_3_interactive_prompt()
    # example_4_using_auth_class()
    # example_5_making_api_calls()
    # example_6_realized_savings_report()
    
    print("\n" + "=" * 60)
    print("Note: Update the examples with your actual Turbonomic URL")
    print("      and credentials before running.")
    print("=" * 60)


if __name__ == '__main__':
    main()

# Made with Bob
