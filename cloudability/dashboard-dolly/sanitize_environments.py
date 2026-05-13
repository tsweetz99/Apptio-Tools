#!/usr/bin/env python3
"""
Sanitize environment configurations before packaging.
Removes API keys and credentials from config files.
"""

import os
import json
import shutil
from pathlib import Path

def sanitize_config(config_path):
    """Remove sensitive data from a config file."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Remove sensitive fields
        sensitive_fields = ['cldyKey', 'api_key', 'public_key', 'private_key']
        removed = []
        
        for field in sensitive_fields:
            if field in config:
                config[field] = ""
                removed.append(field)
        
        # Write back sanitized config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return True, removed
    except Exception as e:
        return False, str(e)

def sanitize_environments(env_dir='Environments'):
    """Sanitize all environment configurations."""
    print("="*60)
    print("Environment Configuration Sanitizer")
    print("="*60)
    print()
    
    if not os.path.exists(env_dir):
        print(f"✓ No {env_dir} directory found - nothing to sanitize")
        return True
    
    sanitized_count = 0
    error_count = 0
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(env_dir):
        for file in files:
            if file.endswith('.json') and not file.endswith('.example'):
                config_path = os.path.join(root, file)
                rel_path = os.path.relpath(config_path, env_dir)
                
                print(f"Processing: {rel_path}")
                success, result = sanitize_config(config_path)
                
                if success:
                    if result:
                        print(f"  ✓ Removed: {', '.join(result)}")
                        sanitized_count += 1
                    else:
                        print(f"  ✓ No sensitive data found")
                else:
                    print(f"  ✗ Error: {result}")
                    error_count += 1
    
    print()
    print("="*60)
    print(f"Sanitized {sanitized_count} file(s)")
    if error_count > 0:
        print(f"⚠️  {error_count} error(s) occurred")
    else:
        print("✅ All configurations sanitized successfully")
    print("="*60)
    
    return error_count == 0

def create_example_configs(env_dir='Environments'):
    """Create example configuration files."""
    print()
    print("Creating example configurations...")
    
    # Template config
    template_dir = os.path.join(env_dir, 'template')
    os.makedirs(template_dir, exist_ok=True)
    
    example_config = {
        "cldyKey": "your-api-key-here",
        "region": "",
        "notes": "Leave region empty for US, or use 'eu', 'au', 'usgov'"
    }
    
    example_path = os.path.join(template_dir, 'config.json.example')
    with open(example_path, 'w') as f:
        json.dump(example_config, f, indent=2)
    
    print(f"✓ Created: {example_path}")
    
    # Create README
    readme_path = os.path.join(env_dir, 'README.txt')
    readme_content = """Dashboard Dolly - Environment Configuration

To add your own environment:

1. Create a new folder in this directory (e.g., "production")
2. Create a config.json file inside with this format:

{
  "cldyKey": "your-cloudability-api-key",
  "region": ""
}

Region options:
  - "" (empty) = US
  - "eu" = Europe
  - "au" = Australia
  - "usgov" = US Government

3. Restart Dashboard Dolly
4. Your environment will appear in the dropdown

OR simply use the "Connect with Key" option in the GUI to enter
your API key directly without creating a config file.

For more information, see END_USER_GUIDE.md
"""
    
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"✓ Created: {readme_path}")
    print()

def main():
    """Main entry point."""
    print()
    
    # Sanitize existing configs
    success = sanitize_environments()
    
    if success:
        # Create example configs
        create_example_configs()
        
        print()
        print("✅ Ready for packaging!")
        print()
        print("Next steps:")
        print("  1. Review the Environments folder")
        print("  2. Run: python3 build_executable.py")
        print("  3. Test the executable")
        print("  4. Distribute to users")
        print()
    else:
        print()
        print("⚠️  Please fix errors before packaging")
        print()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

# Made with Bob
