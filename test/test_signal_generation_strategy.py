#!/usr/bin/env python3
"""
Signal Generation Strategy Test
Tests the modified signal generation strategy to verify correct average score calculation.
"""

import sys
import os
from pymongo import MongoClient
import logging
from bson import ObjectId

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the strategy
from strategies.signal_generation_v1_strategy import SignalGenerationV1Strategy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockDBManager:
    """Mock database manager for testing."""

    def __init__(self, db):
        self.db = db
        self.strategies_collection = db['strategies']

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

def test_signal_generation_strategy():
    """Test the signal generation strategy."""
    print("Signal Generation Strategy Test")
    print("="*30)

    # Connect to MongoDB
    db = connect_to_mongodb()
    if db is None:
        print("Failed to connect to database")
        return 1

    # Create mock DB manager
    mock_db_manager = MockDBManager(db)

    # Create strategy instance
    strategy = SignalGenerationV1Strategy()

    # Test _get_global_strategy_count method
    print("\nTesting _get_global_strategy_count method:")
    global_strategy_count = strategy._get_global_strategy_count(mock_db_manager)
    print(f"Global strategy count (excluding self): {global_strategy_count}")

    # Test _analyze_stock method with a sample stock
    print("\nTesting _analyze_stock method:")

    # Get a sample stock from the pool
    pool_collection = db['pool']
    latest_pool_record = pool_collection.find_one(sort=[("_id", -1)])

    if latest_pool_record and latest_pool_record.get("stocks"):
        sample_stock = latest_pool_record["stocks"][0]  # Get first stock
        print(f"Analyzing stock: {sample_stock.get('code', 'Unknown')}")

        # Analyze the stock
        analysis_result = strategy._analyze_stock(sample_stock, global_strategy_count)

        if analysis_result:
            print(f"Analysis result:")
            print(f"  Selection reason: {analysis_result.get('selection_reason', 'N/A')}")
            print(f"  Score: {analysis_result.get('score', 'N/A')}")
            value_data = analysis_result.get('value', {})
            print(f"  Count: {value_data.get('count', 'N/A')}")
            print(f"  Score calc: {value_data.get('score_calc', 'N/A')}")
            print(f"  Signal calc: {value_data.get('signal_calc', 'N/A')}")
            print(f"  Score AI: {value_data.get('score_ai', 'N/A')}")
            print(f"  Signal AI: {value_data.get('signal_ai', 'N/A')}")
        else:
            print("Failed to analyze stock")
    else:
        print("No stocks found in pool")

    return 0

def main():
    """Main function to run the test."""
    return test_signal_generation_strategy()

if __name__ == "__main__":
    sys.exit(main())

