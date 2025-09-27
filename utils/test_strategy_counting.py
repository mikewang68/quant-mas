#!/usr/bin/env python3
"""
Strategy Counting Test
Tests the modified signal generation strategy to verify correct strategy counting.
"""

import sys
import os
from pymongo import MongoClient
import logging

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

def test_strategy_counting():
    """Test strategy counting in the signal generation strategy."""
    print("Strategy Counting Test")
    print("="*20)

    # Connect to MongoDB
    db = connect_to_mongodb()
    if db is None:
        print("Failed to connect to database")
        return 1

    # Create mock DB manager
    mock_db_manager = MockDBManager(db)

    # Create strategy instance
    strategy = SignalGenerationV1Strategy()

    # Get a sample stock to analyze
    pool_collection = db['pool']
    latest_pool_record = pool_collection.find_one(sort=[("_id", -1)])

    if not latest_pool_record or not latest_pool_record.get("stocks"):
        print("No stocks found in pool")
        return 1

    sample_stock = latest_pool_record["stocks"][0]
    stock_code = sample_stock.get('code', 'Unknown')

    print(f"Analyzing stock: {stock_code}")

    # Show the stock structure
    print(f"Stock fields: {list(sample_stock.keys())}")

    # Count strategy fields manually
    strategy_fields = {}
    for field_name, field_value in sample_stock.items():
        if isinstance(field_value, dict) and field_name not in ['signal', 'code', 'signals']:
            strategy_fields[field_name] = list(field_value.keys())

    print(f"Strategy fields (excluding 'signal', 'code', 'signals'):")
    total_strategies = 0
    for field_name, strategies in strategy_fields.items():
        print(f"  {field_name}: {len(strategies)} strategies - {strategies}")
        total_strategies += len(strategies)

    print(f"Total strategies: {total_strategies}")

    # Get the global strategy count
    global_strategy_count = strategy._get_global_strategy_count(mock_db_manager)
    print(f"Global strategy count (excluding self): {global_strategy_count}")

    # Analyze the stock
    analysis_result = strategy._analyze_stock(sample_stock, global_strategy_count)

    if not analysis_result:
        print("Failed to analyze stock")
        return 1

    # Extract values for verification
    value_data = analysis_result.get('value', {})
    score_calc = value_data.get('score_calc', 0)
    count = value_data.get('count', 0)
    selection_reason = analysis_result.get('selection_reason', '')

    print(f"\nAnalysis Results:")
    print(f"  Strategies satisfied (count): {count}")
    print(f"  Calculated score: {score_calc:.4f}")
    print(f"  Selection reason: {selection_reason}")

    # Verify the count
    print(f"\nVerification:")
    print(f"  Manual count: {total_strategies}")
    print(f"  Strategy count: {count}")
    print(f"  Status: {'✓ PASS' if total_strategies == count else '✗ FAIL'}")

    return 0

def main():
    """Main function to run the strategy counting test."""
    return test_strategy_counting()

if __name__ == "__main__":
    sys.exit(main())

