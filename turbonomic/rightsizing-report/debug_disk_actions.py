#!/usr/bin/env python3
"""Debug script to inspect disk/storage actions from Turbonomic API."""

import requests
import json
import sys

def debug_storage_actions(turbo_url, jsessionid):
    """Fetch and display storage action details for debugging."""
    url = f"{turbo_url.rstrip('/')}/api/v3/markets/Market/actions"
    
    session = requests.Session()
    session.cookies.set('JSESSIONID', jsessionid)
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    params = {
        'actionStateList': ['READY', 'ACCEPTED', 'QUEUED', 'IN_PROGRESS'],
        'limit': 100  # Get more to find volume actions
    }
    
    print(f"Fetching storage actions from {url}...")
    print(f"Parameters: {json.dumps(params, indent=2)}\n")
    
    try:
        response = session.post(url, json=params)
        response.raise_for_status()
        data = response.json()
        
        # Handle both list and dict responses
        if isinstance(data, list):
            actions = data[:10]
        else:
            actions = data.get('result', [])[:10]
        
        print(f"Retrieved {len(actions)} actions\n")
        
        # Filter for volume actions
        volume_actions = []
        for action in actions:
            target = action.get('target', {})
            target_class = target.get('className', '')
            if 'volume' in target_class.lower() or 'storage' in target_class.lower():
                volume_actions.append(action)
        
        print(f"Found {len(volume_actions)} volume/storage actions out of {len(actions)} total\n")
        print("="*80)
        
        for i, action in enumerate(volume_actions[:10], 1):
            print(f"\nACTION {i}:")
            print(f"  UUID: {action.get('uuid', 'N/A')}")
            print(f"  Action Type: {action.get('actionType', 'N/A')}")
            print(f"  Action State: {action.get('actionState', 'N/A')}")
            
            target = action.get('target', {})
            print(f"\n  Target:")
            print(f"    Display Name: {target.get('displayName', 'N/A')}")
            print(f"    Class Name: {target.get('className', 'N/A')}")
            print(f"    UUID: {target.get('uuid', 'N/A')}")
            
            current_entity = action.get('currentEntity', {})
            new_entity = action.get('newEntity', {})
            
            print(f"\n  Current Entity:")
            print(f"    Display Name: {current_entity.get('displayName', 'N/A')}")
            print(f"    Class Name: {current_entity.get('className', 'N/A')}")
            
            print(f"\n  New Entity:")
            print(f"    Display Name: {new_entity.get('displayName', 'N/A')}")
            print(f"    Class Name: {new_entity.get('className', 'N/A')}")
            
            print(f"\n  Details: {action.get('details', 'N/A')[:100]}...")
            
            # Check for providers (attached VM)
            providers = target.get('providers', [])
            if providers:
                print(f"\n  Providers (Attached VMs):")
                for provider in providers[:3]:
                    if isinstance(provider, dict):
                        print(f"    - {provider.get('displayName', 'N/A')}")
            
            print("\n" + "-"*80)
        
        # Save full response for detailed inspection
        output_file = "disk_actions_debug.json"
        with open(output_file, 'w') as f:
            json.dump(actions, f, indent=2)
        print(f"\n✓ Full response saved to: {output_file}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 debug_disk_actions.py <TURBO_URL> <JSESSIONID>")
        print("Example: python3 debug_disk_actions.py https://turbo.example.com node01abc123")
        sys.exit(1)
    
    turbo_url = sys.argv[1]
    jsessionid = sys.argv[2]
    
    debug_storage_actions(turbo_url, jsessionid)

# Made with Bob
