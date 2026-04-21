# Quick Start Guide - Turbonomic Rightsizing Reports

Get your rightsizing reports in 3 simple steps!

## Step 0: Setup (First Time Only)

If you get "pip: command not found", see **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** for detailed installation instructions.

**Quick fix for macOS:**
```bash
# Use pip3 instead of pip
pip3 install -r requirements.txt

# Or use python3 -m pip
python3 -m pip install -r requirements.txt
```

## Step 1: Install Dependencies

```bash
cd turbonomic/rightsizing-report

# Try one of these commands:
pip3 install -r requirements.txt
# or
python3 -m pip install -r requirements.txt
# or (minimal - CSV only)
pip3 install requests
```

## Step 2: Get Your Session ID

### Option A: Using curl

```bash
curl -X POST 'https://your-turbo-instance.com/api/v3/login?hateoas=true' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -d 'username=your-username&password=your-password' \
     -c cookies.txt

# Extract JSESSIONID
grep JSESSIONID cookies.txt | awk '{print $7}'
```

### Option B: Using Postman

1. Open the Postman collection: `../postman-collection/Turbo API.postman_collection.json`
2. Run the "Login" request
3. Copy the JSESSIONID from the response cookies

## Step 3: Generate Reports

### Single Report (All Environments)

```bash
# Use python3 on macOS
python3 generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --output all_environments.xlsx
```

### Individual Reports by Environment

```bash
# Make script executable
chmod +x generate_all_environment_reports.sh

# Run it
./generate_all_environment_reports.sh YOUR_SESSION_ID
```

This generates 6 reports:
- `Dev_rightsizing_report.xlsx`
- `UAT_rightsizing_report.xlsx`
- `Pre-Prod_rightsizing_report.xlsx`
- `Prod_rightsizing_report.xlsx`
- `DR_rightsizing_report.xlsx`
- `All_Environments_rightsizing_report.xlsx`

## Common Use Cases

### Production Downsizing Only

```bash
python3 generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --environment Prod \
    --action-type downsize \
    --output prod_downsizing.xlsx
```

### Development Upsizing Only

```bash
python3 generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --environment Dev \
    --action-type upsize \
    --output dev_upsizing.xlsx
```

### CSV Export (No Excel Dependencies)

```bash
python3 generate_rightsizing_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --output report.csv
```

## What You'll Get

Each report includes:

| Column | Description |
|--------|-------------|
| **Server Name** | VM/server identifier |
| **Customer Friendly Name** | Business/app name from CustomerID tag |
| **Current Configuration** | Current VM size (e.g., m5.large) |
| **Recommendation** | Suggested VM size |
| **Action Type** | Downsize, Upsize, or Resize |
| **Monthly Savings** | Cost reduction (downsizing) |
| **Net Add Cost** | Additional cost (upsizing in Prod) |
| **Environment** | Dev, UAT, Pre-Prod, Prod, or DR |

## Troubleshooting

### "pip: command not found" or "python: command not found"
See **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** for complete installation instructions.

Quick fix:
```bash
# Use pip3 and python3 instead
pip3 install -r requirements.txt
python3 generate_rightsizing_report.py --help
```

### "Error: 401 Unauthorized"
Your session expired. Get a new JSESSIONID (Step 2).

### "pandas not installed"
For Excel export, install pandas:
```bash
pip3 install pandas openpyxl
```
CSV export works without pandas.

### "No data in report"
- Check if there are pending recommendations in Turbonomic
- Try without filters first
- Verify VMs have proper tags (CustomerID, Environment)

## Next Steps

- See [README.md](./README.md) for detailed documentation
- Customize the script for your specific needs
- Schedule automated report generation with cron

## Support

For issues:
1. Check [README.md](./README.md) troubleshooting section
2. Verify your Turbonomic credentials
3. Ensure VMs have required tags configured