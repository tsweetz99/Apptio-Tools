# Customer Name Mapping Guide

This guide explains how to use customer ID to name mapping in the Turbonomic rightsizing report generator.

## Overview

The customer mapping feature allows you to automatically translate customer IDs (like `10061075`) into friendly names (like `AIG A&H`) in your reports. This makes reports more readable and easier to share with stakeholders.

## Quick Start

1. **Use the provided mapping file**:
   ```bash
   python3 generate_rightsizing_report_v3.py \
       --url https://your-turbo-instance.com \
       --jsessionid YOUR_SESSION_ID \
       --customer-mapping customer_mapping.json \
       --output-dir ./reports
   ```

2. **Check the output**:
   - Reports will include both "Customer ID" and "Customer Friendly Name" columns
   - Mapped IDs show friendly names
   - Unmapped IDs show the original ID

## Mapping File Format

The mapping file is a simple JSON file with customer ID to name pairs:

```json
{
  "10061075": "AIG A&H",
  "10060801": "AIG CL NA",
  "10061026": "AIG PCG",
  "10059376": "PURE",
  "10058664": "Pacific Specialty"
}
```

### Key Points:
- Customer IDs are strings (in quotes)
- Names can contain spaces and special characters
- File must be valid JSON

## Creating Your Own Mapping File

### Method 1: Start from Scratch

Create a new JSON file:

```json
{
  "customer_id_1": "Customer Name 1",
  "customer_id_2": "Customer Name 2"
}
```

### Method 2: Convert from Turbonomic Business Dimension

If you have a Turbonomic business dimension JSON (like the one you provided), you can extract the mappings:

1. Save your business dimension JSON to a file
2. Use this Python script to convert it:

```python
import json

# Load the business dimension JSON
with open('business_dimension.json', 'r') as f:
    data = json.load(f)

# Extract mappings
mappings = {}
for statement in data['result']['statements']:
    # Extract customer ID from matchExpression
    match = statement['matchExpression']
    if "TAG['customer'] ==" in match:
        customer_id = match.split("'")[3]  # Extract ID between quotes
        
        # Extract customer name from valueExpression
        customer_name = statement['valueExpression'].strip("'")
        
        mappings[customer_id] = customer_name

# Save to mapping file
with open('customer_mapping.json', 'w') as f:
    json.dump(mappings, f, indent=2)

print(f"Created mapping file with {len(mappings)} entries")
```

### Method 3: Update Existing Mapping

To add new mappings to an existing file:

```python
import json

# Load existing mappings
with open('customer_mapping.json', 'r') as f:
    mappings = json.load(f)

# Add new mappings
mappings['10099999'] = 'New Customer Name'
mappings['10088888'] = 'Another Customer'

# Save updated mappings
with open('customer_mapping.json', 'w') as f:
    json.dump(mappings, f, indent=2)
```

## Report Output

### With Mapping File

| Customer ID | Customer Friendly Name | Server Name | ... |
|-------------|------------------------|-------------|-----|
| 10061075 | AIG A&H | server-001 | ... |
| 10059376 | PURE | server-002 | ... |
| 99999999 | 99999999 | server-003 | ... |

Note: Unmapped IDs (like `99999999`) show the ID in both columns.

### Without Mapping File

| Customer ID | Customer Friendly Name | Server Name | ... |
|-------------|------------------------|-------------|-----|
| 10061075 | 10061075 | server-001 | ... |
| 10059376 | 10059376 | server-002 | ... |
| 99999999 | 99999999 | server-003 | ... |

## Troubleshooting

### Issue: "Warning: Customer mapping file not found"

**Solution**: Check the file path. Use absolute path or ensure the file is in the correct location:
```bash
# Absolute path
--customer-mapping /full/path/to/customer_mapping.json

# Relative path (from current directory)
--customer-mapping ./customer_mapping.json
```

### Issue: "Warning: Invalid JSON in customer mapping file"

**Solution**: Validate your JSON:
1. Use a JSON validator (e.g., jsonlint.com)
2. Check for:
   - Missing commas between entries
   - Missing quotes around keys/values
   - Trailing commas (not allowed in JSON)

### Issue: Some customers not mapping

**Solution**: 
1. Check if the customer ID in your mapping file exactly matches the ID in Turbonomic
2. IDs are case-sensitive
3. Check for extra spaces or special characters

### Issue: Special characters in customer names

**Solution**: JSON supports Unicode. Ensure your file is saved as UTF-8:
```json
{
  "10062794": "AXA Seguros, S.A. de C.V.",
  "10062781": "Private Client Select Insurance Services, LLC"
}
```

## Best Practices

1. **Keep mapping file updated**: Regularly update with new customers
2. **Use version control**: Track changes to your mapping file
3. **Document special cases**: Add comments in a separate README if needed
4. **Backup regularly**: Keep a backup of your mapping file
5. **Validate before use**: Test with a small dataset first

## Example Workflow

1. **Initial Setup**:
   ```bash
   # Copy the sample mapping file
   cp customer_mapping.json my_customer_mapping.json
   
   # Edit to add your customers
   nano my_customer_mapping.json
   ```

2. **Generate Reports**:
   ```bash
   python3 generate_rightsizing_report_v3.py \
       --url https://your-turbo-instance.com \
       --jsessionid YOUR_SESSION_ID \
       --customer-mapping my_customer_mapping.json \
       --output-dir ./reports
   ```

3. **Review Output**:
   - Check for unmapped customers (where ID = Name)
   - Add missing mappings to your file
   - Regenerate reports if needed

## Included Mapping File

The repository includes [`customer_mapping.json`](customer_mapping.json) with 170+ customer mappings extracted from a Turbonomic business dimension. You can:
- Use it as-is
- Customize it for your environment
- Use it as a template for your own mappings

## Support

For issues or questions:
- See [USAGE_V3.md](USAGE_V3.md) for general usage
- See [SETUP_GUIDE.md](SETUP_GUIDE.md) for installation help
- Check [DEBUG_INSTRUCTIONS.md](DEBUG_INSTRUCTIONS.md) for troubleshooting