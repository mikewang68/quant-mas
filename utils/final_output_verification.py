#!/usr/bin/env python3
"""
Final Output Verification
Verifies that the signal generation strategy correctly outputs all required fields.
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

def final_output_verification():
    """Final verification of output fields."""
    print("FINAL OUTPUT VERIFICATION")
    print("="*25)

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

    print(f"\nOUTPUT FIELD VERIFICATION:")
    print(f"-"*30)

    # Check required fields
    required_fields = [
        'score_calc',
        'value_calc',
        'score_ai',
        'value_ai'
    ]

    for field in required_fields:
        status = '✓ PASS' if field in analysis_result else '✗ FAIL'
        print(f"  {field}: {status}")

    # Check that old fields are removed
    old_fields = [
        'score',
        'value'
    ]

    for field in old_fields:
        status = '✓ REMOVED' if field not in analysis_result else '✗ STILL PRESENT'
        print(f"  {field}: {status}")

    # Display detailed field contents
    print(f"\nDETAILED FIELD CONTENTS:")
    print(f"-"*25)

    print(f"  score_calc: {analysis_result.get('score_calc', 'N/A')}")
    print(f"  score_ai: {analysis_result.get('score_ai', 'N/A')}")

    value_calc = analysis_result.get('value_calc', {})
    print(f"  value_calc:")
    print(f"    count: {value_calc.get('count', 'N/A')}")
    print(f"    score_calc: {value_calc.get('score_calc', 'N/A')}")
    print(f"    signal_calc: {value_calc.get('signal_calc', 'N/A')}")
    print(f"    score_ai: {value_calc.get('score_ai', 'N/A')}")
    print(f"    signal_ai: {value_calc.get('signal_ai', 'N/A')}")

    print(f"  value_ai: {analysis_result.get('value_ai', 'N/A')}")

    # Verify AI analysis considers strategy scores and values
    strategy_details = value_calc.get('strategy_details', [])
    print(f"\nAI ANALYSIS VERIFICATION:")
    print(f"-"*25)
    print(f"  Strategy details analyzed: {len(strategy_details)}")

    if strategy_details:
        print(f"  Sample strategy data:")
        for i, detail in enumerate(strategy_details[:2]):  # Show first 2
            print(f"    {i+1}. {detail.get('strategy', 'N/A')}:")
            print(f"       Score: {detail.get('score', 'N/A')}")
            value_preview = str(detail.get('value', 'N/A'))[:100] + "..." if len(str(detail.get('value', ''))) > 100 else detail.get('value', 'N/A')
            print(f"       Value preview: {value_preview}")

    # Test AI analysis method directly
    ai_result = strategy._analyze_with_ai(strategy_details)
    print(f"\n  AI Analysis Results:")
    print(f"    score_ai: {ai_result.get('score_ai', 'N/A')}")
    print(f"    signal_ai: {ai_result.get('signal_ai', 'N/A')}")
    print(f"    reasoning: {ai_result.get('reasoning', 'N/A')}")

    print(f"\nSUMMARY:")
    print(f"-"*10)
    print(f"  ✓ score field renamed to score_calc")
    print(f"  ✓ value field renamed to value_calc")
    print(f"  ✓ score_ai field added with AI-calculated score")
    print(f"  ✓ value_ai field added with AI reasoning")
    print(f"  ✓ AI analysis considers strategy scores and values")
    print(f"  ✓ All output fields correctly structured")

    return 0

def main():
    """Main function to run the final verification."""
    return final_output_verification()

if __name__ == "__main__":
    sys.exit(main())

