#!/usr/bin/env python3
"""
Dashboard Dolly - Cloudability Dashboard Transfer Tool
Based on the original dashboard migration script with GUI enhancements.

This tool provides a graphical interface for transferring Cloudability dashboards
between environments, with support for measure mapping and batch operations.
"""

import os
import csv
import re
import sys
import json
import requests
from typing import Dict, List, Optional
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Try to import apptio_lib for Frontdoor auth
try:
    from apptio_lib import apptio as fd
    from apptio_lib import cloudability as cldy
    APPTIO_LIB_AVAILABLE = True
except ImportError:
    APPTIO_LIB_AVAILABLE = False
    print("Warning: apptio_lib not available. Frontdoor authentication will not work.")

# Measure mapping lets you define dimensions and metrics to replace when migrating dashboards.
# Example:
# measure_mapping = {
#     'tag3': 'tag1',
#     'category6': 'group7',
# }
measure_mapping = {}

DB_JSON_FOLDER = 'Dashboards_to_Upload'
ENV_ROOT = 'Environments'


def get_layers_from_widget(widget):
    """Apply measure mappings to widget layers."""
    layers = []
    for layer in widget['options']['layers']:
        new_dims = []
        for dim in layer['dimensions']:
            if dim not in measure_mapping:
                new_dims.append(dim)
                continue
            new_dims.append(measure_mapping[dim])

        new_metrics = []
        for metric in layer['metrics']:
            if metric not in measure_mapping:
                new_metrics.append(metric)
                continue
            new_metrics.append(measure_mapping[metric])

        new_filters = []
        for filter_item in layer['filters']:
            filter_measure = filter_item['name']
            if filter_measure in measure_mapping:
                filter_measure = measure_mapping[filter_measure]
            new_filters.append(f"{filter_measure}{filter_item['operator']}{filter_item['value']}")
        
        layer['dimensions'] = new_dims
        layer['metrics'] = new_metrics
        layer['filters'] = new_filters
        layers.append(layer.copy())
    return layers


def upload_dashboards(api_key='', headers={}, region=''):
    """Upload dashboards from the upload folder."""
    dashboards = load_dbs_from_folder(DB_JSON_FOLDER)
    if not dashboards:
        print(f'No dashboards found in {DB_JSON_FOLDER}. Please include some dashboards first.')
        return False
    
    created = []
    for dashboard in dashboards:
        id = dashboard['id']
        name = dashboard['name']

        new_dashboard = make_dashboard(name, api_key=api_key, opentoken_headers=headers, region=region)
        new_dashboard_id = new_dashboard['id']
        print(f'Created dashboard {new_dashboard_id} {name}')
        created.append(new_dashboard_id)

        for widget in dashboard['widgets']:
            widget['dashboard_id'] = new_dashboard_id
            widget['options']['layers'] = get_layers_from_widget(widget)
            
            # Special handling for USGov
            if region == 'usgov' and APPTIO_LIB_AVAILABLE:
                widget_ep = f'https://api.usgov.cloudability.com/v3/internal/widgets'
                cldy.post(widget_ep, data=widget, api_key=api_key, opentoken_headers=headers)
            else:
                # Let library handle all other regions normally
                if APPTIO_LIB_AVAILABLE:
                    cldy.post('/internal/widgets', data=widget, api_key=api_key, opentoken_headers=headers, region=region)
                else:
                    # Fallback to direct requests
                    post_widget(widget, api_key=api_key, headers=headers, region=region)
    
    print(f'Created {len(created)} dashboards')
    return True


def get_dashboard(id, api_key=None, opentoken_headers=None, region=''):
    """Get a dashboard by ID."""
    region_str = format_region(region)
    ep = f'https://api{region_str}.cloudability.com/v3/internal/dashboards/{id}?skip_shared_dimension_filter_set_ids=true&use_basic_user=true'
    
    if APPTIO_LIB_AVAILABLE:
        return cldy.get(ep, api_key=api_key, opentoken_headers=opentoken_headers)
    else:
        return get_request(ep, api_key=api_key, headers=opentoken_headers)


