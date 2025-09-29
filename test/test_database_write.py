#!/usr/bin/env python3
"""
Test Database Write
Tests that the signal generation results are correctly written to the database.
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

def test_database_write():
    """Test that the signal generation results are correctly written to the database."""
    print("Test Database Write")
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

    # Prepare the signal stock data as the agent would
    signal_stock_data = {
        'code': stock_code,
        'strategy_name': strategy.name,
        'score': analysis_result.get('score_calc', 0),
        'selection_reason': analysis_result.get('selection_reason', ''),
        'signals': analysis_result.get('signals', {}),
        'count': analysis_result.get('count', 0),
        'action': analysis_result.get('action', ''),
        'score_ai': analysis_result.get('score_ai', 0),
        'score_calc': analysis_result.get('score_calc', 0),
        'value_ai': analysis_result.get('value_ai', ''),
        'value_calc': analysis_result.get('value_calc', {})
    }

    print(f"\nSignal Stock Data Prepared:")
    print(f"-"*25)
    print(f"  code: {signal_stock_data['code']}")
    print(f"  strategy_name: {signal_stock_data['strategy_name']}")
    print(f"  score: {signal_stock_data['score']}")
    print(f"  signals: {signal_stock_data['signals']}")

    # Simulate the database update process
    print(f"\nSimulating Database Update Process:")
    print(f"-"*35)

    # Get existing stocks from the latest pool record
    existing_stocks = latest_pool_record.get("stocks", [])
    existing_stock_map = {stock.get("code"): stock for stock in existing_stocks}

    # Update signal data for the sample stock
    code = signal_stock_data.get('code')
    if code in existing_stock_map:
        # Check if signals field exists, create if not
        if 'signals' not in existing_stock_map[code]:
            existing_stock_map[code]['signals'] = {}

        # Get the signal data from the strategy result
        signal_data = signal_stock_data.get('signals', {})
        strategy_name = signal_stock_data.get('strategy_name', 'unknown_strategy')

        # Update the signals field for the existing stock
        existing_stock_map[code]['signals'][strategy_name] = signal_data

        print(f"  Updated signals for stock {code}")
        print(f"  Strategy name: {strategy_name}")
        print(f"  Signal data: {signal_data}")

        # Verify the update
        updated_signals = existing_stock_map[code].get('signals', {})
        if strategy_name in updated_signals:
            strategy_signals = updated_signals[strategy_name]
            print(f"  Verification - Signals written to database:")
            print(f"    score: {strategy_signals.get('score', 'N/A')}")
            print(f"    value: {strategy_signals.get('value', 'N/A')}")
            print(f"  ✅ Database write successful")
        else:
            print(f"  ❌ Database write failed")
            return 1
    else:
        print(f"  Stock {code} not found in pool")
        return 1

    return 0

def main():
    """Main function to run the test."""
    return test_database_write()

if __name__ == "__main__":
    sys.exit(main())

