# Usage Guide - V3 (Azure-Focused with Environment Parsing)

## What's New in V3

✅ **Azure-only filtering** - Focuses on Azure resources only  
✅ **BusinessAccount extraction** - Pulls account name from cloudAspect  
✅ **Smart environment parsing** - Determines environment from BusinessAccount name  
✅ **Fallback logic** - Uses environment tag if account name doesn't match  
✅ **Automatic report generation** - Creates 1 comprehensive + 6 environment-specific reports  
✅ **Cloud provider detection** - Identifies Azure, AWS, GCP  

## Quick Start

```bash
cd turbonomic/rightsizing-report

# Generate all reports (comprehensive + by environment)
python3 generate_rightsizing_report_v3.py \
    --url https://cldp-duckcreek.apptio.turbonomic.ibmappdomain.cloud \
    --jsessionid YOUR_SESSION_ID \
    --output-dir reports/
```

## What Gets Generated

Running the script creates **8 reports**:

1. **Comprehensive_Rightsizing_Report_TIMESTAMP.xlsx** - All Azure actions
2. **Summary_Report_TIMESTAMP.txt** - Executive summary with statistics (text format)
3. **Dev_Rightsizing_Report_TIMESTAMP.xlsx** - Development environment only
4. **UAT_Rightsizing_Report_TIMESTAMP.xlsx** - UAT environment only
5. **Pre-Prod_Rightsizing_Report_TIMESTAMP.xlsx** - Pre-Production environment only
6. **Prod_Rightsizing_Report_TIMESTAMP.xlsx** - Production environment only
7. **DR_Rightsizing_Report_TIMESTAMP.xlsx** - Disaster Recovery environment only
8. **Unmapped_Rightsizing_Report_TIMESTAMP.xlsx** - Resources that couldn't be categorized

## Environment Detection Logic

The script uses a **3-tier fallback approach**:

### Tier 1: Parse from BusinessAccount Name (Primary)

Looks for these patterns in the account name:

| Pattern | Environment |
|---------|-------------|
| PRODUCTION, PRD-, -PRD- | **Prod** |
| PRE-PROD, PREPROD | **Pre-Prod** |
| DR-, -DR-, DISASTER RECOVERY | **DR** |
| UAT, USER ACCEPTANCE | **UAT** |
| DEVELOPMENT, DEV-, -DEV- | **Dev** |

**Example:**
- `Duck Creek On Demand Production` → **Prod**
- `Azure Dev Subscription` → **Dev**
- `UAT Environment` → **UAT**

### Tier 2: Fall Back to Environment Tag

If BusinessAccount name doesn't match, checks the `environment` tag:
- Tag value: "Production" → **Prod**
- Tag value: "Development" → **Dev**
- etc.

### Tier 3: Mark as Unmapped

If neither works, the resource is marked as **Unmapped** for manual review.

## Report Columns

Each report includes:

| Column | Description | Source |
|--------|-------------|--------|
| Server Name | VM display name | `target.displayName` |
| Customer ID | Customer identifier | `tags.CustomerID[0]` |
| Customer Friendly Name | Mapped customer name | Mapping file or CustomerID |
| Current Configuration | Current instance type | `currentEntity.displayName` |
| Recommendation | Suggested instance type | `newEntity.displayName` |
| Action Type | Upsize/Downsize/Resize | Calculated |
| Monthly Savings | Cost reduction | `stats` ($/h * 730) |
| Net Add Cost | Additional cost (Prod upsizing) | `stats` ($/h * 730) |
| Environment | Parsed environment | BusinessAccount → Tag → Unmapped |
| **Turbonomic Link** | Direct link to action in Turbonomic UI | Generated from action UUID |
| **Business Account** | Azure account name | `cloudAspect.businessAccount.displayName` |
| **Cloud Provider** | Azure/AWS/GCP | `discoveredBy.type` |
| Action State | READY/QUEUED/etc | `actionState` |
| Risk | MINOR/MAJOR/etc | `risk.severity` |
| Details | Action description | `details` |
| UUID | Unique identifier | `target.uuid` |

## Summary Report

The **Summary_Report.txt** provides an executive overview in an easy-to-read text format with:

### Overall Summary
- Total recommendations count
- Downsizing actions (count and percentage)
- Upsizing actions (count and percentage)
- Other actions (count and percentage)

### Financial Impact
- Estimated monthly savings (from downsizing)
- Estimated monthly add cost (from upsizing in Prod)
- Net monthly impact (savings minus add cost)

### Environment Breakdown
For each environment (Dev, UAT, Pre-Prod, Prod, DR, Unmapped):
- Total action count and percentage
- Downsizing count with savings amount
- Upsizing count with add cost amount
- Net impact per environment

This report is ideal for:
- Executive presentations
- Budget planning discussions
- Quick environment-level analysis

## Customer Name Mapping

The script supports mapping customer IDs to friendly names using a JSON mapping file.

### Mapping File Format

Create a JSON file with customer ID to name mappings:

```json
{
  "10061075": "AIG A&H",
  "10060801": "AIG CL NA",
  "10061026": "AIG PCG",
  "10059376": "PURE",
  "10058664": "Pacific Specialty"
}
```

### Using the Mapping File

```bash
python3 generate_rightsizing_report_v3.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --customer-mapping customer_mapping.json \
    --output-dir ./reports
```

### How It Works

1. **With Mapping File**: Customer IDs are automatically translated to friendly names
   - Customer ID: `10061075` → Customer Friendly Name: `AIG A&H`
   - Customer ID: `10059376` → Customer Friendly Name: `PURE`

2. **Without Mapping File**: Customer IDs are displayed as-is
   - Customer ID: `10061075` → Customer Friendly Name: `10061075`

