# Setup Guide - Installing Python and Dependencies

## Issue: "pip: command not found"

This means pip (Python package installer) is not installed or not in your system PATH. Here's how to fix it on macOS.

## Solution Options

### Option 1: Use pip3 (Most Common on macOS)

On macOS, Python 3 is usually installed, and the command is `pip3` instead of `pip`:

```bash
# Try pip3 instead
pip3 --version

# Install dependencies
pip3 install -r requirements.txt

# Run the script with python3
python3 generate_rightsizing_report.py --help
```

### Option 2: Install Python 3 with Homebrew (Recommended)

If pip3 doesn't work, install Python 3 using Homebrew:

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3
brew install python

# Verify installation
python3 --version
pip3 --version

# Install dependencies
pip3 install -r requirements.txt
```

### Option 3: Use Python's Built-in Module

Python 3 includes pip as a module, even if the command isn't in PATH:

```bash
# Install using Python module
python3 -m pip install -r requirements.txt

# Or install packages individually
python3 -m pip install requests
python3 -m pip install pandas
python3 -m pip install openpyxl
```

### Option 4: Install Minimal Dependencies (CSV Only)

If you only need CSV export (not Excel), you only need `requests`:

```bash
# Install just requests
python3 -m pip install requests

# Run script with CSV output
python3 generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid <SESSION_ID> \
    --output report.csv
```

## Verification Steps

After installation, verify everything works:

```bash
# 1. Check Python version
python3 --version
# Should show: Python 3.x.x

# 2. Check pip
pip3 --version
# or
python3 -m pip --version

# 3. Verify installed packages
pip3 list | grep requests
pip3 list | grep pandas
pip3 list | grep openpyxl

# 4. Test the script
python3 generate_rightsizing_report.py --help
```

## Complete Setup Process

Here's the complete setup from scratch:

```bash
# 1. Navigate to the directory
cd turbonomic/rightsizing-report

# 2. Check Python installation
python3 --version

# 3. Install dependencies (choose one method)
# Method A: Using pip3
pip3 install -r requirements.txt

# Method B: Using python3 -m pip
python3 -m pip install -r requirements.txt

# Method C: Install individually
python3 -m pip install requests pandas openpyxl

# 4. Verify installation
python3 -c "import requests; import pandas; import openpyxl; print('All packages installed successfully!')"

# 5. Test the script
python3 generate_rightsizing_report.py --help
```

## Troubleshooting

### Issue: "python3: command not found"

**Solution**: Python 3 is not installed. Install it:

```bash
# macOS with Homebrew
brew install python

# Or download from python.org
# Visit: https://www.python.org/downloads/
```

### Issue: "Permission denied" when installing

**Solution**: Use `--user` flag to install in user directory:

```bash
pip3 install --user -r requirements.txt
```

### Issue: "SSL Certificate" errors

**Solution**: Update certificates:

```bash
# macOS
/Applications/Python\ 3.*/Install\ Certificates.command

# Or use --trusted-host
pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Issue: Multiple Python versions

**Solution**: Use specific Python version:

```bash
# Check available Python versions
ls -l /usr/local/bin/python*

# Use specific version
python3.11 -m pip install -r requirements.txt
python3.11 generate_rightsizing_report.py --help
```

## Alternative: Use Virtual Environment (Best Practice)

Create an isolated environment for the project:

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate it
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the script
python generate_rightsizing_report.py --help

# 5. When done, deactivate
deactivate
```

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python3 --version` | Check Python version |
| `pip3 --version` | Check pip version |
| `pip3 install -r requirements.txt` | Install all dependencies |
| `pip3 install requests` | Install single package |
| `pip3 list` | List installed packages |
| `python3 -m pip install <package>` | Alternative pip command |
| `pip3 install --user <package>` | Install for current user only |

## Minimal Installation (No Excel Support)

If you just want to generate CSV reports without Excel dependencies:

```bash
# Install only requests
pip3 install requests

# Run with CSV output
python3 generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid <SESSION_ID> \
    --output report.csv
```

## System Requirements

- **macOS**: 10.13 or later
- **Python**: 3.7 or later
- **Disk Space**: ~50MB for dependencies

## Getting Help

If you continue to have issues:

1. Check your Python installation:
   ```bash
   which python3
   python3 --version
   ```

2. Check your PATH:
   ```bash
   echo $PATH
   ```

3. Try the virtual environment approach (most reliable)

4. Contact your system administrator if on a managed system

## Next Steps

Once dependencies are installed:
1. See [QUICKSTART.md](./QUICKSTART.md) for usage
2. See [README.md](./README.md) for detailed documentation
3. Run `python3 generate_rightsizing_report.py --help` for options