# Changelog

All notable changes to the Turbonomic Rightsizing Report Generator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-23

### Initial Release

#### Added
- **VM Rightsizing Report Generator** - Comprehensive VM rightsizing recommendations with cost analysis
- **Disk Optimization Report Generator** - Storage tier optimization with policy enforcement
- **Monthly Action Plan Generator** - Categorized action plan for maintenance window execution
- **Unified Report Runner** - Generate all three reports with a single command
- **Shared Authentication Module** - Flexible authentication supporting username/password, environment variables, and JSESSIONID
- **Customer Mapping** - Map CustomerID tags to business-friendly names
- **Consolidated Excel Format** - Single workbook with multiple environment sheets
- **Professional Formatting** - Color-coded headers, clickable links, frozen headers, and optimized column widths
- **Environment Categorization** - Automatic filtering into Dev, UAT, Pre-Prod, Prod, DR, and Unmapped
- **Policy Violation Highlighting** - Red highlighting for Premium SSD usage in Dev/UAT environments
- **Cost Analysis** - Monthly savings calculations for downsizing and net add costs for upsizing
- **Summary Sheets** - High-level statistics and environment breakdowns

#### Documentation
- README.md - Comprehensive overview and quick start guide
- INSTALLATION.md - Detailed installation and setup instructions
- QUICKSTART.md - 5-minute getting started guide
- CUSTOMER_MAPPING.md - Customer mapping configuration guide
- MONTHLY_ACTION_PLAN.md - Monthly Action Plan documentation
- CHANGELOG.md - Version history and release notes

#### Features by Report Type

**VM Rightsizing Report**
- Current and recommended VM configurations
- Monthly cost savings and net add costs
- Environment categorization
- Customer-friendly names
- Clickable links to Turbonomic UI
- Action state and risk level tracking

**Disk Optimization Report**
- Current and recommended disk configurations
- Storage tier changes (Premium SSD, Standard SSD, Standard HDD)
- Policy violation highlighting
- Monthly cost savings
- Environment categorization
- Customer-friendly names

**Monthly Action Plan**
- Actions grouped by category (Resize, Disk, Network, etc.)
- Priority sorting (Critical → Low)
- Customer ID and friendly name mapping
- Clickable action detail links
- Policy violation highlighting
- Execution-ready format for maintenance windows

#### Technical Details
- Python 3.6+ compatibility
- Turbonomic API v3 support
- Excel output using openpyxl
- Data processing with pandas
- SSL verification disabled for self-signed certificates
- Session-based authentication with automatic validation

---

## Release Notes

### v1.0.0 - Initial Customer Delivery

This is the first production release of the Turbonomic Rightsizing Report Generator toolkit. All features have been tested and validated for customer delivery.

**Key Highlights:**
- Three comprehensive report types covering VM, disk, and action plan optimization
- Unified runner for generating all reports with a single command
- Flexible authentication supporting multiple methods
- Professional Excel formatting ready for stakeholder presentation
- Customer mapping for business-friendly reporting

**Compatibility:**
- Turbonomic 8.x
- API v3
- Python 3.6+

**Known Limitations:**
- OAuth2 authentication not supported (Turbonomic API v3 limitation)
- Session-based authentication requires periodic re-authentication
- Customer mapping requires CustomerID tags on VMs in Turbonomic

**Future Enhancements:**
- Additional report customization options
- Enhanced filtering capabilities
- Automated scheduling support
- API v4 support when available