#!/bin/bash

# Turbonomic Audit Logs - Direct View Script
# This script streams audit logs directly to terminal without saving files

# Configuration
TURBO_URL="${TURBO_URL:-https://cldp-autodesk.apptio.turbonomic.ibmappdomain.cloud}"
DAYS="${DAYS:-1}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo "Usage: $0 <JSESSIONID> [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -d, --days <N>        Number of days of logs (default: 1)"
    echo "  -u, --url <URL>       Turbonomic instance URL"
    echo "  -s, --search <TEXT>   Search for specific text in logs"
    echo "  -o, --output <FILE>   Save logs to file while viewing"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  # View logs directly"
    echo "  $0 node01g4tqattmvscf1a9b0us8iw6xw232.node0"
    echo ""
    echo "  # View last 7 days"
    echo "  $0 <JSESSIONID> --days 7"
    echo ""
    echo "  # Search for specific text"
    echo "  $0 <JSESSIONID> --search \"Update Group\""
    echo ""
    echo "  # Save to file while viewing"
    echo "  $0 <JSESSIONID> --output audit.log"
    echo ""
    echo "Environment Variables:"
    echo "  TURBO_URL    Turbonomic instance URL (default: cldp-autodesk instance)"
    echo "  DAYS         Number of days of logs (default: 1)"
    exit 1
}

# Check if JSESSIONID is provided
if [ -z "$1" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
fi

JSESSIONID=$1
shift

# Parse additional arguments
SEARCH_TEXT=""
OUTPUT_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--days)
            DAYS="$2"
            shift 2
            ;;
        -u|--url)
            TURBO_URL="$2"
            shift 2
            ;;
        -s|--search)
            SEARCH_TEXT="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

echo -e "${GREEN}Fetching audit logs from Turbonomic...${NC}"
echo "URL: ${TURBO_URL}/api/v3/admin/auditlogs?days=${DAYS}"
echo ""

# Build the curl command
CURL_CMD="curl --location '${TURBO_URL}/api/v3/admin/auditlogs?days=${DAYS}' \
     --header 'Cookie: JSESSIONID=${JSESSIONID}' \
     --silent"

# Build the pipeline based on options
if [ -n "$OUTPUT_FILE" ]; then
    # Save to file while viewing
    echo -e "${YELLOW}Saving logs to: ${OUTPUT_FILE}${NC}"
    eval "$CURL_CMD" | tar -xzO | tee "$OUTPUT_FILE" | less
elif [ -n "$SEARCH_TEXT" ]; then
    # Search for specific text
    echo -e "${YELLOW}Searching for: ${SEARCH_TEXT}${NC}"
    echo ""
    eval "$CURL_CMD" | tar -xzO | grep --color=always "$SEARCH_TEXT" | less -R
else
    # Just view in less
    eval "$CURL_CMD" | tar -xzO | less
fi

# Check if command was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Done${NC}"
else
    echo -e "${RED}✗ Error fetching audit logs${NC}"
    echo "Possible issues:"
    echo "  - JSESSIONID expired (re-authenticate)"
    echo "  - Network connectivity"
    echo "  - Insufficient permissions"
    exit 1
fi

# Made with Bob
