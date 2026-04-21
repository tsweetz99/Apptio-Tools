#!/usr/bin/env python3
"""
Turbonomic Rightsizing Recommendations Report Generator (Azure-Focused Version)

This script generates detailed rightsizing reports from Turbonomic with:
- Azure-only filtering
- BusinessAccount extraction
- Environment parsing from BusinessAccount name
- Separate reports by environment (Dev, UAT, Pre-Prod, Prod, DR)

Requirements:
    pip install requests pandas openpyxl

Usage:
    python3 generate_rightsizing_report_v3.py --url https://your-turbo-instance.com --jsessionid <SESSION_ID> --output-dir reports/
"""

import requests
import json
import argparse
import sys
import re
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import csv

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class TurbonomicRightsizingReport:
    """Generate rightsizing recommendations report from Turbonomic API."""
    
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
        
        # Try exact match first
        if customer_id in self.customer_mapping:
            return self.customer_mapping[customer_id]
        
        # Return original ID if no mapping found
        return customer_id
    
    def get_recommended_actions(self, fetch_all: bool = True) -> List[Dict]:
        """Fetch all recommended actions with pagination support."""
        url = f"{self.turbo_url}/api/v3/markets/Market/actions"
        
        payload = {
            "actionStateList": ["READY", "QUEUED", "IN_PROGRESS", "ACCEPTED"],
            "actionTypeList": ["RESIZE", "SCALE"],
            "relatedEntityTypes": ["VirtualMachine"],
            "environmentType": "CLOUD",
            "detailLevel": "EXECUTION"
        }
        
        all_actions = []
        cursor = 0
        page_size = 500
        
        try:
            print(f"Fetching recommended actions from {url}...")
            
            while True:
                params = {
                    "ascending": "false",
                    "cursor": str(cursor),
                    "disable_hateoas": "true",
                    "forceExpansionOfAggregatedEntities": "true",
                    "order_by": "savings",
                    "limit": str(page_size)
                }
                
                response = self.session.post(url, json=payload, params=params)
                response.raise_for_status()
                
                data = response.json()
                actions = data if isinstance(data, list) else []
                
                if not actions:
                    break
                
                all_actions.extend(actions)
                print(f"  Retrieved {len(actions)} actions (total: {len(all_actions)})")
                
                if len(actions) < page_size or not fetch_all:
                    break
                
                cursor += page_size
            
            print(f"Total actions retrieved: {len(all_actions)}")
            return all_actions
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching actions: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return []
    
    def _get_cloud_provider(self, action: Dict) -> str:
        """Determine cloud provider from action data."""
        target = action.get('target', {})
        discovered_by = target.get('discoveredBy', {})
        probe_type = discovered_by.get('type', '').lower()
        
        if 'azure' in probe_type:
            return 'Azure'
        elif 'aws' in probe_type:
            return 'AWS'
        elif 'gcp' in probe_type or 'google' in probe_type:
            return 'GCP'
        
        # Check aspects
        aspects = target.get('aspects', {})
        if 'cloudAspect' in aspects:
            return 'Azure'  # Based on your data structure
        
        return 'Unknown'
    
    def _get_business_account(self, action: Dict) -> str:
        """Extract BusinessAccount name from cloudAspect."""
        target = action.get('target', {})
        aspects = target.get('aspects', {})
        cloud_aspect = aspects.get('cloudAspect', {})
        business_account = cloud_aspect.get('businessAccount', {})
        
        return business_account.get('displayName', 'N/A')
    
    def _parse_environment_from_account(self, account_name: str) -> Optional[str]:
        """
        Parse environment from BusinessAccount name.
        
        Common patterns:
        - Contains 'PRD', 'PROD', 'Production' -> Prod
        - Contains 'DEV', 'Development' -> Dev
        - Contains 'UAT', 'User Acceptance' -> UAT
        - Contains 'PRE-PROD', 'PREPROD', 'Pre-Production' -> Pre-Prod
        - Contains 'DR', 'Disaster Recovery' -> DR
        
        Returns None if no match found.
        """
        account_upper = account_name.upper()
        
        # Check for Production (most specific first)
        if any(x in account_upper for x in ['PRODUCTION', ' PRD ', '-PRD-', '_PRD_', 'PRD-', '-PRD']):
            return 'Prod'
        
        # Check for Pre-Prod
        if any(x in account_upper for x in ['PRE-PROD', 'PREPROD', 'PRE-PRODUCTION', 'PREPRODUCTION']):
            return 'Pre-Prod'
        
        # Check for DR
        if any(x in account_upper for x in [' DR ', '-DR-', '_DR_', 'DR-', '-DR', 'DISASTER RECOVERY', 'DISASTERRECOVERY']):
            return 'DR'
        
        # Check for UAT
        if any(x in account_upper for x in ['UAT', 'USER ACCEPTANCE', 'USERACCEPTANCE']):
            return 'UAT'
        
        # Check for Dev
        if any(x in account_upper for x in ['DEVELOPMENT', ' DEV ', '-DEV-', '_DEV_', 'DEV-', '-DEV']):
            return 'Dev'
        
        return None  # No match found
    
    def _determine_environment(self, action: Dict) -> str:
        """
        Determine environment with fallback logic:
        1. Parse from BusinessAccount name
        2. Fall back to environment tag
        3. Mark as 'Unmapped' if neither works
        """
        # Try BusinessAccount first
        account_name = self._get_business_account(action)
        if account_name != 'N/A':
            env_from_account = self._parse_environment_from_account(account_name)
            if env_from_account:
                return env_from_account
        
        # Fall back to environment tag
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
                return env_tag  # Return as-is if it doesn't match patterns
        
        return 'Unmapped'
    
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
    
    def _determine_action_type(self, action: Dict) -> str:
        """Determine if action is upsize or downsize."""
        current_entity = action.get('currentEntity', {})
        new_entity = action.get('newEntity', {})
        current_name = current_entity.get('displayName', '')
        new_name = new_entity.get('displayName', '')
        
        risk = action.get('risk', {})
        risk_sub_category = risk.get('subCategory', '').lower()
        risk_description = risk.get('description', '').lower()
        details = action.get('details', '').lower()
        
        if 'underutilized' in risk_sub_category or 'underutilized' in details:
            return 'Downsize'
        
        if 'overutilized' in risk_sub_category or 'overutilized' in details:
            return 'Upsize'
        
        if current_name and new_name:
            current_nums = re.findall(r'\d+', current_name)
            new_nums = re.findall(r'\d+', new_name)
            
            if current_nums and new_nums:
                try:
                    current_size = int(current_nums[0])
                    new_size = int(new_nums[0])
                    if new_size > current_size:
                        return 'Upsize'
                    elif new_size < current_size:
                        return 'Downsize'
                except (ValueError, IndexError):
                    pass
        
        stats = action.get('stats', [])
        for stat in stats:
            if isinstance(stat, dict):
                stat_name = stat.get('name', '').lower()
                value = stat.get('value', 0)
                
                if 'cost' in stat_name:
                    if value > 0:
                        return 'Upsize'
                    elif value < 0:
                        return 'Downsize'
        
        return 'Resize'
    
    def _format_configuration(self, action: Dict) -> str:
        """Format current VM configuration."""
        current_entity = action.get('currentEntity', {})
        return current_entity.get('displayName', 'N/A')
    
    def _format_recommendation(self, action: Dict) -> str:
        """Format recommended configuration."""
        new_entity = action.get('newEntity', {})
        return new_entity.get('displayName', 'N/A')
    
    def _calculate_monthly_savings(self, action: Dict, action_type: str) -> float:
        """Calculate monthly savings."""
        if action_type != 'Downsize':
            return 0.0
        
        stats = action.get('stats', [])
        for stat in stats:
            if isinstance(stat, dict):
                stat_name = stat.get('name', '').lower()
                value = stat.get('value', 0)
                
                if 'cost' in stat_name and value != 0:
                    hourly_rate = abs(float(value))
                    return hourly_rate * 730
        
        return 0.0
    
    def _calculate_net_add_cost(self, action: Dict, action_type: str, environment: str) -> float:
        """Calculate net additional cost (for upsizing in Prod only)."""
        if action_type != 'Upsize':
            return 0.0
        
        if environment and 'prod' not in environment.lower():
            return 0.0
        
        stats = action.get('stats', [])
        for stat in stats:
            if isinstance(stat, dict):
                stat_name = stat.get('name', '').lower()
                value = stat.get('value', 0)
                
                if 'cost' in stat_name and value != 0:
                    hourly_rate = abs(float(value))
                    return hourly_rate * 730
        
        return 0.0
    
    def generate_report_data(self, azure_only: bool = True, 
                            action_type_filter: Optional[str] = None) -> List[Dict]:
        """Generate report data from Turbonomic actions."""
        actions = self.get_recommended_actions()
        
        report_data = []
        
        for action in actions:
            target = action.get('target', {})
            
            # Filter for Azure only
            cloud_provider = self._get_cloud_provider(action)
            if azure_only and cloud_provider != 'Azure':
                continue
            
            # Determine environment
            environment = self._determine_environment(action)
            
            # Determine action type
            action_type = self._determine_action_type(action)
            
            # Apply action type filter
            if action_type_filter:
                if action_type_filter.lower() == 'downsize' and action_type != 'Downsize':
                    continue
                if action_type_filter.lower() == 'upsize' and action_type != 'Upsize':
                    continue
            
            # Get customer ID and map to friendly name
            customer_id = self._get_tag_value(target, 'CustomerID')
            customer_name = self._map_customer_name(customer_id)
            
            # Generate Turbonomic action link
            action_uuid = action.get('uuid', '')
            turbo_link = f"{self.turbo_url}/#/app/action-center/{action_uuid}" if action_uuid else 'N/A'
            
            # Build report row
            row = {
                'Server Name': target.get('displayName', 'N/A'),
                'Customer ID': customer_id,
                'Customer Friendly Name': customer_name,
                'Current Configuration': self._format_configuration(action),
                'Recommendation': self._format_recommendation(action),
                'Action Type': action_type,
                'Monthly Savings': self._calculate_monthly_savings(action, action_type),
                'Net Add Cost': self._calculate_net_add_cost(action, action_type, environment),
                'Environment': environment,
                'Turbonomic Link': turbo_link,
                'Business Account': self._get_business_account(action),
                'Cloud Provider': cloud_provider,
                'Action State': action.get('actionState', 'N/A'),
                'Risk': action.get('risk', {}).get('severity', 'N/A'),
                'Details': action.get('details', 'N/A'),
                'UUID': target.get('uuid', 'N/A')
            }
            
            report_data.append(row)
        
        return report_data
    
    def export_to_csv(self, report_data: List[Dict], filename: str):
        """Export report data to CSV."""
        if not report_data:
            print(f"No data to export to {filename}")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=report_data[0].keys())
            writer.writeheader()
            writer.writerows(report_data)
        
        print(f"  ✓ Exported {len(report_data)} records to: {filename}")
    
    def export_to_excel(self, report_data: List[Dict], filename: str):
        """Export report data to Excel."""
        if not PANDAS_AVAILABLE:
            print("Error: pandas not installed. Falling back to CSV.")
            self.export_to_csv(report_data, filename.replace('.xlsx', '.csv'))
            return
        
        if not report_data:
            print(f"No data to export to {filename}")
            return
        
        import pandas as pd  # type: ignore
        
        df = pd.DataFrame(report_data)
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Rightsizing Report', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Rightsizing Report']
            
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
        
        print(f"  ✓ Exported {len(report_data)} records to: {filename}")
    
    def print_summary(self, report_data: List[Dict], title: str = "RIGHTSIZING REPORT SUMMARY"):
        """Print report summary statistics."""
        if not report_data:
            print(f"No data in {title}")
            return
        
        total_actions = len(report_data)
        downsizes = len([r for r in report_data if r['Action Type'] == 'Downsize'])
        upsizes = len([r for r in report_data if r['Action Type'] == 'Upsize'])
        
        total_monthly_savings = sum(r['Monthly Savings'] for r in report_data)
        total_add_cost = sum(r['Net Add Cost'] for r in report_data)
        
        print("\n" + "="*80)
        print(title)
        print("="*80)
        print(f"Total Recommendations: {total_actions}")
        print(f"  - Downsizing: {downsizes}")
        print(f"  - Upsizing: {upsizes}")
        print(f"  - Other: {total_actions - downsizes - upsizes}")
        print(f"\nEstimated Monthly Savings: ${total_monthly_savings:,.2f}")
        print(f"Estimated Monthly Add Cost: ${total_add_cost:,.2f}")
        print(f"Net Monthly Impact: ${total_monthly_savings - total_add_cost:,.2f}")
        
        environments = {}
        for row in report_data:
            env = row.get('Environment', 'Unknown')
            environments[env] = environments.get(env, 0) + 1
        
        if environments:
            print(f"\nEnvironment Breakdown:")
            for env, count in sorted(environments.items()):
                print(f"  - {env}: {count}")
        
        print("="*80)

    
    def export_summary_report(self, all_data: List[Dict], output_dir: str, timestamp: str, format_type: str = 'excel'):
        """Export summary statistics to a text file with formatted output matching terminal display."""
        # Calculate overall statistics
        total_actions = len(all_data)
        downsizes = len([r for r in all_data if r['Action Type'] == 'Downsize'])
        upsizes = len([r for r in all_data if r['Action Type'] == 'Upsize'])
        other = total_actions - downsizes - upsizes
        
        total_monthly_savings = sum(r['Monthly Savings'] for r in all_data)
        total_add_cost = sum(r['Net Add Cost'] for r in all_data)
        net_impact = total_monthly_savings - total_add_cost
        
        # Environment breakdown
        env_breakdown = {}
        env_savings = {}
        env_costs = {}
        env_downsizes = {}
        env_upsizes = {}
        
        for row in all_data:
            env = row.get('Environment', 'Unknown')
            env_breakdown[env] = env_breakdown.get(env, 0) + 1
            env_savings[env] = env_savings.get(env, 0) + row['Monthly Savings']
            env_costs[env] = env_costs.get(env, 0) + row['Net Add Cost']
            
            if row['Action Type'] == 'Downsize':
                env_downsizes[env] = env_downsizes.get(env, 0) + 1
            elif row['Action Type'] == 'Upsize':
                env_upsizes[env] = env_upsizes.get(env, 0) + 1
        
        # Build formatted text output
        summary_text = []
        divider = "=" * 80
        
        # Overall summary
        summary_text.append(divider)
        summary_text.append("COMPREHENSIVE REPORT SUMMARY")
        summary_text.append(divider)
        summary_text.append(f"Total Recommendations: {total_actions}")
        summary_text.append(f"  - Downsizing: {downsizes}")
        summary_text.append(f"  - Upsizing: {upsizes}")
        summary_text.append(f"  - Other: {other}")
        summary_text.append("")
        summary_text.append(f"Estimated Monthly Savings: ${total_monthly_savings:,.2f}")
        summary_text.append(f"Estimated Monthly Add Cost: ${total_add_cost:,.2f}")
        summary_text.append(f"Net Monthly Impact: ${net_impact:,.2f}")
        summary_text.append("")
        summary_text.append("Environment Breakdown:")
        for env in sorted(env_breakdown.keys()):
            summary_text.append(f"  - {env}: {env_breakdown[env]}")
        summary_text.append(divider)
        summary_text.append("")
        
        # Per-environment summaries
        for env in sorted(env_breakdown.keys()):
            count = env_breakdown[env]
            savings = env_savings.get(env, 0)
            costs = env_costs.get(env, 0)
            down = env_downsizes.get(env, 0)
            up = env_upsizes.get(env, 0)
            other_env = count - down - up
            net = savings - costs
            
            summary_text.append(divider)
            summary_text.append(f"{env.upper()} ENVIRONMENT SUMMARY")
            summary_text.append(divider)
            summary_text.append(f"Total Recommendations: {count}")
            summary_text.append(f"  - Downsizing: {down}")
            summary_text.append(f"  - Upsizing: {up}")
            summary_text.append(f"  - Other: {other_env}")
            summary_text.append("")
            summary_text.append(f"Estimated Monthly Savings: ${savings:,.2f}")
            summary_text.append(f"Estimated Monthly Add Cost: ${costs:,.2f}")
            summary_text.append(f"Net Monthly Impact: ${net:,.2f}")
            summary_text.append("")
            summary_text.append("Environment Breakdown:")
            summary_text.append(f"  - {env}: {count}")
            summary_text.append(divider)
            summary_text.append("")
        
        # Export to text file
        summary_file = os.path.join(output_dir, f"Summary_Report_{timestamp}.txt")
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(summary_text))
        
        print(f"  ✓ Summary report exported to: {summary_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate Turbonomic rightsizing reports (Azure-focused with environment parsing)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all reports in a directory
  python3 generate_rightsizing_report_v3.py --url https://turbo.example.com --jsessionid <ID> --output-dir reports/
  
  # Generate reports in current directory
  python3 generate_rightsizing_report_v3.py --url https://turbo.example.com --jsessionid <ID>
  
  # CSV format
  python3 generate_rightsizing_report_v3.py --url https://turbo.example.com --jsessionid <ID> --format csv
        """
    )
    
    parser.add_argument('--url', required=True, help='Turbonomic instance URL')
    parser.add_argument('--jsessionid', required=True, help='JSESSIONID from login')
    parser.add_argument('--output-dir', default='.', help='Output directory for reports (default: current directory)')
    parser.add_argument('--action-type', choices=['upsize', 'downsize'], help='Filter by action type')
    parser.add_argument('--format', choices=['csv', 'excel'], default='excel', help='Output format (default: excel)')
    parser.add_argument('--all-clouds', action='store_true', help='Include all cloud providers (not just Azure)')
    parser.add_argument('--customer-mapping', help='Path to customer ID to name mapping JSON file')
    
    args = parser.parse_args()
    
    try:
        # Validate and create output directory
        output_dir = args.output_dir
        
        # Check if output_dir is actually a file (common mistake)
        if os.path.isfile(output_dir):
            print(f"Error: '{output_dir}' is a file, not a directory.")
            print(f"Use --output-dir to specify a directory, not a filename.")
            print(f"Example: --output-dir ./reports/")
            return 1
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        report = TurbonomicRightsizingReport(args.url, args.jsessionid, args.customer_mapping)
        
        print("Generating comprehensive rightsizing report...")
        all_data = report.generate_report_data(
            azure_only=not args.all_clouds,
            action_type_filter=args.action_type
        )
        
        # Generate comprehensive report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = '.xlsx' if args.format == 'excel' else '.csv'
        
        comprehensive_file = os.path.join(args.output_dir, f"Comprehensive_Rightsizing_Report_{timestamp}{ext}")
        
        if args.format == 'excel':
            report.export_to_excel(all_data, comprehensive_file)
        else:
            report.export_to_csv(all_data, comprehensive_file)
        
        report.print_summary(all_data, "COMPREHENSIVE REPORT SUMMARY")
        
        # Export summary report
        print(f"\nGenerating summary report...")
        report.export_summary_report(all_data, args.output_dir, timestamp, args.format)
        
        # Generate environment-specific reports
        environments = ['Dev', 'UAT', 'Pre-Prod', 'Prod', 'DR', 'Unmapped']
        
        print(f"\nGenerating environment-specific reports...")
        for env in environments:
            env_data = [r for r in all_data if r['Environment'] == env]
            
            if env_data:
                env_file = os.path.join(args.output_dir, f"{env}_Rightsizing_Report_{timestamp}{ext}")
                
                if args.format == 'excel':
                    report.export_to_excel(env_data, env_file)
                else:
                    report.export_to_csv(env_data, env_file)
                
                report.print_summary(env_data, f"{env.upper()} ENVIRONMENT SUMMARY")
            else:
                print(f"  ℹ No data for {env} environment")
        
        print(f"\n✓ All reports generated in: {args.output_dir}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())

# Made with Bob
