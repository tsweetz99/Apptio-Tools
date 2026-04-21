#!/usr/bin/env python3
"""
Get Redshift Cluster Node Information

This script retrieves Redshift cluster details including the number of nodes
using the AWS API (boto3), since this information is not available through
the Cloudability API.

Prerequisites:
    1. AWS credentials configured (see AWS_CREDENTIALS_SETUP.md)
    2. Python dependencies: pip install -r requirements.txt

Setup AWS Credentials:
    # Quick setup
    aws configure
    # Enter your AWS Access Key ID and Secret Access Key when prompted
    
    # Or set environment variables
    export AWS_ACCESS_KEY_ID="your-access-key-id"
    export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
    export AWS_DEFAULT_REGION="us-east-1"

Usage:
    # List all clusters in default region
    python get_redshift_nodes.py

    # List clusters in specific region
    python get_redshift_nodes.py --region us-west-2

    # Get specific cluster details
    python get_redshift_nodes.py --cluster my-cluster-name

    # Export to JSON
    python get_redshift_nodes.py --output clusters.json

    # List clusters across all regions
    python get_redshift_nodes.py --all-regions

For detailed AWS credentials setup, see: AWS_CREDENTIALS_SETUP.md
"""

import boto3
import json
import argparse
from datetime import datetime
from typing import List, Dict, Optional


def get_all_regions() -> List[str]:
    """Get list of all AWS regions where Redshift is available."""
    ec2 = boto3.client('ec2')
    regions = ec2.describe_regions()
    return [region['RegionName'] for region in regions['Regions']]


def get_redshift_clusters(region: str = 'us-east-1', cluster_id: Optional[str] = None) -> List[Dict]:
    """
    Get Redshift cluster information from AWS.
    
    Args:
        region: AWS region to query
        cluster_id: Optional specific cluster identifier
        
    Returns:
        List of cluster information dictionaries
    """
    try:
        redshift = boto3.client('redshift', region_name=region)
        
        if cluster_id:
            response = redshift.describe_clusters(ClusterIdentifier=cluster_id)
        else:
            response = redshift.describe_clusters()
        
        clusters = []
        for cluster in response['Clusters']:
            cluster_info = {
                'cluster_identifier': cluster['ClusterIdentifier'],
                'node_type': cluster['NodeType'],
                'number_of_nodes': cluster['NumberOfNodes'],
                'cluster_status': cluster['ClusterStatus'],
                'availability_zone': cluster.get('AvailabilityZone', 'N/A'),
                'region': region,
                'database_name': cluster.get('DBName', 'N/A'),
                'master_username': cluster.get('MasterUsername', 'N/A'),
                'cluster_create_time': cluster.get('ClusterCreateTime', '').isoformat() if cluster.get('ClusterCreateTime') else 'N/A',
                'encrypted': cluster.get('Encrypted', False),
                'vpc_id': cluster.get('VpcId', 'N/A'),
                'publicly_accessible': cluster.get('PubliclyAccessible', False),
                'endpoint': cluster.get('Endpoint', {}).get('Address', 'N/A') if cluster.get('Endpoint') else 'N/A',
                'port': cluster.get('Endpoint', {}).get('Port', 'N/A') if cluster.get('Endpoint') else 'N/A',
                'cluster_version': cluster.get('ClusterVersion', 'N/A'),
                'allow_version_upgrade': cluster.get('AllowVersionUpgrade', False),
                'automated_snapshot_retention_period': cluster.get('AutomatedSnapshotRetentionPeriod', 0),
                'tags': {tag['Key']: tag['Value'] for tag in cluster.get('Tags', [])}
            }
            clusters.append(cluster_info)
        
        return clusters
    
    except boto3.exceptions.Boto3Error as e:
        print(f"Error querying region {region}: {e}")
        return []


def get_all_clusters_all_regions() -> List[Dict]:
    """Get Redshift clusters from all AWS regions."""
    all_clusters = []
    regions = get_all_regions()
    
    print(f"Scanning {len(regions)} regions for Redshift clusters...")
    
    for region in regions:
        print(f"  Checking {region}...", end=' ')
        clusters = get_redshift_clusters(region)
        if clusters:
            print(f"Found {len(clusters)} cluster(s)")
            all_clusters.extend(clusters)
        else:
            print("No clusters")
    
    return all_clusters


