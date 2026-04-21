# Debug Instructions - Fixing Missing Data

The report is missing data because the script needs to be updated to match your Turbonomic API's actual response structure. Let's debug this together.

## Step 1: Run the Debug Script

This will show us the actual structure of your Turbonomic API responses:

```bash
cd turbonomic/rightsizing-report

python3 debug_api_response.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --limit 3
```

This will:
1. Fetch 3 sample actions from Turbonomic
2. Print the structure to the console
3. Save the full response to `api_response_sample.json`

## Step 2: Share the Output

Please share:

1. **The console output** - Copy everything printed to the terminal
2. **The file `api_response_sample.json`** - This contains the full API response

With this information, I can update the script to correctly extract:
- Customer Friendly Name (CustomerID tag)
- Current Configuration (VM specs)
- Recommendation (new VM specs)
- Action Type (Upsize/Downsize)
- Monthly Savings
- Net Add Cost
- Environment tag

## Step 3: Issues to Fix

Based on your feedback, here's what needs to be corrected:

### Issue 1: Missing Customer Friendly Name (all N/A)
**Cause**: The CustomerID tag path is incorrect
**Need**: The actual path to tags in the API response

### Issue 2: Missing Current Configuration (all N/A)
**Cause**: The VM specs path is incorrect
**Need**: The actual path to CPU/memory or instance type

### Issue 3: Missing Monthly Savings and Net Add Cost
**Cause**: The cost/savings data path is incorrect
**Need**: The actual path to cost statistics

### Issue 4: Missing Environment (all N/A)
**Cause**: The Environment tag path is incorrect
**Need**: The actual path to environment tags

### Issue 5: Action Type shows "Other" instead of Upsize/Downsize
**Cause**: The logic to determine action type needs adjustment
**Need**: The actual fields that indicate upsize vs downsize

### Issue 6: Only 500 Records Returned
**Cause**: API pagination limit
**Solution**: Need to implement pagination to fetch all records

## What to Look For in the Debug Output

When you run the debug script, look for these sections in the output:

### 1. Tags Structure
```
Tags: [{"key": "CustomerID", "value": "..."}, ...]
```
or
```
Tags: {"CustomerID": "...", "Environment": "..."}
```

### 2. VM Configuration
Look for fields like:
- `instanceType`
- `numCPUs` / `cpuCount`
- `memoryMB` / `memory`
- `vmSize`

### 3. Cost/Savings Data
Look for fields like:
- `savings`
- `cost`
- `costImpact`
- `stats` array with cost information

### 4. Action Details
Look for fields that indicate upsize vs downsize:
- `riskSubCategory`
- `details`
- `description`
- Comparison of current vs new values

## Example Debug Output

Here's what you might see:

```
Fetching 3 actions from Turbonomic...
URL: https://your-turbo-instance.com/api/v3/markets/Market/actions

Retrieved 3 actions

================================================================================
FIRST ACTION STRUCTURE:
================================================================================
{
  "actionType": "RESIZE",
  "target": {
    "displayName": "web-server-01",
    "uuid": "abc123",
    "tags": [
      {"key": "CustomerID", "value": "Customer123"},
      {"key": "Environment", "value": "Prod"}
    ],
    "aspects": {
      "virtualMachineAspect": {
        "instanceType": "m5.large",
        "numCPUs": 2,
        "memoryMB": 8192
      }
    }
  },
  "newEntity": {
    "aspects": {
      "virtualMachineAspect": {
        "instanceType": "m5.medium"
      }
    }
  },
  "stats": [
    {"name": "savings", "value": 45.60}
  ]
}
```

## Once You Share the Output

I will:
1. Analyze the actual API response structure
2. Update the `generate_rightsizing_report.py` script with correct data paths
3. Add pagination support to fetch all records (not just 500)
4. Fix the upsize/downsize detection logic
5. Test and provide you with the updated script

## Alternative: Share Sample Data Directly

If you prefer, you can also:

1. Run the report generator and save output:
   ```bash
   python3 generate_rightsizing_report.py \
       --url https://your-turbo-instance.com \
       --jsessionid YOUR_SESSION_ID \
       --output sample.csv
   ```

2. Open the `api_response_sample.json` file created by the debug script

3. Share a few sample records (with sensitive data redacted if needed)

## Quick Test

To verify the debug script works:

```bash
# Test that it runs
python3 debug_api_response.py --help

# Run with your credentials
python3 debug_api_response.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --limit 3
```

The output will help me fix all the missing data issues!