#!/usr/bin/env python3
"""
Turbonomic Rightsizing Recommendations Report Generator

This script generates a detailed rightsizing report from Turbonomic with the following columns:
- Server Name (VM/entity name)
- Customer Friendly Name (from CustomerID tag)
- Current Configuration (current VM size/specs)
- Recommendation (suggested VM size)
- Action Type (Downsize/Upsize)
- Monthly Savings (for downsizing)
- Net Add Cost (for upsizing, Prod only)

The script can filter by environment (Dev, UAT, Pre-Prod, Prod, DR) based on tags.

Requirements:
    pip install requests pandas openpyxl

Usage:
    # Generate report for all environments
    python generate_rightsizing_report.py --url https://your-turbo-instance.com --jsessionid <SESSION_ID>
    
    # Generate report for specific environment
    python generate_rightsizing_report.py --url https://your-turbo-instance.com --jsessionid <SESSION_ID> --environment Prod
    
    # Export to Excel
    python generate_rightsizing_report.py --url https://your-turbo-instance.com --jsessionid <SESSION_ID> --output rightsizing_report.xlsx
    
    # Filter by action type
    python generate_rightsizing_report.py --url https://your-turbo-instance.com --jsessionid <SESSION_ID> --action-type downsize
"""

import requests
import json
import argparse
import sys
from datetime import datetime
from typing import List, Dict, Optional
import csv

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas not installed. Excel export will not be available.")
    print("Install with: pip install pandas openpyxl")