3. **Unmapped IDs**: If an ID isn't in the mapping file, the original ID is shown
   - Customer ID: `99999999` → Customer Friendly Name: `99999999`

### Report Columns

When using customer mapping, reports include both columns:
- **Customer ID**: The original CustomerID tag value
- **Customer Friendly Name**: The mapped name (or ID if no mapping exists)

This allows you to:
- Sort/filter by customer name
- Still reference the original ID if needed
- Identify unmapped customers easily

### Sample Mapping File

A sample mapping file [`customer_mapping.json`](customer_mapping.json) is included in the repository with common customer mappings.

- Tracking optimization opportunities

## Command Options

```bash
python3 generate_rightsizing_report_v3.py \
    --url <TURBO_URL> \
    --jsessionid <SESSION_ID> \
    [OPTIONS]
```

### Required Arguments

- `--url` - Turbonomic instance URL
- `--jsessionid` - Session ID from login

### Optional Arguments

- `--output-dir <DIR>` - Output directory (default: current directory)
- `--action-type <TYPE>` - Filter by `upsize` or `downsize`
- `--format <FORMAT>` - Output format: `excel` (default) or `csv`
- `--all-clouds` - Include all cloud providers (not just Azure)
- `--customer-mapping <FILE>` - Path to customer ID to name mapping JSON file

## Examples

### Example 1: Basic Usage (Azure only, all environments)

```bash
python3 generate_rightsizing_report_v3.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --output-dir ./reports
```

**Output:**
- 8 Excel files in `./reports/` directory (1 comprehensive + 1 summary + 6 environment-specific)
### Example 5: With Customer Name Mapping

```bash
python3 generate_rightsizing_report_v3.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --customer-mapping customer_mapping.json \
    --output-dir ./reports
```

- Console summary for each environment

### Example 2: Downsizing Only

```bash
python3 generate_rightsizing_report_v3.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --action-type downsize \
    --output-dir ./downsizing_reports
```

### Example 3: CSV Format

```bash
python3 generate_rightsizing_report_v3.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --format csv \
    --output-dir ./csv_reports
```

### Example 4: All Cloud Providers

```bash
python3 generate_rightsizing_report_v3.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --all-clouds \
    --output-dir ./all_clouds
```

## Console Output Example

```
Fetching recommended actions from https://your-turbo-instance.com/api/v3/markets/Market/actions...
  Retrieved 500 actions (total: 500)
  Retrieved 342 actions (total: 842)
Total actions retrieved: 842

  ✓ Exported 842 records to: reports/Comprehensive_Rightsizing_Report_20260421_123456.xlsx

================================================================================
COMPREHENSIVE REPORT SUMMARY
================================================================================
Total Recommendations: 842
  - Downsizing: 523
  - Upsizing: 287
  - Other: 32

Estimated Monthly Savings: $45,230.50
Estimated Monthly Add Cost: $12,450.00
Net Monthly Impact: $32,780.50

Environment Breakdown:
  - Dev: 145
  - DR: 23
  - Prod: 456
  - UAT: 89
  - Unmapped: 129
================================================================================

Generating summary report...
  ✓ Summary report exported to: reports/Summary_Report_20260421_123456.txt

Generating environment-specific reports...
  ✓ Exported 145 records to: reports/Dev_Rightsizing_Report_20260421_123456.xlsx
  ✓ Exported 89 records to: reports/UAT_Rightsizing_Report_20260421_123456.xlsx
  ℹ No data for Pre-Prod environment
  ✓ Exported 456 records to: reports/Prod_Rightsizing_Report_20260421_123456.xlsx
  ✓ Exported 23 records to: reports/DR_Rightsizing_Report_20260421_123456.xlsx
  ✓ Exported 129 records to: reports/Unmapped_Rightsizing_Report_20260421_123456.xlsx

✓ All reports generated in: reports/
```

## Customizing Environment Patterns

To customize how environments are detected from BusinessAccount names, edit the `_parse_environment_from_account()` method:

```python
def _parse_environment_from_account(self, account_name: str) -> Optional[str]:
    account_upper = account_name.upper()
    
    # Add your custom patterns here
    if 'YOUR_CUSTOM_PATTERN' in account_upper:
        return 'YourEnvironment'
    
    # ... existing patterns ...
```

## Troubleshooting

### Issue: Many resources in "Unmapped"

**Solution:** Check the Unmapped report and identify common patterns in BusinessAccount names. Add those patterns to `_parse_environment_from_account()`.

### Issue: Wrong environment assignments

**Solution:** Review the pattern matching logic. More specific patterns should come first (e.g., check for "PRE-PROD" before "PROD").

### Issue: No Azure resources found

**Solution:** 
- Verify you have Azure resources in Turbonomic
- Try with `--all-clouds` to see all providers
- Check the cloud provider detection logic

## Comparison: V2 vs V3

| Feature | V2 | V3 |
|---------|----|----|
| Cloud filtering | All clouds | Azure-only (optional all) |
| Environment source | Tag only | BusinessAccount → Tag → Unmapped |
| BusinessAccount column | ❌ No | ✅ Yes |
| Cloud Provider column | ❌ No | ✅ Yes |
| Auto environment reports | ❌ No | ✅ Yes (6 reports) |
| Unmapped tracking | ❌ No | ✅ Yes |

## Next Steps

1. Run the script and review the comprehensive report
2. Check the Unmapped report for resources needing attention
3. Customize environment patterns if needed
4. Schedule automated runs for regular reporting

## Support

For issues or questions, see:
- [SETUP_GUIDE.md](./SETUP_GUIDE.md) - Installation help
- [DEBUG_INSTRUCTIONS.md](./DEBUG_INSTRUCTIONS.md) - Debugging API issues
- [README.md](./README.md) - Full documentation