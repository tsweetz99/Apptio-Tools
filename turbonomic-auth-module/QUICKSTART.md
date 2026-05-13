# Quick Start Guide - Turbonomic Authentication Module

## For Your Realized Savings Report Project

This authentication module provides everything you need to authenticate with Turbonomic API for your realized savings report.

## Installation

1. Extract the package:
```bash
unzip turbonomic-auth-module.zip
# or
tar -xzf turbonomic-auth-module.tar.gz
```

2. Install dependencies:
```bash
cd turbonomic-auth-module
pip install -r requirements.txt
```

## Simplest Integration

Add this to your realized savings script:

```python
from turbo_auth import setup_authentication
import requests

# Authenticate (will prompt for password)
url, jsessionid = setup_authentication(
    url="https://your-turbonomic-instance.com",
    username="your-username"
)

# Create session for API calls
session = requests.Session()
session.cookies.set('JSESSIONID', jsessionid)
session.verify = False

# Now make your API calls
response = session.get(f"{url}/api/v3/actions?state=SUCCEEDED")
data = response.json()
```

## Using Environment Variables (Recommended for Scripts)

Set these once:
```bash
export TURBO_URL="https://your-turbonomic-instance.com"
export TURBO_USERNAME="your-username"
export TURBO_PASSWORD="your-password"
```

Then in your script:
```python
from turbo_auth import setup_authentication

# Automatically uses environment variables
url, jsessionid = setup_authentication()
```

## Key Features for Your Project

### 1. Automatic Session Management
The module handles session validation and expiry tracking automatically.

### 2. Multiple Auth Methods
- Username/password
- Environment variables
- Interactive prompts
- Direct JSESSIONID (backward compatible)

### 3. Error Handling
Provides clear error messages for authentication failures.

### 4. Self-Signed Certificate Support
Works with Turbonomic instances using self-signed certificates.

## Example: Fetching Realized Savings

```python
#!/usr/bin/env python3
from turbo_auth import setup_authentication
import requests
import json

def get_realized_savings():
    # Authenticate
    url, jsessionid = setup_authentication()
    
    # Setup session
    session = requests.Session()
    session.cookies.set('JSESSIONID', jsessionid)
    session.verify = False
    
    # Fetch succeeded actions
    response = session.get(
        f"{url}/api/v3/actions",
        params={
            'state': 'SUCCEEDED',
            'actionType': 'RESIZE'
        }
    )
    
    if response.status_code == 200:
        actions = response.json()
        print(f"Found {len(actions)} realized savings actions")
        
        # Calculate total savings
        total = sum(a.get('stats', {}).get('costSavings', 0) for a in actions)
        print(f"Total savings: ${total:,.2f}")
        
        return actions
    else:
        raise Exception(f"API call failed: {response.status_code}")

if __name__ == '__main__':
    savings = get_realized_savings()
```

## Testing the Module

Test authentication before integrating:
```bash
python3 turbo_auth.py https://your-turbonomic-instance.com your-username
```

## Files Included

- **turbo_auth.py** - Main authentication module
- **requirements.txt** - Python dependencies
- **README.md** - Complete documentation
- **example_usage.py** - Multiple usage examples
- **QUICKSTART.md** - This file
- **LICENSE** - License information

## Common API Endpoints for Realized Savings

```python
# Get all succeeded actions
f"{url}/api/v3/actions?state=SUCCEEDED"

# Get actions by type
f"{url}/api/v3/actions?state=SUCCEEDED&actionType=RESIZE"

# Get actions with date range
f"{url}/api/v3/actions?state=SUCCEEDED&startDate=2024-01-01&endDate=2024-12-31"

# Get action details
f"{url}/api/v3/actions/{action_uuid}"
```

## Need Help?

1. Check **README.md** for complete documentation
2. Review **example_usage.py** for more examples
3. Test with the standalone script: `python3 turbo_auth.py <url> <username>`

## Tips

- Use environment variables for automated scripts
- The module automatically handles session expiry
- Sessions are valid for 30 minutes
- SSL warnings are disabled for self-signed certificates
- All API calls should use the same session object

## Integration Checklist

- [ ] Extract the package
- [ ] Install requirements: `pip install -r requirements.txt`
- [ ] Test authentication: `python3 turbo_auth.py <url> <username>`
- [ ] Import in your script: `from turbo_auth import setup_authentication`
- [ ] Set up environment variables (optional but recommended)
- [ ] Update your API calls to use the authenticated session

Good luck with your realized savings report! 🚀