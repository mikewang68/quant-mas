#!/usr/bin/env python3
"""
Detailed test script to check the current structure of pool collection in MongoDB
"""

import sys
import os
import pymongo
from datetime import datetime
import json

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Main function to check pool structure"""
    print("Checking Pool Collection Structure (Detailed)...")

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

            # Print sample stocks structure with detailed tech analysis
            if 'stocks' in latest_pool_record and latest_pool_record['stocks']:
                stocks = latest_pool_record['stocks']
                print(f"\nAnalyzing {len(stocks)} stocks:")

                # Count different types of stocks
                stocks_with_tech = [s for s in stocks if 'tech' in s]
                stocks_with_strategy_fields = [s for s in stocks if 'strategy_name' in s]
                stocks_with_technical_analysis = [s for s in stocks if 'technical_analysis' in s]

                print(f"  Stocks with 'tech' field: {len(stocks_with_tech)}")
                print(f"  Stocks with 'strategy_name' field: {len(stocks_with_strategy_fields)}")
                print(f"  Stocks with 'technical_analysis' field: {len(stocks_with_technical_analysis)}")

                # Show detailed structure for first few stocks
                print(f"\nDetailed structure of first 3 stocks:")
                for i, stock in enumerate(stocks[:3]):
                    print(f"  Stock {i+1} ({stock.get('code', 'N/A')}):")
                    for key, value in stock.items():
                        if key == 'tech':
                            print(f"    {key}: {{")
                            if isinstance(value, dict):
                                for tech_key, tech_value in value.items():
                                    print(f"      {tech_key}: {{")
                                    if isinstance(tech_value, dict):
                                        for sub_key, sub_value in tech_value.items():
                                            print(f"        {sub_key}: {sub_value}")
                                    else:
                                        print(f"        {tech_value}")
                                    print(f"      }}")
                            print(f"    }}")
                        elif key == 'technical_analysis':
                            print(f"    {key}: {{...}} (technical analysis data)")
                        elif isinstance(value, (dict, list)) and len(str(value)) > 100:
                            print(f"    {key}: <{type(value).__name__} with {len(value)} items>")
                        else:
                            print(f"    {key}: {value}")

                # Look for stocks with the expected tech structure
                print(f"\nLooking for stocks with expected tech structure:")
                stocks_with_expected_tech = []
                for stock in stocks:
                    if 'tech' in stock and isinstance(stock['tech'], dict):
                        for strategy_name, strategy_data in stock['tech'].items():
                            if isinstance(strategy_data, dict) and 'score' in strategy_data and 'value' in strategy_data:
                                stocks_with_expected_tech.append((stock['code'], strategy_name, strategy_data))

                if stocks_with_expected_tech:
                    print(f"  Found {len(stocks_with_expected_tech)} stocks with expected tech structure:")
                    for code, strategy_name, data in stocks_with_expected_tech[:3]:
                        print(f"    {code}: tech.{strategy_name} = {{score: {data['score']}, value: '{data['value']}'}}")
                else:
                    print(f"  No stocks found with expected tech structure")

        else:
            print("No records found in pool collection")

        client.close()

    except Exception as e:
        print(f"Error checking pool structure: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\nDetailed check completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