def print_cluster_table(clusters: List[Dict]):
    """Print clusters in a formatted table."""
    if not clusters:
        print("No Redshift clusters found.")
        return
    
    # Print header
    print("\n" + "="*120)
    print(f"{'Cluster ID':<30} {'Region':<15} {'Node Type':<15} {'Nodes':<6} {'Status':<12} {'Created':<20}")
    print("="*120)
    
    # Print each cluster
    for cluster in clusters:
        print(f"{cluster['cluster_identifier']:<30} "
              f"{cluster['region']:<15} "
              f"{cluster['node_type']:<15} "
              f"{cluster['number_of_nodes']:<6} "
              f"{cluster['cluster_status']:<12} "
              f"{cluster['cluster_create_time']:<20}")
    
    print("="*120)
    print(f"\nTotal clusters: {len(clusters)}")
    print(f"Total nodes: {sum(c['number_of_nodes'] for c in clusters)}")


def print_cluster_details(cluster: Dict):
    """Print detailed information for a single cluster."""
    print("\n" + "="*80)
    print(f"Cluster Details: {cluster['cluster_identifier']}")
    print("="*80)
    
    for key, value in cluster.items():
        if key != 'tags':
            print(f"{key.replace('_', ' ').title():<35}: {value}")
    
    if cluster['tags']:
        print(f"\n{'Tags':<35}:")
        for tag_key, tag_value in cluster['tags'].items():
            print(f"  {tag_key:<33}: {tag_value}")
    
    print("="*80)


def export_to_json(clusters: List[Dict], filename: str):
    """Export cluster data to JSON file."""
    output = {
        'export_date': datetime.now().isoformat(),
        'total_clusters': len(clusters),
        'total_nodes': sum(c['number_of_nodes'] for c in clusters),
        'clusters': clusters
    }
    
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\nData exported to: {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='Get Redshift cluster node information from AWS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all clusters in default region
  python get_redshift_nodes.py
  
  # List clusters in specific region
  python get_redshift_nodes.py --region us-west-2
  
  # Get specific cluster details
  python get_redshift_nodes.py --cluster my-cluster-name --region us-east-1
  
  # Export to JSON
  python get_redshift_nodes.py --output clusters.json
  
  # Scan all regions
  python get_redshift_nodes.py --all-regions --output all_clusters.json

Note: Requires AWS credentials configured (via AWS CLI, environment variables, or IAM role)
        """
    )
    
    parser.add_argument(
        '--region',
        default='us-east-1',
        help='AWS region to query (default: us-east-1)'
    )
    
    parser.add_argument(
        '--cluster',
        help='Specific cluster identifier to query'
    )
    
    parser.add_argument(
        '--all-regions',
        action='store_true',
        help='Scan all AWS regions for Redshift clusters'
    )
    
    parser.add_argument(
        '--output',
        help='Export results to JSON file'
    )
    
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed information for each cluster'
    )
    
    args = parser.parse_args()
    
    try:
        # Get cluster data
        if args.all_regions:
            clusters = get_all_clusters_all_regions()
        else:
            clusters = get_redshift_clusters(args.region, args.cluster)
        
        # Display results
        if args.detailed and clusters:
            for cluster in clusters:
                print_cluster_details(cluster)
        else:
            print_cluster_table(clusters)
        
        # Export if requested
        if args.output:
            export_to_json(clusters, args.output)
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n" + "="*80)
        print("TROUBLESHOOTING:")
        print("="*80)
        print("\n1. AWS Credentials Not Configured")
        print("   Run: aws configure")
        print("   You need: AWS Access Key ID and Secret Access Key")
        print("   See: AWS_CREDENTIALS_SETUP.md for detailed instructions")
        print("\n2. Missing Dependencies")
        print("   Run: pip install -r requirements.txt")
        print("\n3. Insufficient IAM Permissions")
        print("   Required: redshift:DescribeClusters")
        print("   Contact your AWS administrator")
        print("\n4. Verify Your Setup")
        print("   Test credentials: aws sts get-caller-identity")
        print("   Test Redshift access: aws redshift describe-clusters")
        print("\n" + "="*80)
        print("\nFor complete setup guide, see: AWS_CREDENTIALS_SETUP.md")
        print("="*80)
        return 1


if __name__ == '__main__':
    exit(main())

# Made with Bob