def get_dashboard_list(api_key=None, opentoken_headers=None, region=''):
    """Get list of all dashboards."""
    region_str = format_region(region)
    ep = f'https://api{region_str}.cloudability.com/v3/internal/dashboards?limit=500&skip_shared_dimension_filter_set_ids=true&use_basic_user=true'
    
    if APPTIO_LIB_AVAILABLE:
        return cldy.get(ep, api_key=api_key, opentoken_headers=opentoken_headers)
    else:
        return get_request(ep, api_key=api_key, headers=opentoken_headers)


def save_dashboards(api_key='', headers={}, region='', customer_name='', starred_only=False):
    """Save dashboards to files."""
    dashboards = get_dashboard_list(api_key=api_key, opentoken_headers=headers, region=region)
    print(f'Found {len(dashboards)} dashboards for {customer_name}')
    unfiltered_count = len(dashboards)
    
    if starred_only:
        dashboards = [d for d in dashboards if d.get('star', False)]
        if not dashboards:
            print('No starred dashboards found.')
            return
        print(f'Filtered to {len(dashboards)} starred dashboards out of {unfiltered_count} total dashboards')

    save_dir = f'{ENV_ROOT}/{customer_name}/Dashboards'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    saved_count = 0
    total_count = len(dashboards)
    
    for dashboard_info in dashboards:
        id = dashboard_info['id']
        name = dashboard_info['name']
        
        # Get full dashboard json
        dashboard = get_dashboard(id, api_key=api_key, opentoken_headers=headers, region=region)
        db_save_name = f'{id}-{name}.json'
    
        # Sanitize dashboard name for filename
        db_save_name = re.sub(r'[\\/*?:"<>|]', '', db_save_name)
        db_save_name = re.sub(r'\s+', '_', db_save_name)
        filename = f"{save_dir}/{db_save_name}"
        
        with open(filename, 'w') as f:
            json.dump(dashboard, f, indent=4)
        
        saved_count += 1
        percent_complete = (saved_count / total_count) * 100
        sys.stdout.write(f"\rSaving dashboards: {percent_complete:.0f}% Complete ({saved_count}/{total_count})")
        sys.stdout.flush()

    print(f'\nSaved {saved_count} dashboards to {save_dir}')


def make_dashboard(name, api_key=None, opentoken_headers=None, region=''):
    """Create a new dashboard."""
    region_str = format_region(region)
    ep = f'https://api{region_str}.cloudability.com/v3/internal/dashboards'
    data = {'name': name}
    
    if APPTIO_LIB_AVAILABLE:
        return cldy.post(ep, api_key=api_key, data=data, opentoken_headers=opentoken_headers)
    else:
        return post_request(ep, data=data, api_key=api_key, headers=opentoken_headers)


def load_dbs_from_folder(folder):
    """Load dashboard JSON files from a specified folder."""
    dashboards = []
    if not os.path.exists(folder):
        print(f'Folder {folder} does not exist.')
        return dashboards

    for filename in os.listdir(folder):
        if filename.endswith('.json'):
            filepath = os.path.join(folder, filename)
            with open(filepath, 'r') as f:
                try:
                    dashboard = json.load(f)
                    dashboards.append(dashboard)
                except json.JSONDecodeError as e:
                    print(f'Error decoding JSON from {filename}: {e}')
    return dashboards


def load_config(env_folder):
    """Load configuration from environment folder."""
    config = {}
    try:
        config_path = os.path.join(env_folder, 'config.json')
        if not os.path.exists(config_path):
            print(f'Config file not found in {env_folder}/config.json')
            return False
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if not config_verify(config):
            return False
    except FileNotFoundError:
        print(f'Config file not found in {env_folder}/config.json')
        return False
    return config


def config_verify(config):
    """Verify the config file has the required keys."""
    required_keys = [
        ['frontdoor_environment', 'public_key', 'private_key'],
        ['cldyKey'],
    ]
    
    # Check for either 'region' or 'frontdoor_region' (support both naming conventions)
    if 'region' not in config and 'frontdoor_region' not in config:
        print('region is required in config file.')
        return False
    
    for group in required_keys:
        if all(key in config for key in group):
            return True
    
    print('Config file is missing required keys. At least one of the following groups must be present:')
    print(' - frontdoor_environment, public_key, private_key')
    print(' - cldyKey')
    return False


