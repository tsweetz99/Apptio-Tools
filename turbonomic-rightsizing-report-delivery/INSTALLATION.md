# Installation Guide - Turbonomic Rightsizing Report Generator

Complete step-by-step installation instructions for all platforms.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Steps](#installation-steps)
- [Platform-Specific Instructions](#platform-specific-instructions)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

## Prerequisites

### Required Software

1. **Python 3.6 or higher**
   - Check version: `python --version` or `python3 --version`
   - Download: [python.org](https://www.python.org/downloads/)

2. **pip (Python package manager)**
   - Usually included with Python
   - Check version: `pip --version` or `pip3 --version`

3. **Network Access**
   - Access to your Turbonomic instance
   - Internet access for downloading Python packages

### Required Permissions

- Turbonomic user account with:
  - Read access to actions
  - Read access to entities (VMs, storage, etc.)
  - Ability to view recommendations

## Installation Steps

### Step 1: Extract the Package

```bash
# If you received a zip file
unzip turbonomic-rightsizing-report-delivery.zip
cd turbonomic-rightsizing-report-delivery

# If you received a tar.gz file
tar -xzf turbonomic-rightsizing-report-delivery.tar.gz
cd turbonomic-rightsizing-report-delivery
```

### Step 2: Install Python Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using pip3 (if pip points to Python 2)
pip3 install -r requirements.txt

# Or using python -m pip
python -m pip install -r requirements.txt
```

**What gets installed:**
- `requests` - HTTP library for API calls
- `pandas` - Data manipulation and Excel export
- `openpyxl` - Excel file format support

### Step 3: Verify Installation

```bash
# Check if all dependencies are installed
python -c "import requests, pandas, openpyxl; print('All dependencies installed successfully!')"
```

If you see "All dependencies installed successfully!", you're ready to go!

### Step 4: Configure Customer Mapping (Optional)

If you want to use customer-friendly names in reports:

```bash
# Copy the example file
cp customer_mapping.json.example customer_mapping.json

# Edit with your mappings
nano customer_mapping.json
# or use your preferred text editor
```

See [CUSTOMER_MAPPING.md](CUSTOMER_MAPPING.md) for detailed configuration instructions.

## Platform-Specific Instructions

### macOS

#### Install Python (if not already installed)

```bash
# Using Homebrew (recommended)
brew install python3

# Verify installation
python3 --version
pip3 --version
```

#### Install Dependencies

```bash
# Navigate to the tool directory
cd turbonomic-rightsizing-report-delivery

# Install dependencies
pip3 install -r requirements.txt
```

#### Run the Tool

```bash
# Use python3 command
python3 generate_rightsizing_report.py --help
```

### Windows

#### Install Python (if not already installed)

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Restart Command Prompt after installation

#### Install Dependencies

```cmd
# Open Command Prompt or PowerShell
cd turbonomic-rightsizing-report-delivery

# Install dependencies
pip install -r requirements.txt
```

#### Run the Tool

```cmd
# Use python command
python generate_rightsizing_report.py --help
```

### Linux (Ubuntu/Debian)

#### Install Python (if not already installed)

```bash
# Update package list
sudo apt update

# Install Python 3 and pip
sudo apt install python3 python3-pip

# Verify installation
python3 --version
pip3 --version
```

#### Install Dependencies

```bash
# Navigate to the tool directory
cd turbonomic-rightsizing-report-delivery

# Install dependencies
pip3 install -r requirements.txt
```

#### Run the Tool

```bash
# Use python3 command
python3 generate_rightsizing_report.py --help
```

### Linux (RHEL/CentOS)

#### Install Python (if not already installed)

```bash
# RHEL/CentOS 8+
sudo dnf install python3 python3-pip

# RHEL/CentOS 7
sudo yum install python3 python3-pip

# Verify installation
python3 --version
pip3 --version
```

#### Install Dependencies

```bash
# Navigate to the tool directory
cd turbonomic-rightsizing-report-delivery

# Install dependencies
pip3 install -r requirements.txt
```

## Verification

### Test Basic Functionality

```bash
# Display help to verify the script works
python generate_rightsizing_report.py --help
```

You should see usage information and available options.

### Test Turbonomic Connection

```bash
# Get a session ID first
curl -X POST 'https://your-turbo-instance.com/api/v3/login' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -d 'username=your-username&password=your-password' \
     -c cookies.txt

# Extract session ID
SESSION_ID=$(grep JSESSIONID cookies.txt | awk '{print $7}')

# Test connection with a dry run
python generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid $SESSION_ID \
    --output test_report.xlsx
```

If the script runs without errors and creates a report file, installation is successful!

## Troubleshooting

### Issue: "python: command not found"

**Solution**: Use `python3` instead of `python`:
```bash
python3 generate_rightsizing_report.py --help
```

### Issue: "pip: command not found"

**Solution**: Use `pip3` or `python -m pip`:
```bash
pip3 install -r requirements.txt
# or
python3 -m pip install -r requirements.txt
```

### Issue: "Permission denied" when installing packages

**Solution**: Install packages for your user only:
```bash
pip install --user -r requirements.txt
# or
pip3 install --user -r requirements.txt
```

### Issue: "ModuleNotFoundError: No module named 'requests'"

**Solution**: Dependencies not installed. Run:
```bash
pip install -r requirements.txt
```

### Issue: SSL Certificate Errors

**Solution**: The scripts handle self-signed certificates automatically. If you still have issues:
```bash
# For testing only - not recommended for production
export PYTHONHTTPSVERIFY=0
python generate_rightsizing_report.py ...
```

### Issue: "Error: 401 Unauthorized"

**Solution**: Your session ID expired. Get a new one:
```bash
curl -X POST 'https://your-turbo-instance.com/api/v3/login' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -d 'username=your-username&password=your-password' \
     -c cookies.txt
```

### Issue: Excel files won't open

**Solution**: Ensure openpyxl is installed:
```bash
pip install openpyxl
```

### Issue: Reports are empty

**Possible causes:**
1. No pending recommendations in Turbonomic
2. Environment filter too restrictive
3. VMs missing required tags

**Solution**: Try without filters first:
```bash
python generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --output test.xlsx
```

## Virtual Environment (Optional but Recommended)

For isolated Python environments:

### Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Deactivate Virtual Environment

```bash
deactivate
```

## Upgrading

To upgrade to a newer version:

```bash
# Backup your configuration
cp customer_mapping.json customer_mapping.json.backup

# Extract new version
unzip turbonomic-rightsizing-report-delivery-v2.zip

# Restore your configuration
cp customer_mapping.json.backup turbonomic-rightsizing-report-delivery/customer_mapping.json

# Reinstall dependencies (in case they changed)
cd turbonomic-rightsizing-report-delivery
pip install -r requirements.txt
```

## Uninstallation

To remove the tool:

```bash
# Remove the directory
rm -rf turbonomic-rightsizing-report-delivery

# Optionally remove Python packages (if not used by other tools)
pip uninstall requests pandas openpyxl
```

## Next Steps

After successful installation:

1. **Quick Start**: See [QUICKSTART.md](QUICKSTART.md) for your first report
2. **Configuration**: Set up customer mapping if needed
3. **Automation**: Consider scheduling regular report generation
4. **Documentation**: Review [README.md](README.md) for all features

## Getting Help

If you encounter issues not covered here:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Review error messages carefully
3. Verify Python and pip versions meet requirements
4. Ensure network connectivity to Turbonomic instance
5. Confirm Turbonomic user permissions

## System Requirements Summary

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.6 | 3.8+ |
| RAM | 512 MB | 1 GB+ |
| Disk Space | 50 MB | 100 MB+ |
| Network | HTTP/HTTPS access | Stable connection |
| OS | Any Python-compatible | macOS, Linux, Windows 10+ |

---

**Installation complete?** Head to [QUICKSTART.md](QUICKSTART.md) to generate your first report!