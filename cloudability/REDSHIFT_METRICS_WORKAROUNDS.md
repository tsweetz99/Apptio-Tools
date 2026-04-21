# Getting Redshift Number of Nodes from Cloudability

## Problem Statement
The Redshift "number of nodes" metric is visible in the Cloudability Resource Inventory UI but is **NOT available through the Cloudability API**.

## Prerequisites

Before using the AWS API methods below, you need AWS credentials configured. See **[AWS_CREDENTIALS_SETUP.md](./AWS_CREDENTIALS_SETUP.md)** for detailed setup instructions.

**Quick Setup:**
```bash
# Install AWS CLI
brew install awscli  # or: pip install awscli

# Configure credentials
aws configure
# Enter your AWS Access Key ID and Secret Access Key when prompted

# Verify
aws sts get-caller-identity
```

## Current API Limitations

The Cloudability API does not provide:
- A Resource Inventory endpoint
- Direct access to Redshift cluster configuration details
- Number of nodes per Redshift cluster

## Workarounds

### Option 1: Use AWS API Directly (Recommended)

Since Cloudability doesn't expose this data via API, query AWS directly using the AWS CLI or SDK:

#### Using AWS CLI:

**Note**: Requires AWS credentials. See [AWS_CREDENTIALS_SETUP.md](./AWS_CREDENTIALS_SETUP.md) if you get authentication errors.

```bash
# List all Redshift clusters with node information
aws redshift describe-clusters --query 'Clusters[*].[ClusterIdentifier,NodeType,NumberOfNodes,ClusterStatus]' --output table

# Get specific cluster details
aws redshift describe-clusters --cluster-identifier your-cluster-name

# Export to JSON for processing
aws redshift describe-clusters --output json > redshift_clusters.json
```

#### Using Python (boto3):

**Note**: Requires AWS credentials configured. See [AWS_CREDENTIALS_SETUP.md](./AWS_CREDENTIALS_SETUP.md).

```python
import boto3
import json

# Initialize Redshift client (uses credentials from ~/.aws/credentials)
redshift = boto3.client('redshift', region_name='us-east-1')

# Get all clusters
response = redshift.describe_clusters()

# Extract node information
for cluster in response['Clusters']:
    print(f"Cluster: {cluster['ClusterIdentifier']}")
    print(f"  Node Type: {cluster['NodeType']}")
    print(f"  Number of Nodes: {cluster['NumberOfNodes']}")
    print(f"  Status: {cluster['ClusterStatus']}")
    print(f"  Region: {cluster['AvailabilityZone']}")
    print()
```

### Option 2: Export from Cloudability UI

1. Navigate to **Resource Inventory** in Cloudability UI
2. Filter for Redshift clusters
3. Export the data to CSV/Excel
4. Parse the exported file programmatically

**Limitations:**
- Manual process or requires UI automation
- Not suitable for real-time or frequent queries
- May not scale well

### Option 3: Use Cloudability Reporting API (Indirect Method)

While not providing node counts directly, you can use the Cloudability Reporting API to get Redshift cost data and infer some information:

```bash
# Get Redshift costs (may help identify clusters)
curl -X GET "https://api.cloudability.com/v3/reporting/cost" \
  -u "API_KEY:" \
  -H "Content-Type: application/json" \
  -d '{
    "dimensions": ["service", "resource_identifier"],
    "filters": [
      {
        "field": "service",
        "comparator": "==",
        "value": "Amazon Redshift"
      }
    ],
    "start_date": "2026-04-01",
    "end_date": "2026-04-16"
  }'
```

**Limitations:**
- Does not provide node count
- Only provides cost and resource identifiers
- Still requires AWS API to get node details

### Option 4: Request Feature from IBM Cloudability

Contact IBM Cloudability support to request:
- Resource Inventory API endpoint
- Redshift cluster details in API responses
- Include number of nodes in the data model

## Recommended Approach

**Use AWS API directly** for the most reliable and up-to-date information:

1. **For one-time queries**: Use AWS CLI
2. **For automation**: Use boto3 (Python) or AWS SDK in your preferred language
3. **For integration**: Combine AWS API data with Cloudability cost data

## Example: Combined Approach

Get Redshift configuration from AWS and costs from Cloudability:

```python
import boto3
import requests
from requests.auth import HTTPBasicAuth
import json

# Get Redshift cluster details from AWS
def get_redshift_clusters():
    redshift = boto3.client('redshift')
    response = redshift.describe_clusters()
    
    clusters = []
    for cluster in response['Clusters']:
        clusters.append({
            'cluster_id': cluster['ClusterIdentifier'],
            'node_type': cluster['NodeType'],
            'number_of_nodes': cluster['NumberOfNodes'],
            'status': cluster['ClusterStatus'],
            'region': cluster['AvailabilityZone']
        })
    return clusters

# Get Redshift costs from Cloudability
def get_redshift_costs(api_key, start_date, end_date):
    url = "https://api.cloudability.com/v3/reporting/cost"
    
    payload = {
        "dimensions": ["resource_identifier"],
        "filters": [{
            "field": "service",
            "comparator": "==",
            "value": "Amazon Redshift"
        }],
        "start_date": start_date,
        "end_date": end_date
    }
    
    response = requests.post(
        url,
        auth=HTTPBasicAuth(api_key, ''),
        json=payload
    )
    
    return response.json()

# Combine the data
def combine_redshift_data(api_key, start_date, end_date):
    clusters = get_redshift_clusters()
    costs = get_redshift_costs(api_key, start_date, end_date)
    
    # Merge data based on cluster identifier
    # (implementation depends on your specific needs)
    
    return {
        'clusters': clusters,
        'costs': costs
    }

# Usage
if __name__ == "__main__":
    API_KEY = "your_cloudability_api_key"
    data = combine_redshift_data(API_KEY, "2026-04-01", "2026-04-16")
    print(json.dumps(data, indent=2))
```

## Summary

| Method | Node Count Available | Real-time | Automation-Friendly | Recommended |
|--------|---------------------|-----------|---------------------|-------------|
| AWS API | ✅ Yes | ✅ Yes | ✅ Yes | ✅ **Best** |
| Cloudability UI Export | ✅ Yes | ❌ No | ⚠️ Limited | ❌ No |
| Cloudability API | ❌ No | N/A | N/A | ❌ No |
| Combined Approach | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Good |

## Additional Resources

- [AWS Redshift API Documentation](https://docs.aws.amazon.com/redshift/latest/APIReference/Welcome.html)
- [Boto3 Redshift Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift.html)
- [Cloudability API Documentation](https://developers.cloudability.com/)
- [IBM Cloudability Resource Inventory](https://www.ibm.com/docs/en/cloudability-commercial/cloudability-premium/saas?topic=inventory-aws-resource)