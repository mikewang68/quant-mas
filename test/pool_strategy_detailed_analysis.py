#!/usr/bin/env python3
"""
Pool Strategy Detailed Analysis
Analyzes the strategies in pool data to determine the correct count for signal generation.
"""

import sys
import os
from pymongo import MongoClient
from typing import Dict, Any, Set
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

def analyze_pool_strategies(db) -> Dict[str, Any]:
    """
    Analyze strategies in pool data to determine correct counts.

    Args:
        db: MongoDB database instance

    Returns:
        Dict with analysis results
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

        logger.info(f"Analyzing {len(pool_stocks)} stocks from pool")

        # Track unique strategies in each field
        field_strategies: Dict[str, Set[str]] = {
            'trend': set(),
            'tech': set(),
            'fund': set(),
            'pub': set()
        }

        # Track all unique strategies across all fields
        all_unique_strategies: Set[str] = set()

        # Process each stock
        for stock in pool_stocks:
            # Process all fields in the stock
            for field_name, field_value in stock.items():
                # Only process the specified fields and ensure field_value is a dict
                if field_name in field_strategies and isinstance(field_value, dict):
                    # Add strategy names to the set for this field
                    for strategy_name in field_value.keys():
                        field_strategies[field_name].add(strategy_name)
                        all_unique_strategies.add(f"{field_name}.{strategy_name}")

        # Convert to counts
        field_strategy_counts = {
            field: len(strategies) for field, strategies in field_strategies.items()
        }

        total_unique_strategies = len(all_unique_strategies)

        # Detailed information
        results = {
            'field_strategy_counts': field_strategy_counts,
            'total_unique_strategies': total_unique_strategies,
            'field_strategies_detail': field_strategies,
            'all_unique_strategies': list(all_unique_strategies),
            'total_stocks': len(pool_stocks)
        }

        return results

    except Exception as e:
        logger.error(f"Error analyzing pool strategies: {e}")
        return {}

def main():
    """Main function to run the pool strategy analysis."""
    print("Pool Strategy Detailed Analysis")
    print("="*32)

    # Connect to MongoDB
    db = connect_to_mongodb()
    if db is None:
        print("Failed to connect to database")
        return 1

    # Analyze pool strategies
    results = analyze_pool_strategies(db)

    if not results:
        print("No results to display")
        return 1

    # Display results
    print(f"\nPool Analysis Results:")
    print(f"Total Stocks Analyzed: {results['total_stocks']}")

    print(f"\nStrategy Counts by Field:")
    print("-"*25)
    field_counts = results['field_strategy_counts']
    for field, count in field_counts.items():
        print(f"{field.upper():>5}: {count} unique strategies")

    print("-"*25)
    print(f"TOTAL: {results['total_unique_strategies']} unique strategies")

    print(f"\nDetailed Strategy Information:")
    print("-"*30)
    field_details = results['field_strategies_detail']
    for field, strategies in field_details.items():
        print(f"\n{field.upper()} strategies ({len(strategies)}):")
        for strategy in sorted(list(strategies)):
            print(f"  - {strategy}")

    print(f"\nAll Unique Strategies ({results['total_unique_strategies']}):")
    for strategy in sorted(results['all_unique_strategies']):
        print(f"  - {strategy}")

    return 0

if __name__ == "__main__":
    sys.exit(main())

