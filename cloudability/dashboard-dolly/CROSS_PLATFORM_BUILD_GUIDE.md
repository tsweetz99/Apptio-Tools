# Cross-Platform Build Guide

## Important: Platform-Specific Builds

**PyInstaller creates executables for the platform it runs on:**
- Build on macOS → Creates `.app` for macOS
- Build on Windows → Creates `.exe` for Windows
- Build on Linux → Creates Linux executable

**You cannot cross-compile!** To create executables for multiple platforms, you need access to each platform.

## Building for macOS (on macOS)

```bash
cd cloudability/dashboard-dolly
python3 build_executable.py
# or
./build.sh
```

**Output:** `dist/DashboardDolly.app`

## Building for Windows (on Windows)

```cmd
cd cloudability\dashboard-dolly
python build_executable.py
REM or
build.bat
```

**Output:** `dist\DashboardDolly\DashboardDolly.exe`

## Building for Linux (on Linux)

```bash
cd cloudability/dashboard-dolly
python3 build_executable.py
# or
./build.sh
```

**Output:** `dist/DashboardDolly/DashboardDolly`

## Options for Multi-Platform Builds

### Option 1: Use Multiple Machines (Recommended)

**Pros:**
- Native builds are most reliable
- Full testing on target platform
- No additional tools needed

**Cons:**
- Requires access to each platform
- Manual process

**Steps:**
1. Copy source code to each platform
2. Run build script on each platform
3. Test on each platform
4. Collect all executables for distribution

### Option 2: Use Virtual Machines

**Tools:**
- VMware Workstation/Fusion
- VirtualBox
- Parallels (macOS)

**Steps:**
1. Set up VM for target platform
2. Install Python and dependencies
3. Copy source code to VM
4. Build in VM
5. Extract executable

### Option 3: Use Cloud Build Services

**GitHub Actions (Free for public repos):**

Create `.github/workflows/build.yml`:

```yaml
name: Build Executables

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd cloudability/dashboard-dolly
          pip install -r requirements.txt
          pip install pyinstaller
      - name: Build
        run: |
          cd cloudability/dashboard-dolly
          python build_executable.py
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: DashboardDolly-Windows
          path: cloudability/dashboard-dolly/dist/DashboardDolly/

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd cloudability/dashboard-dolly
          pip install -r requirements.txt
          pip install pyinstaller
      - name: Build
        run: |
          cd cloudability/dashboard-dolly
          python3 build_executable.py
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: DashboardDolly-macOS
          path: cloudability/dashboard-dolly/dist/DashboardDolly.app/
```

### Option 4: Docker (Advanced)

**Note:** Docker can build Linux executables on any platform, but macOS and Windows executables still need native builds.

## Current Situation

Since you're on macOS, you can:

1. **Build macOS version now:**
   ```bash
   cd cloudability/dashboard-dolly
   python3 build_executable.py
   ```

2. **For Windows version, choose one:**
   - **A. Use a Windows machine** (colleague, VM, etc.)
   - **B. Set up GitHub Actions** (automated, free)
   - **C. Use a Windows VM** (VirtualBox, Parallels, etc.)
   - **D. Provide Python source** and let Windows users run from source

## Recommended Approach

For internal distribution:

1. **Build macOS version** on your Mac
2. **Provide Python source** for Windows users with instructions:
   ```cmd
   cd cloudability\dashboard-dolly
   pip install -r requirements.txt
   python dashboard_dolly_gui.py
   ```

For external/customer distribution:

1. **Set up GitHub Actions** for automated builds
2. **Or** get access to a Windows machine for manual builds
3. **Test on both platforms** before distributing

## Quick Windows Build Instructions

If you have access to a Windows machine:

1. **Install Python 3.8+** from python.org
2. **Copy the entire `cloudability/dashboard-dolly` folder** to Windows
3. **Open Command Prompt** in that folder
4. **Run:**
   ```cmd
   pip install -r requirements.txt
   pip install pyinstaller
   python build_executable.py
   ```
5. **Find executable** in `dist\DashboardDolly\DashboardDolly.exe`

## Testing Checklist

Before distributing, test on target platform:

- [ ] Executable launches
- [ ] GUI displays correctly
- [ ] Can connect to environments
- [ ] Can load dashboards
- [ ] Can transfer dashboards
- [ ] Widgets appear in target
- [ ] No API keys embedded
- [ ] Config folder accessible

## Distribution Package Structure

```
DashboardDolly-v1.0/
├── macOS/
│   └── DashboardDolly.app (zipped)
├── Windows/
│   └── DashboardDolly/ (folder, zipped)
├── END_USER_GUIDE.md
├── SECURITY_PACKAGING_GUIDE.md
└── README.txt
```

## Troubleshooting

**"I don't have access to Windows"**
→ Use GitHub Actions or provide Python source

**"GitHub Actions failing"**
→ Check Python version compatibility
→ Ensure all dependencies in requirements.txt

**"Executable too large"**
→ Normal (15-25 MB), includes Python runtime
→ Use `--onedir` mode (already default)

**"Users can't run executable"**
→ macOS: Right-click → Open (first time)
→ Windows: Click "More info" → "Run anyway"

## Summary

- ✅ You can build macOS version now
- ❌ You cannot build Windows version on macOS
- ✅ Options: Windows machine, VM, GitHub Actions, or provide source
- ✅ All build scripts are ready for Windows when you have access

For most internal use cases, providing the Python source code with instructions is often the simplest solution!