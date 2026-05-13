# Quick Start Guide - Turbonomic Rightsizing Reports

Get your first report in 5 minutes!

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.6+ installed (`python --version` or `python3 --version`)
- ✅ Access to your Turbonomic instance
- ✅ Turbonomic username and password

**Need to install?** See [INSTALLATION.md](INSTALLATION.md) for detailed setup.

## 3-Step Quick Start

### Step 1: Install Dependencies (2 minutes)

```bash
cd turbonomic-rightsizing-report-delivery

# Try one of these commands:
pip install -r requirements.txt
# or
pip3 install -r requirements.txt
# or
python3 -m pip install -r requirements.txt
```

### Step 2: Get Your Session ID (1 minute)

```bash
# Replace with your Turbonomic URL and credentials
curl -X POST 'https://your-turbo-instance.com/api/v3/login' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -d 'username=YOUR_USERNAME&password=YOUR_PASSWORD' \
     -c cookies.txt

# Extract the session ID
grep JSESSIONID cookies.txt | awk '{print $7}'
```

**Copy the session ID** - you'll need it for the next step.

### Step 3: Generate Your First Report (2 minutes)

```bash
# Replace YOUR_SESSION_ID with the ID from Step 2
python generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --output my_first_report.xlsx
```

**Done!** Open `my_first_report.xlsx` to see your rightsizing recommendations.

## What You'll See

Your report includes:

| Column | What It Shows |
|--------|---------------|
| **Server Name** | VM identifier |
| **Current Configuration** | Current VM size (e.g., m5.large) |
| **Recommendation** | Suggested VM size |
| **Action Type** | Downsize, Upsize, or Resize |
| **Monthly Savings** | Cost reduction for downsizing |
| **Environment** | Dev, UAT, Pre-Prod, Prod, or DR |

## Common Commands

### All Environments Report

```bash
python generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --output all_environments.xlsx
```

### Production Only

```bash
python generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --environment Prod \
    --output production_report.xlsx
```

### Downsizing Opportunities (Cost Savings)

```bash
python generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --action-type downsize \
    --output cost_savings.xlsx
```

### Generate All Environment Reports at Once


### Monthly Action Plan (NEW!)

Generate a categorized action plan for monthly maintenance windows:

```bash
python3 generate_monthly_action_plan.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID
```

Creates a report with three sheets:
- **Must-Do Actions**: Policy violations + validated downsizing
- **Cost Optimization**: Recommended cost savings
- **Reliability Investment**: Prod upsizing requiring budget

See [MONTHLY_ACTION_PLAN.md](MONTHLY_ACTION_PLAN.md) for detailed usage.

```bash
# Make script executable
chmod +x generate_all_environment_reports.sh

# Run it (creates 6 reports)
./generate_all_environment_reports.sh YOUR_SESSION_ID
```

This creates:
- `Dev_Rightsizing_Report.xlsx`
- `UAT_Rightsizing_Report.xlsx`
- `Pre-Prod_Rightsizing_Report.xlsx`
- `Prod_Rightsizing_Report.xlsx`
- `DR_Rightsizing_Report.xlsx`
- `Comprehensive_Rightsizing_Report.xlsx` (all environments)

## Using Different Versions

### Version 1 (Basic) - Recommended for Getting Started

```bash
python generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --output report.xlsx
```

### Version 2 (Enhanced Filtering)

```bash
python generate_rightsizing_report_v2.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --output report.xlsx
```

### Version 3 (Customer Mapping)

```bash
# First, set up customer mapping
cp customer_mapping.json.example customer_mapping.json
# Edit customer_mapping.json with your mappings

# Generate report with friendly names
python generate_rightsizing_report_v3.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --output customer_report.xlsx
```

### Disk Optimization Report

```bash
python generate_disk_optimization_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --output disk_report.xlsx
```

## Quick Troubleshooting

### "python: command not found"

**Fix**: Use `python3` instead:
```bash
python3 generate_rightsizing_report.py --help
```

### "pip: command not found"

**Fix**: Use `pip3` or `python3 -m pip`:
```bash
pip3 install -r requirements.txt
```

### "Error: 401 Unauthorized"

**Fix**: Your session expired. Get a new session ID (repeat Step 2).

### "pandas not installed"

**Fix**: Install dependencies:
```bash
pip install pandas openpyxl
```

### "No data in report"

**Possible causes:**
- No pending recommendations in Turbonomic
- Environment filter too restrictive
- VMs missing required tags

**Fix**: Try without filters:
```bash
python generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --output test.xlsx
```

## Platform-Specific Notes

### macOS Users

Use `python3` and `pip3`:
```bash
pip3 install -r requirements.txt
python3 generate_rightsizing_report.py --help
```

### Windows Users

Use `python` and `pip`:
```bash
pip install -r requirements.txt
python generate_rightsizing_report.py --help
```

### Linux Users

Use `python3` and `pip3`:
```bash
pip3 install -r requirements.txt
python3 generate_rightsizing_report.py --help
```

## Available Options

View all options for any script:

```bash
python generate_rightsizing_report.py --help
```

Common options:
- `--url` - Turbonomic instance URL (required)
- `--jsessionid` - Session ID from login (required)
- `--output` - Output filename (default: report.xlsx)
- `--environment` - Filter by environment (Dev, UAT, Pre-Prod, Prod, DR)
- `--action-type` - Filter by action type (downsize, upsize)

## Next Steps

Now that you have your first report:

1. **Explore Features**: Try different filters and options
2. **Customer Mapping**: Set up friendly names for customer-facing reports
3. **Automation**: Schedule regular report generation
4. **Advanced Usage**: See [README.md](README.md) for all features

## Getting Help

- **Installation Issues**: See [INSTALLATION.md](INSTALLATION.md)
- **All Features**: See [README.md](README.md)
- **Customer Mapping**: See [CUSTOMER_MAPPING.md](CUSTOMER_MAPPING.md)

## Tips for Success

1. **Session IDs expire** - Get a fresh one if you see 401 errors
2. **Start simple** - Use basic commands first, add filters later
3. **Check your data** - Ensure VMs have Environment tags in Turbonomic
4. **Use batch scripts** - Generate all environment reports at once
5. **Save your commands** - Create shell scripts for repeated tasks

## Example Workflow

Here's a typical workflow for monthly reporting:

```bash
# 1. Get fresh session ID
curl -X POST 'https://turbo.example.com/api/v3/login' \
     -d 'username=admin&password=pass' -c cookies.txt
SESSION_ID=$(grep JSESSIONID cookies.txt | awk '{print $7}')

# 2. Generate all environment reports
./generate_all_environment_reports.sh $SESSION_ID

# 3. Generate cost savings report
python generate_rightsizing_report.py \
    --url https://turbo.example.com \
    --jsessionid $SESSION_ID \
    --action-type downsize \
    --output monthly_savings_$(date +%Y%m).xlsx

# 4. Generate disk optimization report
python generate_disk_optimization_report.py \
    --url https://turbo.example.com \
    --jsessionid $SESSION_ID \
    --output disk_optimization_$(date +%Y%m).xlsx
```

---

**Questions?** Check [README.md](README.md) for comprehensive documentation or [INSTALLATION.md](INSTALLATION.md) for setup help.