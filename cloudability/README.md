# Cloudability Tools

This directory contains scripts and tools for working with IBM Cloudability.

## Available Tools

### 1. Redshift Node Information
Get Redshift cluster details including number of nodes (not available via Cloudability API).

- **[get_redshift_nodes.py](./get_redshift_nodes.py)** - Python script to query AWS Redshift clusters
- **[REDSHIFT_METRICS_WORKAROUNDS.md](./REDSHIFT_METRICS_WORKAROUNDS.md)** - Complete guide with multiple approaches
- **[AWS_CREDENTIALS_SETUP.md](./AWS_CREDENTIALS_SETUP.md)** - Detailed AWS credentials configuration guide

**Quick Start:**
```bash
# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials (one-time setup)
aws configure
# Enter your AWS Access Key ID and Secret Access Key

# Run the script
python get_redshift_nodes.py
```

### 2. Account Group Updater
Update Cloudability account group entries from CSV.

- **[account-group-updater/update_ag_entries.py](./account-group-updater/update_ag_entries.py)**
- **[account-group-updater/test.csv.example](./account-group-updater/test.csv.example)**

### 3. Business Mapping Update
Update Cloudability business mappings from CSV.

- **[business-mapping-update/update_mappings_from_csv.py](./business-mapping-update/update_mappings_from_csv.py)**
- **[business-mapping-update/bm-test.csv.example](./business-mapping-update/bm-test.csv.example)**

### 4. Hierarchical Business Mapping Update
Update hierarchical business mappings.

- **[update-hierarchical-bm/update_hbm.py](./update-hierarchical-bm/update_hbm.py)**
- **[update-hierarchical-bm/Test.csv](./update-hierarchical-bm/Test.csv)**

### 5. Views Updater
Update Cloudability views.

- **[views-updater/views_updater.py](./views-updater/views_updater.py)**
- **[views-updater/adesk view test.csv](./views-updater/adesk%20view%20test.csv)**

### 6. Postman Collections
API collections for testing Cloudability endpoints.

- **[postman-collection/Cloudability.postman_collection.json.example](./postman-collection/Cloudability.postman_collection.json.example)**
- **[postman-collection/Business Metrics.postman_collection.json](./postman-collection/Business%20Metrics.postman_collection.json)**
- **[postman-collection/README.md](./postman-collection/README.md)**

## Common Setup

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Cloudability API Authentication
Most Cloudability scripts use Basic Authentication with API keys:

```python
import requests
from requests.auth import HTTPBasicAuth

api_key = "your_api_key"
response = requests.get(
    "https://api.cloudability.com/v3/endpoint",
    auth=HTTPBasicAuth(api_key, '')
)
```

### AWS API Authentication (for Redshift tools)
See **[AWS_CREDENTIALS_SETUP.md](./AWS_CREDENTIALS_SETUP.md)** for complete setup instructions.

Quick setup:
```bash
aws configure
# Enter AWS Access Key ID and Secret Access Key
```

## Getting Help

### Redshift Metrics Issue
If you need Redshift cluster information (like number of nodes), see:
- **[REDSHIFT_METRICS_WORKAROUNDS.md](./REDSHIFT_METRICS_WORKAROUNDS.md)** - Why it's not in Cloudability API and how to get it
- **[AWS_CREDENTIALS_SETUP.md](./AWS_CREDENTIALS_SETUP.md)** - How to set up AWS credentials

### AWS Credentials Issues
If you get password prompts or authentication errors when running AWS scripts:
- See **[AWS_CREDENTIALS_SETUP.md](./AWS_CREDENTIALS_SETUP.md)**
- You need AWS Access Keys, not a password
- Run `aws configure` to set up credentials

## Documentation

- [Cloudability API Documentation](https://developers.cloudability.com/)
- [IBM Cloudability Documentation](https://www.ibm.com/docs/en/cloudability)
- [AWS Redshift API Documentation](https://docs.aws.amazon.com/redshift/latest/APIReference/Welcome.html)

## Support

For issues or questions:
1. Check the relevant README or documentation file
2. Review error messages and troubleshooting sections
3. Verify your API credentials are configured correctly
4. Contact your Cloudability or AWS administrator for access issues