class TurbonomicRightsizingReport:
    """Generate rightsizing recommendations report from Turbonomic API."""
    
    def __init__(self, turbo_url: str, jsessionid: str):
        """
        Initialize the report generator.
        
        Args:
            turbo_url: Base URL of Turbonomic instance (e.g., https://turbo.example.com)
            jsessionid: Session ID from login
        """
        self.turbo_url = turbo_url.rstrip('/')
        self.session = requests.Session()
        self.session.cookies.set('JSESSIONID', jsessionid)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def get_recommended_actions(self, environment: Optional[str] = None) -> List[Dict]:
        """
        Fetch recommended actions from Turbonomic API.
        
        Args:
            environment: Optional environment filter (Dev, UAT, Pre-Prod, Prod, DR)
            
        Returns:
            List of action dictionaries
        """
        url = f"{self.turbo_url}/api/v3/markets/Market/actions"
        
        # Build request payload
        payload = {
            "actionStateList": [
                "READY",
                "QUEUED",
                "IN_PROGRESS",
                "ACCEPTED"
            ],
            "actionTypeList": [
                "RESIZE",
                "SCALE"
            ],
            "relatedEntityTypes": [
                "VirtualMachine"
            ],
            "environmentType": "CLOUD",
            "detailLevel": "EXECUTION"
        }
        
        params = {
            "ascending": "false",
            "cursor": "0",
            "disable_hateoas": "true",
            "forceExpansionOfAggregatedEntities": "true",
            "order_by": "savings"
        }
        
        try:
            print(f"Fetching recommended actions from {url}...")
            response = self.session.post(url, json=payload, params=params)
            response.raise_for_status()
            
            data = response.json()
            actions = data if isinstance(data, list) else []
            
            print(f"Retrieved {len(actions)} recommended actions")
            
            # Filter by environment if specified
            if environment:
                actions = self._filter_by_environment(actions, environment)
                print(f"Filtered to {len(actions)} actions for environment: {environment}")
            
            return actions
            
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
            # Check entity tags for environment
            entity = action.get('target', {})
            tags = entity.get('tags', [])
            
            # Look for environment tag
            for tag in tags:
                if isinstance(tag, dict):
                    tag_value = tag.get('value', '').lower()
                    if env_lower in tag_value or tag_value in env_lower:
                        filtered.append(action)
                        break
        
        return filtered
    
    def _get_tag_value(self, entity: Dict, tag_key: str) -> str:
        """Extract tag value from entity."""
        tags = entity.get('tags', [])
        for tag in tags:
            if isinstance(tag, dict) and tag.get('key', '').lower() == tag_key.lower():
                return tag.get('value', 'N/A')
        return 'N/A'
    
    def _determine_action_type(self, action: Dict) -> str:
        """Determine if action is upsize or downsize based on resource changes."""
        action_type = action.get('actionType', '')
        
        # Check risk sub-category or details
        risk_sub_category = action.get('riskSubCategory', '').lower()
        details = action.get('details', '').lower()
        
        if 'underutilized' in risk_sub_category or 'underutilized' in details:
            return 'Downsize'
        elif 'overutilized' in risk_sub_category or 'overutilized' in details:
            return 'Upsize'
        elif action_type == 'RESIZE':
            # Try to determine from current vs new values
            current_value = action.get('currentValue', {})
            new_value = action.get('newValue', {})
            
            # Compare resource values if available
            if isinstance(current_value, dict) and isinstance(new_value, dict):
                current_avg = current_value.get('avg', 0)
                new_avg = new_value.get('avg', 0)
                if new_avg < current_avg:
                    return 'Downsize'
                elif new_avg > current_avg:
                    return 'Upsize'
        
        return 'Resize'
    
    def _format_configuration(self, entity: Dict) -> str:
        """Format current VM configuration."""
        # Try to get VM template or instance type
        aspects = entity.get('aspects', {})
        
        # Check for cloud-specific info
        vm_data = aspects.get('virtualMachineAspect', {})
        instance_type = vm_data.get('instanceType', '')
        
        if instance_type:
            return instance_type
        
        # Fallback to resource specs
        cpu = entity.get('numCPUs', 'N/A')
        mem_mb = entity.get('memoryMB', 0)
        mem_gb = round(mem_mb / 1024, 2) if mem_mb else 'N/A'
        
        return f"{cpu} vCPU, {mem_gb} GB RAM"
    
    def _format_recommendation(self, action: Dict) -> str:
        """Format recommended configuration."""
        new_entity = action.get('newEntity', {})
        
        # Try to get recommended instance type
        aspects = new_entity.get('aspects', {})
        vm_data = aspects.get('virtualMachineAspect', {})
        instance_type = vm_data.get('instanceType', '')
        
        if instance_type:
            return instance_type
        
        # Fallback to resource changes
        risk = action.get('risk', {})
        description = risk.get('description', '')
        
        if description:
            return description
        
        return 'See Turbonomic for details'
    
    def _calculate_monthly_savings(self, action: Dict, action_type: str) -> float:
        """Calculate monthly savings (for downsizing)."""
        if action_type != 'Downsize':
            return 0.0
        
        # Get savings from action
        stats = action.get('stats', [])
        for stat in stats:
            if isinstance(stat, dict):
                stat_name = stat.get('name', '').lower()
                if 'saving' in stat_name or 'cost' in stat_name:
                    value = stat.get('value', 0)
                    # Convert to monthly if needed (assuming value is in dollars)
                    return abs(float(value)) * 30  # Rough monthly estimate
        
        return 0.0
    
    def _calculate_net_add_cost(self, action: Dict, action_type: str, environment: str) -> float:
        """Calculate net additional cost (for upsizing in Prod only)."""
        if action_type != 'Upsize':
            return 0.0
        
        if environment and environment.lower() != 'prod':
            return 0.0
        
        # Get cost increase from action
        stats = action.get('stats', [])
        for stat in stats:
            if isinstance(stat, dict):
                stat_name = stat.get('name', '').lower()
                if 'cost' in stat_name:
                    value = stat.get('value', 0)
                    # Convert to monthly if needed
                    return abs(float(value)) * 30  # Rough monthly estimate
        
        return 0.0
    
    def generate_report_data(self, environment: Optional[str] = None, 
                            action_type_filter: Optional[str] = None) -> List[Dict]:
        """
        Generate report data from Turbonomic actions.
        
        Args:
            environment: Optional environment filter
            action_type_filter: Optional filter for 'upsize' or 'downsize'
            
        Returns:
            List of report row dictionaries
        """
        actions = self.get_recommended_actions(environment)
        
        report_data = []
        
        for action in actions:
            target = action.get('target', {})
            
            # Determine action type
            action_type = self._determine_action_type(action)
            
            # Apply action type filter if specified
            if action_type_filter:
                if action_type_filter.lower() == 'downsize' and action_type != 'Downsize':
                    continue
                if action_type_filter.lower() == 'upsize' and action_type != 'Upsize':
                    continue
            
            # Build report row
            row = {
                'Server Name': target.get('displayName', 'N/A'),
                'Customer Friendly Name': self._get_tag_value(target, 'CustomerID'),
                'Current Configuration': self._format_configuration(target),
                'Recommendation': self._format_recommendation(action),
                'Action Type': action_type,
                'Monthly Savings': self._calculate_monthly_savings(action, action_type),
                'Net Add Cost': self._calculate_net_add_cost(action, action_type, environment or ''),
                'Environment': self._get_tag_value(target, 'Environment'),
                'Action State': action.get('actionState', 'N/A'),
                'Risk': action.get('risk', {}).get('severity', 'N/A'),
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
            print("Install with: pip install pandas openpyxl")
            return
        
        if not report_data:
            print("No data to export")
            return
        
        # pandas is available at this point due to PANDAS_AVAILABLE check
        import pandas as pd  # type: ignore
        
        df = pd.DataFrame(report_data)
        
        # Create Excel writer
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Rightsizing Report', index=False)
            
            # Get workbook and worksheet
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
        description='Generate Turbonomic rightsizing recommendations report',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate report for all environments
  python generate_rightsizing_report.py --url https://turbo.example.com --jsessionid <SESSION_ID>
  
  # Generate report for Production environment only
  python generate_rightsizing_report.py --url https://turbo.example.com --jsessionid <SESSION_ID> --environment Prod
  
  # Generate report with only downsizing recommendations
  python generate_rightsizing_report.py --url https://turbo.example.com --jsessionid <SESSION_ID> --action-type downsize
  
  # Export to Excel
  python generate_rightsizing_report.py --url https://turbo.example.com --jsessionid <SESSION_ID> --output report.xlsx
  
  # Export to CSV
  python generate_rightsizing_report.py --url https://turbo.example.com --jsessionid <SESSION_ID> --output report.csv

Environment Options: Dev, UAT, Pre-Prod, Prod, DR
Action Type Options: upsize, downsize
        """
    )
    
    parser.add_argument(
        '--url',
        required=True,
        help='Turbonomic instance URL (e.g., https://turbo.example.com)'
    )
    
    parser.add_argument(
        '--jsessionid',
        required=True,
        help='JSESSIONID from Turbonomic login'
    )
    
    parser.add_argument(
        '--environment',
        choices=['Dev', 'UAT', 'Pre-Prod', 'Prod', 'DR'],
        help='Filter by environment (based on tags)'
    )
    
    parser.add_argument(
        '--action-type',
        choices=['upsize', 'downsize'],
        help='Filter by action type'
    )
    
    parser.add_argument(
        '--output',
        help='Output file (CSV or Excel based on extension)'
    )
    
    parser.add_argument(
        '--format',
        choices=['csv', 'excel'],
        help='Output format (auto-detected from filename if not specified)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize report generator
        report = TurbonomicRightsizingReport(args.url, args.jsessionid)
        
        # Generate report data
        print("Generating rightsizing report...")
        report_data = report.generate_report_data(
            environment=args.environment,
            action_type_filter=args.action_type
        )
        
        # Print summary
        report.print_summary(report_data)
        
        # Export if requested
        if args.output:
            # Determine format
            output_format = args.format
            if not output_format:
                if args.output.lower().endswith('.xlsx'):
                    output_format = 'excel'
                else:
                    output_format = 'csv'
            
            if output_format == 'excel':
                report.export_to_excel(report_data, args.output)
            else:
                report.export_to_csv(report_data, args.output)
        else:
            # Print first few rows as preview
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
        return 1


if __name__ == '__main__':
    exit(main())

# Made with Bob
