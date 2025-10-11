#!/usr/bin/env python3
"""
Test script to verify if update_latest_pool_record can correctly write to database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.fundamental_selector import FundamentalStockSelector
from strategies.llm_fundamental_strategy import LLMFundamentalStrategy
from config.mongodb_config import MongoDBConfig
from pymongo import MongoClient
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_update_latest_pool_record():
    """Test if update_latest_pool_record can correctly write to database"""
    print("=== Testing update_latest_pool_record Database Write ===")

    # Create strategy instance
    strategy = LLMFundamentalStrategy(name="LLM基本面分析策略")

    # Test with a stock
    test_stock = "000985"  # 大庆华科

    print(f"\n1. Testing strategy execution for {test_stock}:")

    # Create mock stock_data
    stock_data = {test_stock: None}

    # Mock db_manager
    class MockDBManager:
        def __init__(self):
            self.db = {}

    db_manager = MockDBManager()

    selected_stocks = strategy.execute(stock_data, "test_agent", db_manager)

    if selected_stocks:
        first_stock = selected_stocks[0]
        print(f"  Strategy returned score: {first_stock.get('score')}")
        print(f"  Strategy returned value length: {len(first_stock.get('value', ''))}")

        # Check the value content
        try:
            import json
            parsed_value = json.loads(first_stock.get('value', ''))
            print(f"  Value JSON score: {parsed_value.get('score')}")
        except Exception as e:
            print(f"  Error parsing value: {e}")

    print(f"\n2. Creating fundamental selector with real database connection:")

    # Load MongoDB configuration
    mongodb_config = MongoDBConfig()
    config = mongodb_config.get_mongodb_config()

    # Connect to MongoDB
    if config.get("username") and config.get("password"):
        # With authentication
        uri = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?authSource={config.get('auth_database', 'admin')}"
    else:
        # Without authentication
        uri = f"mongodb://{config['host']}:{config['port']}/"

    client = MongoClient(uri)
    db = client[config["database"]]
    pool_collection = db["pool"]

    # Create a mock pool record for testing
    print(f"\n3. Creating test pool record:")

    # First, check if there's an existing pool record
    latest_pool_record = pool_collection.find_one(sort=[("_id", -1)])

    if latest_pool_record:
        print(f"  Found existing pool record with _id: {latest_pool_record.get('_id')}")
        print(f"  Existing stocks count: {len(latest_pool_record.get('stocks', []))}")

        # Check if our test stock exists in the pool
        existing_stocks = latest_pool_record.get("stocks", [])
        test_stock_exists = any(stock.get("code") == test_stock for stock in existing_stocks)

        if test_stock_exists:
            print(f"  Test stock {test_stock} exists in pool")
        else:
            print(f"  Test stock {test_stock} does not exist in pool, adding it...")
            # Add test stock to existing pool
            existing_stocks.append({
                "code": test_stock,
                "score": 0.01,  # Simulate the problematic score
                "trend": {}
            })

            # Update the pool record
            result = pool_collection.update_one(
                {"_id": latest_pool_record["_id"]},
                {"$set": {"stocks": existing_stocks}}
            )
            print(f"  Updated pool record: {result.modified_count} documents modified")
    else:
        print(f"  No existing pool records found, creating new one...")
        # Create a new pool record
        new_pool_record = {
            "stocks": [
                {
                    "code": test_stock,
                    "score": 0.01,  # Simulate the problematic score
                    "trend": {}
                }
            ],
            "created_at": datetime.now()
        }
        result = pool_collection.insert_one(new_pool_record)
        print(f"  Created new pool record with _id: {result.inserted_id}")

    print(f"\n4. Testing update_latest_pool_record method:")

    # Create fundamental selector with real database manager
    class RealDBManager:
        def __init__(self):
            self.db = db

    real_db_manager = RealDBManager()

    # Create fundamental selector
    fundamental_selector = FundamentalStockSelector(real_db_manager, None)

    # Prepare fundamental stocks data
    fundamental_stocks = selected_stocks

    # Add strategy_name to each stock
    for stock in fundamental_stocks:
        stock['strategy_name'] = 'LLM基本面分析策略'

    print(f"  Fundamental stocks to update: {len(fundamental_stocks)}")
    for stock in fundamental_stocks:
        print(f"    - {stock.get('code')}: score={stock.get('score')}, value_length={len(stock.get('value', ''))}")

    # Call update_latest_pool_record
    success = fundamental_selector.update_latest_pool_record(fundamental_stocks)

    print(f"  Update result: {'SUCCESS' if success else 'FAILED'}")

    print(f"\n5. Verifying database update:")

    # Check the updated pool record
    updated_pool_record = pool_collection.find_one(sort=[("_id", -1)])

    if updated_pool_record:
        print(f"  Updated pool record _id: {updated_pool_record.get('_id')}")
        print(f"  Updated stocks count: {len(updated_pool_record.get('stocks', []))}")

        # Find our test stock in the updated record
        for stock in updated_pool_record.get("stocks", []):
            if stock.get("code") == test_stock:
                print(f"  Found test stock {test_stock}:")
                print(f"    Top-level score: {stock.get('score')}")

                if 'fund' in stock:
                    fund_data = stock['fund']
                    print(f"    Fund data: {list(fund_data.keys())}")

                    if 'LLM基本面分析策略' in fund_data:
                        strategy_data = fund_data['LLM基本面分析策略']
                        print(f"    Strategy score: {strategy_data.get('score')}")
                        print(f"    Strategy value length: {len(strategy_data.get('value', ''))}")

                        # Parse the value to check the score
                        try:
                            parsed_value = json.loads(strategy_data.get('value', ''))
                            print(f"    Value JSON score: {parsed_value.get('score')}")
                        except Exception as e:
                            print(f"    Error parsing value: {e}")
                    else:
                        print(f"    Strategy 'LLM基本面分析策略' not found in fund data")
                else:
                    print(f"    No fund data found")
                break
        else:
            print(f"  Test stock {test_stock} not found in updated pool record")

    # Clean up - close database connection
    client.close()

if __name__ == "__main__":
    test_update_latest_pool_record()

