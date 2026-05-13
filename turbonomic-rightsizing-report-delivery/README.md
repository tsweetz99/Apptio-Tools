# Turbonomic Rightsizing Report Generator

**Professional tool for generating comprehensive VM rightsizing recommendations from IBM Turbonomic**

## Overview

This tool extracts rightsizing recommendations from Turbonomic and generates detailed Excel reports with cost analysis, environment filtering, and customizable customer mapping. Perfect for presenting optimization opportunities to stakeholders and tracking cost savings initiatives.

## Key Features

✅ **Consolidated Reporting** - Single Excel workbook with multiple environment sheets  
✅ **Three Report Types** - VM Rightsizing, Disk Optimization, and Monthly Action Plan  
✅ **Environment Filtering** - Separate sheets for Dev, UAT, Pre-Prod, Prod, and DR  
✅ **Cost Analysis** - Calculate monthly savings (downsizing) and net add costs (upsizing)  
✅ **Customer Mapping** - Map technical VMs to business-friendly customer names  
✅ **Professional Formatting** - Color-coded, clickable links, ready for stakeholder review  
✅ **Unified Runner** - Generate all reports with a single command  
✅ **Flexible Authentication** - Username/password, environment variables, or JSESSIONID  

## What's Included

```
turbonomic-rightsizing-report-delivery/
├── README.md                              # This file
├── INSTALLATION.md                        # Detailed setup instructions
├── QUICKSTART.md                          # Get started in 5 minutes
├── CUSTOMER_MAPPING.md                    # Customer mapping configuration
├── MONTHLY_ACTION_PLAN.md                 # Monthly Action Plan guide
├── requirements.txt                       # Python dependencies
├── turbo_auth.py                          # Shared authentication module
├── generate_all_reports.py                # Unified report generator
├── generate_rightsizing_report.py         # VM rightsizing report generator
├── generate_disk_optimization_report.py   # Disk/storage optimization reports
├── generate_monthly_action_plan.py        # Monthly action plan generator
├── customer_mapping.json.example          # Customer mapping template
└── LICENSE                                # Apache 2.0 License
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Customer Mapping (Optional)

```bash
cp customer_mapping.json.example customer_mapping.json
# Edit customer_mapping.json with your customer ID mappings
```

### 3. Generate Reports

**Option A: Generate All Reports (Recommended)**

```bash
python3 generate_all_reports.py \
    --url https://your-turbo-instance.com \
    --username your-username \
    --password your-password
```

**Option B: Generate Individual Reports**

```bash
# VM Rightsizing Report
python3 generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --username your-username \
    --password your-password

# Disk Optimization Report
python3 generate_disk_optimization_report.py \
    --url https://your-turbo-instance.com \
    --username your-username \
    --password your-password

# Monthly Action Plan
python3 generate_monthly_action_plan.py \
    --url https://your-turbo-instance.com \
    --username your-username \
    --password your-password
```

## Authentication Methods

The tools support three authentication methods:

### 1. Username/Password (Recommended)
```bash
python3 generate_all_reports.py \
    --url https://your-turbo-instance.com \
    --username your-username \
    --password your-password
```

### 2. Environment Variables
```bash
export TURBO_URL="https://your-turbo-instance.com"
export TURBO_USERNAME="your-username"
export TURBO_PASSWORD="your-password"

