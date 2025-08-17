import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# Configuration management
class Config:
    def __init__(self):
        self.project_root = project_root
        self.config_dir = project_root / "config"
        self.data_dir = project_root / "data"
        self.logs_dir = project_root / "logs"

        # Create directories if they don't exist
        self.logs_dir.mkdir(exist_ok=True)

        # Load configuration
        self.load_config()

    def load_config(self):
        """Load configuration from YAML files"""
        import yaml

        config_file = self.config_dir / "config.yaml"
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}

    def get(self, key, default=None):
        """Get configuration value using dot notation (e.g., 'mongodb.host')"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value


# Global configuration instance
config = Config()
