#!/usr/bin/env python3
"""
Stock Analysis Tool
Analyzes specific stocks in the pool collection with detailed strategy and signal information.
"""

import sys
import os
from pymongo import MongoClient
from typing import Dict, Any, List
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

def analyze_stock(db, stock_code: str) -> Dict[str, Any]:
    """
    Analyze a specific stock in the pool collection.

    Args:
        db: MongoDB database instance
        stock_code: Stock code to analyze

    Returns:
        Dictionary with stock analysis results
    """
    try:
        # Get the pool collection
        pool_collection = db['pool']

        # Find the latest pool record
        latest_pool_record = pool_collection.find_one(sort=[("_id", -1)])

        if not latest_pool_record:
            logger.error("No records found in pool collection")
            return {}

        # Get stocks from the latest pool record
        pool_stocks = latest_pool_record.get("stocks", [])

        # Find the specific stock
        target_stock = None
        for stock in pool_stocks:
            if stock.get('code') == stock_code:
                target_stock = stock
                break

        if not target_stock:
            logger.error(f"Stock {stock_code} not found in pool")
            return {}

        logger.info(f"Analyzing stock {stock_code}")

        # Initialize analysis results
        results = {
            'code': stock_code,
            'strategies': {},
            'signals': {},
            'trend': {},
            'raw_data': target_stock
        }

        # Extract strategy information
        for field_name, field_value in target_stock.items():
            # Skip non-strategy fields
            if field_name in ['code', 'signals', 'trend']:
                if field_name == 'signals':
                    results['signals'] = field_value
                elif field_name == 'trend':
                    results['trend'] = field_value
                continue

            # Process strategy fields
            if isinstance(field_value, dict):
                results['strategies'][field_name] = {}
                for strategy_name, strategy_info in field_value.items():
                    if isinstance(strategy_info, dict):
                        results['strategies'][field_name][strategy_name] = {
                            'score': strategy_info.get('score', 0),
                            'value': strategy_info.get('value', ''),
                            'selection_reason': strategy_info.get('selection_reason', '')
                        }

        return results

    except Exception as e:
        logger.error(f"Error analyzing stock {stock_code}: {e}")
        return {}

def print_stock_analysis(results: Dict[str, Any]):
    """Print formatted stock analysis results."""
    if not results:
        print("No results to display")
        return

    stock_code = results.get('code', 'Unknown')
    print(f"\n" + "="*60)
    print(f"STOCK ANALYSIS REPORT FOR {stock_code}")
    print("="*60)

    # Trend information
    trend = results.get('trend', {})
    if trend:
        print(f"\nTrend Information:")
        for key, value in trend.items():
            print(f"  {key}: {value}")

    # Strategy analysis
    strategies = results.get('strategies', {})
    if strategies:
        print(f"\nStrategy Analysis:")
        for field_name, field_strategies in strategies.items():
            print(f"  {field_name.upper()} Strategies:")
            for strategy_name, strategy_info in field_strategies.items():
                score = strategy_info.get('score', 0)
                value = strategy_info.get('value', '')
                selection_reason = strategy_info.get('selection_reason', '')

                print(f"    {strategy_name}:")
                print(f"      Score: {score}")
                if value:
                    print(f"      Value: {value}")
                if selection_reason:
                    print(f"      Reason: {selection_reason}")
            print()

    # Signal generation results
    signals = results.get('signals', {})
    if signals:
        print(f"Signal Generation Results:")
        for signal_name, signal_data in signals.items():
            print(f"  {signal_name}:")
            for key, value in signal_data.items():
                print(f"    {key}: {value}")
    else:
        print(f"\nNo signal generation results found for this stock.")

def main(stock_code: str = "002067"):
    """Main function to run the stock analyzer."""
    print(f"Stock Analyzer for {stock_code}")
    print("="*30)

    # Connect to MongoDB
    db = connect_to_mongodb()
    if db is None:
        print("Failed to connect to database")
        return 1

    # Analyze the stock
    results = analyze_stock(db, stock_code)

    # Print results
    print_stock_analysis(results)

    return 0

if __name__ == "__main__":
    # Get stock code from command line argument or use default
    stock_code = sys.argv[1] if len(sys.argv) > 1 else "002067"
    sys.exit(main(stock_code))

