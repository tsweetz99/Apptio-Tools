#!/usr/bin/env python3
"""
Turbonomic Unified Report Generator
Generates all three reports (Rightsizing, Disk Optimization, Monthly Action Plan) with a single command.
"""

import argparse
import sys
import os
from datetime import datetime
from typing import Optional
import subprocess

# Import shared authentication module
from turbo_auth import setup_authentication


def run_report(script_name: str, url: str, jsessionid: str, 
               output_dir: str, customer_mapping: str,
               additional_args: list = None) -> bool:
    """
    Run a single report generator script.
    
    Args:
        script_name: Name of the script to run
        url: Turbonomic URL
        jsessionid: Authentication session ID
        output_dir: Output directory for reports
        customer_mapping: Path to customer mapping file
        additional_args: Additional arguments to pass to script
        
    Returns:
        True if successful, False otherwise
    """
    print(f"\n{'='*80}")
    print(f"Running {script_name}...")
    print(f"{'='*80}")
    
    cmd = [
        'python3',
        script_name,
        '--url', url,
        '--jsessionid', jsessionid,
        '--output-dir', output_dir,
        '--customer-mapping', customer_mapping
    ]
    
    if additional_args:
        cmd.extend(additional_args)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✓ {script_name} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {script_name} failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"✗ {script_name} failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Generate all Turbonomic reports with a single command',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all reports with username/password
  python3 generate_all_reports.py --url https://turbo.example.com --username admin@local
  
  # Generate all reports using environment variables
  export TURBO_URL="https://turbo.example.com"
  export TURBO_USERNAME="admin@local"
  export TURBO_PASSWORD="SecurePassword123"
  python3 generate_all_reports.py
  
  # Generate specific reports only
  python3 generate_all_reports.py --url https://turbo.example.com --username admin@local --reports rightsizing disk
  
  # Use existing JSESSIONID (backward compatible)
  python3 generate_all_reports.py --url https://turbo.example.com --jsessionid abc123...
        """
    )
    
    # Authentication options
    auth_group = parser.add_argument_group('Authentication')
    auth_group.add_argument('--url', help='Turbonomic instance URL (or set TURBO_URL)')
    auth_group.add_argument('--username', help='Username for authentication')
    auth_group.add_argument('--password', help='Password (will prompt if not provided)')
    auth_group.add_argument('--jsessionid', help='Existing JSESSIONID (legacy method)')
    
    # Report options
    report_group = parser.add_argument_group('Report Options')
    report_group.add_argument(
        '--reports',
        nargs='+',
        choices=['rightsizing', 'disk', 'monthly', 'all'],
        default=['all'],
        help='Which reports to generate (default: all)'
    )
    report_group.add_argument(
        '--output-dir',
        default='./reports',
        help='Output directory for all reports (default: ./reports)'
    )
    report_group.add_argument(
        '--customer-mapping',
        default='customer_mapping.json',
        help='Path to customer mapping file (default: customer_mapping.json)'
    )
    
    # Additional options
    parser.add_argument('--all-clouds', action='store_true', 
                       help='Include all cloud providers (not just Azure)')
    
    args = parser.parse_args()
    
    try:
        # Setup authentication
        print("="*80)
        print("TURBONOMIC UNIFIED REPORT GENERATOR")
        print("="*80)
        print()
        
        url, jsessionid = setup_authentication(
            url=args.url,
            username=args.username,
            password=args.password,
            jsessionid=args.jsessionid
        )
        
        print(f"\nConnected to: {url}")
        print(f"Output directory: {args.output_dir}")
        print()
        
        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Determine which reports to run
        reports_to_run = []
        if 'all' in args.reports:
            reports_to_run = ['rightsizing', 'disk', 'monthly']
        else:
            reports_to_run = args.reports
        
        # Track results
        results = {}
        
        # Additional arguments for reports
        additional_args = []
        if args.all_clouds:
            additional_args.append('--all-clouds')
        
        # Run Rightsizing Report
        if 'rightsizing' in reports_to_run:
            results['rightsizing'] = run_report(
                'generate_rightsizing_report_v4.py',
                url,
                jsessionid,
                args.output_dir,
                args.customer_mapping,
                additional_args
            )
        
        # Run Disk Optimization Report
        if 'disk' in reports_to_run:
            results['disk'] = run_report(
                'generate_disk_optimization_report_v2.py',
                url,
                jsessionid,
                args.output_dir,
                args.customer_mapping,
                additional_args
            )
        
        # Run Monthly Action Plan
        if 'monthly' in reports_to_run:
            # Monthly Action Plan uses --output instead of --output-dir
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            monthly_output = os.path.join(args.output_dir, f"Monthly_Action_Plan_{timestamp}.xlsx")
            
            print(f"\n{'='*80}")
            print(f"Running generate_monthly_action_plan.py...")
            print(f"{'='*80}")
            
            cmd = [
                'python3',
                'generate_monthly_action_plan.py',
                '--url', url,
                '--jsessionid', jsessionid,
                '--output', monthly_output,
                '--customer-mapping', args.customer_mapping
            ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=False)
                print(f"✓ generate_monthly_action_plan.py completed successfully")
                results['monthly'] = True
            except subprocess.CalledProcessError as e:
                print(f"✗ generate_monthly_action_plan.py failed with exit code {e.returncode}")
                results['monthly'] = False
            except Exception as e:
                print(f"✗ generate_monthly_action_plan.py failed: {e}")
                results['monthly'] = False
        
        # Print summary
        print(f"\n{'='*80}")
        print("REPORT GENERATION SUMMARY")
        print(f"{'='*80}")
        
        for report_name, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            print(f"{report_name.capitalize():20} {status}")
        
        print(f"\nAll reports saved to: {args.output_dir}")
        print(f"{'='*80}")
        
        # Return exit code based on results
        if all(results.values()):
            print("\n✓ All reports generated successfully!")
            return 0
        elif any(results.values()):
            print("\n⚠ Some reports failed. Check output above for details.")
            return 1
        else:
            print("\n✗ All reports failed.")
            return 1
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

# Made with Bob
