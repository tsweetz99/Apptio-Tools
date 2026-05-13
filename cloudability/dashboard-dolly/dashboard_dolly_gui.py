#!/usr/bin/env python3
"""
Dashboard Dolly GUI - Cloudability Dashboard Transfer Tool
Graphical interface for transferring dashboards between environments.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import os
import threading
from datetime import datetime
from typing import Dict, List, Optional

# Import our modules
from dashboard_api_client import DashboardAPIClient
from config_manager import ConfigManager
import dashboard_dolly as dd


class DashboardDollyGUI:
    """Main GUI application for Dashboard Dolly."""
    
    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Dashboard Dolly - Dashboard Transfer Tool")
        self.root.geometry("1200x800")
        
        # State
        self.config_manager = ConfigManager()
        self.source_client: Optional[DashboardAPIClient] = None
        self.target_client: Optional[DashboardAPIClient] = None
        self.source_dashboards: List[Dict] = []
        self.selected_dashboards: List[Dict] = []
        
        self.setup_ui()
        self.load_environments()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_connection_tab()
        self.create_transfer_tab()
        self.create_log_tab()
    
    def create_connection_tab(self):
        """Create the connection configuration tab."""
        conn_frame = ttk.Frame(self.notebook)
        self.notebook.add(conn_frame, text="🔌 Connections")
        
        # Source section
        source_frame = ttk.LabelFrame(conn_frame, text="Source Environment", padding="10")
        source_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(source_frame, text="Environment:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.source_env_combo = ttk.Combobox(source_frame, state="readonly", width=40)
        self.source_env_combo.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=2)
        
        ttk.Button(source_frame, text="Connect",
                  command=lambda: self.connect_environment("source")).grid(row=0, column=2, padx=5)
        
        # Direct API key option
        ttk.Label(source_frame, text="OR API Key:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.source_api_key_var = tk.StringVar()
        ttk.Entry(source_frame, textvariable=self.source_api_key_var, width=40, show="*").grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=2)
        ttk.Button(source_frame, text="Connect with Key",
                  command=lambda: self.connect_with_api_key("source")).grid(row=1, column=2, padx=5)
        
        self.source_status_var = tk.StringVar(value="Not connected")
        ttk.Label(source_frame, textvariable=self.source_status_var,
                 foreground="gray").grid(row=2, column=0, columnspan=3, pady=5)
        
        source_frame.columnconfigure(1, weight=1)
        
        # Target section
        target_frame = ttk.LabelFrame(conn_frame, text="Target Environment", padding="10")
        target_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(target_frame, text="Environment:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.target_env_combo = ttk.Combobox(target_frame, state="readonly", width=40)
        self.target_env_combo.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=2)
        
        ttk.Button(target_frame, text="Connect",
                  command=lambda: self.connect_environment("target")).grid(row=0, column=2, padx=5)
        
        # Direct API key option
        ttk.Label(target_frame, text="OR API Key:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.target_api_key_var = tk.StringVar()
        ttk.Entry(target_frame, textvariable=self.target_api_key_var, width=40, show="*").grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=2)
        ttk.Button(target_frame, text="Connect with Key",
                  command=lambda: self.connect_with_api_key("target")).grid(row=1, column=2, padx=5)
        
        self.target_status_var = tk.StringVar(value="Not connected")
        ttk.Label(target_frame, textvariable=self.target_status_var,
                 foreground="gray").grid(row=2, column=0, columnspan=3, pady=5)
        
        target_frame.columnconfigure(1, weight=1)
        
        # Environment management
        mgmt_frame = ttk.LabelFrame(conn_frame, text="Environment Management", padding="10")
        mgmt_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(mgmt_frame, text="Refresh List",
                  command=self.load_environments).pack(side=tk.LEFT, padx=5)
        ttk.Button(mgmt_frame, text="Open Config Folder",
                  command=self.open_config_folder).pack(side=tk.LEFT, padx=5)
    
    def create_transfer_tab(self):
        """Create the dashboard transfer tab."""
        transfer_frame = ttk.Frame(self.notebook)
        self.notebook.add(transfer_frame, text="📊 Transfer Dashboards")
        
        # Top controls
        controls_frame = ttk.Frame(transfer_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(controls_frame, text="🔄 Load Source Dashboards",
                  command=self.load_source_dashboards).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="🎯 Load Target Dashboards",
                  command=self.load_target_dashboards).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="⭐ Starred Only",
                  command=self.filter_starred).pack(side=tk.LEFT, padx=5)
        
        # Search
        ttk.Label(controls_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_dashboards())
        ttk.Entry(controls_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=5)
        
        # Main content area
        content_frame = ttk.Frame(transfer_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Source list
        source_frame = ttk.LabelFrame(content_frame, text="Source Dashboards", padding="5")
        source_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        source_scroll = ttk.Scrollbar(source_frame)
        source_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.source_listbox = tk.Listbox(source_frame, selectmode=tk.EXTENDED,
                                         yscrollcommand=source_scroll.set)
        self.source_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        source_scroll.config(command=self.source_listbox.yview)
        
        # Transfer buttons - larger with better sizing
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="    ➡️    \n   Add   ",
                  command=self.add_selected, width=12).pack(pady=5)
        ttk.Button(button_frame, text="  ➡️➡️  \n Add All ",
                  command=self.add_all, width=12).pack(pady=5)
        ttk.Button(button_frame, text="    ⬅️    \n Remove ",
                  command=self.remove_selected, width=12).pack(pady=5)
        ttk.Button(button_frame, text="  ⬅️⬅️  \n  Clear  ",
                  command=self.remove_all, width=12).pack(pady=5)
        
        # Selected list
        selected_frame = ttk.LabelFrame(content_frame, text="Selected for Transfer", padding="5")
        selected_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        selected_scroll = ttk.Scrollbar(selected_frame)
        selected_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.selected_listbox = tk.Listbox(selected_frame, selectmode=tk.EXTENDED,
                                           yscrollcommand=selected_scroll.set)
        self.selected_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        selected_scroll.config(command=self.selected_listbox.yview)
        
        # Bottom action buttons
        action_frame = ttk.Frame(transfer_frame)
        action_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(action_frame, text="💾 Save to Files", 
                  command=self.save_to_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="📤 Upload to Target", 
                  command=self.upload_to_target).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="📁 Load from Files", 
                  command=self.load_from_files).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(transfer_frame, variable=self.progress_var,
                                           maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(transfer_frame, textvariable=self.status_var).pack(pady=5)
    
    def create_log_tab(self):
        """Create the log tab."""
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="📝 Logs")
        
        # Controls
        controls = ttk.Frame(log_frame)
        controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls, text="Clear Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls, text="Save Logs", command=self.save_logs).pack(side=tk.LEFT, padx=2)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=30)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure tags
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("warning", foreground="orange")
        self.log_text.tag_config("info", foreground="blue")
    
    # Connection methods
    def load_environments(self):
        """Load available environments."""
        environments = self.config_manager.list_environments()
        self.source_env_combo['values'] = environments
        self.target_env_combo['values'] = environments
        
        if environments:
            self.source_env_combo.current(0)
            if len(environments) > 1:
                self.target_env_combo.current(1)
            else:
                self.target_env_combo.current(0)
        
        self.log(f"Loaded {len(environments)} environment(s)", "info")
    
    def connect_environment(self, env_type: str):
        """Connect to an environment."""
        combo = self.source_env_combo if env_type == "source" else self.target_env_combo
        env_name = combo.get()
        
        if not env_name:
            messagebox.showwarning("Warning", "Please select an environment")
            return
        
        self.log(f"Connecting to {env_type} environment: {env_name}", "info")
        
        try:
            config = self.config_manager.load_environment(env_name)
            if not config:
                raise ValueError(f"Failed to load config for {env_name}")
            
            # Create client
            api_key = config.get('cldyKey', '')
            region = config.get('region', config.get('frontdoor_region', ''))
            
            if api_key:
                client = DashboardAPIClient(api_key=api_key, region=region)
            else:
                # Frontdoor auth
                client = DashboardAPIClient(
                    auth_type="frontdoor",
                    region=region,
                    frontdoor_env=config.get('frontdoor_environment', ''),
                    public_key=config.get('public_key', ''),
                    private_key=config.get('private_key', '')
                )
            
            # Test connection
            success, message = client.test_connection()
            
            if success:
                if env_type == "source":
                    self.source_client = client
                    self.source_status_var.set(f"✓ Connected to {env_name}")
                else:
                    self.target_client = client
                    self.target_status_var.set(f"✓ Connected to {env_name}")
                
                self.log(f"Successfully connected to {env_name}", "success")
                
                # Get org info
                org_info = client.get_organization_info()
                if org_info:
                    self.log(f"Organization: {org_info.get('name', 'Unknown')}", "info")
            else:
                raise ValueError(message)
                
        except Exception as e:
            self.log(f"Connection failed: {e}", "error")
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
            
            if env_type == "source":
                self.source_status_var.set("✗ Connection failed")
            else:
                self.target_status_var.set("✗ Connection failed")
    
    def connect_with_api_key(self, env_type: str):
        """Connect using direct API key input."""
        api_key_var = self.source_api_key_var if env_type == "source" else self.target_api_key_var
        api_key = api_key_var.get().strip()
        
        if not api_key:
            messagebox.showwarning("Warning", "Please enter an API key")
            return
        
        self.log(f"Connecting to {env_type} with direct API key...", "info")
        
        try:
            # Create client with API key (default US region)
            client = DashboardAPIClient(api_key=api_key, region="")
            
            # Test connection
            success, message = client.test_connection()
            
            if success:
                if env_type == "source":
                    self.source_client = client
                    self.source_status_var.set(f"✓ Connected with API key")
                else:
                    self.target_client = client
                    self.target_status_var.set(f"✓ Connected with API key")
                
                self.log(f"Successfully connected with API key", "success")
                
                # Get org info
                org_info = client.get_organization_info()
                if org_info:
                    self.log(f"Organization: {org_info.get('name', 'Unknown')}", "info")
            else:
                raise ValueError(message)
                
        except Exception as e:
            self.log(f"Connection failed: {e}", "error")
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
            
            if env_type == "source":
                self.source_status_var.set("✗ Connection failed")
            else:
                self.target_status_var.set("✗ Connection failed")
    
    def open_config_folder(self):
        """Open the configuration folder."""
        import subprocess
        import platform
        
        config_dir = self.config_manager.config_dir
        
        if platform.system() == "Darwin":  # macOS
            subprocess.run(["open", config_dir])
        elif platform.system() == "Windows":
            subprocess.run(["explorer", config_dir])
        else:  # Linux
            subprocess.run(["xdg-open", config_dir])
    
    # Dashboard transfer methods
    def load_source_dashboards(self):
        """Load dashboards from source."""
        if not self.source_client:
            messagebox.showerror("Error", "Please connect to source environment first")
            return
        
        self.log("Loading dashboards from source...", "info")
        self.status_var.set("Loading dashboards...")
        
        def load_thread():
            try:
                dashboards = self.source_client.get_dashboard_list()
                self.source_dashboards = dashboards
                
                self.root.after(0, lambda: self.populate_source_list(dashboards))
                self.root.after(0, lambda: self.log(f"Loaded {len(dashboards)} dashboards", "success"))
                self.root.after(0, lambda: self.status_var.set(f"Loaded {len(dashboards)} dashboards"))
            except Exception as e:
                self.root.after(0, lambda: self.log(f"Error loading dashboards: {e}", "error"))
                self.root.after(0, lambda: self.status_var.set("Error loading dashboards"))
        
        threading.Thread(target=load_thread, daemon=True).start()
    def load_target_dashboards(self):
        """Load dashboards from target for reference."""
        if not self.target_client:
            messagebox.showerror("Error", "Please connect to target environment first")
            return
        
        self.log("Loading dashboards from target...", "info")
        self.status_var.set("Loading target dashboards...")
        
        def load_thread():
            try:
                dashboards = self.target_client.get_dashboard_list()
                
                self.root.after(0, lambda: self.log(f"Target has {len(dashboards)} existing dashboards", "info"))
                self.root.after(0, lambda: self.status_var.set(f"Target has {len(dashboards)} dashboards"))
                
                # Show dashboard names in log
                for db in dashboards[:10]:  # Show first 10
                    self.root.after(0, lambda name=db['name']: self.log(f"  - {name}", "info"))
                if len(dashboards) > 10:
                    self.root.after(0, lambda: self.log(f"  ... and {len(dashboards) - 10} more", "info"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.log(f"Error loading target dashboards: {e}", "error"))
                self.root.after(0, lambda: self.status_var.set("Error loading target dashboards"))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    
    def populate_source_list(self, dashboards: List[Dict]):
        """Populate source listbox."""
        self.source_listbox.delete(0, tk.END)
        for db in dashboards:
            star = "⭐ " if db.get('star', False) else ""
            self.source_listbox.insert(tk.END, f"{star}{db['name']} (ID: {db['id']})")
    
    def filter_starred(self):
        """Filter to starred dashboards only."""
        starred = [db for db in self.source_dashboards if db.get('star', False)]
        self.populate_source_list(starred)
        self.log(f"Filtered to {len(starred)} starred dashboards", "info")
    
    def filter_dashboards(self):
        """Filter dashboards by search text."""
        search_text = self.search_var.get().lower()
        if not search_text:
            self.populate_source_list(self.source_dashboards)
            return
        
        filtered = [db for db in self.source_dashboards 
                   if search_text in db['name'].lower() or search_text in str(db['id'])]
        self.populate_source_list(filtered)
    
    def add_selected(self):
        """Add selected dashboards to transfer list."""
        selection = self.source_listbox.curselection()
        if not selection:
            return
        
        for idx in selection:
            dashboard = self.source_dashboards[idx]
            if dashboard not in self.selected_dashboards:
                self.selected_dashboards.append(dashboard)
        
        self.populate_selected_list()
        self.log(f"Added {len(selection)} dashboard(s)", "info")
    
    def add_all(self):
        """Add all dashboards."""
        self.selected_dashboards = self.source_dashboards.copy()
        self.populate_selected_list()
        self.log(f"Added all {len(self.selected_dashboards)} dashboards", "info")
    
    def remove_selected(self):
        """Remove selected dashboards."""
        selection = self.selected_listbox.curselection()
        if not selection:
            return
        
        for idx in reversed(selection):
            del self.selected_dashboards[idx]
        
        self.populate_selected_list()
        self.log(f"Removed {len(selection)} dashboard(s)", "info")
    
    def remove_all(self):
        """Remove all dashboards."""
        count = len(self.selected_dashboards)
        self.selected_dashboards.clear()
        self.populate_selected_list()
        self.log(f"Removed all {count} dashboards", "info")
    
    def populate_selected_list(self):
        """Populate selected listbox."""
        self.selected_listbox.delete(0, tk.END)
        for db in self.selected_dashboards:
            self.selected_listbox.insert(tk.END, f"{db['name']} (ID: {db['id']})")
    
    def save_to_files(self):
        """Save dashboards to files."""
        if not self.selected_dashboards:
            messagebox.showwarning("Warning", "No dashboards selected")
            return
        
        if not self.source_client:
            messagebox.showerror("Error", "Source client not connected")
            return
        
        directory = filedialog.askdirectory(title="Select directory to save dashboards")
        if not directory:
            return
        
        self.log(f"Saving {len(self.selected_dashboards)} dashboards...", "info")
        self.status_var.set("Saving dashboards...")
        
        def save_thread():
            saved_count = 0
            total = len(self.selected_dashboards)
            
            for i, db_info in enumerate(self.selected_dashboards):
                try:
                    dashboard = self.source_client.get_dashboard(db_info['id'])
                    
                    import re
                    filename = f"{db_info['id']}-{db_info['name']}.json"
                    filename = re.sub(r'[\\/*?:"<>|]', '', filename)
                    filename = re.sub(r'\s+', '_', filename)
                    
                    filepath = os.path.join(directory, filename)
                    with open(filepath, 'w') as f:
                        json.dump(dashboard, f, indent=2)
                    
                    saved_count += 1
                    progress = (i + 1) / total * 100
                    self.root.after(0, lambda p=progress: self.progress_var.set(p))
                    
                except Exception as e:
                    self.root.after(0, lambda e=e, name=db_info['name']: 
                                  self.log(f"Error saving {name}: {e}", "error"))
            
            self.root.after(0, lambda: self.log(f"Saved {saved_count}/{total} dashboards", "success"))
            self.root.after(0, lambda: self.status_var.set(f"Saved {saved_count}/{total} dashboards"))
            self.root.after(0, lambda: self.progress_var.set(0))
        
        threading.Thread(target=save_thread, daemon=True).start()
    
    def upload_to_target(self):
        """Upload dashboards to target."""
        if not self.selected_dashboards:
            messagebox.showwarning("Warning", "No dashboards selected")
            return
        
        if not self.target_client:
            messagebox.showerror("Error", "Please connect to target environment first")
            return
        
        if not messagebox.askyesno("Confirm", 
                                   f"Upload {len(self.selected_dashboards)} dashboards to target?"):
            return
        
        self.log(f"Uploading {len(self.selected_dashboards)} dashboards...", "info")
        self.status_var.set("Uploading dashboards...")
        
        def upload_thread():
            created_count = 0
            total = len(self.selected_dashboards)
            
            for i, db_info in enumerate(self.selected_dashboards):
                try:
                    dashboard = self.source_client.get_dashboard(db_info['id'])
                    
                    new_dashboard = self.target_client.create_dashboard(dashboard['name'])
                    new_dashboard_id = new_dashboard['id']
                    
                    self.root.after(0, lambda name=dashboard['name'], id=new_dashboard_id:
                                  self.log(f"Created: {name} (ID: {id})", "success"))
                    
                    # Get the full dashboard to find the default tab_id
                    new_dashboard_full = self.target_client.get_dashboard(new_dashboard_id)
                    
                    # Find the default tab ID (dashboards should have at least one tab)
                    default_tab_id = None
                    if 'tabs' in new_dashboard_full and new_dashboard_full['tabs']:
                        default_tab_id = str(new_dashboard_full['tabs'][0]['id'])
                    elif 'widgets' in new_dashboard_full and new_dashboard_full['widgets']:
                        # If there are already widgets, get tab_id from first one
                        default_tab_id = new_dashboard_full['widgets'][0].get('tab_id')
                    
                    if not default_tab_id:
                        # Fallback: try to get from dashboard itself
                        default_tab_id = str(new_dashboard_full.get('tab_id', '1'))
                    
                    self.root.after(0, lambda tid=default_tab_id:
                                  self.log(f"  Using tab_id: {tid}", "info"))
                    
                    # Upload widgets
                    widgets = dashboard.get('widgets', [])
                    widget_count = 0
                    widget_errors = 0
                    
                    for widget in widgets:
                        try:
                            # Update dashboard_id and tab_id to point to new dashboard
                            widget['dashboard_id'] = new_dashboard_id
                            widget['tab_id'] = default_tab_id
                            
                            # Remove fields that shouldn't be copied
                            widget.pop('id', None)
                            widget.pop('created_at', None)
                            widget.pop('updated_at', None)
                            
                            # Create widget
                            result = self.target_client.create_widget(widget)
                            
                            # Check if widget creation failed
                            if isinstance(result, dict) and 'error' in result:
                                widget_errors += 1
                                self.root.after(0, lambda err=result.get('error'):
                                              self.log(f"  Widget error: {err}", "warning"))
                            else:
                                widget_count += 1
                                
                        except Exception as widget_error:
                            widget_errors += 1
                            self.root.after(0, lambda e=str(widget_error):
                                          self.log(f"  Widget creation failed: {e}", "warning"))
                    
                    # Log widget results
                    if widget_count > 0:
                        self.root.after(0, lambda count=widget_count:
                                      self.log(f"  Added {count} widget(s)", "info"))
                    if widget_errors > 0:
                        self.root.after(0, lambda count=widget_errors:
                                      self.log(f"  {count} widget(s) failed", "warning"))
                    
                    created_count += 1
                    progress = (i + 1) / total * 100
                    self.root.after(0, lambda p=progress: self.progress_var.set(p))
                    
                except Exception as e:
                    self.root.after(0, lambda e=e, name=db_info['name']:
                                  self.log(f"Error uploading {name}: {e}", "error"))
            
            self.root.after(0, lambda: self.log(f"Uploaded {created_count}/{total} dashboards", "success"))
            self.root.after(0, lambda: self.status_var.set(f"Uploaded {created_count}/{total} dashboards"))
            self.root.after(0, lambda: self.progress_var.set(0))
        
        threading.Thread(target=upload_thread, daemon=True).start()
    
    def load_from_files(self):
        """Load dashboards from files."""
        directory = filedialog.askdirectory(title="Select directory with dashboard JSON files")
        if not directory:
            return
        
        dashboards = []
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                filepath = os.path.join(directory, filename)
                try:
                    with open(filepath, 'r') as f:
                        dashboard = json.load(f)
                        dashboards.append(dashboard)
                except Exception as e:
                    self.log(f"Error loading {filename}: {e}", "error")
        
        if dashboards:
            self.selected_dashboards = dashboards
            self.populate_selected_list()
            self.log(f"Loaded {len(dashboards)} dashboards from files", "success")
        else:
            messagebox.showwarning("Warning", "No valid dashboard JSON files found")
    
    # Logging methods
    def log(self, message: str, level: str = "info"):
        """Add message to log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_message, level)
        self.log_text.see(tk.END)
    
    def clear_logs(self):
        """Clear logs."""
        self.log_text.delete(1.0, tk.END)
    
    def save_logs(self):
        """Save logs to file."""
        filepath = filedialog.asksaveasfilename(
            title="Save logs",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filepath:
            return
        
        try:
            with open(filepath, 'w') as f:
                f.write(self.log_text.get(1.0, tk.END))
            self.log("Logs saved successfully", "success")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save logs: {e}")


def main():
    """Main entry point."""
    root = tk.Tk()
    app = DashboardDollyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

# Made with Bob
