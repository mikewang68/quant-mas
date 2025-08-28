#!/usr/bin/env python3
"""
Test script to check the current structure of pool collection in MongoDB
"""

import sys
import os
import pymongo
from datetime import datetime

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Main function to check pool structure"""
    print("Checking Pool Collection Structure...")

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

        # Get the latest pool record
        latest_pool_record = pool_collection.find_one(sort=[('selection_date', -1)])

        if latest_pool_record:
            print("\nLatest Pool Record Structure:")
            print("=" * 50)

            # Print top-level fields
            print("Top-level fields:")
            for key, value in latest_pool_record.items():
                if key == '_id':
                    print(f"  {key}: {value} (ObjectId)")
                elif key == 'stocks':
                    print(f"  {key}: {len(value)} stocks")
                elif isinstance(value, datetime):
                    print(f"  {key}: {value.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print(f"  {key}: {value} ({type(value).__name__})")

            # Print sample stocks structure
            if 'stocks' in latest_pool_record and latest_pool_record['stocks']:
                print("\nSample Stock Structure (first 2 stocks):")
                for i, stock in enumerate(latest_pool_record['stocks'][:2]):
                    print(f"  Stock {i+1}:")
                    for key, value in stock.items():
                        if key == 'tech':
                            print(f"    {key}: {{")
                            if isinstance(value, dict):
                                for tech_key, tech_value in value.items():
                                    print(f"      {tech_key}: {{")
                                    if isinstance(tech_value, dict):
                                        for sub_key, sub_value in tech_value.items():
                                            print(f"        {sub_key}: {sub_value}")
                                    print(f"      }}")
                            print(f"    }}")
                        else:
                            print(f"    {key}: {value}")

            # Count stocks with tech data
            stocks_with_tech = [s for s in latest_pool_record.get('stocks', []) if 'tech' in s]
            print(f"\nStocks with tech data: {len(stocks_with_tech)}/{len(latest_pool_record.get('stocks', []))}")

        else:
            print("No records found in pool collection")

        client.close()

    except Exception as e:
        print(f"Error checking pool structure: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\nCheck completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

