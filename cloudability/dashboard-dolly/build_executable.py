#!/usr/bin/env python3
"""
Build script for creating Dashboard Dolly executables.
Creates standalone executables for Windows and macOS.
"""

import os
import sys
import platform
import subprocess
import shutil
import json

def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """Install PyInstaller."""
    print("Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def sanitize_environments():
    """Remove API keys from environment configs before packaging."""
    print("\n" + "="*60)
    print("Sanitizing environment configurations...")
    print("="*60)
    
    env_dir = "Environments"
    if not os.path.exists(env_dir):
        print("✓ No Environments directory - skipping sanitization")
        return True
    
    sanitized = 0
    for root, dirs, files in os.walk(env_dir):
        for file in files:
            if file.endswith('.json') and not file.endswith('.example'):
                config_path = os.path.join(root, file)
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    
                    # Check for sensitive data
                    sensitive_fields = ['cldyKey', 'api_key', 'public_key', 'private_key']
                    has_sensitive = any(config.get(field) for field in sensitive_fields)
                    
                    if has_sensitive:
                        # Remove sensitive data
                        for field in sensitive_fields:
                            if field in config:
                                config[field] = ""
                        
                        # Write back
                        with open(config_path, 'w') as f:
                            json.dump(config, f, indent=2)
                        
                        rel_path = os.path.relpath(config_path, env_dir)
                        print(f"✓ Sanitized: {rel_path}")
                        sanitized += 1
                        
                except Exception as e:
                    print(f"⚠️  Error processing {config_path}: {e}")
    
    if sanitized > 0:
        print(f"\n✓ Sanitized {sanitized} configuration file(s)")
        print("⚠️  IMPORTANT: You must rebuild to include these changes!")
    else:
        print("✓ No API keys found in configurations")
    
    print("="*60 + "\n")
    return True

def build_executable():
    """Build the executable."""
    system = platform.system()
    
    # Sanitize environments first
    if not sanitize_environments():
        print("❌ Sanitization failed. Please fix errors before building.")
        return False
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name=DashboardDolly",
        "--windowed",  # No console window
        "--onedir",    # Directory mode (required for macOS .app bundles)
        "--add-data=Environments:Environments",  # Include config folder
        "dashboard_dolly_gui.py"
    ]
    
    # Platform-specific adjustments
    if system == "Darwin":  # macOS
        print("Building for macOS...")
        cmd.append("--osx-bundle-identifier=com.ibm.dashboarddolly")
        # Note: --onefile doesn't work well with --windowed on macOS
    elif system == "Windows":
        print("Building for Windows...")
        # Windows-specific options can go here
    else:
        print(f"Building for {system}...")
    
    print(f"Running: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    
    print("\n" + "="*60)
    print("Build complete!")
    print("="*60)
    
    if system == "Darwin":
        print(f"\nExecutable location: dist/DashboardDolly.app")
        print("To run: open dist/DashboardDolly.app")
        print("\nNote: The .app bundle contains a folder structure.")
        print("To distribute: Zip the entire DashboardDolly.app folder")
    elif system == "Windows":
        print(f"\nExecutable location: dist\\DashboardDolly\\DashboardDolly.exe")
        print("To run: dist\\DashboardDolly\\DashboardDolly.exe")
        print("\nNote: Distribute the entire DashboardDolly folder")
    else:
        print(f"\nExecutable location: dist/DashboardDolly/DashboardDolly")
        print("To run: ./dist/DashboardDolly/DashboardDolly")
        print("\nNote: Distribute the entire DashboardDolly folder")
    
    print("\nNote: The Environments folder has been bundled with the executable.")
    print("Users can add their own environment configs to the Environments folder.")

def main():
    """Main build process."""
    print("\nDashboard Dolly Executable Builder")
    print("="*60)
    print("\n⚠️  SECURITY NOTE:")
    print("This script will automatically remove API keys from")
    print("environment configurations before packaging.")
    print("="*60)
    
    # Check for PyInstaller
    if not check_pyinstaller():
        print("PyInstaller not found.")
        response = input("Install PyInstaller? (y/n): ")
        if response.lower() == 'y':
            install_pyinstaller()
        else:
            print("PyInstaller is required to build executables.")
            sys.exit(1)
    
    # Clean previous builds
    if os.path.exists("build"):
        print("Cleaning build directory...")
        shutil.rmtree("build")
    if os.path.exists("dist"):
        print("Cleaning dist directory...")
        shutil.rmtree("dist")
    if os.path.exists("DashboardDolly.spec"):
        print("Cleaning spec file...")
        os.remove("DashboardDolly.spec")
    
    # Build
    build_executable()

if __name__ == "__main__":
    main()

# Made with Bob
