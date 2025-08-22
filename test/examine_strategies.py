#!/usr/bin/env python3
"""
Script to examine the strategies collection in MongoDB to verify the program field structure.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config.mongodb_config import MongoDBConfig
import pymongo

def examine_strategies_collection():
    """Examine the strategies collection in MongoDB to verify the program field structure."""
    try:
        # Load database configuration
        config_loader = MongoDBConfig()
        mongodb_config = config_loader.get_mongodb_config()
        database_name = config_loader.get_database_name()
        strategies_collection_name = config_loader.get_collection_name('strategies')

        print(f"Connecting to MongoDB at {mongodb_config['host']}:{mongodb_config['port']}")
        print(f"Database: {database_name}")
        print(f"Strategies collection: {strategies_collection_name}")

        # Establish connection to MongoDB
        if mongodb_config.get('username') and mongodb_config.get('password'):
            # With authentication
            uri = f"mongodb://{mongodb_config['username']}:{mongodb_config['password']}@{mongodb_config['host']}:{mongodb_config['port']}/{database_name}?authSource={mongodb_config.get('auth_database', 'admin')}"
        else:
            # Without authentication
            uri = f"mongodb://{mongodb_config['host']}:{mongodb_config['port']}/"

        client = pymongo.MongoClient(uri)
        # Test connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB")

        # Access the database and collection
        db = client[database_name]
        strategies_collection = db[strategies_collection_name]

        # Get all strategies
        strategies = list(strategies_collection.find({}, {'_id': 1, 'name': 1, 'type': 1, 'description': 1, 'parameters': 1, 'program': 1, 'file': 1, 'class_name': 1}))

        print(f"\nFound {len(strategies)} strategies in the database:")
        print("=" * 80)

        for strategy in strategies:
            print(f"\nStrategy ID: {strategy.get('_id', 'N/A')}")
            print(f"Name: {strategy.get('name', 'N/A')}")
            print(f"Type: {strategy.get('type', 'N/A')}")
            print(f"Description: {strategy.get('description', 'N/A')}")

            # Check program field
            if 'program' in strategy:
                program = strategy['program']
                print(f"Program field: {program} (type: {type(program)})")
                if isinstance(program, dict):
                    print(f"  File: {program.get('file', 'N/A')}")
                    print(f"  Class: {program.get('class', 'N/A')}")

            # Check file and class_name fields
            if 'file' in strategy:
                print(f"File field: {strategy['file']}")
            if 'class_name' in strategy:
                print(f"Class name field: {strategy['class_name']}")

            # Check parameters
            if 'parameters' in strategy:
                print(f"Parameters: {strategy['parameters']}")

            print("-" * 40)

        # Close connection
        client.close()
        print("\nConnection closed.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    examine_strategies_collection()

