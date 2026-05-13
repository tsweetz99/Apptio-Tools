#!/usr/bin/env python3
"""
Configuration Manager
Handles saving and loading environment configurations.
"""

import json
import os
from typing import Dict, List, Optional


class ConfigManager:
    """Manages environment configurations."""
    
    def __init__(self, config_dir: str = "Environments"):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory to store environment configurations
        """
        self.config_dir = os.path.join(os.path.dirname(__file__), config_dir)
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Ensure configuration directory exists."""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            self._create_template()
    
    def _create_template(self):
        """Create a template configuration."""
        template_dir = os.path.join(self.config_dir, 'template')
        if not os.path.exists(template_dir):
            os.makedirs(template_dir)
        
        template_config = {
            'auth_type': 'cloudability',
            'region': '',
            'region_instructions': 'Required field. The region is "" for US, "au" for Australia, "eu" for Europe, "usgov" for US Government',
            'api_key': '',
            'frontdoor_environment': '',
            'public_key': '',
            'private_key': '',
            'instructions': 'Fill in either api_key (for Cloudability auth) OR all of frontdoor_environment, public_key, and private_key (for Frontdoor auth)'
        }
        
        template_path = os.path.join(template_dir, 'config.json')
        with open(template_path, 'w') as f:
            json.dump(template_config, f, indent=2)
    
    def save_environment(self, name: str, config: Dict) -> bool:
        """
        Save an environment configuration.
        
        Args:
            name: Environment name
            config: Configuration dictionary
            
        Returns:
            True if successful
        """
        try:
            env_dir = os.path.join(self.config_dir, name)
            if not os.path.exists(env_dir):
                os.makedirs(env_dir)
            
            config_path = os.path.join(env_dir, 'config.json')
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving environment: {e}")
            return False
    
    def load_environment(self, name: str) -> Optional[Dict]:
        """
        Load an environment configuration.
        
        Args:
            name: Environment name
            
        Returns:
            Configuration dictionary or None if not found
        """
        try:
            config_path = os.path.join(self.config_dir, name, 'config.json')
            if not os.path.exists(config_path):
                return None
            
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading environment: {e}")
            return None
    
    def list_environments(self) -> List[str]:
        """
        List all saved environments.
        
        Returns:
            List of environment names
        """
        environments = []
        
        if not os.path.exists(self.config_dir):
            return environments
        
        for item in os.listdir(self.config_dir):
            item_path = os.path.join(self.config_dir, item)
            if os.path.isdir(item_path) and item != 'template':
                config_path = os.path.join(item_path, 'config.json')
                if os.path.exists(config_path):
                    environments.append(item)
        
        return sorted(environments)
    
    def delete_environment(self, name: str) -> bool:
        """
        Delete an environment configuration.
        
        Args:
            name: Environment name
            
        Returns:
            True if successful
        """
        try:
            import shutil
            env_dir = os.path.join(self.config_dir, name)
            if os.path.exists(env_dir):
                shutil.rmtree(env_dir)
                return True
            return False
        except Exception as e:
            print(f"Error deleting environment: {e}")
            return False

# Made with Bob
