# Dashboard Dolly - Cloudability Dashboard Transfer Tool

Dashboard Dolly is a tool for transferring Cloudability dashboards between environments. It supports both command-line and GUI interfaces, with features for measure mapping, batch operations, and environment management.

## Features

- **Transfer dashboards** between Cloudability environments
- **Save dashboards** to JSON files for backup or migration
- **Upload dashboards** from JSON files to target environments
- **Measure mapping** - Replace dimensions and metrics during transfer
- **Starred dashboard filtering** - Save only starred dashboards
- **Multiple authentication methods** - Cloudability API key or Frontdoor authentication
- **Environment management** - Save and reuse environment configurations
- **Batch operations** - Transfer multiple dashboards at once

## Installation Options

### Option 1: Standalone Executable (No Python Required) ⭐ Recommended for End Users

**For End Users who don't have Python:**
1. Download the pre-built executable for your platform:
   - **macOS**: `DashboardDolly.app`
   - **Windows**: `DashboardDolly.exe`
2. See [`END_USER_GUIDE.md`](END_USER_GUIDE.md) for usage instructions

**To Build Your Own Executable:**
```bash
python3 build_executable.py
```
See [`BUILD_EXECUTABLE_GUIDE.md`](BUILD_EXECUTABLE_GUIDE.md) for detailed build instructions.

### Option 2: Python Installation (For Developers)

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) For Frontdoor authentication, ensure `apptio_lib` is available in your Python environment.

## Quick Start

### GUI Interface (Recommended)

The GUI version provides a visual interface for all operations:
```bash
python dashboard_dolly_gui.py
```

**Features:**
- Visual dashboard selection
- Drag-and-drop style transfers
- Real-time progress tracking
- Connection management
- Search and filter capabilities

See [`GUI_QUICKSTART.md`](GUI_QUICKSTART.md) for detailed GUI usage.

### Command-Line Interface

Run the CLI version:
```bash
python dashboard_dolly.py
```

The CLI will guide you through:
1. Selecting an environment configuration
2. Choosing to save or upload dashboards
3. Filtering options (e.g., starred only)

## Configuration

### Environment Setup

Dashboard Dolly uses environment folders to store configurations. Each environment has its own folder under `Environments/`:

```
Environments/
├── template/
│   └── config.json (template configuration)
├── production/
│   ├── config.json
│   └── Dashboards/ (saved dashboards)
└── staging/
    ├── config.json
    └── Dashboards/
```

### Configuration File Format

Create a `config.json` file in each environment folder:

**Using Cloudability API Key:**
```json
{
  "auth_type": "cloudability",
  "frontdoor_region": "",
  "cldyKey": "your-api-key-here"
}
```

**Using Frontdoor Authentication:**
```json
{
  "auth_type": "frontdoor",
  "frontdoor_region": "",
  "frontdoor_environment": "environment-id",
  "public_key": "your-public-key",
  "private_key": "your-private-key"
}
```

**Region Values:**
- `""` - US region (default)
- `"au"` - Australia
- `"eu"` - Europe
- `"usgov"` - US Government

## Usage

### Saving Dashboards

1. Configure your source environment in `Environments/[env-name]/config.json`
2. Run the tool and select "Save Dashboards"
3. Choose whether to save all dashboards or only starred ones
4. Dashboards will be saved to `Environments/[env-name]/Dashboards/`

### Uploading Dashboards

1. Place dashboard JSON files in the `Dashboards_to_Upload/` folder
2. Configure your target environment
3. Run the tool and select "Upload Dashboards"
4. Dashboards will be created in the target environment

### Measure Mapping

To replace dimensions or metrics during transfer, edit the `measure_mapping` dictionary in `dashboard_dolly.py`:

```python
measure_mapping = {
    'tag3': 'tag1',           # Replace tag3 with tag1
    'category6': 'group7',    # Replace category6 with group7
}
```

This is useful when:
- Dimension names differ between environments
- Metric names have changed
- Custom tags need to be remapped

## File Structure

```
dashboard-dolly/
├── dashboard_dolly.py          # CLI version
├── dashboard_dolly_gui.py      # GUI version (in development)
├── dashboard_api_client.py     # API client module
├── config_manager.py           # Configuration management
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── QUICKSTART.md              # Quick start guide
├── Environments/              # Environment configurations
│   └── template/
│       └── config.json
└── Dashboards_to_Upload/      # Staging area for uploads
```

## API Client Module

The `dashboard_api_client.py` module provides a clean interface for Cloudability API operations:

```python
from dashboard_api_client import DashboardAPIClient

# Create client
client = DashboardAPIClient(api_key="your-key", region="")

# Test connection
success, message = client.test_connection()

# Get dashboards
dashboards = client.get_dashboard_list()

# Get specific dashboard
dashboard = client.get_dashboard(dashboard_id)

# Create dashboard
new_dashboard = client.create_dashboard("Dashboard Name")

# Create widget
client.create_widget(widget_data)
```

## Configuration Manager

The `config_manager.py` module handles environment configurations:

```python
from config_manager import ConfigManager

manager = ConfigManager()

# Save environment
manager.save_environment("production", config_dict)

# Load environment
config = manager.load_environment("production")

# List environments
environments = manager.list_environments()

# Delete environment
manager.delete_environment("old-env")
```

## Troubleshooting

### Connection Issues

**Problem:** "Connection failed" error

**Solutions:**
- Verify your API key or Frontdoor credentials
- Check the region setting matches your environment
- Ensure network connectivity to Cloudability API
- For Frontdoor auth, verify `apptio_lib` is installed

### Dashboard Upload Failures

**Problem:** Dashboards fail to upload

**Solutions:**
- Check dashboard JSON files are valid
- Verify target environment has necessary permissions
- Review measure mappings for invalid references
- Check widget configurations are compatible with target environment

### Missing Dashboards

**Problem:** Not all dashboards are saved

**Solutions:**
- Increase the limit in `get_dashboard_list()` (default: 500)
- Check if dashboards are shared vs. personal
- Verify user permissions in source environment

## Best Practices

1. **Always test with a single dashboard first** before batch operations
2. **Back up dashboards** before making changes
3. **Use measure mapping** when transferring between different environments
4. **Save environment configurations** for reuse
5. **Review dashboard JSON** before uploading to ensure compatibility
6. **Use starred filtering** to transfer only important dashboards

## Security Notes

- API keys and credentials are stored in local `config.json` files
- Never commit `config.json` files with real credentials to version control
- Use environment variables or secure vaults for production deployments
- The tool disables SSL verification - use with caution in production

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the QUICKSTART.md guide
3. Examine the sample code provided by your co-worker
4. Contact your team's Cloudability administrator

## License

Internal IBM tool - see LICENSE file for details.

## Version History

- **v1.0** - Initial release with CLI interface
- **v1.1** - Added API client and configuration manager modules
- **v2.0** - GUI interface (in development)