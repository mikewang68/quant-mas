#!/usr/bin/env python3
"""
Script to remove extra fields from pool collection stocks
Removes: selection_reason, position, strategy_name, technical_analysis, uptrend_accelerating
"""

import sys
import os
import pymongo
from datetime import datetime

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def remove_extra_fields_from_pool():
    """Remove extra fields from pool collection stocks"""
    print("Removing extra fields from pool collection...")

    try:
        # Database connection parameters
        host = "192.168.1.2"
        port = 27017
        database = "stock"
        username = "stock"
        password = "681123"
        auth_database = "admin"

        # Connect to MongoDB with authentication
        uri = f"mongodb://{username}:{password}@{host}:{port}/{database}?authSource={auth_database}"
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)

        # Test connection
        client.admin.command('ping')
        print(f"✓ Successfully connected to MongoDB: {host}:{port}/{database}")

        # Access database and collection
        db = client[database]
        pool_collection = db['pool']

        # Define the fields to remove
        fields_to_remove = ['selection_reason', 'position', 'strategy_name', 'technical_analysis', 'uptrend_accelerating']

        # Get all pool records
        records = list(pool_collection.find())
        print(f"Found {len(records)} records in pool collection")

        # Process each record
        updated_count = 0
        for record in records:
            record_id = record.get('_id')
            stocks = record.get('stocks', [])

            if not stocks:
                continue

            # Check if any stock has the extra fields
            has_extra_fields = False
            for stock in stocks:
                if any(field in stock for field in fields_to_remove):
                    has_extra_fields = True
                    break

            if has_extra_fields:
                # Remove extra fields from all stocks in this record
                cleaned_stocks = []
                for stock in stocks:
                    # Create a new stock dict without the extra fields
                    cleaned_stock = {key: value for key, value in stock.items() if key not in fields_to_remove}
                    cleaned_stocks.append(cleaned_stock)

                # Update the record
                result = pool_collection.update_one(
                    {'_id': record_id},
                    {'$set': {'stocks': cleaned_stocks}}
                )

                if result.modified_count > 0:
                    updated_count += 1
                    print(f"  Updated record {record_id}")

        print(f"✓ Updated {updated_count} records")
        client.close()
        print("✓ Database connection closed")

        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("Pool Collection Extra Fields Removal Script")
    print("=" * 50)

    success = remove_extra_fields_from_pool()

    if success:
        print("\n✓ Extra fields removal completed successfully!")
        return 0
    else:
        print("\n✗ Extra fields removal failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())

