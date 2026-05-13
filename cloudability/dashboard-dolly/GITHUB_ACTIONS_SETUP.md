# GitHub Actions Setup Guide

This guide will help you set up automated builds for Dashboard Dolly using GitHub Actions.

## What You Get

✅ Automatic builds for **both Windows and macOS**
✅ Triggered by git tags or manually
✅ Downloadable executables from GitHub
✅ Optional: Automatic GitHub Releases

## Prerequisites

- GitHub repository (public or private)
- Git installed locally
- Repository pushed to GitHub

## Step-by-Step Setup

### Step 1: Verify the Workflow File Exists

The workflow file should be at:
```
.github/workflows/build-dashboard-dolly.yml
```

✅ This file has been created for you!

### Step 2: Commit and Push to GitHub

```bash
# Navigate to your repo
cd /Users/tsweetz/Library/CloudStorage/OneDrive-IBM/github-repo/Apptio-Tools

# Add the workflow file
git add .github/workflows/build-dashboard-dolly.yml

# Add any other Dashboard Dolly changes
git add cloudability/dashboard-dolly/

# Commit
git commit -m "Add GitHub Actions workflow for Dashboard Dolly builds"

# Push to GitHub
git push origin main
```

### Step 3: Enable GitHub Actions (if needed)

1. Go to your GitHub repository
2. Click on **"Actions"** tab
3. If prompted, click **"I understand my workflows, go ahead and enable them"**

### Step 4: Trigger a Build

You have two options:

#### Option A: Manual Trigger (Easiest for Testing)

1. Go to your GitHub repository
2. Click **"Actions"** tab
3. Click **"Build Dashboard Dolly Executables"** in the left sidebar
4. Click **"Run workflow"** button (top right)
5. Select branch (usually `main`)
6. Click **"Run workflow"**

#### Option B: Tag-Based Trigger (For Releases)

```bash
# Create and push a tag
git tag dashboard-dolly-v1.0.0
git push origin dashboard-dolly-v1.0.0
```

This will:
- Build both Windows and macOS versions
- Create a GitHub Release
- Attach the executables to the release

### Step 5: Monitor the Build

1. Go to **Actions** tab
2. Click on the running workflow
3. Watch the progress of both jobs:
   - **Build Windows Executable**
   - **Build macOS Executable**

Build typically takes 5-10 minutes.

### Step 6: Download the Executables

#### If you used Manual Trigger:

1. Wait for build to complete (green checkmark)
2. Click on the completed workflow run
3. Scroll down to **"Artifacts"** section
4. Download:
   - `DashboardDolly-Windows.zip`
   - `DashboardDolly-macOS.zip`

#### If you used Tag Trigger:

1. Go to **"Releases"** tab
2. Find your release (e.g., `dashboard-dolly-v1.0.0`)
3. Download the attached files

### Step 7: Test the Executables

**Windows:**
1. Extract `DashboardDolly-Windows.zip`
2. Run `DashboardDolly\DashboardDolly.exe`
3. Test all functionality

**macOS:**
1. Extract `DashboardDolly-macOS.zip`
2. Right-click `DashboardDolly.app` → Open
3. Test all functionality

## Workflow Triggers

The workflow runs when:

1. **Manual trigger**: Click "Run workflow" in Actions tab
2. **Tag push**: Push a tag starting with `dashboard-dolly-v`
   ```bash
   git tag dashboard-dolly-v1.0.1
   git push origin dashboard-dolly-v1.0.1
   ```

## Customization

### Change Python Version

Edit `.github/workflows/build-dashboard-dolly.yml`:
```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'  # Change this
```

### Change Artifact Retention

Default is 90 days. To change:
```yaml
- name: Upload Windows artifact
  uses: actions/upload-artifact@v4
  with:
    name: DashboardDolly-Windows
    path: cloudability/dashboard-dolly/dist/DashboardDolly-Windows.zip
    retention-days: 30  # Change this
```

### Add Linux Build

Add this job to the workflow:
```yaml
build-linux:
  name: Build Linux Executable
  runs-on: ubuntu-latest
  
  steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd cloudability/dashboard-dolly
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Sanitize and build
      run: |
        cd cloudability/dashboard-dolly
        python3 build_executable.py
    
    - name: Create distribution package
      run: |
        cd cloudability/dashboard-dolly/dist
        tar -czf DashboardDolly-Linux.tar.gz DashboardDolly/
    
    - name: Upload Linux artifact
      uses: actions/upload-artifact@v4
      with:
        name: DashboardDolly-Linux
        path: cloudability/dashboard-dolly/dist/DashboardDolly-Linux.tar.gz
        retention-days: 90
```

## Troubleshooting

### Build Fails on Windows

**Error**: `ModuleNotFoundError`
**Solution**: Add missing package to `requirements.txt`

### Build Fails on macOS

**Error**: `Icon file not found`
**Solution**: Already fixed - we removed the icon parameter

### Artifacts Not Appearing

**Check**:
1. Build completed successfully (green checkmark)
2. Scroll down to "Artifacts" section
3. Artifacts expire after retention period (default 90 days)

### Release Not Created

**Check**:
1. You pushed a tag (not just committed)
2. Tag starts with `dashboard-dolly-v`
3. Both builds completed successfully

### Permission Denied

**Error**: `Resource not accessible by integration`
**Solution**: 
1. Go to Settings → Actions → General
2. Under "Workflow permissions"
3. Select "Read and write permissions"
4. Save

## Best Practices

### Version Numbering

Use semantic versioning:
```bash
git tag dashboard-dolly-v1.0.0  # Major.Minor.Patch
git tag dashboard-dolly-v1.1.0  # New features
git tag dashboard-dolly-v1.1.1  # Bug fixes
```

### Testing Before Release

1. Use manual trigger to test builds
2. Download and test both executables
3. Only create tagged release when ready

### Security

✅ The workflow automatically sanitizes API keys
✅ No secrets are exposed in logs
✅ Artifacts are only accessible to repo collaborators

### Documentation

Always include with releases:
- `END_USER_GUIDE.md`
- `SECURITY_PACKAGING_GUIDE.md`
- Release notes

## Quick Reference

### Create a Release

```bash
# 1. Commit all changes
git add .
git commit -m "Release v1.0.0"
git push

# 2. Create and push tag
git tag dashboard-dolly-v1.0.0
git push origin dashboard-dolly-v1.0.0

# 3. Wait for build (5-10 minutes)
# 4. Check Releases tab for downloads
```

### Manual Build

```bash
# 1. Go to Actions tab
# 2. Click "Build Dashboard Dolly Executables"
# 3. Click "Run workflow"
# 4. Wait for completion
# 5. Download from Artifacts section
```

## Cost

GitHub Actions is **free** for:
- Public repositories (unlimited)
- Private repositories (2,000 minutes/month)

Each build uses approximately:
- Windows: ~5 minutes
- macOS: ~8 minutes
- **Total: ~13 minutes per build**

## Support

If you encounter issues:

1. Check the workflow run logs in Actions tab
2. Look for red X marks indicating failures
3. Click on failed job to see detailed logs
4. Common issues are usually dependency-related

## Summary

✅ Workflow file created: `.github/workflows/build-dashboard-dolly.yml`
✅ Builds both Windows and macOS automatically
✅ Can trigger manually or with tags
✅ Executables available as artifacts or releases
✅ Automatic API key sanitization included

**Next step**: Commit and push the workflow file to GitHub!