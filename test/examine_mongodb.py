#!/usr/bin/env python3
"""
Script to examine the structure of k_data collection in MongoDB
"""

import pymongo
from datetime import datetime
import yaml
import os

def examine_k_data_structure():
    """Examine the structure of k_data collection"""
    try:
        # Load database configuration
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'database.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        host = config['mongodb']['host']
        port = config['mongodb']['port']
        database = config['mongodb']['database']
        
        # Collection names
        k_data_collection_name = config['collections']['k_data']
        
        # Connect to MongoDB
        client = pymongo.MongoClient(f"mongodb://{host}:{port}/")
        db = client[database]
        
        # Get k_data collection
        k_data_collection = db[k_data_collection_name]
        
        # Find the first record
        first_record = k_data_collection.find_one()
        
        if first_record:
            print("First record in k_data collection:")
            print("-" * 50)
            for key, value in first_record.items():
                print(f"{key}: {value} (type: {type(value).__name__})")
        else:
            print("No records found in k_data collection")
            
        # Get collection stats
        stats = db.command("collStats", k_data_collection_name)
        print("\nCollection statistics:")
        print("-" * 50)
        print(f"Total documents: {stats['count']}")
        print(f"Average object size: {stats['avgObjSize']} bytes")
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"Error examining k_data structure: {e}")

if __name__ == "__main__":
    examine_k_data_structure()

