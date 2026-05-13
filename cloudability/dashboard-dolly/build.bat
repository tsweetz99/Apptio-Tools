@echo off
REM Quick build script for Dashboard Dolly executable (Windows)

echo ==================================
echo Dashboard Dolly - Build Script
echo ==================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Python found
python --version
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found
    set /p install="Install PyInstaller? (y/n): "
    if /i "%install%"=="y" (
        echo Installing PyInstaller...
        pip install pyinstaller
    ) else (
        echo PyInstaller is required to build executables
        pause
        exit /b 1
    )
)

echo PyInstaller found
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist DashboardDolly.spec del DashboardDolly.spec
echo Cleaned
echo.

REM Build
echo Building executable...
echo.

pyinstaller ^
    --name=DashboardDolly ^
    --windowed ^
    --onedir ^
    --add-data=Environments;Environments ^
    dashboard_dolly_gui.py

if errorlevel 1 (
    echo.
    echo ==================================
    echo Build failed
    echo ==================================
    pause
    exit /b 1
)

echo.
echo ==================================
echo Build successful!
echo ==================================
echo.
echo Executable: dist\DashboardDolly\DashboardDolly.exe
echo.
echo To run:
echo   dist\DashboardDolly\DashboardDolly.exe
echo.
echo To distribute:
echo   1. Test the executable first
echo   2. Zip the entire dist\DashboardDolly folder
echo   3. Share the zip file with users
echo   4. Include END_USER_GUIDE.md for instructions
echo.
echo Note: The executable is in a folder, not a single file.
echo.
pause

@REM Made with Bob
