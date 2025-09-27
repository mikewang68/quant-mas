#!/usr/bin/env python3
"""
Test script to simulate multiple strategies updating the same stock
"""

import sys
import os
import pymongo
from datetime import datetime

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Main function to test multiple strategies"""
    print("Testing Multiple Strategies Update...")

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
            print("\nAnalyzing stocks with multiple strategies:")
            stocks = latest_pool_record['stocks']

            # Count stocks with multiple strategies in tech field
            stocks_with_multiple_strategies = []
            for stock in stocks:
                if 'tech' in stock and isinstance(stock['tech'], dict):
                    strategy_count = len(stock['tech'])
                    if strategy_count > 1:
                        stocks_with_multiple_strategies.append((stock['code'], strategy_count, list(stock['tech'].keys())))

            print(f"Stocks with multiple strategies: {len(stocks_with_multiple_strategies)}")

            if stocks_with_multiple_strategies:
                print("Examples:")
                for code, count, strategies in stocks_with_multiple_strategies[:3]:
                    print(f"  {code}: {count} strategies - {strategies}")
            else:
                print("No stocks found with multiple strategies yet")

            # Show structure of a stock with tech data
            stocks_with_tech = [s for s in stocks if 'tech' in s]
            if stocks_with_tech:
                print(f"\nSample stock with tech data:")
                stock = stocks_with_tech[0]
                print(f"  Code: {stock['code']}")
                print(f"  Tech structure:")
                for strategy_name, strategy_data in stock['tech'].items():
                    print(f"    {strategy_name}:")
                    print(f"      score: {strategy_data.get('score', 'N/A')}")
                    print(f"      value: {strategy_data.get('value', 'N/A')}")
        else:
            print("No records found in pool collection")

        client.close()

    except Exception as e:
        print(f"Error testing multiple strategies: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\nMultiple strategies test completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

