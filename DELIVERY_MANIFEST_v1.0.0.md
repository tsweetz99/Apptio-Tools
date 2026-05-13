# Turbonomic Rightsizing Reports - Delivery Manifest

**Version**: 1.0.0  
**Release Date**: April 23, 2026  
**Package Name**: turbonomic-rightsizing-reports-v1.0.0

## Package Contents

### Delivery Archives

Two archive formats are provided for customer convenience:

- **turbonomic-rightsizing-reports-v1.0.0.tar.gz** (47 KB)
  - Linux/macOS preferred format
  - Preserves file permissions
  
- **turbonomic-rightsizing-reports-v1.0.0.zip** (50 KB)
  - Windows preferred format
  - Universal compatibility

Both archives contain identical content.

### Included Files

#### Core Scripts (5 files)
- `turbo_auth.py` - Shared authentication module
- `generate_rightsizing_report.py` - VM rightsizing report generator
- `generate_disk_optimization_report.py` - Disk optimization report generator
- `generate_monthly_action_plan.py` - Monthly action plan generator
- `generate_all_reports.py` - Unified report runner

#### Configuration Files (3 files)
- `customer_mapping.json` - Customer ID to friendly name mappings (156 entries)
- `customer_mapping.json.example` - Template for customer mapping
- `requirements.txt` - Python dependencies

#### Documentation (6 files)
- `README.md` - Comprehensive overview and quick start guide
- `INSTALLATION.md` - Detailed installation and setup instructions
- `QUICKSTART.md` - 5-minute getting started guide
- `CUSTOMER_MAPPING.md` - Customer mapping configuration guide
- `MONTHLY_ACTION_PLAN.md` - Monthly Action Plan documentation
- `CHANGELOG.md` - Version history and release notes

#### Legal (1 file)
- `LICENSE` - Apache 2.0 License

**Total Files**: 15  
**Total Size**: ~47-50 KB (compressed)

## System Requirements

- **Python**: 3.6 or higher
- **Operating System**: Windows, macOS, or Linux
- **Network**: Access to Turbonomic instance
- **Permissions**: Turbonomic user with read access to actions and entities

## Dependencies

All dependencies are listed in `requirements.txt`:
- pandas >= 1.3.0
- openpyxl >= 3.0.0
- requests >= 2.26.0
- urllib3 >= 1.26.0

## Installation

```bash
# Extract archive
tar -xzf turbonomic-rightsizing-reports-v1.0.0.tar.gz
# or
unzip turbonomic-rightsizing-reports-v1.0.0.zip

# Navigate to directory
cd turbonomic-rightsizing-report-delivery

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

```bash
# Generate all reports with single command
python3 generate_all_reports.py \
    --url https://your-turbo-instance.com \
    --username your-username \
    --password your-password
```

See `QUICKSTART.md` for detailed instructions.

## Features

### Report Types

1. **VM Rightsizing Report**
   - Current and recommended VM configurations
   - Monthly cost savings and net add costs
   - Environment categorization
   - Customer-friendly names
   - Clickable links to Turbonomic UI

2. **Disk Optimization Report**
   - Storage tier optimization recommendations
   - Policy violation highlighting
   - Monthly cost savings
   - Environment categorization

3. **Monthly Action Plan**
   - Categorized action plan for maintenance windows
   - Priority sorting
   - Customer ID and friendly name mapping
   - Clickable action detail links

### Key Capabilities

- ✅ Consolidated Excel workbooks with multiple environment sheets
- ✅ Professional formatting with color-coding and clickable links
- ✅ Flexible authentication (username/password, env vars, JSESSIONID)
- ✅ Customer mapping for business-friendly reporting
- ✅ Environment filtering (Dev, UAT, Pre-Prod, Prod, DR)
- ✅ Cost analysis with monthly savings calculations
- ✅ Policy violation highlighting

## Authentication Methods

The tools support three authentication methods:

1. **Username/Password** (Recommended)
2. **Environment Variables**
3. **JSESSIONID** (Manual session ID)

See `INSTALLATION.md` for detailed authentication setup.

## Customer Mapping

The package includes a pre-configured `customer_mapping.json` file with 156 customer ID mappings. This file maps CustomerID tags in Turbonomic to business-friendly names for stakeholder reporting.

To customize:
1. Edit `customer_mapping.json` with your specific mappings
2. Ensure VMs in Turbonomic have CustomerID tags configured
3. Run reports with `--customer-mapping customer_mapping.json`

See `CUSTOMER_MAPPING.md` for complete configuration guide.

## Output

Each report generates a timestamped Excel workbook with:
- Summary sheet with high-level statistics
- Comprehensive sheet with all data
- Separate sheets for each environment (Dev, UAT, Pre-Prod, Prod, DR, Unmapped)
- Professional formatting with frozen headers and optimized column widths

Example output files:
- `Rightsizing_Report_20260423_140000.xlsx`
- `Disk_Optimization_Report_20260423_140000.xlsx`
- `Monthly_Action_Plan_20260423_140000.xlsx`

## Support

For issues or questions:
1. Review the troubleshooting section in `README.md`
2. Check the detailed documentation files
3. Verify Turbonomic credentials and permissions
4. Ensure VMs have required tags configured

## Version Information

**Release**: 1.0.0  
**Date**: April 23, 2026  
**Compatibility**: Turbonomic 8.x API v3  
**License**: Apache 2.0

## Checksum Verification

To verify package integrity:

```bash
# For tar.gz
sha256sum turbonomic-rightsizing-reports-v1.0.0.tar.gz

# For zip
sha256sum turbonomic-rightsizing-reports-v1.0.0.zip
```

## Next Steps

1. Extract the archive
2. Review `README.md` for overview
3. Follow `QUICKSTART.md` for 5-minute setup
4. Configure `customer_mapping.json` if needed
5. Generate your first report

---

**Package prepared by**: IBM Turbonomic Tools Team  
**Delivery Date**: April 23, 2026  
**Package Status**: Production Ready