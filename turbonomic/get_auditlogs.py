#!/usr/bin/env python3
"""
Turbonomic Audit Logs Retrieval Script

This script downloads and extracts audit logs from the Turbonomic API.
The API returns a tar.gz compressed archive containing log files.

Usage:
    python get_auditlogs.py --jsessionid <JSESSIONID> [--days <DAYS>] [--url <TURBO_URL>]

Example:
    python get_auditlogs.py --jsessionid node01g4tqattmvscf1a9b0us8iw6xw232.node0 --days 1
"""

import argparse
import requests
import tarfile
import os
from datetime import datetime
from pathlib import Path


def download_auditlogs(turbo_url, jsessionid, days=1):
    """
    Download audit logs from Turbonomic API.
    
    Args:
        turbo_url: Base URL of Turbonomic instance
        jsessionid: Session ID for authentication
        days: Number of days of logs to retrieve (default: 1)
    
    Returns:
        Path to downloaded tar.gz file
    """
    api_endpoint = f"{turbo_url}/api/v3/admin/auditlogs"
    params = {"days": days}
    headers = {"Cookie": f"JSESSIONID={jsessionid}"}
    
    print(f"Downloading audit logs for the last {days} day(s)...")
    print(f"URL: {api_endpoint}")
    
    try:
        response = requests.get(api_endpoint, params=params, headers=headers, stream=True)
        response.raise_for_status()
        
        # Save to file
        output_file = "auditlog.tar.gz"
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Download complete: {output_file}")
        return output_file
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading audit logs: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        raise


def extract_auditlogs(tar_file, output_dir=None):
    """
    Extract the tar.gz audit log archive.
    
    Args:
        tar_file: Path to tar.gz file
        output_dir: Directory to extract to (default: auto-generated)
    
    Returns:
        Path to extraction directory
    """
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"auditlogs_{timestamp}"
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"Extracting archive to: {output_dir}")
    
    try:
        with tarfile.open(tar_file, 'r:gz') as tar:
            tar.extractall(path=output_dir)
        
        print("Extraction successful!")
        
        # List extracted files
        extracted_files = list(Path(output_dir).rglob('*'))
        log_files = [f for f in extracted_files if f.is_file()]
        print(f"\nExtracted {len(log_files)} log file(s):")
        for file in log_files:
            size = file.stat().st_size
            print(f"  - {file.relative_to(output_dir)} ({size:,} bytes)")
        
        return output_dir
        
    except Exception as e:
        print(f"Error extracting archive: {e}")
        raise


def read_log_file(log_file, num_lines=None):
    """
    Read and display contents of a log file.
    
    Args:
        log_file: Path to log file
        num_lines: Number of lines to display (None = all)
    """
    print(f"\n{'='*80}")
    print(f"Contents of: {log_file}")
    print('='*80)
    
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            if num_lines:
                for i, line in enumerate(f):
                    if i >= num_lines:
                        print(f"\n... (showing first {num_lines} lines)")
                        break
                    print(line.rstrip())
            else:
                print(f.read())
    except Exception as e:
        print(f"Error reading file: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Download and extract Turbonomic audit logs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download last 1 day of logs
  python get_auditlogs.py --jsessionid node01g4tqattmvscf1a9b0us8iw6xw232.node0
  
  # Download last 7 days of logs
  python get_auditlogs.py --jsessionid <SESSION_ID> --days 7
  
  # Specify custom Turbonomic URL
  python get_auditlogs.py --jsessionid <SESSION_ID> --url https://your-turbo-instance.com
        """
    )
    
    parser.add_argument(
        '--jsessionid',
        required=True,
        help='JSESSIONID for authentication (obtained from login API)'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=1,
        help='Number of days of logs to retrieve (default: 1)'
    )
    
    parser.add_argument(
        '--url',
        default='https://cldp-autodesk.apptio.turbonomic.ibmappdomain.cloud',
        help='Turbonomic instance URL (default: cldp-autodesk instance)'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Directory to extract logs to (default: auto-generated with timestamp)'
    )
    
    parser.add_argument(
        '--preview',
        type=int,
        metavar='LINES',
        help='Preview first N lines of each log file after extraction'
    )
    
    parser.add_argument(
        '--keep-archive',
        action='store_true',
        help='Keep the tar.gz file after extraction (default: delete)'
    )
    
    args = parser.parse_args()
    
    try:
        # Download audit logs
        tar_file = download_auditlogs(args.url, args.jsessionid, args.days)
        
        # Extract archive
        output_dir = extract_auditlogs(tar_file, args.output_dir)
        
        # Preview log files if requested
        if args.preview:
            log_files = [f for f in Path(output_dir).rglob('*') if f.is_file() and f.suffix in ['.log', '.txt', '']]
            for log_file in log_files:
                read_log_file(log_file, args.preview)
        
        # Clean up tar.gz file unless --keep-archive is specified
        if not args.keep_archive:
            os.remove(tar_file)
            print(f"\nRemoved archive file: {tar_file}")
        
        print(f"\n✓ Audit logs successfully extracted to: {output_dir}")
        
        # Find actual log files and provide correct paths
        log_files = [f for f in Path(output_dir).rglob('*') if f.is_file()]
        if log_files:
            print(f"\nTo view the logs:")
            for log_file in log_files:
                print(f"  cat {log_file}")
                print(f"  # or")
                print(f"  less {log_file}")
                break  # Just show one example
            if len(log_files) > 1:
                print(f"\n  # Or view all files:")
                print(f"  find {output_dir} -type f -exec cat {{}} \\;")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

# Made with Bob
