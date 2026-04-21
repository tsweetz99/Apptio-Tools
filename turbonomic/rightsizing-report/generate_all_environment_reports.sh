#!/bin/bash

# Generate Turbonomic Rightsizing Reports for All Environments
# This script generates individual reports for Dev, UAT, Pre-Prod, Prod, and DR

# Configuration
TURBO_URL="${TURBO_URL:-https://cldp-autodesk.apptio.turbonomic.ibmappdomain.cloud}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${OUTPUT_DIR:-reports_$(date +%Y%m%d_%H%M%S)}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo "Usage: $0 <JSESSIONID> [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -u, --url <URL>           Turbonomic instance URL (default: cldp-autodesk instance)"
    echo "  -o, --output-dir <DIR>    Output directory (default: reports_TIMESTAMP)"
    echo "  -f, --format <FORMAT>     Output format: excel or csv (default: excel)"
    echo "  -h, --help                Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  TURBO_URL                 Turbonomic instance URL"
    echo "  OUTPUT_DIR                Output directory for reports"
    echo ""
    echo "Examples:"
    echo "  # Generate all environment reports"
    echo "  $0 node01g4tqattmvscf1a9b0us8iw6xw232.node0"
    echo ""
    echo "  # Specify custom URL and output directory"
    echo "  $0 <SESSION_ID> --url https://turbo.example.com --output-dir ./reports"
    echo ""
    echo "  # Generate CSV reports instead of Excel"
    echo "  $0 <SESSION_ID> --format csv"
    exit 1
}

# Check if JSESSIONID is provided
if [ -z "$1" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
fi

JSESSIONID=$1
shift

# Parse additional arguments
FORMAT="excel"

while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--url)
            TURBO_URL="$2"
            shift 2
            ;;
        -o|--output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -f|--format)
            FORMAT="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

# Determine file extension
if [ "$FORMAT" = "csv" ]; then
    EXT="csv"
else
    EXT="xlsx"
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Turbonomic Rightsizing Report Generator${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Turbonomic URL: $TURBO_URL"
echo "Output Directory: $OUTPUT_DIR"
echo "Output Format: $FORMAT"
echo ""

# Array of environments
ENVIRONMENTS=("Dev" "UAT" "Pre-Prod" "Prod" "DR")

# Generate report for each environment
TOTAL_ENVS=${#ENVIRONMENTS[@]}
CURRENT=0

for ENV in "${ENVIRONMENTS[@]}"; do
    CURRENT=$((CURRENT + 1))
    echo -e "${YELLOW}[$CURRENT/$TOTAL_ENVS] Generating report for $ENV...${NC}"
    
    OUTPUT_FILE="$OUTPUT_DIR/${ENV}_rightsizing_report.$EXT"
    
    python "$SCRIPT_DIR/generate_rightsizing_report.py" \
        --url "$TURBO_URL" \
        --jsessionid "$JSESSIONID" \
        --environment "$ENV" \
        --output "$OUTPUT_FILE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $ENV report generated successfully${NC}"
    else
        echo -e "${RED}✗ Failed to generate $ENV report${NC}"
    fi
    echo ""
done

# Generate combined report (all environments)
echo -e "${YELLOW}[$((TOTAL_ENVS + 1))/$((TOTAL_ENVS + 1))] Generating combined report (all environments)...${NC}"

OUTPUT_FILE="$OUTPUT_DIR/All_Environments_rightsizing_report.$EXT"

python "$SCRIPT_DIR/generate_rightsizing_report.py" \
    --url "$TURBO_URL" \
    --jsessionid "$JSESSIONID" \
    --output "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Combined report generated successfully${NC}"
else
    echo -e "${RED}✗ Failed to generate combined report${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Report Generation Complete${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Reports saved to: $OUTPUT_DIR"
echo ""
echo "Generated files:"
ls -lh "$OUTPUT_DIR"

echo ""
echo -e "${GREEN}Done!${NC}"

# Made with Bob
