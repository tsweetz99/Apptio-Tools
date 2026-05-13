# Quick Build Reference

## TL;DR - Build an Executable

```bash
# Navigate to directory
cd cloudability/dashboard-dolly

# Run build script (installs PyInstaller if needed)
python3 build_executable.py

# Find your executable:
# macOS: dist/DashboardDolly.app
# Windows: dist\DashboardDolly.exe
```

## One-Line Manual Build

**macOS:**
```bash
pyinstaller --name=DashboardDolly --windowed --onefile --add-data=Environments:Environments --osx-bundle-identifier=com.ibm.dashboarddolly dashboard_dolly_gui.py
```

**Windows:**
```cmd
pyinstaller --name=DashboardDolly --windowed --onefile --add-data=Environments;Environments dashboard_dolly_gui.py
```

## What You Need

- Python 3.8+
- PyInstaller: `pip install pyinstaller`
- All dependencies: `pip install -r requirements.txt`

## Output

- **Build files**: `build/` (can delete)
- **Executable**: `dist/DashboardDolly.app` or `dist/DashboardDolly.exe`
- **Spec file**: `DashboardDolly.spec` (can delete)

## Distribution Checklist

- [ ] Build executable
- [ ] Test on clean system (no Python)
- [ ] Test all features work
- [ ] Include END_USER_GUIDE.md
- [ ] Zip/package for distribution
- [ ] (Optional) Code sign for production

## File Sizes

- macOS: ~15-25 MB
- Windows: ~10-20 MB

## Common Issues

**"PyInstaller not found"**
```bash
pip install pyinstaller
```

**"Module not found"**
```bash
pip install -r requirements.txt
```

**macOS: "App is damaged"**
```bash
xattr -cr dist/DashboardDolly.app
```

## Full Documentation

See [`BUILD_EXECUTABLE_GUIDE.md`](BUILD_EXECUTABLE_GUIDE.md) for complete details.