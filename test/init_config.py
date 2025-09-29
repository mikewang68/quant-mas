#!/usr/bin/env python3
"""
Initialize MongoDB config collection with default values
"""

import sys
import os
import yaml
from pymongo import MongoClient

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def init_config():
    """Initialize config collection with default values"""
    
    # Load database configuration
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'database.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        db_config = yaml.safe_load(f)

    # Initialize MongoDB connection
    mongo_config = db_config["mongodb"]
    auth_db = mongo_config.get("auth_database", "admin")
    mongo_uri = f"mongodb://{mongo_config['username']}:{mongo_config['password']}@{mongo_config['host']}:{mongo_config['port']}/{mongo_config['database']}?authSource={auth_db}"

    try:
        mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # Test the connection
        mongo_client.admin.command("ping")
        db = mongo_client[mongo_config["database"]]
        print("Successfully connected to MongoDB")
        
        # Check if config collection exists and has data
        config_collection = db['config']
        config_record = config_collection.find_one()
        
        if config_record is None:
            # Initialize with default configuration
            default_config = {
                "max_position": 0.1,
                "stop_loss": 0.05,
                "take_profit": 0.1,
                "commission": 0.001,
                "data_adjustment": "qfq"  # Default to pre-adjusted
            }
            
            # Insert default configuration
            result = config_collection.insert_one(default_config)
            print(f"Initialized config collection with default values. Inserted ID: {result.inserted_id}")
        else:
            print("Config collection already has data. No initialization needed.")
            
            # Ensure data_adjustment field exists
            if 'data_adjustment' not in config_record:
                config_collection.update_one({}, {"$set": {"data_adjustment": "qfq"}})
                print("Added data_adjustment field to existing config record")
            
        # Close connection
        mongo_client.close()
        
    except Exception as e:
        print(f"Error initializing config: {e}")

if __name__ == "__main__":
    init_config()

