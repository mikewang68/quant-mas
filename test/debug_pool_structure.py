"""
Debug script to examine pool data structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.mongodb_config import MongoDBConfig
from pymongo import MongoClient

def debug_pool_structure():
    """Examine the structure of pool data"""

    # Load MongoDB configuration
    mongodb_config = MongoDBConfig()
    config = mongodb_config.get_mongodb_config()

    # Connect to MongoDB
    if config.get("username") and config.get("password"):
        uri = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?authSource={config.get('auth_database', 'admin')}"
    else:
        uri = f"mongodb://{config['host']}:{config['port']}/"

    client = MongoClient(uri)
    db = client[config["database"]]
    pool_collection = db['pool']

    # Get the latest pool record
    latest_pool_record = pool_collection.find_one(sort=[("_id", -1)])

    if not latest_pool_record:
        print("No records found in pool collection")
        return

    print("Latest pool record structure:")
    print(f"Record ID: {latest_pool_record.get('_id')}")
    print(f"Created at: {latest_pool_record.get('created_at')}")
    print(f"Number of stocks: {len(latest_pool_record.get('stocks', []))}")

    # Examine the first stock to see available fields
    stocks = latest_pool_record.get('stocks', [])
    if stocks:
        first_stock = stocks[0]
        print(f"\nFirst stock fields: {list(first_stock.keys())}")

        # Print all fields and their types
        for field_name, field_value in first_stock.items():
            print(f"  {field_name}: {type(field_value)} - {field_value}")

            # If it's a dict, show its keys
            if isinstance(field_value, dict):
                print(f"    Sub-fields: {list(field_value.keys())}")
                for sub_key, sub_value in field_value.items():
                    print(f"      {sub_key}: {type(sub_value)} - {sub_value}")

if __name__ == "__main__":
    debug_pool_structure()

