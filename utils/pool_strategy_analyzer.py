#!/usr/bin/env python3
"""
Utility to analyze strategies in the pool collection.
Counts total strategies and calculates average scores.
"""

import sys
import os
from pymongo import MongoClient
from typing import Dict, Any, Tuple
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

def count_strategies_in_pool(db) -> Tuple[int, float]:
    """
    Count total strategies in the pool collection and calculate average score.

    Args:
        db: MongoDB database instance

    Returns:
        Tuple of (total_strategy_count, average_score)
    """
    try:
        # Get the pool collection
        pool_collection = db['pool']

        # Find the latest pool record
        latest_pool_record = pool_collection.find_one(sort=[("_id", -1)])

        if not latest_pool_record:
            logger.error("No records found in pool collection")
            return 0, 0.0

        # Get stocks from the latest pool record
        pool_stocks = latest_pool_record.get("stocks", [])

        if not pool_stocks:
            logger.error("No stocks found in latest pool record")
            return 0, 0.0

        logger.info(f"Analyzing {len(pool_stocks)} stocks from latest pool record")

        # Initialize counters
        total_strategy_count = 0
        total_score_sum = 0.0
        score_count = 0

        # Process each stock
        for stock in pool_stocks:
            # Process all fields in the stock
            for field_name, field_value in stock.items():
                # Skip non-dict fields and excluded fields (code, signals)
                if field_name in ['code', 'signals'] or not isinstance(field_value, dict):
                    continue

                # Process each strategy in the field
                for strategy_name, strategy_info in field_value.items():
                    if isinstance(strategy_info, dict):
                        total_strategy_count += 1

                        # Try to get score for averaging
                        score = strategy_info.get('score')
                        if score is not None:
                            try:
                                score_float = float(score)
                                total_score_sum += score_float
                                score_count += 1
                            except (ValueError, TypeError):
                                pass  # Skip invalid scores

        # Calculate average score
        average_score = total_score_sum / score_count if score_count > 0 else 0.0

        logger.info(f"Total strategies found: {total_strategy_count}")
        logger.info(f"Average score: {average_score:.4f}")

        return total_strategy_count, average_score

    except Exception as e:
        logger.error(f"Error counting strategies in pool: {e}")
        return 0, 0.0

def main():
    """Main function to run the analyzer."""
    print("Pool Strategy Analyzer")
    print("======================")

    # Connect to MongoDB
    db = connect_to_mongodb()
    if db is None:
        print("Failed to connect to database")
        return 1

    # Count strategies and calculate average score
    total_count, avg_score = count_strategies_in_pool(db)

    print(f"Total strategies in pool: {total_count}")
    print(f"Average strategy score: {avg_score:.4f}")

    return 0

if __name__ == "__main__":
    sys.exit(main())

