#!/usr/bin/env python3
"""
Test Modified Signal Generation
Tests the modified signal generation strategy with updated output fields and AI analysis.
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

def test_modified_signal_generation():
    """Test the modified signal generation strategy."""
    print("Test Modified Signal Generation")
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

    # Get the global strategy count
    global_strategy_count = strategy._get_global_strategy_count(mock_db_manager)
    print(f"Global strategy count (excluding self): {global_strategy_count}")

    # Get a sample stock to analyze
    pool_collection = db['pool']
    latest_pool_record = pool_collection.find_one(sort=[("_id", -1)])

    if not latest_pool_record or not latest_pool_record.get("stocks"):
        print("No stocks found in pool")
        return 1

    sample_stock = latest_pool_record["stocks"][0]
    stock_code = sample_stock.get('code', 'Unknown')

    print(f"\nAnalyzing stock: {stock_code}")

    # Analyze the stock
    analysis_result = strategy._analyze_stock(sample_stock, global_strategy_count)

    if not analysis_result:
        print("Failed to analyze stock")
        return 1

    # Display the modified output fields
    print(f"\nModified Output Fields:")
    print(f"  score_calc: {analysis_result.get('score_calc', 'N/A')}")
    print(f"  value_calc: {analysis_result.get('value_calc', 'N/A')}")
    print(f"  score_ai: {analysis_result.get('score_ai', 'N/A')}")
    print(f"  value_ai: {analysis_result.get('value_ai', 'N/A')}")

    # Display detailed value_calc structure
    value_calc = analysis_result.get('value_calc', {})
    print(f"\nDetailed value_calc structure:")
    print(f"  count: {value_calc.get('count', 'N/A')}")
    print(f"  score_calc: {value_calc.get('score_calc', 'N/A')}")
    print(f"  signal_calc: {value_calc.get('signal_calc', 'N/A')}")
    print(f"  score_ai: {value_calc.get('score_ai', 'N/A')}")
    print(f"  signal_ai: {value_calc.get('signal_ai', 'N/A')}")
    print(f"  strategy_details: {len(value_calc.get('strategy_details', []))} strategies")

    # Display AI analysis details
    ai_result = strategy._analyze_with_ai(value_calc.get('strategy_details', []))
    print(f"\nAI Analysis Details:")
    print(f"  score_ai: {ai_result.get('score_ai', 'N/A')}")
    print(f"  signal_ai: {ai_result.get('signal_ai', 'N/A')}")
    print(f"  reasoning: {ai_result.get('reasoning', 'N/A')}")

    # Display signals structure
    signals = analysis_result.get('signals', {})
    print(f"\nSignals structure:")
    print(f"  score: {signals.get('score', 'N/A')}")
    print(f"  value: {signals.get('value', 'N/A')}")

    # Verify field changes
    print(f"\nField Verification:")
    print(f"  'score' field replaced with 'score_calc': {'✓ PASS' if 'score_calc' in analysis_result else '✗ FAIL'}")
    print(f"  'value' field replaced with 'value_calc': {'✓ PASS' if 'value_calc' in analysis_result else '✗ FAIL'}")
    print(f"  'score_ai' field added: {'✓ PASS' if 'score_ai' in analysis_result else '✗ FAIL'}")
    print(f"  'value_ai' field added: {'✓ PASS' if 'value_ai' in analysis_result else '✗ FAIL'}")

    return 0

def main():
    """Main function to run the test."""
    return test_modified_signal_generation()

if __name__ == "__main__":
    sys.exit(main())

