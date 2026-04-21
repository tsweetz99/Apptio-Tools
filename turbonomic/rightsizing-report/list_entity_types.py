#!/usr/bin/env python3
"""List all entity types available in Turbonomic to find the correct one for Azure disks."""

import requests
import json
import sys

def list_entity_types(turbo_url, jsessionid):
    """List all entity types and search for disk/storage/volume related ones."""
    session = requests.Session()
    session.cookies.set('JSESSIONID', jsessionid)
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    # Get supply chain - this shows all entity types
    url = f"{turbo_url.rstrip('/')}/api/v3/supplychains"
    
    print(f"Fetching supply chain from {url}...")
    
    try:
        response = session.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Extract unique entity types
        entity_types = set()
        
        def extract_types(obj):
            if isinstance(obj, dict):
                if 'className' in obj:
                    entity_types.add(obj['className'])
                if 'templateClass' in obj:
                    entity_types.add(obj['templateClass'])
                for value in obj.values():
                    extract_types(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_types(item)
        
        extract_types(data)
        
        print(f"\nFound {len(entity_types)} entity types\n")
        print("="*80)
        print("All Entity Types:")
        print("="*80)
        
        for entity_type in sorted(entity_types):
            print(f"  - {entity_type}")
        
        print("\n" + "="*80)
        print("Storage/Disk/Volume Related Types:")
        print("="*80)
        
        storage_related = [t for t in entity_types if any(keyword in t.lower() for keyword in ['storage', 'disk', 'volume'])]
        for entity_type in sorted(storage_related):
            print(f"  - {entity_type}")
        
        # Save to file
        with open('entity_types.json', 'w') as f:
            json.dump({
                'all_types': sorted(list(entity_types)),
                'storage_related': sorted(storage_related)
            }, f, indent=2)
        
        print(f"\n✓ Full list saved to: entity_types.json")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 list_entity_types.py <TURBO_URL> <JSESSIONID>")
        sys.exit(1)
    
    turbo_url = sys.argv[1]
    jsessionid = sys.argv[2]
    
    list_entity_types(turbo_url, jsessionid)

# Made with Bob
