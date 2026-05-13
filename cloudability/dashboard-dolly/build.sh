#!/bin/bash
# Quick build script for Dashboard Dolly executable

echo "=================================="
echo "Dashboard Dolly - Build Script"
echo "=================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "⚠️  PyInstaller not found"
    read -p "Install PyInstaller? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing PyInstaller..."
        pip3 install pyinstaller
    else
        echo "❌ PyInstaller is required to build executables"
        exit 1
    fi
fi

echo "✓ PyInstaller found"
echo ""

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist *.spec
echo "✓ Cleaned"
echo ""

# Build
echo "Building executable..."
echo ""

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - use onedir mode (onefile doesn't work well with .app bundles)
    pyinstaller \
        --name=DashboardDolly \
        --windowed \
        --onedir \
        --add-data=Environments:Environments \
        --osx-bundle-identifier=com.ibm.dashboarddolly \
        dashboard_dolly_gui.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "=================================="
        echo "✅ Build successful!"
        echo "=================================="
        echo ""
        echo "Executable: dist/DashboardDolly.app"
        echo ""
        echo "To run:"
        echo "  open dist/DashboardDolly.app"
        echo ""
        echo "To distribute:"
        echo "  1. Test the app first"
        echo "  2. Zip it: cd dist && zip -r DashboardDolly.zip DashboardDolly.app"
        echo "  3. Share DashboardDolly.zip with users"
        echo ""
        echo "Note: The .app is a folder bundle, not a single file."
        echo ""
    else
        echo "❌ Build failed"
        exit 1
    fi
else
    # Linux - use onedir for consistency
    pyinstaller \
        --name=DashboardDolly \
        --windowed \
        --onedir \
        --add-data=Environments:Environments \
        dashboard_dolly_gui.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "=================================="
        echo "✅ Build successful!"
        echo "=================================="
        echo ""
        echo "Executable: dist/DashboardDolly/DashboardDolly"
        echo ""
        echo "To run:"
        echo "  ./dist/DashboardDolly/DashboardDolly"
        echo ""
        echo "To distribute:"
        echo "  Zip the entire dist/DashboardDolly folder"
        echo ""
    else
        echo "❌ Build failed"
        exit 1
    fi
fi

# Made with Bob
