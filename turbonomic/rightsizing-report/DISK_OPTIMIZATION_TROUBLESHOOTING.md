# Disk Optimization Report Troubleshooting Guide

## Issue: No Storage Actions Returned

If the disk optimization report returns no results, follow this diagnostic process:

## Step 1: Run the Storage Discovery Debug Script

This script will help identify what storage entities and actions are available in your Turbonomic instance:

```bash
cd turbonomic/rightsizing-report

python3 debug_storage_entities.py \
    --url https://your-turbo-instance.com \
    --jsessionid YOUR_SESSION_ID
```

**What it checks:**
1. Searches for different storage entity types (Storage, Volume, VirtualMachineVolume, etc.)
2. Analyzes all available actions to find storage-related ones
3. Tests specific storage action queries
4. Checks VM actions for disk tier information

## Step 2: Understand the Results

### Scenario A: No Storage Entities Found

**Output:**
```
✗ Storage: 0 entities
✗ Volume: 0 entities
✗ VirtualMachineVolume: 0 entities
```

**Possible Causes:**
1. **Turbonomic hasn't discovered storage resources yet**
   - Check if Azure storage accounts are being discovered
   - Verify Azure target configuration in Turbonomic
   - Wait for discovery cycle to complete (can take 10-30 minutes)

2. **Storage optimization is not enabled**
   - Check Turbonomic policies for storage optimization
   - Verify that storage tier recommendations are enabled
   - Review automation policies for storage actions

3. **Permissions issue**
   - Verify the Azure service principal has storage read permissions
   - Check Turbonomic target credentials

**Solution:**
- Review Turbonomic target configuration
- Enable storage optimization in policies
- Wait for next discovery cycle

### Scenario B: Storage Entities Found, But No Actions

**Output:**
```
✓ Storage: Found 150 entities
✓ Volume: Found 75 entities
Storage-related actions found: 0
```

**Possible Causes:**
1. **No optimization opportunities detected**
   - All disks are already optimally configured
   - Turbonomic hasn't identified any tier change opportunities

2. **Actions are in different states**
   - Actions might be in SUCCEEDED, FAILED, or REJECTED states
   - Try querying for all action states

3. **Policy restrictions**
   - Storage optimization policies might be set to "recommend" only
   - Actions might be disabled for certain environments

**Solution:**
```bash
# Check for actions in all states
python3 debug_storage_entities.py --url <URL> --jsessionid <ID> --all-states
```

### Scenario C: Actions Found, But Wrong Type

**Output:**
```
Target Class Distribution:
  - VirtualMachine: 450
  - VirtualMachineSpec: 120
  - Storage: 0
```

**This means:**
- Turbonomic is generating VM rightsizing actions
- But NOT generating storage tier optimization actions
- Storage tier changes might be bundled with VM actions

**Solution:**
Check if disk tier information is embedded in VM actions:
- Look at VM action details for disk/storage mentions
- Disk tier changes might be part of VM resize recommendations
- May need to extract disk info from VM actions instead

## Step 3: Check Turbonomic Configuration

### Verify Storage Discovery

1. **Log into Turbonomic UI**
2. **Navigate to:** Settings → Target Configuration
3. **Check Azure targets:**
   - Are storage accounts being discovered?
   - Are managed disks visible?
   - Check last discovery time

### Verify Storage Policies

1. **Navigate to:** Settings → Policies
2. **Check Automation Policies:**
   - Are storage actions enabled?
   - What's the action mode (Manual/Recommend/Automatic)?
   - Are there environment-specific restrictions?

3. **Check Placement Policies:**
   - Are there policies affecting storage tier selection?
   - Are certain tiers restricted?

## Step 4: Alternative Approaches

### Approach 1: Query All Actions and Filter

If storage-specific queries don't work, try getting all actions:

```python
# In generate_disk_optimization_report.py
payload = {
    "actionStateList": ["READY", "ACCEPTED", "QUEUED", "IN_PROGRESS"],
    "environmentType": "CLOUD",
    "detailLevel": "EXECUTION"
}
# Then filter for storage in the results
```

### Approach 2: Use Search API

Query storage entities directly, then check for actions:

```python
# Search for storage entities
search_url = f"{turbo_url}/api/v3/search"
payload = {
    "className": "Storage",
    "environmentType": "CLOUD"
}
# Then query actions for each storage entity
```

### Approach 3: Extract from VM Actions

If disk tier changes are part of VM actions:

```python
# Query VM actions
# Look for disk tier information in:
# - action.details
# - action.currentEntity
# - action.newEntity
# Extract disk tier recommendations from VM resize actions
```

## Step 5: API Documentation Reference

According to IBM Turbonomic API documentation:

### Storage Entity Types
- `Storage` - Storage containers/accounts
- `Volume` - Individual volumes/disks
- `VirtualMachineVolume` - VM-attached volumes
- `VirtualDisk` - Virtual disk entities

### Action Types for Storage
- `RESIZE` - Change storage size
- `SCALE` - Scale storage capacity
- `RECONFIGURE` - Change storage configuration (including tier)
- `MOVE` - Move storage to different tier/location

### Query Parameters
```json
{
  "actionStateList": ["READY", "ACCEPTED", "QUEUED", "IN_PROGRESS"],
  "actionTypeList": ["RESIZE", "SCALE", "RECONFIGURE"],
  "relatedEntityTypes": ["Storage", "Volume", "VirtualMachineVolume"],
  "environmentType": "CLOUD",
  "detailLevel": "EXECUTION"
}
```

## Step 6: Contact Support

If none of the above resolves the issue:

1. **Collect debug output:**
   ```bash
   python3 debug_storage_entities.py --url <URL> --jsessionid <ID> > debug_output.txt
   ```

2. **Check Turbonomic version:**
   - Some storage features require specific Turbonomic versions
   - Azure disk tier optimization was added in version 8.x

3. **Review Turbonomic logs:**
   - Check for discovery errors
   - Look for policy evaluation issues
   - Review action generation logs

## Common Solutions Summary

| Issue | Solution |
|-------|----------|
| No storage entities | Wait for discovery, check Azure target config |
| Entities but no actions | Enable storage optimization policies |
| Wrong action types | Check if disk info is in VM actions |
| API errors | Verify JSESSIONID, check permissions |
| Empty results | Verify Azure has disks that need optimization |

## Updated Script Features

The updated `generate_disk_optimization_report.py` now includes:

1. **Better API query** - Uses proper payload structure with entity types
2. **Fallback method** - Tries alternative query if primary fails
3. **Enhanced debugging** - Shows what's being queried and found
4. **Multiple entity types** - Checks Storage, Volume, VirtualMachineVolume, VirtualDisk
5. **Detailed error messages** - Explains why no results were found

## Next Steps

1. Run the debug script to understand your Turbonomic instance
2. Review the output to identify the specific issue
3. Apply the appropriate solution from this guide
4. Re-run the disk optimization report
5. If still no results, the instance may not have storage optimization opportunities

## Need Help?

If you're still having issues:
- Review Turbonomic documentation for your version
- Check if storage optimization is a licensed feature
- Verify Azure managed disks are being discovered
- Consider opening a support ticket with IBM