python3 generate_all_reports.py
```

### 3. JSESSIONID (Manual)
```bash
# Get session ID from browser DevTools or curl
python3 generate_all_reports.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID
```

## Report Types

### 1. VM Rightsizing Report

Comprehensive VM rightsizing recommendations with:
- Current and recommended VM configurations
- Monthly cost savings and net add costs
- Environment categorization (Dev, UAT, Pre-Prod, Prod, DR)
- Customer-friendly names (when mapping configured)
- Clickable links to Turbonomic UI

**Output**: `Rightsizing_Report_YYYYMMDD_HHMMSS.xlsx`

### 2. Disk Optimization Report

Storage tier optimization recommendations with:
- Current and recommended disk configurations
- Storage tier changes (Premium SSD, Standard SSD, Standard HDD)
- Policy violation highlighting (Premium SSD in Dev/UAT)
- Monthly cost savings
- Environment categorization

**Output**: `Disk_Optimization_Report_YYYYMMDD_HHMMSS.xlsx`

### 3. Monthly Action Plan

Categorized action plan for maintenance window execution:
- Actions grouped by category (Resize, Disk, Network, etc.)
- Priority sorting (Critical → Low)
- Customer ID and friendly name mapping
- Clickable action detail links
- Policy violation highlighting

**Output**: `Monthly_Action_Plan_YYYYMMDD_HHMMSS.xlsx`

## Report Output Structure

Each consolidated report includes:

**Summary Sheet**
- Total actions by environment
- Cost savings breakdown
- Action type distribution
- High-level statistics

**Comprehensive Sheet**
- All actions across all environments
- Complete data set for analysis

**Environment Sheets**
- Dev, UAT, Pre-Prod, Prod, DR, Unmapped
- Filtered data for each environment
- Professional formatting with frozen headers

## Common Use Cases

### Generate All Reports with Customer Mapping

```bash
python3 generate_all_reports.py \
    --url https://your-turbo-instance.com \
    --username your-username \
    --password your-password \
    --customer-mapping customer_mapping.json
```

### Generate Specific Reports Only

```bash
# Only VM Rightsizing and Disk Optimization
python3 generate_all_reports.py \
    --url https://your-turbo-instance.com \
    --username your-username \
    --skip-monthly-plan

# Only Monthly Action Plan
python3 generate_monthly_action_plan.py \
    --url https://your-turbo-instance.com \
    --username your-username
```

### Custom Output Directory

```bash
python3 generate_all_reports.py \
    --url https://your-turbo-instance.com \
    --username your-username \
    --output-dir /path/to/reports/
```

## Customer Mapping

Map CustomerID tags to business-friendly names for stakeholder reports:

```json
{
  "10061075": "AIG A&H",
  "10060876": "Chubb",
  "10060877": "Liberty Mutual"
}
```

See [`CUSTOMER_MAPPING.md`](CUSTOMER_MAPPING.md) for complete configuration guide.

## Documentation

- **[INSTALLATION.md](INSTALLATION.md)** - Detailed installation and setup guide
- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[CUSTOMER_MAPPING.md](CUSTOMER_MAPPING.md)** - Customer mapping configuration guide
- **[MONTHLY_ACTION_PLAN.md](MONTHLY_ACTION_PLAN.md)** - Monthly Action Plan documentation

## System Requirements

- **Python**: 3.6 or higher
- **Operating System**: Windows, macOS, or Linux
- **Network**: Access to Turbonomic instance
- **Permissions**: Turbonomic user with read access to actions and entities

## Troubleshooting

### "Error: 401 Unauthorized"
Your credentials are invalid or session expired. Verify username/password or get a new JSESSIONID.

### "pandas not installed"
Install required dependencies:
```bash
pip install -r requirements.txt
```

### "No data in report"
- Verify there are pending recommendations in Turbonomic
- Check that VMs have proper tags (Environment, CustomerID)
- Ensure your Turbonomic user has appropriate permissions

### "Customer mapping not working"
- Verify `customer_mapping.json` exists (not just `.example`)
- Check that CustomerID tags match the keys in your mapping file
- Ensure VMs have CustomerID tags configured in Turbonomic

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the detailed documentation files
3. Verify Turbonomic credentials and permissions
4. Ensure VMs have required tags configured

## License

Copyright IBM. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0

This tool is provided as-is for use with IBM Turbonomic. See LICENSE file for details.

## Version

**Release**: 1.0.0  
**Date**: April 2026  
**Compatibility**: Turbonomic 8.x API v3

---

**Ready to get started?** See [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide.