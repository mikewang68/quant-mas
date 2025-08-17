"""
MongoDB Configuration Module
Handles loading and parsing of MongoDB database configuration
"""

import yaml
import os
from typing import Dict, Any


class MongoDBConfig:
    """MongoDB configuration loader and manager"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize MongoDB configuration
        
        Args:
            config_path: Path to the database configuration file
        """
        if config_path is None:
            # Default path relative to this file
            config_path = os.path.join(os.path.dirname(__file__), 'database.yaml')
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file
        
        Returns:
            Dictionary containing database configuration
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Database configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration file: {e}")
    
    def get_mongodb_config(self) -> Dict[str, Any]:
        """
        Get MongoDB connection configuration
        
        Returns:
            Dictionary containing MongoDB connection parameters
        """
        return self.config.get('mongodb', {})
    
    def get_collections_config(self) -> Dict[str, str]:
        """
        Get collections configuration
        
        Returns:
            Dictionary mapping collection names to their database names
        """
        return self.config.get('collections', {})
    
    def get_database_name(self) -> str:
        """
        Get the main database name
        
        Returns:
            Database name
        """
        return self.config.get('mongodb', {}).get('database', 'stock')
    
    def get_collection_name(self, collection_key: str) -> str:
        """
        Get the actual collection name for a given key
        
        Args:
            collection_key: Key for the collection in the config
            
        Returns:
            Actual collection name in database
        """
        collections = self.config.get('collections', {})
        return collections.get(collection_key, collection_key)


# Global instance for easy access
mongodb_config = MongoDBConfig()

if __name__ == "__main__":
    # Example usage
    config = MongoDBConfig()
    print("MongoDB Config:", config.get_mongodb_config())
    print("Collections Config:", config.get_collections_config())

