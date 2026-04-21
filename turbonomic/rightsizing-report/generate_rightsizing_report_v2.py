#!/usr/bin/env python3
"""
Turbonomic Rightsizing Recommendations Report Generator (Fixed Version)

This script generates a detailed rightsizing report from Turbonomic with proper data extraction
based on the actual API response structure.

Requirements:
    pip install requests pandas openpyxl

Usage:
    python3 generate_rightsizing_report_v2.py --url https://your-turbo-instance.com --jsessionid <SESSION_ID> --output report.xlsx
"""

import requests
import json
import argparse
import sys
import re
from datetime import datetime
from typing import List, Dict, Optional
import csv

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class TurbonomicRightsizingReport:
    """Generate rightsizing recommendations report from Turbonomic API."""
    
    def __init__(self, turbo_url: str, jsessionid: str):
        self.turbo_url = turbo_url.rstrip('/')
        self.session = requests.Session()
        self.session.cookies.set('JSESSIONID', jsessionid)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def get_recommended_actions(self, environment: Optional[str] = None, fetch_all: bool = True) -> List[Dict]:
        """Fetch recommended actions with pagination support."""
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
            
            if environment:
                all_actions = self._filter_by_environment(all_actions, environment)
                print(f"Filtered to {len(all_actions)} actions for environment: {environment}")
            
            return all_actions
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching actions: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return []
    
    def _filter_by_environment(self, actions: List[Dict], environment: str) -> List[Dict]:
        """Filter actions by environment tag."""
        filtered = []
        env_lower = environment.lower()
        
        for action in actions:
            target = action.get('target', {})
            env_tag = self._get_tag_value(target, 'environment')
            
            if env_lower in env_tag.lower():
                filtered.append(action)
        
        return filtered
    
    def _get_tag_value(self, entity: Dict, tag_key: str) -> str:
        """Extract tag value from entity. Tags are dict with array values."""
        tags = entity.get('tags', {})
        
        if isinstance(tags, dict):
            # Try exact match
            if tag_key in tags:
                tag_value = tags[tag_key]
                if isinstance(tag_value, list) and tag_value:
                    return tag_value[0] if tag_value[0] else 'N/A'
                return str(tag_value) if tag_value else 'N/A'
            
            # Try case-insensitive match
            for key, value in tags.items():
                if key.lower() == tag_key.lower():
                    if isinstance(value, list) and value:
                        return value[0] if value[0] else 'N/A'
                    return str(value) if value else 'N/A'
        
        return 'N/A'
    
    def _determine_action_type(self, action: Dict) -> str:
        """Determine if action is upsize or downsize."""
        # Get current and new instance types
        current_entity = action.get('currentEntity', {})
        new_entity = action.get('newEntity', {})
        current_name = current_entity.get('displayName', '')
        new_name = new_entity.get('displayName', '')
        
        # Check risk description
        risk = action.get('risk', {})
        risk_sub_category = risk.get('subCategory', '').lower()
        risk_description = risk.get('description', '').lower()
        details = action.get('details', '').lower()
        
        # Check for underutilized (downsize)
        if 'underutilized' in risk_sub_category or 'underutilized' in details:
            return 'Downsize'
        
        # Check for overutilized (upsize)
        if 'overutilized' in risk_sub_category or 'overutilized' in details:
            return 'Upsize'
        
        # Try to determine from instance type comparison
        if current_name and new_name:
            # Extract numbers from instance types
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
        
        # Check stats for cost impact
        stats = action.get('stats', [])
        for stat in stats:
            if isinstance(stat, dict):
                stat_name = stat.get('name', '').lower()
                value = stat.get('value', 0)
                
                # Positive cost = increase (upsize), negative = savings (downsize)
                if 'cost' in stat_name:
                    if value > 0:
                        return 'Upsize'
                    elif value < 0:
                        return 'Downsize'
        
        return 'Resize'
    
    def _format_configuration(self, action: Dict) -> str:
        """Format current VM configuration from currentEntity."""
        current_entity = action.get('currentEntity', {})
        instance_type = current_entity.get('displayName', 'N/A')
        return instance_type if instance_type else 'N/A'
    
    def _format_recommendation(self, action: Dict) -> str:
        """Format recommended configuration from newEntity."""
        new_entity = action.get('newEntity', {})
        instance_type = new_entity.get('displayName', 'N/A')
        return instance_type if instance_type else 'N/A'
    
    def _calculate_monthly_savings(self, action: Dict, action_type: str) -> float:
        """Calculate monthly savings (for downsizing)."""
        if action_type != 'Downsize':
            return 0.0
        
        # Get cost stats - they're in $/h
        stats = action.get('stats', [])
        for stat in stats:
            if isinstance(stat, dict):
                stat_name = stat.get('name', '').lower()
                value = stat.get('value', 0)
                
                if 'cost' in stat_name and value != 0:
                    hourly_rate = abs(float(value))
                    # Convert hourly to monthly (730 hours/month average)
                    return hourly_rate * 730
        
        return 0.0
    
    def _calculate_net_add_cost(self, action: Dict, action_type: str, environment: str) -> float:
        """Calculate net additional cost (for upsizing in Prod only)."""
        if action_type != 'Upsize':
            return 0.0
        
        # Check if environment is Production
        if environment and 'prod' not in environment.lower():
            return 0.0
        
        # Get cost stats - they're in $/h
        stats = action.get('stats', [])
        for stat in stats:
            if isinstance(stat, dict):
                stat_name = stat.get('name', '').lower()
                value = stat.get('value', 0)
                
                if 'cost' in stat_name and value != 0:
                    hourly_rate = abs(float(value))
                    # Convert hourly to monthly
                    return hourly_rate * 730
        
        return 0.0
    
    def generate_report_data(self, environment: Optional[str] = None, 
                            action_type_filter: Optional[str] = None) -> List[Dict]:
        """Generate report data from Turbonomic actions."""
        actions = self.get_recommended_actions(environment)
        
        report_data = []
        
        for action in actions:
            target = action.get('target', {})
            
            # Determine action type
            action_type = self._determine_action_type(action)
            
            # Apply action type filter
            if action_type_filter:
                if action_type_filter.lower() == 'downsize' and action_type != 'Downsize':
                    continue
                if action_type_filter.lower() == 'upsize' and action_type != 'Upsize':
                    continue
            
            # Get environment for this action
            env = self._get_tag_value(target, 'environment')
            
            # Build report row
            row = {
                'Server Name': target.get('displayName', 'N/A'),
                'Customer Friendly Name': self._get_tag_value(target, 'CustomerID'),
                'Current Configuration': self._format_configuration(action),
                'Recommendation': self._format_recommendation(action),
                'Action Type': action_type,
                'Monthly Savings': self._calculate_monthly_savings(action, action_type),
                'Net Add Cost': self._calculate_net_add_cost(action, action_type, env),
                'Environment': env,
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
            print("No data to export")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=report_data[0].keys())
            writer.writeheader()
            writer.writerows(report_data)
        
        print(f"Report exported to: {filename}")
    
    def export_to_excel(self, report_data: List[Dict], filename: str):
        """Export report data to Excel with formatting."""
        if not PANDAS_AVAILABLE:
            print("Error: pandas not installed. Cannot export to Excel.")
            print("Install with: pip3 install pandas openpyxl")
            return
        
        if not report_data:
            print("No data to export")
            return
        
        import pandas as pd  # type: ignore
        
        df = pd.DataFrame(report_data)
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Rightsizing Report', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Rightsizing Report']
            
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
        
        print(f"Report exported to: {filename}")
    
    def print_summary(self, report_data: List[Dict]):
        """Print report summary statistics."""
        if not report_data:
            print("No data in report")
            return
        
        total_actions = len(report_data)
        downsizes = len([r for r in report_data if r['Action Type'] == 'Downsize'])
        upsizes = len([r for r in report_data if r['Action Type'] == 'Upsize'])
        
        total_monthly_savings = sum(r['Monthly Savings'] for r in report_data)
        total_add_cost = sum(r['Net Add Cost'] for r in report_data)
        
        print("\n" + "="*80)
        print("RIGHTSIZING REPORT SUMMARY")
        print("="*80)
        print(f"Total Recommendations: {total_actions}")
        print(f"  - Downsizing: {downsizes}")
        print(f"  - Upsizing: {upsizes}")
        print(f"  - Other: {total_actions - downsizes - upsizes}")
        print(f"\nEstimated Monthly Savings: ${total_monthly_savings:,.2f}")
        print(f"Estimated Monthly Add Cost: ${total_add_cost:,.2f}")
        print(f"Net Monthly Impact: ${total_monthly_savings - total_add_cost:,.2f}")
        
        # Environment breakdown
        environments = {}
        for row in report_data:
            env = row.get('Environment', 'Unknown')
            environments[env] = environments.get(env, 0) + 1
        
        if environments:
            print(f"\nEnvironment Breakdown:")
            for env, count in sorted(environments.items()):
                print(f"  - {env}: {count}")
        
        print("="*80)


