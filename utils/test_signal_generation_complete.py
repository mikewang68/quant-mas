#!/usr/bin/env python3
"""
Complete Signal Generation Strategy Test
Tests the modified signal generation strategy with all stocks to verify correct average score calculation.
"""

import sys
import os
from pymongo import MongoClient
import logging
import numpy as np

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

def test_complete_signal_generation():
    """Test the signal generation strategy with all stocks."""
    print("Complete Signal Generation Strategy Test")
    print("="*40)

    # Connect to MongoDB
    db = connect_to_mongodb()
    if db is None:
        print("Failed to connect to database")
        return 1

    # Create mock DB manager
    mock_db_manager = MockDBManager(db)

    # Create strategy instance
    strategy = SignalGenerationV1Strategy()

    # Get the latest pool record
    pool_collection = db['pool']
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

    # Get the global strategy count
    global_strategy_count = strategy._get_global_strategy_count(mock_db_manager)
    print(f"Global strategy count (excluding self): {global_strategy_count}")

    # Process each stock to calculate signals
    analyzed_stocks = []
    score_calc_values = []

    for stock in pool_stocks:
        try:
            code = stock.get('code')
            if not code:
                continue

            # Analyze the stock using global strategy count
            analysis_result = strategy._analyze_stock(stock, global_strategy_count)

            if analysis_result:
                # Add code to the result
                analysis_result['code'] = code
                analyzed_stocks.append(analysis_result)

                # Collect score_calc for statistics
                value_data = analysis_result.get('value', {})
                score_calc = value_data.get('score_calc', 0)
                score_calc_values.append(score_calc)

        except Exception as e:
            logger.warning(f"Error processing stock {code}: {e}")
            continue

    print(f"Analyzed {len(analyzed_stocks)} stocks")

    # Calculate statistics
    if score_calc_values:
        avg_score = np.mean(score_calc_values)
        median_score = np.median(score_calc_values)
        min_score = np.min(score_calc_values)
        max_score = np.max(score_calc_values)
        std_score = np.std(score_calc_values)

        print(f"\nScore Calculation Statistics:")
        print(f"  Average score: {avg_score:.4f}")
        print(f"  Median score: {median_score:.4f}")
        print(f"  Min score: {min_score:.4f}")
        print(f"  Max score: {max_score:.4f}")
        print(f"  Std deviation: {std_score:.4f}")

        # Show some sample results
        print(f"\nSample Results (first 5 stocks):")
        for i, stock in enumerate(analyzed_stocks[:5]):
            code = stock.get('code', 'Unknown')
            value_data = stock.get('value', {})
            score_calc = value_data.get('score_calc', 0)
            signal_calc = value_data.get('signal_calc', 'N/A')
            count = value_data.get('count', 0)
            print(f"  {i+1}. {code}: Score={score_calc:.4f}, Signal={signal_calc}, Count={count}")

    return 0

def main():
    """Main function to run the complete test."""
    return test_complete_signal_generation()

if __name__ == "__main__":
    sys.exit(main())

