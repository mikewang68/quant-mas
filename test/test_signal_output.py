#!/usr/bin/env python3
"""
Test Signal Output
Tests that the signal generation strategy outputs the correct 6 fields.
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

def test_signal_output():
    """Test that the signal generation strategy outputs the correct 6 fields."""
    print("Test Signal Output")
    print("="*18)

    # Connect to MongoDB
    db = connect_to_mongodb()
    if db is None:
        print("Failed to connect to database")
        return 1

    # Create mock DB manager
    mock_db_manager = MockDBManager(db)

    # Create strategy instance
    strategy = SignalGenerationV1Strategy()

    # Get the global strategy count
    global_strategy_count = strategy._get_global_strategy_count(mock_db_manager)

    # Get a sample stock to analyze
    pool_collection = db['pool']
    latest_pool_record = pool_collection.find_one(sort=[("_id", -1)])

    if not latest_pool_record or not latest_pool_record.get("stocks"):
        print("No stocks found in pool")
        return 1

    sample_stock = latest_pool_record["stocks"][0]
    stock_code = sample_stock.get('code', 'Unknown')

    print(f"Analyzing stock: {stock_code}")

    # Analyze the stock
    analysis_result = strategy._analyze_stock(sample_stock, global_strategy_count)

    if not analysis_result:
        print("Failed to analyze stock")
        return 1

    # Check the 6 required output fields
    print(f"\nRequired Output Fields Verification:")
    print(f"-"*35)

    required_fields = [
        ('count', int),
        ('action', str),
        ('score_ai', float),
        ('score_calc', float),
        ('value_ai', str),
        ('value_calc', dict)
    ]

    all_fields_present = True
    for field_name, expected_type in required_fields:
        if field_name in analysis_result:
            actual_type = type(analysis_result[field_name])
            status = '✓ PASS' if isinstance(analysis_result[field_name], expected_type) else f'✗ TYPE MISMATCH (expected {expected_type.__name__}, got {actual_type.__name__})'
            print(f"  {field_name}: {status}")
        else:
            print(f"  {field_name}: ✗ MISSING")
            all_fields_present = False

    # Display the actual values
    print(f"\nActual Values:")
    print(f"-"*15)
    print(f"  count: {analysis_result.get('count', 'N/A')}")
    print(f"  action: {analysis_result.get('action', 'N/A')}")
    print(f"  score_ai: {analysis_result.get('score_ai', 'N/A')}")
    print(f"  score_calc: {analysis_result.get('score_calc', 'N/A')}")
    print(f"  value_ai: {analysis_result.get('value_ai', 'N/A')}")

    value_calc = analysis_result.get('value_calc', {})
    print(f"  value_calc:")
    print(f"    count: {value_calc.get('count', 'N/A')}")
    print(f"    score_calc: {value_calc.get('score_calc', 'N/A')}")
    print(f"    signal_calc: {value_calc.get('signal_calc', 'N/A')}")
    print(f"    score_ai: {value_calc.get('score_ai', 'N/A')}")
    print(f"    signal_ai: {value_calc.get('signal_ai', 'N/A')}")

    # Check signals structure for pool update
    signals = analysis_result.get('signals', {})
    print(f"\nSignals Structure (for pool update):")
    print(f"-"*38)
    print(f"  score: {signals.get('score', 'N/A')}")
    print(f"  value: {signals.get('value', 'N/A')}")

    return 0 if all_fields_present else 1

def main():
    """Main function to run the test."""
    return test_signal_output()

if __name__ == "__main__":
    sys.exit(main())

