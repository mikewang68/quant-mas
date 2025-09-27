"""
Test script to check database connection and account data
"""

import sys
import os
sys.path.append('.')

from data.mongodb_manager import MongoDBManager
import json

def test_database_connection():
    """Test database connection and account data"""
    try:
        # Initialize MongoDBManager
        print("Initializing MongoDB connection...")
        manager = MongoDBManager()
        print("MongoDB connection successful!")

        # Test accounts collection
        print("\nTesting accounts collection...")
        try:
            accounts = list(manager.accounts_collection.find())
            print(f"Found {len(accounts)} accounts")
            if accounts:
                print("First account:")
                print(json.dumps(accounts[0], indent=2, default=str))
            else:
                print("No accounts found")
        except Exception as e:
            print(f"Error accessing accounts collection: {e}")

        # Test config collection
        print("\nTesting config collection...")
        try:
            config = manager.config_collection.find_one()
            if config:
                print("Config found:")
                print(json.dumps(config, indent=2, default=str))
            else:
                print("No config found")
        except Exception as e:
            print(f"Error accessing config collection: {e}")

        # Test pool collection
        print("\nTesting pool collection...")
        try:
            pool_records = list(manager.pool_collection.find().limit(5))
            print(f"Found {len(pool_records)} pool records")
            if pool_records:
                print("First pool record:")
                print(json.dumps(pool_records[0], indent=2, default=str))
            else:
                print("No pool records found")
        except Exception as e:
            print(f"Error accessing pool collection: {e}")

        # Close connection
        manager.close_connection()
        print("\nDatabase connection closed.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_connection()

