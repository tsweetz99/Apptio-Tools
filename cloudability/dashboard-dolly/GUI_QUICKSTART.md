# Dashboard Dolly GUI - Quick Start Guide

## Launch the GUI

```bash
cd cloudability/dashboard-dolly
python3 dashboard_dolly_gui.py
```

## Quick Workflow

### 1. Connect to Environments

**Connections Tab:**
1. Select **Source Environment** from dropdown (e.g., "my-production")
2. Click **Connect** button
3. Wait for "✓ Connected" status
4. Select **Target Environment** from dropdown
5. Click **Connect** button
6. Wait for "✓ Connected" status

### 2. Load and Select Dashboards

**Transfer Dashboards Tab:**
1. Click **🔄 Load Source Dashboards** button
2. Wait for dashboards to load (shows count in status)
3. **Optional:** Click **⭐ Starred Only** to filter
4. **Optional:** Use **Search** box to find specific dashboards
5. Select dashboards in left list (use Ctrl/Cmd+Click for multiple)
6. Click **➡️ Add** to move to transfer list
   - Or click **➡️➡️ Add All** to select everything

### 3. Transfer Dashboards

**Choose one option:**

**Option A: Save to Files (Backup)**
1. Click **💾 Save to Files**
2. Select destination folder
3. Wait for progress bar to complete
4. Dashboards saved as JSON files

**Option B: Upload to Target (Direct Transfer)**
1. Click **📤 Upload to Target**
2. Confirm the upload
3. Wait for progress bar to complete
4. Dashboards created in target environment

**Option C: Load from Files (Restore)**
1. Click **📁 Load from Files**
2. Select folder with dashboard JSON files
3. Dashboards loaded into transfer list
4. Then use **📤 Upload to Target**

### 4. Monitor Progress

**Logs Tab:**
- View detailed operation logs
- Color-coded messages:
  - 🔵 Blue = Info
  - 🟢 Green = Success
  - 🟠 Orange = Warning
  - 🔴 Red = Error
- Click **Save Logs** to export log file

## Features

### Connection Management
- ✅ Load saved environment configurations
- ✅ Test connections before operations
- ✅ Support for multiple authentication methods
- ✅ Quick access to config folder

### Dashboard Operations
- ✅ Load all dashboards from source
- ✅ Filter by starred status
- ✅ Search by name or ID
- ✅ Multi-select with Ctrl/Cmd+Click
- ✅ Drag-style add/remove interface
- ✅ Progress tracking with progress bar
- ✅ Real-time status updates

### File Operations
- ✅ Save dashboards to JSON files
- ✅ Load dashboards from JSON files
- ✅ Automatic filename sanitization
- ✅ Folder selection dialogs

## Tips

1. **Always connect both environments first** before loading dashboards
2. **Test with one dashboard** before bulk transfers
3. **Use starred filtering** to transfer only important dashboards
4. **Save to files first** as a backup before uploading
5. **Check logs tab** for detailed operation information
6. **Use search** to quickly find specific dashboards

## Keyboard Shortcuts

- **Ctrl/Cmd+Click**: Select multiple dashboards
- **Shift+Click**: Select range of dashboards
- **Ctrl/Cmd+A**: Select all (when list is focused)

## Troubleshooting

### "Please connect to source environment first"
**Solution:** Go to Connections tab and connect to source

### "Please connect to target environment first"
**Solution:** Go to Connections tab and connect to target

### "No dashboards selected"
**Solution:** Add dashboards to the transfer list first

### Connection fails
**Solution:** 
1. Check API key is valid
2. Verify region setting
3. Check network connectivity
4. Review logs tab for details

### Dashboards don't load
**Solution:**
1. Verify source connection is successful
2. Check API key permissions
3. Review logs tab for error details

## Environment Setup

If you don't see any environments in the dropdown:

1. Click **Open Config Folder** button
2. Copy the `template` folder
3. Rename to your environment name (e.g., "production")
4. Edit `config.json` with your credentials
5. Click **Refresh List** in GUI

Or use the CLI to create environments:
```bash
cp -r Environments/template Environments/my-env
vi Environments/my-env/config.json
```

## Comparison: GUI vs CLI

| Feature | GUI | CLI |
|---------|-----|-----|
| Visual interface | ✅ | ❌ |
| Progress tracking | ✅ Visual bar | ✅ Text |
| Multi-select | ✅ Easy | ❌ Manual |
| Search/Filter | ✅ Built-in | ❌ Manual |
| Logs | ✅ Color-coded | ✅ Text |
| Measure mapping | ❌ Use CLI | ✅ |
| Automation | ❌ | ✅ |

**Use GUI for:** Interactive transfers, exploring dashboards, visual feedback

**Use CLI for:** Automation, scripting, measure mapping, batch operations

## Example Workflow

**Scenario: Migrate starred dashboards from Production to Staging**

1. Launch GUI: `python3 dashboard_dolly_gui.py`
2. **Connections Tab:**
   - Source: Select "production", click Connect
   - Target: Select "staging", click Connect
3. **Transfer Tab:**
   - Click "Load Source Dashboards"
   - Click "⭐ Starred Only"
   - Click "➡️➡️ Add All"
   - Click "💾 Save to Files" (backup)
   - Click "📤 Upload to Target"
4. **Logs Tab:**
   - Review success messages
   - Save logs if needed

Done! Your starred dashboards are now in staging.

## Getting Help

- Check the **Logs tab** for detailed error messages
- Review the main [README.md](README.md) for detailed documentation
- Use the CLI [QUICKSTART.md](QUICKSTART.md) for command-line operations
- Check [test_connection.py](test_connection.py) to diagnose connection issues