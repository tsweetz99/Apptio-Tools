#!/usr/bin/env python3
"""
Turbonomic Disk Optimization Report Generator

Generates disk tier optimization reports with policy enforcement:
- DEV/UAT: Policy requires Standard SSD (Premium SSD = violation)
- Pre-Prod/Prod/DR: Recommendations require review

Requirements:
    pip install requests pandas openpyxl

Usage:
    python3 generate_disk_optimization_report.py --url https://your-turbo-instance.com --jsessionid <SESSION_ID> --output-dir reports/
"""

import requests
import json
import argparse
import sys
import os
from datetime import datetime
from typing import List, Dict, Optional
import csv

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class TurbonomicDiskOptimizationReport:
    """Generate disk optimization reports from Turbonomic API with policy enforcement."""
    
    def __init__(self, turbo_url: str, jsessionid: str, customer_mapping_file: Optional[str] = None):
        self.turbo_url = turbo_url.rstrip('/')
        self.session = requests.Session()
        self.session.cookies.set('JSESSIONID', jsessionid)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.customer_mapping = self._load_customer_mapping(customer_mapping_file)
    
    def _load_customer_mapping(self, mapping_file: Optional[str]) -> Dict[str, str]:
        """Load customer ID to name mapping from JSON file."""
        if not mapping_file:
            return {}
        
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mapping = json.load(f)
                print(f"✓ Loaded {len(mapping)} customer mappings from {mapping_file}")
                return mapping
        except FileNotFoundError:
            print(f"Warning: Customer mapping file not found: {mapping_file}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in customer mapping file: {e}")
            return {}
        except Exception as e:
            print(f"Warning: Error loading customer mapping file: {e}")
            return {}
    
    def _map_customer_name(self, customer_id: str) -> str:
        """Map customer ID to friendly name using the mapping file."""
        if not customer_id or customer_id == 'N/A':
            return 'N/A'
        
        if customer_id in self.customer_mapping:
            return self.customer_mapping[customer_id]
        
        return customer_id
    
    def get_storage_actions(self, fetch_all: bool = True) -> List[Dict]:
        """Fetch storage-related actions with pagination support."""
        url = f"{self.turbo_url}/api/v3/markets/Market/actions"
        
        # Don't filter by actionTypeId - get all actions and filter by target type
        params = {
            'actionStateList': ['READY', 'ACCEPTED', 'QUEUED', 'IN_PROGRESS'],
            'limit': 500
        }
        
        all_actions = []
        cursor = None
        
        print(f"Fetching storage actions from {url}...")
        
        while True:
            if cursor:
                params['cursor'] = cursor
            
            try:
                response = self.session.post(url, json=params)
                response.raise_for_status()
                data = response.json()
                
                # Handle both list and dict responses
                if isinstance(data, list):
                    actions = data
                    all_actions.extend(actions)
                    print(f"  Retrieved {len(actions)} actions (total: {len(all_actions)})")
                    break  # List response doesn't support pagination
                else:
                    actions = data.get('result', [])
                    all_actions.extend(actions)
                    print(f"  Retrieved {len(actions)} actions (total: {len(all_actions)})")
                    
                    if not fetch_all or len(actions) < 500:
                        break
                    
                    cursor = data.get('cursor')
                    if not cursor:
                        break
                    
            except requests.exceptions.RequestException as e:
                print(f"Error fetching actions: {e}")
                sys.exit(1)
        
        print(f"Total storage actions retrieved: {len(all_actions)}")
        return all_actions
    
    def _get_tag_value(self, entity: Dict, tag_key: str) -> str:
        """Extract tag value from entity."""
        tags = entity.get('tags', {})
        
        if isinstance(tags, dict):
            if tag_key in tags:
                tag_value = tags[tag_key]
                if isinstance(tag_value, list) and tag_value:
                    return tag_value[0] if tag_value[0] else 'N/A'
                return str(tag_value) if tag_value else 'N/A'
            
            for key, value in tags.items():
                if key.lower() == tag_key.lower():
                    if isinstance(value, list) and value:
                        return value[0] if value[0] else 'N/A'
                    return str(value) if value else 'N/A'
        
        return 'N/A'
    
    def _get_business_account(self, action: Dict) -> str:
        """Extract business account name from action."""
        target = action.get('target', {})
        aspects = target.get('aspects', {})
        cloud_aspect = aspects.get('cloudAspect', {})
        business_account = cloud_aspect.get('businessAccount', {})
        return business_account.get('displayName', 'N/A')
    
    def _parse_environment_from_account(self, account_name: str) -> Optional[str]:
        """Parse environment from BusinessAccount name."""
        account_upper = account_name.upper()
        
        if 'PRODUCTION' in account_upper or 'PRD-' in account_upper or '-PRD-' in account_upper:
            if 'PRE-PROD' not in account_upper and 'PREPROD' not in account_upper:
                return 'Prod'
        
        if 'PRE-PROD' in account_upper or 'PREPROD' in account_upper:
            return 'Pre-Prod'
        
        if 'DR-' in account_upper or '-DR-' in account_upper or 'DISASTER RECOVERY' in account_upper:
            return 'DR'
        
        if 'UAT' in account_upper or 'USER ACCEPTANCE' in account_upper:
            return 'UAT'
        
        if 'DEVELOPMENT' in account_upper or 'DEV-' in account_upper or '-DEV-' in account_upper:
            return 'Dev'
        
        return None
    
    def _determine_environment(self, action: Dict) -> str:
        """Determine environment with fallback logic."""
        account_name = self._get_business_account(action)
        if account_name != 'N/A':
            env_from_account = self._parse_environment_from_account(account_name)
            if env_from_account:
                return env_from_account
        
        target = action.get('target', {})
        env_tag = self._get_tag_value(target, 'environment')
        
        if env_tag and env_tag != 'N/A':
            env_upper = env_tag.upper()
            if 'PROD' in env_upper and 'PRE' not in env_upper:
                return 'Prod'
            elif 'PRE-PROD' in env_upper or 'PREPROD' in env_upper:
                return 'Pre-Prod'
            elif 'UAT' in env_upper:
                return 'UAT'
            elif 'DEV' in env_upper:
                return 'Dev'
            elif 'DR' in env_upper:
                return 'DR'
            else:
                return env_tag
        
        return 'Unmapped'
    
    def _get_cloud_provider(self, action: Dict) -> str:
        """Determine cloud provider from action."""
        target = action.get('target', {})
        discovered_by = target.get('discoveredBy', {})
        disc_type = discovered_by.get('type', '').lower()
        
        if 'azure' in disc_type:
            return 'Azure'
        elif 'aws' in disc_type:
            return 'AWS'
        elif 'gcp' in disc_type or 'google' in disc_type:
            return 'GCP'
        
        return 'Unknown'
    
    def _extract_disk_tier(self, tier_string: str) -> str:
        """Extract disk tier from string."""
        if not tier_string or tier_string == 'N/A':
            return 'N/A'
        
        tier_upper = tier_string.upper()
        
        if 'PREMIUM' in tier_upper and 'SSD' in tier_upper:
            return 'Premium SSD'
        elif 'STANDARD' in tier_upper and 'SSD' in tier_upper:
            return 'Standard SSD'
        elif 'STANDARD' in tier_upper and 'HDD' in tier_upper:
            return 'Standard HDD'
        elif 'ULTRA' in tier_upper:
            return 'Ultra SSD'
        
        return tier_string
    
    def _calculate_monthly_savings(self, action: Dict) -> float:
        """Calculate monthly savings from action stats."""
        stats = action.get('stats', [])
        
        for stat in stats:
            if isinstance(stat, dict):
                stat_name = stat.get('name', '').lower()
                value = stat.get('value', 0)
                
                if 'cost' in stat_name and value < 0:
                    hourly_rate = abs(float(value))
                    return hourly_rate * 730
        
        return 0.0
    
    def _determine_policy_compliance(self, environment: str, current_tier: str) -> str:
        """Determine if disk configuration complies with policy."""
        if environment in ['Dev', 'UAT']:
            if 'Premium' in current_tier:
                return 'VIOLATION - Premium SSD not allowed'
            else:
                return 'Compliant'
        else:
            return 'Review Required'
    
    def _determine_actionable(self, environment: str, current_tier: str, recommended_tier: str) -> str:
        """Determine if action is immediately actionable."""
        if environment in ['Dev', 'UAT']:
            if 'Premium' in current_tier and 'Standard' in recommended_tier:
                return 'Yes - Policy Violation'
            elif current_tier != recommended_tier:
                return 'Yes'
        elif environment in ['Pre-Prod', 'Prod', 'DR']:
            return 'Review Required'
        
        return 'No'
    
    def _get_attached_vm(self, action: Dict) -> str:
        """Get the VM name that the disk is attached to."""
        target = action.get('target', {})
        
        # Try to get from providers
        providers = target.get('providers', [])
        if providers and isinstance(providers, list):
            for provider in providers:
                if isinstance(provider, dict):
                    vm_name = provider.get('displayName', '')
                    if vm_name:
                        return vm_name
        
        # Fallback to target display name if it's a VM
        return target.get('displayName', 'N/A')
    
    def generate_report_data(self, azure_only: bool = True) -> List[Dict]:
        """Generate disk optimization report data."""
        actions = self.get_storage_actions()
        
        report_data = []
        
        for action in actions:
            target = action.get('target', {})
            
            # Filter for Azure only
            cloud_provider = self._get_cloud_provider(action)
            if azure_only and cloud_provider != 'Azure':
                continue
            
            # Only process disk/volume-related actions
            target_type = target.get('className', '')
            action_type = action.get('actionType', '')
            
            # Look for Storage or Volume entities with RESIZE/SCALE actions
            if target_type not in ['Storage', 'VirtualMachineVolume', 'Volume']:
                continue
            
            # Skip if not a tier/resize action
            if action_type not in ['RESIZE', 'SCALE', 'RECONFIGURE']:
                continue
            
            # Determine environment
            environment = self._determine_environment(action)
            
            # Get disk information
            disk_name = target.get('displayName', 'N/A')
            current_entity = action.get('currentEntity', {})
            new_entity = action.get('newEntity', {})
            
            current_tier = self._extract_disk_tier(current_entity.get('displayName', 'N/A'))
            recommended_tier = self._extract_disk_tier(new_entity.get('displayName', 'N/A'))
            
            # Skip if not a tier change
            if current_tier == recommended_tier or current_tier == 'N/A' or recommended_tier == 'N/A':
                continue
            
            # Get attached VM
            vm_name = self._get_attached_vm(action)
            
            # Calculate savings
            monthly_savings = self._calculate_monthly_savings(action)
            
            # Determine policy compliance and actionability
            policy_compliance = self._determine_policy_compliance(environment, current_tier)
            actionable = self._determine_actionable(environment, current_tier, recommended_tier)
            
            # Get customer info
            customer_id = self._get_tag_value(target, 'CustomerID')
            customer_name = self._map_customer_name(customer_id)
            
            # Build report row
            # Generate Turbonomic action link
            action_uuid = action.get('uuid', '')
            turbo_link = f"{self.turbo_url}/#/app/action-center/{action_uuid}" if action_uuid else 'N/A'
            
            row = {
                'Environment': environment,
                'Server Name': vm_name,
                'Disk Name': disk_name,
                'Current Tier': current_tier,
                'Recommended Tier': recommended_tier,
                'Policy Compliance': policy_compliance,
                'Monthly Savings': monthly_savings,
                'Actionable': actionable,
                'Turbonomic Link': turbo_link,
                'Customer ID': customer_id,
                'Customer Friendly Name': customer_name,
                'Business Account': self._get_business_account(action),
                'Cloud Provider': cloud_provider,
                'Action State': action.get('actionState', 'N/A'),
                'Risk': action.get('risk', {}).get('severity', 'N/A'),
                'Details': action.get('details', 'N/A'),
                'UUID': target.get('uuid', 'N/A')
            }
            
            report_data.append(row)
        
        return report_data
    
    def export_to_excel(self, data: List[Dict], filename: str):
        """Export data to Excel file."""
        if not PANDAS_AVAILABLE:
            print("Warning: pandas not available, falling back to CSV")
            self.export_to_csv(data, filename.replace('.xlsx', '.csv'))
            return
        
        if not data:
            print(f"  ℹ No data to export")
            return
        
        import pandas as pd  # type: ignore
        df = pd.DataFrame(data)
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Disk Optimization', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Disk Optimization']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"  ✓ Exported {len(data)} records to: {filename}")
    
    def export_to_csv(self, data: List[Dict], filename: str):
        """Export data to CSV file."""
        if not data:
            print(f"  ℹ No data to export")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        print(f"  ✓ Exported {len(data)} records to: {filename}")
    
    def print_summary(self, data: List[Dict], title: str = "DISK OPTIMIZATION SUMMARY"):
        """Print summary statistics."""
        if not data:
            print(f"\n{title}: No data")
            return
        
        total = len(data)
        policy_violations = len([r for r in data if 'VIOLATION' in r['Policy Compliance']])
        immediately_actionable = len([r for r in data if r['Actionable'].startswith('Yes')])
        review_required = len([r for r in data if r['Actionable'] == 'Review Required'])
        
        total_savings = sum(r['Monthly Savings'] for r in data)
        violation_savings = sum(r['Monthly Savings'] for r in data if 'VIOLATION' in r['Policy Compliance'])
        
        # Environment breakdown
        env_breakdown = {}
        env_violations = {}
        env_savings = {}
        
        for row in data:
            env = row.get('Environment', 'Unknown')
            env_breakdown[env] = env_breakdown.get(env, 0) + 1
            env_savings[env] = env_savings.get(env, 0) + row['Monthly Savings']
            
            if 'VIOLATION' in row['Policy Compliance']:
                env_violations[env] = env_violations.get(env, 0) + 1
        
        print(f"\n{'='*80}")
        print(title)
        print(f"{'='*80}")
        print(f"Total Disk Recommendations: {total}")
        print(f"  - Policy Violations (DEV/UAT Premium SSD): {policy_violations}")
        print(f"  - Immediately Actionable: {immediately_actionable}")
        print(f"  - Review Required: {review_required}")
        print(f"")
        print(f"Estimated Monthly Savings: ${total_savings:,.2f}")
        print(f"  - From Policy Violations: ${violation_savings:,.2f}")
        print(f"")
        print(f"Environment Breakdown:")
        for env in sorted(env_breakdown.keys()):
            violations = env_violations.get(env, 0)
            savings = env_savings.get(env, 0)
            print(f"  - {env}: {env_breakdown[env]} disks (${savings:,.2f} savings)")
            if violations > 0:
                print(f"    └─ {violations} policy violations")
        print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Generate Turbonomic disk optimization reports with policy enforcement',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all reports
  python3 generate_disk_optimization_report.py --url https://turbo.example.com --jsessionid <ID> --output-dir reports/
  
  # With customer mapping
  python3 generate_disk_optimization_report.py --url https://turbo.example.com --jsessionid <ID> --customer-mapping customer_mapping.json --output-dir reports/
        """
    )
    
    parser.add_argument('--url', required=True, help='Turbonomic instance URL')
    parser.add_argument('--jsessionid', required=True, help='JSESSIONID from login')
    parser.add_argument('--output-dir', default='.', help='Output directory for reports (default: current directory)')
    parser.add_argument('--format', choices=['csv', 'excel'], default='excel', help='Output format (default: excel)')
    parser.add_argument('--all-clouds', action='store_true', help='Include all cloud providers (not just Azure)')
    parser.add_argument('--customer-mapping', help='Path to customer ID to name mapping JSON file')
    
    args = parser.parse_args()
    
    try:
        # Validate and create output directory
        output_dir = args.output_dir
        
        if os.path.isfile(output_dir):
            print(f"Error: '{output_dir}' is a file, not a directory.")
            print(f"Use --output-dir to specify a directory, not a filename.")
            print(f"Example: --output-dir ./reports/")
            return 1
        
        os.makedirs(output_dir, exist_ok=True)
        
        report = TurbonomicDiskOptimizationReport(args.url, args.jsessionid, args.customer_mapping)
        
        print("Generating disk optimization report...")
        all_data = report.generate_report_data(azure_only=not args.all_clouds)
        
        # Generate comprehensive report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = '.xlsx' if args.format == 'excel' else '.csv'
        
        comprehensive_file = os.path.join(args.output_dir, f"Disk_Optimization_Report_{timestamp}{ext}")
        
        if args.format == 'excel':
            report.export_to_excel(all_data, comprehensive_file)
        else:
            report.export_to_csv(all_data, comprehensive_file)
        
        report.print_summary(all_data, "COMPREHENSIVE DISK OPTIMIZATION SUMMARY")
        
        # Generate environment-specific reports
        environments = ['Dev', 'UAT', 'Pre-Prod', 'Prod', 'DR', 'Unmapped']
        
        print(f"\nGenerating environment-specific reports...")
        for env in environments:
            env_data = [r for r in all_data if r['Environment'] == env]
            
            if env_data:
                env_file = os.path.join(args.output_dir, f"{env}_Disk_Optimization_{timestamp}{ext}")
                
                if args.format == 'excel':
                    report.export_to_excel(env_data, env_file)
                else:
                    report.export_to_csv(env_data, env_file)
                
                report.print_summary(env_data, f"{env.upper()} DISK OPTIMIZATION SUMMARY")
            else:
                print(f"  ℹ No data for {env} environment")
        
        print(f"\n✓ All reports generated in: {args.output_dir}")
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

# Made with Bob
