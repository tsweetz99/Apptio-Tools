# Dashboard Dolly - Distribution Package

This document explains how to package and distribute Dashboard Dolly to end users who don't have Python installed.

## What to Include in Distribution

### For End Users (Minimal Package)

**macOS Distribution:**
```
DashboardDolly-macOS-v1.0.zip
├── DashboardDolly.app          (The executable)
├── END_USER_GUIDE.md           (User instructions)
└── Environments/               (Sample config folder)
    └── template/
        └── config.json.example
```

**Windows Distribution:**
```
DashboardDolly-Windows-v1.0.zip
├── DashboardDolly.exe          (The executable)
├── END_USER_GUIDE.md           (User instructions)
└── Environments/               (Sample config folder)
    └── template/
        └── config.json.example
```

### For Developers (Full Package)

Include everything above plus:
- `BUILD_EXECUTABLE_GUIDE.md` - How to build from source
- `QUICK_BUILD_REFERENCE.md` - Quick build commands
- `build.sh` / `build.bat` - Build scripts
- `build_executable.py` - Python build script
- Source code files (`.py`)
- `requirements.txt`

## Step-by-Step Distribution Process

### 1. Build the Executable

**Option A: Using build script (Recommended)**
```bash
# macOS/Linux
./build.sh

# Windows
build.bat
```

**Option B: Using Python script**
```bash
python3 build_executable.py
```

**Option C: Manual PyInstaller**
```bash
# See QUICK_BUILD_REFERENCE.md for commands
```

### 2. Test the Executable

**Critical Testing Steps:**
- [ ] Test on a clean system without Python installed
- [ ] Test connecting to environments
- [ ] Test loading dashboards
- [ ] Test transferring dashboards
- [ ] Test saving to files
- [ ] Test loading from files
- [ ] Test all UI buttons and features
- [ ] Test error handling (wrong API key, etc.)

### 3. Create Distribution Package

**macOS:**
```bash
cd dist
mkdir DashboardDolly-macOS-v1.0
cp -r DashboardDolly.app DashboardDolly-macOS-v1.0/
cp ../END_USER_GUIDE.md DashboardDolly-macOS-v1.0/
cp -r ../Environments DashboardDolly-macOS-v1.0/
zip -r DashboardDolly-macOS-v1.0.zip DashboardDolly-macOS-v1.0
```

**Windows:**
```cmd
cd dist
mkdir DashboardDolly-Windows-v1.0
copy DashboardDolly.exe DashboardDolly-Windows-v1.0\
copy ..\END_USER_GUIDE.md DashboardDolly-Windows-v1.0\
xcopy ..\Environments DashboardDolly-Windows-v1.0\Environments\ /E /I
powershell Compress-Archive DashboardDolly-Windows-v1.0 DashboardDolly-Windows-v1.0.zip
```

### 4. (Optional) Code Sign

**macOS:**
```bash
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  DashboardDolly.app
```

**Windows:**
```cmd
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com DashboardDolly.exe
```

### 5. Create Release Notes

Create a `RELEASE_NOTES.md` file:

```markdown
# Dashboard Dolly v1.0 Release Notes

## What's New
- Initial release
- GUI interface for dashboard transfers
- Support for multiple environments
- Direct API key authentication
- Save/load dashboard files

## Installation
See END_USER_GUIDE.md

## System Requirements
- macOS 10.13+ or Windows 10+
- Internet connection
- Cloudability API access

## Known Issues
- None

## Support
Contact: your-email@example.com
```

### 6. Distribution Channels

**Internal Distribution:**
- Company file share
- Internal wiki/documentation site
- Email to users
- Slack/Teams channel

**External Distribution:**
- GitHub Releases
- Company website
- Cloud storage (Google Drive, Dropbox, etc.)

**Distribution Checklist:**
- [ ] Executable tested on clean system
- [ ] User guide included
- [ ] Sample configurations included
- [ ] Release notes created
- [ ] Version number documented
- [ ] Support contact provided
- [ ] (Optional) Code signed
- [ ] (Optional) Virus scanned

## Version Numbering

Use semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

Example: `v1.0.0`, `v1.1.0`, `v1.1.1`

## File Naming Convention

```
DashboardDolly-[Platform]-v[Version].[Extension]

Examples:
- DashboardDolly-macOS-v1.0.0.zip
- DashboardDolly-Windows-v1.0.0.zip
- DashboardDolly-Linux-v1.0.0.tar.gz
```

## Checksums (Recommended)

Generate checksums for verification:

```bash
# macOS/Linux
shasum -a 256 DashboardDolly-macOS-v1.0.0.zip > checksums.txt

# Windows
certutil -hashfile DashboardDolly-Windows-v1.0.0.zip SHA256 > checksums.txt
```

Include `checksums.txt` with your distribution.

## Update Process

When releasing updates:

1. Update version number in code
2. Build new executable
3. Test thoroughly
4. Create new distribution package
5. Update release notes
6. Notify users of update
7. Provide migration instructions if needed

## Support Documentation

Provide users with:
- `END_USER_GUIDE.md` - How to use the application
- `FAQ.md` - Common questions and answers
- Support email or contact method
- Known issues and workarounds

## Example Distribution Email

```
Subject: Dashboard Dolly v1.0 - Dashboard Transfer Tool Now Available

Hi Team,

We're excited to announce Dashboard Dolly v1.0, a new tool for transferring 
Cloudability dashboards between environments.

What it does:
- Transfer dashboards between environments
- Save dashboards as backup files
- Load dashboards from files
- Filter and search dashboards

Download:
- macOS: [Link to DashboardDolly-macOS-v1.0.0.zip]
- Windows: [Link to DashboardDolly-Windows-v1.0.0.zip]

Installation:
1. Download the file for your platform
2. Extract the zip file
3. See END_USER_GUIDE.md for instructions

No Python installation required!

Questions? Contact: your-email@example.com

Best regards,
Your Team
```

## Security Considerations

- **Don't include API keys** in the distribution
- **Don't include credentials** in sample configs
- **Advise users** to keep API keys secure
- **Use HTTPS** for all API communications
- **Consider code signing** for production use
- **Scan for viruses** before distribution

## Legal Considerations

Include appropriate:
- License file (if applicable)
- Copyright notices
- Third-party licenses (for dependencies)
- Terms of use
- Privacy policy (if collecting data)

## Maintenance Plan

- **Bug fixes**: How quickly will bugs be addressed?
- **Updates**: How often will new versions be released?
- **Support**: Who provides support and how?
- **End of life**: When will support end?

## Metrics to Track

Consider tracking:
- Number of downloads
- Active users
- Common issues/support requests
- Feature requests
- User satisfaction

## Success Criteria

Your distribution is successful when:
- [ ] Users can download and run without issues
- [ ] Users can complete tasks without support
- [ ] Support requests are minimal
- [ ] User feedback is positive
- [ ] Adoption rate meets goals

---

**Remember**: The goal is to make it as easy as possible for end users to get started. Clear documentation and thorough testing are key!