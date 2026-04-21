# Turbonomic Rightsizing Report Generator

Generate detailed rightsizing recommendations reports from Turbonomic with customizable filtering and export options.

## Features

- **Comprehensive Data**: Extracts all key rightsizing information
- **Environment Filtering**: Filter by Dev, UAT, Pre-Prod, Prod, or DR
- **Action Type Filtering**: Filter by upsize or downsize recommendations
- **Multiple Export Formats**: CSV and Excel with formatting
- **Cost Analysis**: Monthly savings and net add cost calculations
- **Tag Support**: Extracts CustomerID and other custom tags

## Report Columns

| Column | Description |
|--------|-------------|
| Server Name | VM/entity display name |
| Customer Friendly Name | Business/application name from CustomerID tag |
| Current Configuration | Existing VM size/specs (instance type or vCPU/RAM) |
| Recommendation | Suggested VM size or configuration |
| Action Type | Downsize, Upsize, or Resize |
| Monthly Savings | Estimated monthly cost reduction (downsizing only) |
| Net Add Cost | Additional monthly cost (upsizing in Prod only) |
| Environment | Environment tag value (Dev, UAT, Pre-Prod, Prod, DR) |
| Action State | Current state (READY, QUEUED, etc.) |
| Risk | Risk severity level |
| UUID | Unique identifier for the entity |

## Prerequisites

### 1. Install Dependencies

```bash
# Install required Python packages
pip install requests pandas openpyxl

# Or use requirements file
pip install -r requirements.txt
```

### 2. Get Turbonomic Session ID

You need a valid JSESSIONID from Turbonomic. Get it by logging in:

```bash
# Using curl
curl -X POST 'https://your-turbo-instance.com/api/v3/login?hateoas=true' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -d 'username=your-username&password=your-password' \
     -c cookies.txt

# Extract JSESSIONID from cookies.txt
grep JSESSIONID cookies.txt
```

Or use the Postman collection in `../postman-collection/` to login and get the session ID.

## Usage

### Basic Usage

Generate report for all environments:

```bash
python generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid node01g4tqattmvscf1a9b0us8iw6xw232.node0
```

### Filter by Environment

Generate report for specific environment:

```bash
# Production only
python generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid <SESSION_ID> \
    --environment Prod

# Development only
python generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid <SESSION_ID> \
    --environment Dev
```

Available environments: `Dev`, `UAT`, `Pre-Prod`, `Prod`, `DR`

### Filter by Action Type

Get only downsizing or upsizing recommendations:

```bash
# Downsizing only
python generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid <SESSION_ID> \
    --action-type downsize

# Upsizing only
python generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid <SESSION_ID> \
    --action-type upsize
```

### Export to Excel

```bash
python generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid <SESSION_ID> \
    --output rightsizing_report.xlsx
```

### Export to CSV

```bash
python generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid <SESSION_ID> \
    --output rightsizing_report.csv
```

### Combined Filters

```bash
# Production downsizing recommendations only
python generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid <SESSION_ID> \
    --environment Prod \
    --action-type downsize \
    --output prod_downsizing.xlsx
```

## Generating Reports by Environment

To generate individual reports for each environment as requested:

```bash
#!/bin/bash
# generate_all_reports.sh

TURBO_URL="https://your-turbo-instance.com"
JSESSIONID="your-session-id"
OUTPUT_DIR="reports_$(date +%Y%m%d)"

mkdir -p "$OUTPUT_DIR"

# Generate report for each environment
for ENV in Dev UAT Pre-Prod Prod DR; do
    echo "Generating report for $ENV..."
    python generate_rightsizing_report.py \
        --url "$TURBO_URL" \
        --jsessionid "$JSESSIONID" \
        --environment "$ENV" \
        --output "$OUTPUT_DIR/${ENV}_rightsizing_report.xlsx"
done

echo "All reports generated in $OUTPUT_DIR/"
```

Make it executable and run:

```bash
chmod +x generate_all_reports.sh
./generate_all_reports.sh
```

## Output Examples

### Console Output

