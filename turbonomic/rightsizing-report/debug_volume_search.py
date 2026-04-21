#!/usr/bin/env python3
"""Debug script to search for volume entities and their actions."""

import requests
import json
import sys

def search_volumes(turbo_url, jsessionid):
    """Search for Volume entities and their pending actions."""
    session = requests.Session()
    session.cookies.set('JSESSIONID', jsessionid)
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    # Try searching for Volume entities
    search_url = f"{turbo_url.rstrip('/')}/api/v3/search"
    
    search_params = {
        "className": "Volume",
        "environmentType": "CLOUD",
        "limit": 10
    }
    
    print(f"Searching for Volume entities at {search_url}...")
    print(f"Parameters: {json.dumps(search_params, indent=2)}\n")
    
    try:
        response = session.post(search_url, json=search_params)
        response.raise_for_status()
        volumes = response.json()
        
        print(f"Found {len(volumes)} volumes\n")
        print("="*80)
        
        if volumes:
            # Get actions for first volume
            volume = volumes[0]
            volume_uuid = volume.get('uuid')
            print(f"\nFirst Volume:")
            print(f"  Display Name: {volume.get('displayName', 'N/A')}")
            print(f"  UUID: {volume_uuid}")
            print(f"  Class Name: {volume.get('className', 'N/A')}")
            
            # Try to get actions for this specific volume
            actions_url = f"{turbo_url.rstrip('/')}/api/v3/entities/{volume_uuid}/actions"
            print(f"\nFetching actions for this volume from {actions_url}...")
            
            actions_response = session.get(actions_url)
            actions_response.raise_for_status()
            actions = actions_response.json()
            
            print(f"Found {len(actions)} actions for this volume\n")
            
            for i, action in enumerate(actions[:5], 1):
                print(f"\nACTION {i}:")
                print(f"  UUID: {action.get('uuid', 'N/A')}")
                print(f"  Action Type: {action.get('actionType', 'N/A')}")
                print(f"  Action State: {action.get('actionState', 'N/A')}")
                print(f"  Details: {action.get('details', 'N/A')[:100]}...")
                
                current = action.get('currentEntity', {})
                new = action.get('newEntity', {})
                print(f"  Current: {current.get('displayName', 'N/A')}")
                print(f"  New: {new.get('displayName', 'N/A')}")
            
            # Save full response
            with open('volume_actions_debug.json', 'w') as f:
                json.dump({
                    'volumes': volumes[:5],
                    'sample_actions': actions[:10]
                }, f, indent=2)
            print(f"\n✓ Full response saved to: volume_actions_debug.json")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 debug_volume_search.py <TURBO_URL> <JSESSIONID>")
        sys.exit(1)
    
    turbo_url = sys.argv[1]
    jsessionid = sys.argv[2]
    
    search_volumes(turbo_url, jsessionid)

# Made with Bob
