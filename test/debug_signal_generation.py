"""
Debug script to test signal generation strategy data collection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.signal_generation_v1_strategy import SignalGenerationV1Strategy
from config.mongodb_config import MongoDBConfig
from pymongo import MongoClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def debug_signal_generation():
    """Debug the signal generation strategy data collection"""

    # Load MongoDB configuration
    mongodb_config = MongoDBConfig()
    config = mongodb_config.get_mongodb_config()

    # Connect to MongoDB
    if config.get("username") and config.get("password"):
        uri = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?authSource={config.get('auth_database', 'admin')}"
    else:
        uri = f"mongodb://{config['host']}:{config['port']}/"

    client = MongoClient(uri)
    db = client[config["database"]]
    pool_collection = db['pool']

    # Get the latest pool record
    latest_pool_record = pool_collection.find_one(sort=[("_id", -1)])

    if not latest_pool_record:
        print("No records found in pool collection")
        return

    print("Testing Signal Generation V1 Strategy data collection...")

    # Create strategy instance
    strategy = SignalGenerationV1Strategy()

    # Get stocks from the latest pool record
    pool_stocks = latest_pool_record.get("stocks", [])

    if not pool_stocks:
        print("No stocks found in latest pool record")
        return

    # Test with first stock
    first_stock = pool_stocks[0]
    code = first_stock.get('code')
    print(f"\nTesting stock: {code}")

    # Manually test the _analyze_stock method
    print("\nTesting _analyze_stock method...")

    # Get global strategy count
    global_strategy_count = strategy._get_global_strategy_count(strategy)
    print(f"Global strategy count: {global_strategy_count}")

    # Test analyze_stock method
    result = strategy._analyze_stock(first_stock, global_strategy_count)

    if result:
        print(f"\nAnalysis result:")
        print(f"  Counts: {result.get('counts')}")
        print(f"  Action: {result.get('action')}")
        print(f"  Score calc: {result.get('score_calc')}")
        print(f"  Signal calc: {result.get('signal_calc')}")
        print(f"  Score AI: {result.get('score_ai')}")
        print(f"  Signal AI: {result.get('signal_ai')}")
    else:
        print("Analysis failed")

if __name__ == "__main__":
    debug_signal_generation()

