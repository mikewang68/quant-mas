#!/usr/bin/env python3
"""
Deep search through the latest pool record's stocks for nested structures and position fields
"""

import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from data.mongodb_manager import MongoDBManager
import json

def deep_search_nested(data, target_key, path="", results=None):
    """
    Recursively search for a specific key in nested data structures

    Args:
        data: The data to search through
        target_key: The key to search for
        path: Current path in the nested structure
        results: List to store found results

    Returns:
        List of tuples (path, value) where target_key was found
    """
    if results is None:
        results = []

    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{path}.{key}" if path else key
            if key == target_key:
                results.append((new_path, value))
            if isinstance(value, (dict, list)):
                deep_search_nested(value, target_key, new_path, results)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            new_path = f"{path}[{i}]" if path else f"[{i}]"
            if isinstance(item, (dict, list)):
                deep_search_nested(item, target_key, new_path, results)

    return results

def analyze_stock_structure(stock, stock_index):
    """
    Analyze the structure of a single stock entry

    Args:
        stock: The stock data to analyze
        stock_index: Index of the stock in the stocks array
    """
    print(f"\n--- Stock {stock_index} (Code: {stock.get('code', 'N/A')}) ---")

    # Check if this stock has a position field
    if 'position' in stock:
        print(f"  Position: {stock['position']}")
    else:
        print("  Position: Not found")

    # Perform deep search for 'position' key anywhere in the stock structure
    position_results = deep_search_nested(stock, 'position')
    if len(position_results) > 1:  # More than just the top-level position
        print("  Nested positions found:")
        for path, value in position_results:
            print(f"    {path}: {value}")

    # Show all top-level keys
    print("  Top-level fields:")
    for key in stock.keys():
        value = stock[key]
        if isinstance(value, (dict, list)) and value:
            print(f"    {key}: {type(value).__name__} ({len(value) if isinstance(value, (dict, list)) else 'N/A'})")
        else:
            print(f"    {key}: {value}")

def deep_search_pool_stocks():
    """Deep search through stocks in the latest pool record"""
    print("Performing deep search through stocks in the latest pool record...")

    try:
        # Initialize database manager
        db_manager = MongoDBManager()
        print("✓ Database connection established")

        # Get pool collection
        pool_collection = db_manager.db['pool']

        # Get the latest record sorted by selection date
        latest_record = pool_collection.find_one(sort=[('selection_date', -1)])

        if not latest_record:
            print("No records found in pool collection")
            return False

        print(f"\nLatest record in pool collection:")
        print(f"  ID: {latest_record.get('_id', 'N/A')}")
        print(f"  Agent Name: {latest_record.get('agent_name', 'N/A')}")
        print(f"  Strategy Name: {latest_record.get('strategy_name', 'N/A')}")
        print(f"  Selection Date: {latest_record.get('selection_date', 'N/A')}")
        print(f"  Total Stocks: {latest_record.get('count', 'N/A')}")

        # Get stocks
        stocks = latest_record.get('stocks', [])
        print(f"\nAnalyzing {len(stocks)} stocks...")

        # Count stocks with position field
        stocks_with_position = [s for s in stocks if 'position' in s]
        print(f"Stocks with position field: {len(stocks_with_position)}")

        # Analyze stocks with position
        if stocks_with_position:
            print(f"\n--- Stocks with Position Field ---")
            for i, stock in enumerate(stocks_with_position[:10]):  # Show first 10
                analyze_stock_structure(stock, f"with_position_{i+1}")

            if len(stocks_with_position) > 10:
                print(f"  ... and {len(stocks_with_position) - 10} more stocks with position")

        # Analyze a sample of stocks without position to check for nested structures
        stocks_without_position = [s for s in stocks if 'position' not in s]
        if stocks_without_position:
            print(f"\n--- Sample Stocks without Position Field ---")
            sample_size = min(5, len(stocks_without_position))
            for i, stock in enumerate(stocks_without_position[:sample_size]):
                analyze_stock_structure(stock, f"without_position_{i+1}")

        # Perform deep search for 'position' key in all stocks
        print(f"\n--- Deep Search for 'position' Key ---")
        all_position_results = []
        for i, stock in enumerate(stocks):
            position_results = deep_search_nested(stock, 'position')
            if position_results:
                all_position_results.extend([(i, path, value) for path, value in position_results])

        print(f"Total position references found through deep search: {len(all_position_results)}")

        # Show details of deep search results
        if all_position_results:
            print("Position references found:")
            for stock_idx, path, value in all_position_results[:20]:  # Show first 20
                stock_code = stocks[stock_idx].get('code', 'N/A')
                print(f"  Stock {stock_idx} ({stock_code}) - {path}: {value}")

            if len(all_position_results) > 20:
                print(f"  ... and {len(all_position_results) - 20} more position references")

        # Check for other nested structures in a sample of stocks
        print(f"\n--- Checking for Nested Technical Analysis Structures ---")
        sample_stocks = stocks[:10]  # Check first 10 stocks
        for i, stock in enumerate(sample_stocks):
            # Look for any nested structures that might contain technical indicators
            nested_keys = []
            for key, value in stock.items():
                if isinstance(value, dict) and value:
                    nested_keys.append(key)
                    # Check if this dict has nested technical analysis data
                    tech_results = deep_search_nested(value, 'technical')
                    if tech_results:
                        print(f"  Stock {i} ({stock.get('code', 'N/A')}) - Found 'technical' in {key}:")
                        for path, value in tech_results[:3]:  # Show first 3
                            print(f"    {path}: {str(value)[:100]}...")  # Truncate long values

            if nested_keys:
                print(f"  Stock {i} ({stock.get('code', 'N/A')}) - Nested keys: {nested_keys}")

        db_manager.close_connection()
        print("\n✓ Deep search of latest pool stocks completed successfully")
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = deep_search_pool_stocks()
    sys.exit(0 if success else 1)