```
Fetching recommended actions from https://turbo.example.com/api/v3/markets/Market/actions...
Retrieved 150 recommended actions
Filtered to 45 actions for environment: Prod

================================================================================
RIGHTSIZING REPORT SUMMARY
================================================================================
Total Recommendations: 45
  - Downsizing: 32
  - Upsizing: 13
  - Other: 0

Estimated Monthly Savings: $12,450.00
Estimated Monthly Add Cost: $3,200.00
Net Monthly Impact: $9,250.00

Environment Breakdown:
  - Prod: 45
================================================================================

Report exported to: prod_rightsizing_report.xlsx
```

### Excel Report Preview

| Server Name | Customer Friendly Name | Current Configuration | Recommendation | Action Type | Monthly Savings | Net Add Cost |
|-------------|----------------------|---------------------|----------------|-------------|----------------|--------------|
| web-server-01 | CustomerApp123 | m5.large | m5.medium | Downsize | $45.60 | $0.00 |
| db-server-02 | CustomerDB456 | r5.xlarge | r5.2xlarge | Upsize | $0.00 | $182.40 |
| app-server-03 | CustomerAPI789 | c5.2xlarge | c5.xlarge | Downsize | $91.20 | $0.00 |

## Understanding the Data

### Action Type Determination

The script determines action type based on:
1. Risk sub-category (underutilized vs overutilized)
2. Action details and description
3. Comparison of current vs recommended resource values

### Cost Calculations

- **Monthly Savings**: Calculated for downsizing actions, estimated from Turbonomic's cost statistics
- **Net Add Cost**: Calculated for upsizing actions in Production environment only
- Values are rough monthly estimates based on daily/hourly rates from Turbonomic

### Tag Extraction

The script looks for these tags on VMs:
- `CustomerID`: Used for "Customer Friendly Name" column
- `Environment`: Used for environment filtering (Dev, UAT, Pre-Prod, Prod, DR)

If tags are not found, "N/A" is displayed.

## Troubleshooting

### Issue: "Error fetching actions: 401"

**Solution**: Your JSESSIONID has expired. Re-authenticate to get a new session ID.

```bash
# Get new session ID
curl -X POST 'https://your-turbo-instance.com/api/v3/login' \
     -d 'username=your-username&password=your-password'
```

### Issue: "pandas not installed"

**Solution**: Install pandas and openpyxl for Excel export:

```bash
pip install pandas openpyxl
```

CSV export will still work without pandas.

### Issue: No data in report

**Possible causes**:
1. No pending recommendations in Turbonomic
2. Environment filter too restrictive
3. Action type filter excluding all results
4. Tags not properly configured on VMs

**Solution**: Try without filters first:

```bash
python generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid <SESSION_ID>
```

### Issue: Missing CustomerID or Environment data

**Solution**: Ensure VMs in Turbonomic have proper tags:
- Add `CustomerID` tag with business/application name
- Add `Environment` tag with value: Dev, UAT, Pre-Prod, Prod, or DR

## Customization

### Adding Custom Columns

Edit the `generate_report_data()` method in the script to add custom fields:

```python
row = {
    'Server Name': target.get('displayName', 'N/A'),
    'Custom Field': self._get_tag_value(target, 'CustomTag'),
    # ... other fields
}
```

### Modifying Cost Calculations

Edit the `_calculate_monthly_savings()` and `_calculate_net_add_cost()` methods to adjust cost calculation logic.

### Changing Environment Values

Modify the `--environment` choices in the argument parser to match your organization's environment naming.

## API Reference

The script uses these Turbonomic API endpoints:

- **POST** `/api/v3/markets/Market/actions` - Get recommended actions
  - Filters by action state (READY, QUEUED, etc.)
  - Filters by action type (RESIZE, SCALE)
  - Filters by entity type (VirtualMachine)

## Additional Resources

- [Turbonomic API Documentation](https://www.ibm.com/docs/en/tarm/8.19.3)
- [Postman Collection](../postman-collection/Turbo%20API.postman_collection.json)
- [Turbonomic Login Guide](../AUDITLOGS_README.md#getting-your-jsessionid)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your Turbonomic credentials and permissions
3. Ensure VMs have proper tags configured
4. Review the console output for specific error messages