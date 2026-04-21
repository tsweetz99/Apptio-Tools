#!/bin/bash

# Turbonomic Audit Logs Retrieval Script
# This script downloads and extracts audit logs from Turbonomic API

# Configuration
TURBO_URL="https://cldp-autodesk.apptio.turbonomic.ibmappdomain.cloud"
DAYS=1
OUTPUT_DIR="./auditlogs_$(date +%Y%m%d_%H%M%S)"

# Check if JSESSIONID is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <JSESSIONID>"
    echo "Example: $0 node01g4tqattmvscf1a9b0us8iw6xw232.node0"
    exit 1
fi

JSESSIONID=$1

echo "Downloading audit logs for the last $DAYS day(s)..."

# Download the audit logs
curl --location "${TURBO_URL}/api/v3/admin/auditlogs?days=${DAYS}" \
     --header "Cookie: JSESSIONID=${JSESSIONID}" \
     --output auditlog.tar.gz

# Check if download was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to download audit logs"
    exit 1
fi

echo "Download complete. Extracting archive..."

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Extract the tar.gz file
tar -xzf auditlog.tar.gz -C "$OUTPUT_DIR"

if [ $? -eq 0 ]; then
    echo "Extraction successful!"
    echo "Audit logs extracted to: $OUTPUT_DIR"
    echo ""
    echo "Contents:"
    find "$OUTPUT_DIR" -type f -exec ls -lh {} \;
    echo ""
    echo "To view the logs, use:"
    # Find actual log files and show correct paths
    LOG_FILE=$(find "$OUTPUT_DIR" -type f | head -n 1)
    if [ -n "$LOG_FILE" ]; then
        echo "  cat $LOG_FILE"
        echo "  or"
        echo "  less $LOG_FILE"
        echo ""
        echo "To view all log files:"
        echo "  find $OUTPUT_DIR -type f -exec cat {} \\;"
    fi
else
    echo "Error: Failed to extract archive"
    exit 1
fi

# Optional: Remove the tar.gz file after extraction
# rm auditlog.tar.gz

# Made with Bob