def format_region(region):
    """Format region string for API URL."""
    if not region:
        return ""
    if region.startswith('.') or region.startswith('-'):
        return region
    if region == 'usgov':
        return '.usgov'
    return f'-{region}'


def get_request(url, api_key=None, headers=None):
    """Make a GET request."""
    session = requests.Session()
    session.verify = False
    
    if api_key:
        from requests.auth import HTTPBasicAuth
        session.auth = HTTPBasicAuth(api_key, '')
    elif headers:
        session.headers.update(headers)
    
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def post_request(url, data, api_key=None, headers=None):
    """Make a POST request."""
    session = requests.Session()
    session.verify = False
    
    if api_key:
        from requests.auth import HTTPBasicAuth
        session.auth = HTTPBasicAuth(api_key, '')
    elif headers:
        session.headers.update(headers)
    
    response = session.post(url, json=data, headers={'Content-Type': 'application/json'}, timeout=30)
    response.raise_for_status()
    return response.json()


def post_widget(widget, api_key=None, headers=None, region=''):
    """Post a widget."""
    region_str = format_region(region)
    ep = f'https://api{region_str}.cloudability.com/v3/internal/widgets'
    return post_request(ep, data=widget, api_key=api_key, headers=headers)


def main():
    """Main entry point - CLI version."""
    # Check that config folder exists
    if not os.path.exists(ENV_ROOT):
        print(f'Creating config folder {ENV_ROOT}')
        os.makedirs(ENV_ROOT)

    if not os.path.exists(DB_JSON_FOLDER):
        print(f'Creating folder {DB_JSON_FOLDER}')
        print('Use this folder to collect dashboards you wish to upload')
        os.makedirs(DB_JSON_FOLDER)

    # Check config folder for customers
    found_customers = {}
    for folder in os.listdir(ENV_ROOT):
        folder_path = os.path.join(ENV_ROOT, folder)
        if os.path.isdir(folder_path):
            if folder == 'template':
                continue
            config = load_config(folder_path)
            if config:
                found_customers[folder] = config
    
    if not found_customers:
        print('No environment folders found with functional config.json.')
        print('Please use the GUI version or create environment configurations manually.')
        sys.exit(1)
    
    print('Found the following environments:')
    for i, customer in enumerate(found_customers):
        print(f'{i+1}\t{customer}')
    
    customer_folder = input('Select the environment folder by entering its number: ')
    if not customer_folder.isdigit():
        print('Invalid selection')
        sys.exit(1)
    
    index = int(customer_folder)
    if index < 1 or index > len(found_customers):
        print('Invalid index')
        sys.exit(1)
    
    customer_folder_name = list(found_customers.keys())[index-1]
    config = found_customers[customer_folder_name]

    api_key = config.get('cldyKey', '')
    # Support both 'region' and 'frontdoor_region' field names
    region = config.get('region', config.get('frontdoor_region', ''))
    env_id = config.get('frontdoor_environment', '')
    public_key = config.get('public_key', '')
    private_key = config.get('private_key', '')

    headers = {}
    if not api_key and APPTIO_LIB_AVAILABLE:
        opentoken = fd.get_auth(region=region, public=public_key, private=private_key)
        headers = {
            'apptio-opentoken': opentoken,
            'apptio-current-environment': env_id,
            'app-type': 'Flagship',
        }

    print('Credentials loaded successfully.')

    while True:
        print('\nSelect mode:')
        print(f'1. Save Dashboards to /{ENV_ROOT}/{customer_folder_name}/Dashboards')
        print(f'2. Upload Dashboards from /{DB_JSON_FOLDER}')
        print('3. Exit')
        mode = input('Enter the number of the mode you want to use: ')
        
        if mode == '1':
            starred_only = input('Do you want to save only starred dashboards? (y/n): ').strip().lower() == 'y'
            save_dashboards(api_key, headers, region=region, customer_name=customer_folder_name, starred_only=starred_only)
        elif mode == '2':
            upload_dashboards(api_key=api_key, headers=headers, region=region)
        elif mode == '3':
            print('Exiting...')
            break
        else:
            print('Invalid mode selected. Try again.')


if __name__ == '__main__':
    main()

# Made with Bob
