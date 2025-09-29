#!/usr/bin/env python3
"""
Stock Structure Checker
Checks the structure of stock data in the pool to understand field counting.
"""

import sys
import os
from pymongo import MongoClient
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_to_mongodb():
    """Connect to MongoDB and return the database instance."""
    try:
        # Connection parameters from config/database.yaml
        MONGODB_URI = "mongodb://stock:681123@192.168.1.2:27017/admin"
        DATABASE_NAME = "stock"

        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        # Test connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        return db
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return None

def check_stock_structure(db):
    """Check the structure of stock data in the pool."""
    print("Stock Structure Checker")
    print("="*22)

    # Get the pool collection
    pool_collection = db['pool']

    # Find the latest pool record
    latest_pool_record = pool_collection.find_one(sort=[("_id", -1)])

    if not latest_pool_record:
        print("No records found in pool collection")
        return 1

    # Get stocks from the latest pool record
    pool_stocks = latest_pool_record.get("stocks", [])

    if not pool_stocks:
        print("No stocks found in latest pool record")
        return 1

    print(f"Analyzing {len(pool_stocks)} stocks from latest pool record")

    # Check structure of first few stocks
    for i, stock in enumerate(pool_stocks[:3]):  # Check first 3 stocks
        print(f"\nStock {i+1} ({stock.get('code', 'Unknown')}):")
        print(f"  Fields: {list(stock.keys())}")

        # Count fields that are dictionaries (strategy fields)
        strategy_fields = {}
        non_strategy_fields = []

        for field_name, field_value in stock.items():
            if isinstance(field_value, dict):
                strategy_fields[field_name] = list(field_value.keys())
            else:
                non_strategy_fields.append(field_name)

        print(f"  Strategy fields ({len(strategy_fields)}):")
        for field_name, strategies in strategy_fields.items():
            print(f"    {field_name}: {len(strategies)} strategies - {strategies}")

        print(f"  Non-strategy fields ({len(non_strategy_fields)}): {non_strategy_fields}")

    return 0

def main():
    """Main function to run the stock structure checker."""
    # Connect to MongoDB
    db = connect_to_mongodb()
    if db is None:
        print("Failed to connect to database")
        return 1

    return check_stock_structure(db)

if __name__ == "__main__":
    sys.exit(main())

