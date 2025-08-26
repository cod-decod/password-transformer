import json
import os
from typing import Dict, Any
from datetime import datetime

class Config:
    """Configuration management for the application"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.default_config = {
            "appearance": {
                "theme": "dark",
                "color_theme": "blue",
                "font_size": 12
            },
            "transformation": {
                "default_intensity": "moderate",
                "character_substitution": True,
                "add_year": True,
                "intelligent_patterns": True,
                "preserve_strong": True,
                "increment_numbers": True
            },
            "file_handling": {
                "auto_backup": True,
                "default_output_format": "txt",
                "max_preview_items": 100,
                "supported_encodings": ["utf-8", "utf-16", "latin-1"]
            },
            "advanced": {
                "max_file_size_mb": 50,
                "processing_threads": 4,
                "enable_logging": True,
                "log_level": "INFO"
            },
            "ui": {
                "window_width": 1200,
                "window_height": 800,
                "remember_window_size": True,
                "show_tooltips": True
            }
        }
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._merge_configs(self.default_config, loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.default_config.copy()
        else:
            # Create default config file
            self.save_config_to_file(self.default_config)
            return self.default_config.copy()
            
    def save_config(self):
        """Save current configuration to file"""
        self.save_config_to_file(self.config)
        
    def save_config_to_file(self, config_data: Dict[str, Any]):
        """Save configuration data to file"""
        try:
            # Add metadata
            config_with_meta = {
                "_metadata": {
                    "version": "1.0",
                    "created": datetime.now().isoformat(),
                    "description": "Password Transformer Configuration"
                },
                **config_data
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_with_meta, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation (e.g., 'appearance.theme')"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value
        
    def set(self, key_path: str, value):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
            
        # Set the value
        config[keys[-1]] = value
        self.save_config()
        
    def reset_to_defaults(self):
        """Reset configuration to default values"""
        self.config = self.default_config.copy()
        self.save_config()
        
    def get_section(self, section_name: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self.config.get(section_name, {})
        
    def update_section(self, section_name: str, updates: Dict[str, Any]):
        """Update entire configuration section"""
        if section_name in self.config:
            self.config[section_name].update(updates)
        else:
            self.config[section_name] = updates
        self.save_config()
        
    def _merge_configs(self, default: dict, loaded: dict) -> dict:
        """Recursively merge loaded config with defaults"""
        result = default.copy()
        
        for key, value in loaded.items():
            if key.startswith('_'):  # Skip metadata
                continue
                
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
                
        return result
        
    def export_config(self, export_path: str):
        """Export current configuration to specified file"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting config: {e}")
            return False
            
    def import_config(self, import_path: str):
        """Import configuration from specified file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # Validate and merge
            self.config = self._merge_configs(self.default_config, imported_config)
            self.save_config()
            return True
        except Exception as e:
            print(f"Error importing config: {e}")
            return False