def main():
    parser = argparse.ArgumentParser(
        description='Generate Turbonomic rightsizing recommendations report (Fixed Version)',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--url', required=True, help='Turbonomic instance URL')
    parser.add_argument('--jsessionid', required=True, help='JSESSIONID from login')
    parser.add_argument('--environment', choices=['Dev', 'UAT', 'Pre-Prod', 'Prod', 'DR', 'Production'],
                       help='Filter by environment')
    parser.add_argument('--action-type', choices=['upsize', 'downsize'], help='Filter by action type')
    parser.add_argument('--output', help='Output file (CSV or Excel)')
    parser.add_argument('--format', choices=['csv', 'excel'], help='Output format')
    
    args = parser.parse_args()
    
    try:
        report = TurbonomicRightsizingReport(args.url, args.jsessionid)
        
        print("Generating rightsizing report...")
        report_data = report.generate_report_data(
            environment=args.environment,
            action_type_filter=args.action_type
        )
        
        report.print_summary(report_data)
        
        if args.output:
            output_format = args.format
            if not output_format:
                output_format = 'excel' if args.output.lower().endswith('.xlsx') else 'csv'
            
            if output_format == 'excel':
                report.export_to_excel(report_data, args.output)
            else:
                report.export_to_csv(report_data, args.output)
        else:
            if report_data:
                print(f"\nFirst 5 recommendations:")
                print("-" * 120)
                for i, row in enumerate(report_data[:5]):
                    print(f"{i+1}. {row['Server Name']} ({row['Action Type']}) - {row['Current Configuration']} -> {row['Recommendation']}")
                
                if len(report_data) > 5:
                    print(f"... and {len(report_data) - 5} more")
                
                print(f"\nUse --output filename.xlsx to export full report")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())

# Made with Bob
