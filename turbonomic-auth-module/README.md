# Turbonomic Authentication Module

A standalone Python module for authenticating with Turbonomic API. This module provides flexible authentication methods including username/password credentials, JSESSIONID tokens, and environment variables.

## Features

- **Multiple Authentication Methods**:
  - Username/password authentication
  - Direct JSESSIONID token
  - Environment variables
  - Interactive password prompt
  
- **Session Management**:
  - Automatic session validation
  - Session expiry tracking
  - Session refresh handling

- **Security**:
  - Support for self-signed certificates
  - Secure password handling with getpass
  - No credential storage in code

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Method 1: Username/Password Authentication

```python
from turbo_auth import setup_authentication

# Authenticate with username and password
url, jsessionid = setup_authentication(
    url="https://your-turbonomic-instance.com",
    username="your-username",
    password="your-password"
)

print(f"Authenticated! JSESSIONID: {jsessionid}")
```

### Method 2: Interactive Password Prompt

```python
from turbo_auth import setup_authentication

# Will prompt for password
url, jsessionid = setup_authentication(
    url="https://your-turbonomic-instance.com",
    username="your-username"
)
```

### Method 3: Environment Variables

Set environment variables:
```bash
export TURBO_URL="https://your-turbonomic-instance.com"
export TURBO_USERNAME="your-username"
export TURBO_PASSWORD="your-password"
```

Then in your code:
```python
from turbo_auth import setup_authentication

# Will use environment variables
url, jsessionid = setup_authentication()
```

### Method 4: Direct JSESSIONID (Backward Compatibility)

```python
from turbo_auth import setup_authentication

url, jsessionid = setup_authentication(
    url="https://your-turbonomic-instance.com",
    jsessionid="your-existing-jsessionid"
)
```

## Using the TurbonomicAuth Class

For more control, use the `TurbonomicAuth` class directly:

```python
from turbo_auth import TurbonomicAuth

# Initialize
auth = TurbonomicAuth("https://your-turbonomic-instance.com")

# Authenticate
jsessionid = auth.authenticate_with_credentials("username", "password")

# Validate existing session
is_valid = auth.validate_jsessionid(jsessionid)

# Get current session (raises exception if expired)
current_session = auth.get_session()
```

## Making API Calls

Once authenticated, use the JSESSIONID in your API requests:

```python
import requests
from turbo_auth import setup_authentication

# Authenticate
url, jsessionid = setup_authentication(
    url="https://your-turbonomic-instance.com",
    username="your-username"
)

# Make API call
session = requests.Session()
session.cookies.set('JSESSIONID', jsessionid)
session.verify = False  # For self-signed certificates

response = session.get(f"{url}/api/v3/markets")
if response.status_code == 200:
    data = response.json()
    print("API call successful!")
```

## Environment Variables

The module supports the following environment variables:

- `TURBO_URL`: Turbonomic instance URL
- `TURBO_USERNAME`: Username for authentication
- `TURBO_PASSWORD`: Password for authentication
- `TURBO_JSESSIONID`: Existing JSESSIONID token

## Authentication Priority

The module tries authentication methods in this order:

1. Provided JSESSIONID parameter
2. Provided username/password parameters
3. Environment variable JSESSIONID
4. Environment variable username/password
5. Interactive password prompt (if username provided)

## Testing the Module

Test authentication from command line:

```bash
python3 turbo_auth.py https://your-turbonomic-instance.com your-username
```

This will prompt for password and test the authentication.

## Error Handling

The module provides detailed error messages for common issues:

- Invalid credentials
- Connection errors
- Expired sessions
- Missing authentication parameters

Example:
```python
try:
    url, jsessionid = setup_authentication(
        url="https://your-turbonomic-instance.com",
        username="your-username",
        password="wrong-password"
    )
except Exception as e:
    print(f"Authentication failed: {e}")
```

## Integration Example

Here's a complete example for a realized savings report:

```python
#!/usr/bin/env python3
import requests
from turbo_auth import setup_authentication

def get_realized_savings(url, jsessionid):
    """Fetch realized savings data from Turbonomic."""
    session = requests.Session()
    session.cookies.set('JSESSIONID', jsessionid)
    session.verify = False
    
    # Example API endpoint (adjust based on your needs)
    api_url = f"{url}/api/v3/actions"
    params = {
        'state': 'SUCCEEDED',
        'actionType': 'RESIZE'
    }
    
    response = session.get(api_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API call failed: {response.status_code}")

def main():
    # Authenticate
    url, jsessionid = setup_authentication(
        url="https://your-turbonomic-instance.com",
        username="your-username"
    )
    
    # Fetch data
    savings_data = get_realized_savings(url, jsessionid)
    
    # Process data
    print(f"Retrieved {len(savings_data)} realized savings actions")
    
if __name__ == '__main__':
    main()
```

## Requirements

- Python 3.6+
- requests >= 2.28.0
- urllib3 >= 1.26.0

## License

This module is part of the Apptio-Tools project. See LICENSE file for details.

## Support

For issues or questions, please refer to the main project documentation or contact the development team.

## Notes

- The module disables SSL warnings for self-signed certificates
- Sessions expire after 30 minutes of inactivity
- The module validates sessions before use to prevent expired session errors