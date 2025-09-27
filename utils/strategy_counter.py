#!/usr/bin/env python3
"""
Strategy Counter
Counts the number of strategies in trend, tech, fund, and pub fields.
"""

import sys
import os
from pymongo import MongoClient
from typing import Dict, Any
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

def count_strategies_by_field(db) -> Dict[str, int]:
    """
    Count strategies in trend, tech, fund, and pub fields.

    Args:
        db: MongoDB database instance

    Returns:
        Dictionary with strategy counts by field
    """
    try:
        # Get the pool collection
        pool_collection = db['pool']

        # Find the latest pool record
        latest_pool_record = pool_collection.find_one(sort=[("_id", -1)])

        if not latest_pool_record:
            logger.error("No records found in pool collection")
            return {}

        # Get stocks from the latest pool record
        pool_stocks = latest_pool_record.get("stocks", [])

        if not pool_stocks:
            logger.error("No stocks found in latest pool record")
            return {}

        logger.info(f"Analyzing {len(pool_stocks)} stocks")

        # Initialize counters
        field_strategy_counts = {
            'trend': 0,
            'tech': 0,
            'fund': 0,
            'pub': 0
        }

        # Process each stock
        for stock in pool_stocks:
            # Process all fields in the stock
            for field_name, field_value in stock.items():
                # Only count the specified fields and ensure field_value is a dict
                if field_name in field_strategy_counts and isinstance(field_value, dict):
                    # Count strategies in this field
                    strategy_count = len(field_value)
                    field_strategy_counts[field_name] += strategy_count

        return field_strategy_counts

    except Exception as e:
        logger.error(f"Error counting strategies: {e}")
        return {}

def main():
    """Main function to run the strategy counter."""
    print("Strategy Counter")
    print("="*15)

    # Connect to MongoDB
    db = connect_to_mongodb()
    if db is None:
        print("Failed to connect to database")
        return 1

    # Count strategies by field
    counts = count_strategies_by_field(db)

    # Print results
    print("\nStrategy Counts by Field:")
    print("-"*25)
    total_strategies = 0

    for field, count in counts.items():
        print(f"{field.upper():>5}: {count}")
        total_strategies += count

    print("-"*25)
    print(f"TOTAL: {total_strategies}")

    return 0

if __name__ == "__main__":
    sys.exit(main())

