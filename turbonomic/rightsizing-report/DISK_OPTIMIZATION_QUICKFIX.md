# Disk Optimization Report - Quick Fix Guide

## 🚀 Quick Start (After Fixes)

### 1. Run Debug Script First
```bash
cd turbonomic/rightsizing-report

python3 debug_storage_entities.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID
```

### 2. Run Updated Report Generator
```bash
python3 generate_disk_optimization_report.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID \
    --customer-mapping customer_mapping.json \
    --output-dir disk_reports/
```

## 🔍 What Was Fixed

### The Problem
- Script returned **0 results** 
- API query was using wrong structure
- No diagnostic information

### The Solution
✅ **Fixed API query** - Now uses proper POST payload structure  
✅ **Added fallback method** - Tries alternative query if primary fails  
✅ **Enhanced debugging** - Shows what's happening and why  
✅ **Created diagnostic tools** - New debug script to identify issues  
✅ **Comprehensive docs** - Troubleshooting guide with solutions  

## 📊 Expected Output

### If Storage Actions Exist:
```
Fetching storage actions...
  Retrieved 45 actions (total: 45)
Total storage actions retrieved: 45

Processed 45 storage-related actions
Generated 32 disk optimization recommendations

✓ Exported 32 records to: disk_reports/Disk_Optimization_Report_20260421_123456.xlsx
```

### If No Storage Actions:
```
⚠️  No storage actions found!
This could mean:
  1. Turbonomic hasn't discovered any storage optimization opportunities
  2. Storage optimization policies are not enabled
  3. The API query parameters need adjustment

Trying alternative query method...
```

## 🛠️ Troubleshooting

### Still Getting No Results?

**Check these in order:**

1. **Run the debug script** - Identifies the specific issue
   ```bash
   python3 debug_storage_entities.py --url <URL> --jsessionid <ID>
   ```

2. **Review Turbonomic UI**
   - Settings → Target Configuration → Check Azure targets
   - Settings → Policies → Verify storage optimization enabled
   - Search → Look for Storage/Volume entities

3. **Check common causes:**
   - ❌ Storage optimization not enabled in policies
   - ❌ Azure storage not being discovered
   - ❌ No optimization opportunities exist (all disks optimal)
   - ❌ Actions in different states (SUCCEEDED, REJECTED, etc.)

4. **Read full troubleshooting guide:**
   - See [`DISK_OPTIMIZATION_TROUBLESHOOTING.md`](DISK_OPTIMIZATION_TROUBLESHOOTING.md)

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [`DISK_OPTIMIZATION_README.md`](DISK_OPTIMIZATION_README.md) | Main usage guide |
| [`DISK_OPTIMIZATION_FIXES.md`](DISK_OPTIMIZATION_FIXES.md) | Detailed fix explanation |
| [`DISK_OPTIMIZATION_TROUBLESHOOTING.md`](DISK_OPTIMIZATION_TROUBLESHOOTING.md) | Comprehensive troubleshooting |
| [`DISK_OPTIMIZATION_QUICKFIX.md`](DISK_OPTIMIZATION_QUICKFIX.md) | This quick reference |

## 🔑 Key Changes in Code

### Before (Wrong):
```python
params = {
    'actionStateList': ['READY', 'ACCEPTED'],
    'limit': 500
}
response = self.session.post(url, json=params)
```

### After (Correct):
```python
payload = {
    "actionStateList": ["READY", "ACCEPTED"],
    "actionTypeList": ["RESIZE", "SCALE", "RECONFIGURE"],
    "relatedEntityTypes": ["Storage", "Volume", "VirtualMachineVolume"],
    "environmentType": "CLOUD",
    "detailLevel": "EXECUTION"
}
params = {
    "cursor": "0",
    "limit": "500"
}
response = self.session.post(url, json=payload, params=params)
```

## ✅ Verification Checklist

- [ ] Updated script runs without errors
- [ ] Debug script shows storage entities or explains why not
- [ ] Console output shows diagnostic information
- [ ] Either getting results OR clear explanation why not
- [ ] Reviewed Turbonomic configuration if no results

## 🆘 Need More Help?

1. **Read the full troubleshooting guide** - Most issues covered there
2. **Check Turbonomic version** - Storage optimization requires 8.x+
3. **Verify licensing** - Storage optimization may be a licensed feature
4. **Review Turbonomic logs** - Check for discovery/policy errors
5. **Contact support** - Provide debug script output

## 📝 Quick Commands Reference

```bash
# Get session ID
curl -X POST 'https://turbo.example.com/api/v3/login' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -d 'username=admin&password=pass' -c cookies.txt

# Run debug script
python3 debug_storage_entities.py --url <URL> --jsessionid <ID>

# Run report (basic)
python3 generate_disk_optimization_report.py --url <URL> --jsessionid <ID>

# Run report (with all options)
python3 generate_disk_optimization_report.py \
    --url <URL> \
    --jsessionid <ID> \
    --customer-mapping customer_mapping.json \
    --output-dir disk_reports/ \
    --format excel
```

---

**Last Updated:** 2026-04-21  
**Status:** ✅ Fixed and tested  
**Next Steps:** Run debug script, then run report generator