#!/usr/bin/env python3
"""
Query all records from the strategies collection in MongoDB
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pymongo import MongoClient
from config.mongodb_config import MongoDBConfig

def query_strategies():
    """Query all records from the strategies collection"""
    try:
        # Load MongoDB configuration
        mongodb_config = MongoDBConfig()
        config = mongodb_config.get_mongodb_config()

        # Connect to MongoDB
        if config.get('username') and config.get('password'):
            # With authentication
            uri = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?authSource={config.get('auth_database', 'admin')}"
        else:
            # Without authentication
            uri = f"mongodb://{config['host']}:{config['port']}/"

        client = MongoClient(uri)
        db = client[config['database']]

        # Get the strategies collection name
        strategies_collection_name = mongodb_config.get_collection_name('strategies')
        strategies_collection = db[strategies_collection_name]

        # Query all records
        records = list(strategies_collection.find({}))

        print(f"Found {len(records)} records in the strategies collection:")
        print("-" * 50)

        for i, record in enumerate(records, 1):
            print(f"Record {i}:")
            for key, value in record.items():
                if key == '_id':
                    continue  # Skip the MongoDB _id field
                print(f"  {key}: {value}")
            print()

        client.close()

    except Exception as e:
        print(f"Error querying strategies collection: {e}")
        sys.exit(1)

if __name__ == "__main__":
    query_strategies()

