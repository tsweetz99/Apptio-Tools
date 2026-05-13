# Dashboard Dolly - Executable Build Guide

This guide explains how to create standalone executables for Dashboard Dolly that end users can run without installing Python.

## Overview

We use **PyInstaller** to package the Python application into standalone executables for:
- **macOS**: `.app` bundle
- **Windows**: `.exe` executable

## Prerequisites

### For Building on macOS
- Python 3.8 or higher
- pip (Python package manager)
- macOS 10.13 or higher

### For Building on Windows
- Python 3.8 or higher
- pip (Python package manager)
- Windows 10 or higher

## Quick Start

### Option 1: Automated Build (Recommended)

1. Navigate to the dashboard-dolly directory:
   ```bash
   cd cloudability/dashboard-dolly
   ```

2. Run the build script:
   ```bash
   python3 build_executable.py
   ```

3. The script will:
   - Check for PyInstaller (install if needed)
   - Clean previous builds
   - Create the executable
   - Show you where to find it

### Option 2: Manual Build

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Navigate to the dashboard-dolly directory:
   ```bash
   cd cloudability/dashboard-dolly
   ```

3. Run PyInstaller:

   **For macOS:**
   ```bash
   pyinstaller --name=DashboardDolly \
               --windowed \
               --onefile \
               --add-data=Environments:Environments \
               --osx-bundle-identifier=com.ibm.dashboarddolly \
               dashboard_dolly_gui.py
   ```

   **For Windows:**
   ```cmd
   pyinstaller --name=DashboardDolly ^
               --windowed ^
               --onefile ^
               --add-data=Environments;Environments ^
               dashboard_dolly_gui.py
   ```

## Output Locations

After building, you'll find:

### macOS
- **Executable**: `dist/DashboardDolly.app`
- **To run**: Double-click the app or run `open dist/DashboardDolly.app`
- **To distribute**: Zip the `.app` file and share

### Windows
- **Executable**: `dist\DashboardDolly.exe`
- **To run**: Double-click the `.exe` file
- **To distribute**: Share the `.exe` file directly

## Distribution

### For End Users

1. **macOS Users**:
   - Download the `DashboardDolly.app` (or `.zip` containing it)
   - Move to Applications folder (optional)
   - Double-click to run
   - First time: Right-click → Open (to bypass Gatekeeper)

2. **Windows Users**:
   - Download `DashboardDolly.exe`
   - Save to desired location
   - Double-click to run
   - First time: May need to click "More info" → "Run anyway" (Windows Defender)

### Configuration Files

The executable includes the `Environments` folder. Users can:
1. Run the app once to create the config directory
2. Click "Open Config Folder" in the app
3. Add their environment JSON files to the folder
4. Restart the app to see new environments

## File Size

Typical executable sizes:
- **macOS**: ~15-25 MB
- **Windows**: ~10-20 MB

The size includes Python runtime and all dependencies.

## Troubleshooting

### "PyInstaller not found"
```bash
pip install pyinstaller
```

### "Module not found" errors during build
Install missing dependencies:
```bash
pip install -r requirements.txt
```

### macOS: "App is damaged and can't be opened"
This is a Gatekeeper issue. Users should:
1. Right-click the app
2. Select "Open"
3. Click "Open" in the dialog

Or remove the quarantine attribute:
```bash
xattr -cr DashboardDolly.app
```

### Windows: "Windows protected your PC"
This is Windows Defender SmartScreen. Users should:
1. Click "More info"
2. Click "Run anyway"

### Executable is too large
Use `--onefile` option (already included) to create a single file instead of a folder.

## Advanced Options

### Adding an Icon

1. Create/obtain an icon file:
   - macOS: `.icns` file
   - Windows: `.ico` file

2. Add to PyInstaller command:
   ```bash
   --icon=path/to/icon.icns  # macOS
   --icon=path/to/icon.ico   # Windows
   ```

### Code Signing (Recommended for Distribution)

**macOS:**
```bash
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" DashboardDolly.app
```

**Windows:**
Use a code signing certificate with `signtool.exe`

### Creating an Installer

**macOS:**
- Use `create-dmg` or `Packages.app` to create a `.dmg` installer

**Windows:**
- Use Inno Setup or NSIS to create an installer

## Build Script Customization

Edit `build_executable.py` to customize:
- Application name
- Icon path
- Bundle identifier
- Additional data files
- Build options

## Testing the Executable

Before distributing:

1. **Test on clean system** (no Python installed)
2. **Test all features**:
   - Environment connections
   - Dashboard loading
   - File operations
   - API key authentication
3. **Test on different OS versions**
4. **Check file permissions**

## Continuous Integration

For automated builds, consider:
- GitHub Actions (cross-platform builds)
- GitLab CI/CD
- Jenkins

Example GitHub Actions workflow available in `.github/workflows/build.yml` (create if needed)

## Support

For issues:
1. Check PyInstaller documentation: https://pyinstaller.org
2. Verify all dependencies are in `requirements.txt`
3. Test with `python dashboard_dolly_gui.py` first
4. Check PyInstaller logs in `build/` directory

## Version Management

When releasing new versions:
1. Update version in `dashboard_dolly_gui.py`
2. Rebuild executable
3. Tag release in git
4. Update release notes
5. Distribute new executable

## Security Notes

- Executables contain your source code (obfuscated but not encrypted)
- Don't include API keys or credentials in the build
- Users should manage their own credentials via config files
- Consider code signing for production distribution