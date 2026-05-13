# Dashboard Dolly - Quick Start Guide

Get started with Dashboard Dolly in 5 minutes!

## Prerequisites

- Python 3.7 or higher
- Access to Cloudability environments
- API key or Frontdoor credentials

## Installation

1. Navigate to the dashboard-dolly directory:
```bash
cd cloudability/dashboard-dolly
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## First-Time Setup

### Step 1: Create Your First Environment Configuration

1. The tool will automatically create an `Environments/` folder on first run
2. Copy the template folder:
```bash
cp -r Environments/template Environments/my-production
```

3. Edit `Environments/my-production/config.json`:

**For Cloudability API Key:**
```json
{
  "auth_type": "cloudability",
  "frontdoor_region": "",
  "cldyKey": "your-cloudability-api-key-here"
}
```

**For Frontdoor Authentication:**
```json
{
  "auth_type": "frontdoor",
  "frontdoor_region": "",
  "frontdoor_environment": "your-environment-id",
  "public_key": "your-public-key",
  "private_key": "your-private-key"
}
```

### Step 2: Run the Tool

```bash
python dashboard_dolly.py
```

## Common Tasks

### Task 1: Save All Dashboards from an Environment

1. Run the tool:
```bash
python dashboard_dolly.py
```

2. Select your environment (e.g., `1` for the first environment)

3. Choose option `1` to save dashboards

4. When asked about starred only, enter `n` for all dashboards

5. Dashboards will be saved to `Environments/[your-env]/Dashboards/`

**Example:**
```
Found the following environments:
1	my-production

Select the environment folder by entering its number: 1
Credentials loaded successfully.

Select mode:
1. Save Dashboards to /Environments/my-production/Dashboards
2. Upload Dashboards from /Dashboards_to_Upload
3. Exit
Enter the number of the mode you want to use: 1

Do you want to save only starred dashboards? (y/n): n
Found 45 dashboards for my-production
Saving dashboards: 100% Complete (45/45)
Saved 45 dashboards to Environments/my-production/Dashboards
```

### Task 2: Save Only Starred Dashboards

Follow the same steps as Task 1, but answer `y` when asked about starred dashboards:

```
Do you want to save only starred dashboards? (y/n): y
Found 45 dashboards for my-production
Filtered to 8 starred dashboards out of 45 total dashboards
Saving dashboards: 100% Complete (8/8)
Saved 8 dashboards to Environments/my-production/Dashboards
```

### Task 3: Transfer Dashboards to Another Environment

1. First, save dashboards from source environment (see Task 1)

2. Copy the dashboard JSON files to the upload folder:
```bash
cp Environments/source-env/Dashboards/*.json Dashboards_to_Upload/
```

3. Create a configuration for your target environment:
```bash
cp -r Environments/template Environments/my-target
# Edit Environments/my-target/config.json with target credentials
```

4. Run the tool and select the target environment

5. Choose option `2` to upload dashboards

**Example:**
```
Select the environment folder by entering its number: 2
Credentials loaded successfully.

Select mode:
1. Save Dashboards to /Environments/my-target/Dashboards
2. Upload Dashboards from /Dashboards_to_Upload
3. Exit
Enter the number of the mode you want to use: 2

Created dashboard 12345 Sales Dashboard
Created dashboard 12346 Cost Analysis
Created dashboard 12347 Resource Utilization
Created 3 dashboards
```

### Task 4: Transfer with Measure Mapping

If dimensions or metrics have different names between environments:

1. Edit `dashboard_dolly.py` and update the `measure_mapping` dictionary:
```python
measure_mapping = {
    'old_tag_name': 'new_tag_name',
    'old_category': 'new_category',
}
```

2. Save the file

3. Run the upload process (Task 3)

The tool will automatically replace the old measure names with new ones during transfer.

## Quick Reference

### Environment Configuration Locations

- **Template:** `Environments/template/config.json`
- **Your environments:** `Environments/[env-name]/config.json`
- **Saved dashboards:** `Environments/[env-name]/Dashboards/`
- **Upload staging:** `Dashboards_to_Upload/`

### Region Values

| Region | Value |
|--------|-------|
| US (default) | `""` |
| Australia | `"au"` |
| Europe | `"eu"` |
| US Government | `"usgov"` |

### Authentication Types

| Type | Required Fields |
|------|----------------|
| Cloudability API | `cldyKey` |
| Frontdoor | `frontdoor_environment`, `public_key`, `private_key` |

## Troubleshooting

### "No environment folders found"

**Solution:** Create an environment configuration:
```bash
cp -r Environments/template Environments/my-env
# Edit Environments/my-env/config.json
```

### "Connection failed"

**Solutions:**
1. Verify your API key or credentials are correct
2. Check the `frontdoor_region` value matches your environment
3. Ensure you have network access to Cloudability API

### "No dashboards found in Dashboards_to_Upload"

**Solution:** Copy dashboard JSON files to the upload folder:
```bash
cp Environments/source/Dashboards/*.json Dashboards_to_Upload/
```

### "Config file is missing required keys"

**Solution:** Ensure your config.json has either:
- `cldyKey` for Cloudability auth, OR
- `frontdoor_environment`, `public_key`, and `private_key` for Frontdoor auth

Plus `frontdoor_region` is always required.

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Set up multiple environment configurations for easy switching
- Create measure mappings for cross-environment transfers
- Explore the API client module for custom integrations

## Tips

1. **Start small:** Test with a single dashboard before batch operations
2. **Use starred filtering:** Save time by transferring only important dashboards
3. **Keep backups:** Always save dashboards before making changes
4. **Name environments clearly:** Use descriptive names like "prod-us" or "staging-eu"
5. **Review JSON files:** Check dashboard files before uploading to catch issues early

## Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Review the full README.md
3. Examine your config.json for errors
4. Verify your credentials are valid
5. Contact your Cloudability administrator

## Example Workflow

Here's a complete workflow for migrating dashboards from production to staging:

```bash
# 1. Setup
cd cloudability/dashboard-dolly
pip install -r requirements.txt

# 2. Create environment configs
cp -r Environments/template Environments/production
cp -r Environments/template Environments/staging
# Edit both config.json files with appropriate credentials

# 3. Save dashboards from production
python dashboard_dolly.py
# Select production environment
# Choose option 1 (Save Dashboards)
# Answer 'y' for starred only

# 4. Copy to upload folder
cp Environments/production/Dashboards/*.json Dashboards_to_Upload/

# 5. Upload to staging
python dashboard_dolly.py
# Select staging environment
# Choose option 2 (Upload Dashboards)

# 6. Clean up
rm Dashboards_to_Upload/*.json
```

Done! Your dashboards are now transferred from production to staging.