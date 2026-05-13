# Dashboard Dolly - End User Guide

A simple guide for users who want to run Dashboard Dolly without installing Python.

## What is Dashboard Dolly?

Dashboard Dolly is a tool that helps you transfer Cloudability dashboards between different environments. It has a graphical interface - no command line needed!

## Getting Started

### Download the Application

**For macOS Users:**
- Download `DashboardDolly.app` (or `DashboardDolly.zip`)
- If it's a zip file, double-click to extract it

**For Windows Users:**
- Download `DashboardDolly.exe`
- Save it to a location you'll remember (like Desktop or Documents)

### First Time Setup

#### macOS
1. Move `DashboardDolly.app` to your Applications folder (optional)
2. **First launch**: Right-click the app → Select "Open"
3. Click "Open" in the security dialog
4. Future launches: Just double-click normally

#### Windows
1. Double-click `DashboardDolly.exe`
2. If you see "Windows protected your PC":
   - Click "More info"
   - Click "Run anyway"
3. Future launches: Just double-click normally

## Using Dashboard Dolly

### Main Interface

The application has three tabs:
1. **🔌 Connections** - Connect to your Cloudability environments
2. **📊 Transfer Dashboards** - Select and transfer dashboards
3. **📝 Logs** - View activity and troubleshoot issues

### Step-by-Step: Transferring Dashboards

#### Step 1: Connect to Environments

1. Go to the **Connections** tab
2. Choose how to connect:

   **Option A: Using Saved Environments**
   - Select an environment from the dropdown
   - Click "Connect"
   
   **Option B: Using API Key Directly**
   - Paste your API key in the "OR API Key" field
   - Click "Connect with Key"

3. Repeat for both Source and Target environments
4. Look for green checkmarks (✓) showing successful connections

#### Step 2: Load Dashboards

1. Go to the **Transfer Dashboards** tab
2. Click "🔄 Load Source Dashboards"
3. Wait for dashboards to appear in the left list
4. (Optional) Click "🎯 Load Target Dashboards" to see what's already in target

#### Step 3: Select Dashboards

Choose dashboards to transfer:
- **Select specific dashboards**: Click on them in the left list
- **Add selected**: Click "➡️ Add" button
- **Add all**: Click "➡️➡️ Add All" button
- **Filter starred**: Click "⭐ Starred Only" to see only starred dashboards
- **Search**: Type in the search box to filter by name

Selected dashboards appear in the right list.

#### Step 4: Transfer

Choose your transfer method:

**Option A: Direct Upload**
1. Click "📤 Upload to Target"
2. Confirm the upload
3. Watch the progress bar
4. Check logs for success messages

**Option B: Save to Files (for later)**
1. Click "💾 Save to Files"
2. Choose a folder to save JSON files
3. Later: Click "📁 Load from Files" to load them back

### Tips & Tricks

**Starred Dashboards**
- Dashboards marked with ⭐ are starred in Cloudability
- Use "⭐ Starred Only" button to quickly filter to important dashboards

**Search Function**
- Search by dashboard name or ID
- Search is case-insensitive
- Clears when you delete the search text

**Removing Selections**
- Select dashboards in the right list
- Click "⬅️ Remove" to remove selected
- Click "⬅️⬅️ Clear" to remove all

**Progress Tracking**
- Progress bar shows transfer progress
- Status message shows current operation
- Logs tab shows detailed activity

## Setting Up Environment Configurations

If you want to save environment configurations for quick access:

1. Run Dashboard Dolly once
2. Click "Open Config Folder" in the Connections tab
3. Create a folder for your environment (e.g., "production")
4. Create a `config.json` file inside with this format:

```json
{
  "cldyKey": "your-api-key-here",
  "region": ""
}
```

5. Restart Dashboard Dolly
6. Your environment will appear in the dropdown

### Config File Examples

**US Region (default):**
```json
{
  "cldyKey": "your-api-key-here",
  "region": ""
}
```

**EU Region:**
```json
{
  "cldyKey": "your-api-key-here",
  "region": "eu"
}
```

**AU Region:**
```json
{
  "cldyKey": "your-api-key-here",
  "region": "au"
}
```

## Troubleshooting

### "Please connect to source environment first"
- Make sure you see a green checkmark (✓) in the Source section
- Try connecting again

### "Connection failed"
- Check your API key is correct
- Verify you have internet connection
- Check the Logs tab for detailed error messages

### "No dashboards selected"
- You need to add dashboards to the right list first
- Click "➡️ Add" or "➡️➡️ Add All"

### Dashboards not loading
- Check your connection status
- Try disconnecting and reconnecting
- Check the Logs tab for errors

### Application won't start (macOS)
- Right-click → Open (don't just double-click)
- Or run: `xattr -cr /path/to/DashboardDolly.app`

### Application won't start (Windows)
- Click "More info" → "Run anyway"
- Check Windows Defender isn't blocking it

## Security & Privacy

- Your API keys are never stored by the application
- Credentials are only used during your session
- Saved environment configs are stored locally on your computer
- No data is sent anywhere except to Cloudability APIs

## Getting Help

If you encounter issues:

1. Check the **Logs** tab for error messages
2. Try the troubleshooting steps above
3. Contact your system administrator
4. Provide log files when reporting issues (use "Save Logs" button)

## Keyboard Shortcuts

- **Cmd/Ctrl + Tab**: Switch between tabs
- **Cmd/Ctrl + W**: Close window
- **Cmd/Ctrl + Q**: Quit application

## Best Practices

1. **Test First**: Try transferring one dashboard before doing bulk transfers
2. **Check Target**: Use "Load Target Dashboards" to see what's already there
3. **Save Backups**: Use "Save to Files" to keep local copies
4. **Review Logs**: Check logs after transfers to confirm success
5. **Starred Dashboards**: Star important dashboards in Cloudability for easy filtering

## FAQ

**Q: Do I need Python installed?**
A: No! The executable includes everything needed.

**Q: Can I transfer between different regions?**
A: Yes, just connect to different regions as source and target.

**Q: Will this overwrite existing dashboards?**
A: No, it creates new dashboards. Existing ones are not modified.

**Q: Can I transfer widgets only?**
A: Currently, you transfer complete dashboards with all their widgets.

**Q: How do I update to a new version?**
A: Download the new executable and replace the old one.

**Q: Where are my environment configs stored?**
A: Click "Open Config Folder" to see the location.

## Support

For technical support or questions, contact your Cloudability administrator or the tool maintainer.

---

**Version**: 1.0  
**Last Updated**: 2026-05-13