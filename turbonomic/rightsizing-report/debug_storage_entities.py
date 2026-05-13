#!/usr/bin/env python3
"""
Debug script to discover storage entities and actions in Turbonomic.
This helps identify the correct entity types and action types for disk optimization.
"""

import requests
import json
import sys
import argparse
from collections import Counter


def debug_storage_discovery(turbo_url: str, jsessionid: str):
    """Discover storage entities and actions."""
    
    session = requests.Session()
    session.cookies.set('JSESSIONID', jsessionid)
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    print("="*80)
    print("TURBONOMIC STORAGE DISCOVERY DEBUG")
    print("="*80)
    
    # Step 1: Try to get storage entities directly
    print("\n1. Searching for Storage entities...")
    print("-"*80)
    
    search_url = f"{turbo_url.rstrip('/')}/api/v3/search"
    
    storage_types = [
        "Storage",
        "Volume", 
        "VirtualMachineVolume",
        "VirtualDisk",
        "Disk",
        "StorageTier"
    ]
    
    for entity_type in storage_types:
        try:
            payload = {
                "className": entity_type,
                "environmentType": "CLOUD"
            }
            
            response = session.post(search_url, json=payload)
            if response.status_code == 200:
                entities = response.json()
                count = len(entities) if isinstance(entities, list) else 0
                print(f"  ✓ {entity_type}: Found {count} entities")
                
                if count > 0 and count <= 3:
                    print(f"    Sample: {json.dumps(entities[0], indent=6)[:200]}...")
            else:
                print(f"  ✗ {entity_type}: {response.status_code}")
        except Exception as e:
            print(f"  ✗ {entity_type}: Error - {e}")
    
    # Step 2: Get all actions and analyze
    print("\n2. Analyzing all available actions...")
    print("-"*80)
    
    actions_url = f"{turbo_url.rstrip('/')}/api/v3/markets/Market/actions"
    
    payload = {
        "actionStateList": ["READY", "ACCEPTED", "QUEUED", "IN_PROGRESS"],
        "environmentType": "CLOUD",
        "detailLevel": "EXECUTION"
    }
    
    params = {
        "ascending": "false",
        "cursor": "0",
        "disable_hateoas": "true",
        "limit": "500"
    }
    
    try:
        response = session.post(actions_url, json=payload, params=params)
        response.raise_for_status()
        
        data = response.json()
        actions = data if isinstance(data, list) else []
        
        print(f"  Retrieved {len(actions)} total actions")
        
        # Analyze target class names
        target_classes = Counter()
        action_types = Counter()
        storage_related = []
        
        for action in actions:
            target = action.get('target', {})
            target_class = target.get('className', 'Unknown')
            action_type = action.get('actionType', 'Unknown')
            
            target_classes[target_class] += 1
            action_types[action_type] += 1
            
            # Check if storage-related
            if any(keyword in target_class.lower() for keyword in ['storage', 'volume', 'disk']):
                storage_related.append(action)
        
        print(f"\n  Target Class Distribution:")
        for class_name, count in target_classes.most_common(10):
            print(f"    - {class_name}: {count}")
        
        print(f"\n  Action Type Distribution:")
        for action_type, count in action_types.most_common(10):
            print(f"    - {action_type}: {count}")
        
        print(f"\n  Storage-related actions found: {len(storage_related)}")
        
        if storage_related:
            print(f"\n  Sample storage action:")
            print(json.dumps(storage_related[0], indent=4)[:1000])
            print("  ...")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    # Step 3: Try specific storage action query
    print("\n3. Querying specifically for storage actions...")
    print("-"*80)
    
    storage_payload = {
        "actionStateList": ["READY", "ACCEPTED", "QUEUED", "IN_PROGRESS"],
        "actionTypeList": ["RESIZE", "SCALE", "RECONFIGURE"],
        "relatedEntityTypes": ["Storage", "Volume", "VirtualMachineVolume"],
        "environmentType": "CLOUD",
        "detailLevel": "EXECUTION"
    }
    
    try:
        response = session.post(actions_url, json=storage_payload, params=params)
        response.raise_for_status()
        
        data = response.json()
        actions = data if isinstance(data, list) else []
        
        print(f"  Retrieved {len(actions)} storage-specific actions")
        
        if actions:
            print(f"\n  Sample action:")
            print(json.dumps(actions[0], indent=4)[:1000])
            print("  ...")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    # Step 4: Check for disk tier information in VM actions
    print("\n4. Checking VM actions for disk tier information...")
    print("-"*80)
    
    vm_payload = {
        "actionStateList": ["READY", "ACCEPTED", "QUEUED", "IN_PROGRESS"],
        "relatedEntityTypes": ["VirtualMachine"],
        "environmentType": "CLOUD",
        "detailLevel": "EXECUTION"
    }
    
    try:
        response = session.post(actions_url, json=vm_payload, params=params)
        response.raise_for_status()
        
        data = response.json()
        actions = data if isinstance(data, list) else []
        
        print(f"  Retrieved {len(actions)} VM actions")
        
        # Look for disk-related information in VM actions
        disk_mentions = 0
        for action in actions[:100]:  # Check first 100
            details = action.get('details', '').lower()
            if any(keyword in details for keyword in ['disk', 'storage', 'tier', 'ssd', 'hdd']):
                disk_mentions += 1
                if disk_mentions == 1:
                    print(f"\n  Found disk mention in VM action:")
                    print(f"    Details: {action.get('details', 'N/A')}")
                    print(f"    Action Type: {action.get('actionType', 'N/A')}")
        
        print(f"\n  VM actions mentioning disks: {disk_mentions}")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\n" + "="*80)
    print("DEBUG COMPLETE")
    print("="*80)


def main():
    parser = argparse.ArgumentParser(
        description='Debug storage entity and action discovery in Turbonomic'
    )
    parser.add_argument('--url', required=True, help='Turbonomic instance URL')
    parser.add_argument('--jsessionid', required=True, help='JSESSIONID from login')
    
    args = parser.parse_args()
    
    debug_storage_discovery(args.url, args.jsessionid)


if __name__ == '__main__':
    main()

# Made with Bob
