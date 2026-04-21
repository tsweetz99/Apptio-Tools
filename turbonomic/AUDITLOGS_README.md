# Turbonomic Audit Logs Retrieval Guide

## Overview

The Turbonomic audit logs API endpoint (`/api/v3/admin/auditlogs`) returns a **tar.gz compressed archive**, not plain text. This is why the output appears binary when downloaded directly with curl.

## Problem

When you run:
```bash
curl --location 'https://your-turbo-instance.com/api/v3/admin/auditlogs?days=1' \
     --header 'Cookie: JSESSIONID=your-session-id' \
     --output auditlog.tar.gz
```

The file `auditlog.tar.gz` is a compressed archive that needs to be extracted before you can read the logs.

## Solutions

### Option 1: One-Liner (Fastest - Direct to Terminal)

Stream the audit logs directly to your terminal without saving files:

```bash
# View logs directly in terminal
curl --location 'https://your-turbo-instance.com/api/v3/admin/auditlogs?days=1' \
     --header 'Cookie: JSESSIONID=your-session-id' \
     --silent | tar -xzO

# With pagination (recommended for large logs)
curl --location 'https://your-turbo-instance.com/api/v3/admin/auditlogs?days=1' \
     --header 'Cookie: JSESSIONID=your-session-id' \
     --silent | tar -xzO | less

# Search for specific content
curl --location 'https://your-turbo-instance.com/api/v3/admin/auditlogs?days=1' \
     --header 'Cookie: JSESSIONID=your-session-id' \
     --silent | tar -xzO | grep "Update Group"

# Save to a file while viewing
curl --location 'https://your-turbo-instance.com/api/v3/admin/auditlogs?days=1' \
     --header 'Cookie: JSESSIONID=your-session-id' \
     --silent | tar -xzO | tee audit.log | less
```

**Explanation:**
- `--silent` suppresses curl's progress output
- `tar -xzO` extracts to stdout (capital O) instead of files
- Pipe to `less`, `grep`, or other tools for viewing/filtering

### Option 2: Manual Extraction (If You Need to Save Files)

If you already have the `auditlog.tar.gz` file:

```bash
# Extract the archive
tar -xzf auditlog.tar.gz

# The archive contains a nested directory structure
# Find and view the extracted logs
find . -name "*.log" -type f
cat ./filtered_auditlog/audit.log
# or
less ./filtered_auditlog/audit.log

# Or view all log files recursively
find . -type f -exec cat {} \;
```

### Option 3: Bash Script (Automated with Extraction)

Use the provided [`get_auditlogs.sh`](./get_auditlogs.sh) script:

```bash
# Make the script executable
chmod +x get_auditlogs.sh

# Run the script with your JSESSIONID
./get_auditlogs.sh node01g4tqattmvscf1a9b0us8iw6xw232.node0
```

The script will:
1. Download the audit logs
2. Extract them to a timestamped directory
3. Display the contents

### Option 4: Python Script (Most Flexible)

Use the provided [`get_auditlogs.py`](./get_auditlogs.py) script:

```bash
# Install required dependency
pip install requests

# Basic usage (last 1 day)
python get_auditlogs.py --jsessionid node01g4tqattmvscf1a9b0us8iw6xw232.node0

# Get last 7 days of logs
python get_auditlogs.py --jsessionid <SESSION_ID> --days 7

# Preview first 50 lines of each log file
python get_auditlogs.py --jsessionid <SESSION_ID> --preview 50

# Keep the tar.gz file after extraction
python get_auditlogs.py --jsessionid <SESSION_ID> --keep-archive

# Specify custom output directory
python get_auditlogs.py --jsessionid <SESSION_ID> --output-dir ./my_logs

# Use with different Turbonomic instance
python get_auditlogs.py --jsessionid <SESSION_ID> --url https://your-instance.com
```

## Getting Your JSESSIONID

You need to authenticate first to get a valid JSESSIONID:

### Using curl:
```bash
curl -X POST 'https://your-turbo-instance.com/api/v3/login?hateoas=true' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -d 'username=your-username&password=your-password' \
     -c cookies.txt

# Extract JSESSIONID from cookies.txt
grep JSESSIONID cookies.txt
```

### Using Python:
```python
import requests

response = requests.post(
    'https://your-turbo-instance.com/api/v3/login',
    data={'username': 'your-username', 'password': 'your-password'},
    params={'hateoas': 'true'}
)

jsessionid = response.cookies.get('JSESSIONID')
print(f"JSESSIONID: {jsessionid}")
```

### Using Postman:
1. Use the login request from the [Turbo API collection](./postman-collection/Turbo%20API.postman_collection.json)
2. After successful login, find the JSESSIONID in the response cookies
3. Copy the value (e.g., `node01g4tqattmvscf1a9b0us8iw6xw232.node0`)

