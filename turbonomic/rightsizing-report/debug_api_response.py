#!/usr/bin/env python3
"""
Debug script to inspect Turbonomic API response structure.
This helps understand the actual data format to fix the report generator.
"""

import requests
import json
import argparse


def fetch_and_inspect_actions(turbo_url: str, jsessionid: str, limit: int = 5):
    """Fetch a few actions and print their structure."""
    
    url = f"{turbo_url}/api/v3/markets/Market/actions"
    
    session = requests.Session()
    session.cookies.set('JSESSIONID', jsessionid)
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    payload = {
        "actionStateList": [
            "READY",
            "QUEUED",
            "IN_PROGRESS",
            "ACCEPTED"
        ],
        "actionTypeList": [
            "RESIZE",
            "SCALE"
        ],
        "relatedEntityTypes": [
            "VirtualMachine"
        ],
        "environmentType": "CLOUD",
        "detailLevel": "EXECUTION"
    }
    
    params = {
        "ascending": "false",
        "cursor": "0",
        "disable_hateoas": "true",
        "forceExpansionOfAggregatedEntities": "true",
        "order_by": "savings",
        "limit": str(limit)
    }
    
    print(f"Fetching {limit} actions from Turbonomic...")
    print(f"URL: {url}\n")
    
    try:
        response = session.post(url, json=payload, params=params)
        response.raise_for_status()
        
        data = response.json()
        actions = data if isinstance(data, list) else []
        
        print(f"Retrieved {len(actions)} actions\n")
        print("="*100)
        
        # Inspect first action in detail
        if actions:
            print("FIRST ACTION STRUCTURE:")
            print("="*100)
            print(json.dumps(actions[0], indent=2))
            print("\n" + "="*100)
            
            # Print key paths
            action = actions[0]
            print("\nKEY DATA PATHS:")
            print("="*100)
            
            print(f"\nAction Type: {action.get('actionType')}")
            print(f"Action State: {action.get('actionState')}")
            print(f"Details: {action.get('details')}")
            
            target = action.get('target', {})
            print(f"\nTarget Display Name: {target.get('displayName')}")
            print(f"Target UUID: {target.get('uuid')}")
            print(f"Target Class: {target.get('className')}")
            
            print(f"\nTarget Keys Available: {list(target.keys())}")
            
            # Check for tags
            if 'tags' in target:
                print(f"\nTags: {target.get('tags')}")
            
            # Check for aspects
            if 'aspects' in target:
                print(f"\nAspects Keys: {list(target.get('aspects', {}).keys())}")
            
            # Check for current/new entity
            if 'currentEntity' in action:
                print(f"\nCurrent Entity Keys: {list(action.get('currentEntity', {}).keys())}")
            if 'newEntity' in action:
                print(f"\nNew Entity Keys: {list(action.get('newEntity', {}).keys())}")
            
            # Check for stats
            if 'stats' in action:
                print(f"\nStats: {action.get('stats')}")
            
            # Check for risk
            if 'risk' in action:
                risk = action.get('risk', {})
                print(f"\nRisk Severity: {risk.get('severity')}")
                print(f"Risk Category: {risk.get('category')}")
                print(f"Risk Sub-Category: {risk.get('subCategory')}")
                print(f"Risk Description: {risk.get('description')}")
            
            print("\n" + "="*100)
            
            # Save full response to file
            with open('api_response_sample.json', 'w') as f:
                json.dump(actions, f, indent=2)
            print("\nFull response saved to: api_response_sample.json")
            
        else:
            print("No actions returned!")
        
        return actions
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response text: {e.response.text}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description='Debug Turbonomic API response structure')
    parser.add_argument('--url', required=True, help='Turbonomic instance URL')
    parser.add_argument('--jsessionid', required=True, help='JSESSIONID from login')
    parser.add_argument('--limit', type=int, default=5, help='Number of actions to fetch (default: 5)')
    
    args = parser.parse_args()
    
    fetch_and_inspect_actions(args.url, args.jsessionid, args.limit)


if __name__ == '__main__':
    main()

# Made with Bob
