#!/usr/bin/env python3
"""
Script to check MongoDB k_data collection structure
"""

import pymongo
from datetime import datetime
import yaml
import os

def check_k_data_structure():
    """Check the structure of k_data collection"""
    try:
        # Load database configuration
        config_path = os.path.join('config', 'database.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        host = config['mongodb']['host']
        port = config['mongodb']['port']
        database = config['mongodb']['database']
        k_data_collection_name = config['collections']['k_data']
        
        # Connect to MongoDB
        client = pymongo.MongoClient(f"mongodb://{host}:{port}/")
        db = client[database]
        k_data_collection = db[k_data_collection_name]
        
        print(f"Connected to MongoDB: {host}:{port}/{database}")
        print(f"Collection: {k_data_collection_name}")
        
        # Get the first record
        first_record = k_data_collection.find_one()
        
        if first_record:
            print("\nFirst record in k_data collection:")
            print("-" * 50)
            for key, value in first_record.items():
                print(f"{key}: {value} ({type(value).__name__})")
        else:
            print("No records found in k_data collection")
        
        # Get total count
        total_count = k_data_collection.count_documents({})
        print(f"\nTotal records: {total_count}")
        
        # Get sample records with different adjust types
        print("\nSample records by adjust type:")
        adjust_types = k_data_collection.distinct('adjust_type')
        print(f"Adjust types found: {adjust_types}")
        
        for adjust_type in adjust_types:
            sample = k_data_collection.find_one({'adjust_type': adjust_type})
            print(f"\nSample record for adjust_type='{adjust_type}':")
            if sample:
                for key, value in sample.items():
                    print(f"  {key}: {value}")
        
        client.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_k_data_structure()