## API Documentation

According to the [IBM Turbonomic API documentation](https://www.ibm.com/docs/en/tarm/8.19.3?topic=endpoint-admin-requests#endpoint_admin_requests__title__3):

**Endpoint:** `GET /api/v3/admin/auditlogs`

**Parameters:**
- `days` (optional): Number of days of audit logs to retrieve (default: 1)

**Response:** Returns a tar.gz compressed archive containing audit log files

**Authentication:** Requires valid JSESSIONID cookie

## Understanding the Audit Logs

The extracted audit logs are contained in a nested directory structure:
```
auditlogs_TIMESTAMP/
└── filtered_auditlog/
    └── audit.log
```

The audit logs typically contain:
- User actions and changes (e.g., "Update Group", "Create Group")
- System events
- API calls
- Configuration changes
- Login/logout events
- Timestamps and user information
- IP addresses of requesters

The logs are in text format with fields separated by commas and can be parsed for analysis, compliance, or troubleshooting purposes.

### Log Format Example
```
2026-04-08T00:00:29.387Z -[172.21.122.175] [SYSTEM] TURBONOMICAUDIT: "2026-04-08 00:00:29", "172.21.122.175", "Update Group", "GroupName", "result=Success", "Updated Group GroupName (id: 287197621437840)", 0
```

## Troubleshooting

### Issue: "Binary output" or unreadable file
**Solution:** The file is a tar.gz archive. Extract it using `tar -xzf auditlog.tar.gz`, then navigate to the nested directory (e.g., `filtered_auditlog/`) to find the actual log files.

### Issue: "No matches found" when trying to view logs with wildcards
**Solution:** The logs are in a nested directory structure. Use `find` to locate them:
```bash
find auditlogs_* -type f -name "*.log"
# Then view with the actual path
cat auditlogs_TIMESTAMP/filtered_auditlog/audit.log
```

### Issue: "Authentication failed" or 401 error
**Solution:** Your JSESSIONID has expired (default: 30 minutes). Re-authenticate to get a new session ID.

### Issue: Empty or no log files after extraction
**Solution:**
- Check if there are any audit events in the specified time period
- Verify you have admin permissions to access audit logs
- Try increasing the `days` parameter

### Issue: "Permission denied" when running bash script
**Solution:** Make the script executable: `chmod +x get_auditlogs.sh`

## Quick Reference Scripts

### Direct View Script (Recommended for Terminal Viewing)

Use [`view_auditlogs_direct.sh`](./view_auditlogs_direct.sh) for the easiest terminal viewing:

```bash
# Make executable
chmod +x view_auditlogs_direct.sh

# View logs directly in terminal
./view_auditlogs_direct.sh <JSESSIONID>

# View last 7 days
./view_auditlogs_direct.sh <JSESSIONID> --days 7

# Search for specific text
./view_auditlogs_direct.sh <JSESSIONID> --search "Update Group"

# Save to file while viewing
./view_auditlogs_direct.sh <JSESSIONID> --output audit.log
```

## Examples

### Example 1: Direct terminal view (no files saved)
```bash
# Simple one-liner
curl --location 'https://your-turbo-instance.com/api/v3/admin/auditlogs?days=1' \
     --header 'Cookie: JSESSIONID=your-session-id' \
     --silent | tar -xzO | less

# With search
curl --location 'https://your-turbo-instance.com/api/v3/admin/auditlogs?days=1' \
     --header 'Cookie: JSESSIONID=your-session-id' \
     --silent | tar -xzO | grep "Update Group"
```

### Example 2: Download and search for specific user
```bash
python get_auditlogs.py --jsessionid <SESSION_ID> --days 30 --output-dir logs_30days
find logs_30days -type f -exec grep "username@example.com" {} \;
```

### Example 3: Automated daily backup
```bash
#!/bin/bash
# Add to cron for daily execution
JSESSIONID=$(curl -s -X POST 'https://your-turbo-instance.com/api/v3/login' \
             -d 'username=admin&password=secret' | grep -o 'JSESSIONID=[^;]*' | cut -d= -f2)

python get_auditlogs.py --jsessionid "$JSESSIONID" --days 1 \
       --output-dir "/backup/auditlogs/$(date +%Y%m%d)"
```

## Additional Resources

- [Turbonomic API Documentation](https://www.ibm.com/docs/en/tarm/8.19.3?topic=endpoint-admin-requests)
- [Postman Collection](./postman-collection/Turbo%20API.postman_collection.json)
- [Group Creator Script](./group-creator/README.md)

## Notes

- Session IDs expire after 30 minutes (or your configured timeout)
- Audit logs may be large for longer time periods
- Ensure you have sufficient disk space before downloading
- Admin privileges are required to access audit logs