#!/usr/bin/env python3
"""
Detailed analysis of stocks in the latest pool record, looking for nested structures
"""

import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from data.mongodb_manager import MongoDBManager
import json

def analyze_nested_structure(data, path="", level=0):
    """
    Recursively analyze nested structure of data

    Args:
        data: The data to analyze
        path: Current path in the nested structure
        level: Current nesting level
    """
    indent = "  " * level

    if isinstance(data, dict):
        print(f"{indent}{{dict}} {path if path else 'root'}:")
        for key, value in data.items():
            new_path = f"{path}.{key}" if path else key
            if isinstance(value, (dict, list)) and value:
                analyze_nested_structure(value, new_path, level + 1)
            else:
                print(f"{indent}  {key}: {value}")
    elif isinstance(data, list):
        print(f"{indent}[list] {path if path else 'root'} (length: {len(data)}):")
        for i, item in enumerate(data[:3]):  # Only show first 3 items to avoid too much output
            new_path = f"{path}[{i}]" if path else f"[{i}]"
            if isinstance(item, (dict, list)) and item:
                analyze_nested_structure(item, new_path, level + 1)
            else:
                print(f"{indent}  [{i}]: {item}")
        if len(data) > 3:
            print(f"{indent}  ... ({len(data) - 3} more items)")
    else:
        print(f"{indent}{data}")

def check_latest_pool_stocks_detailed():
    """Detailed check of stocks in the latest pool record"""
    print("Checking stocks in the latest pool record with detailed nested structure analysis...")

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
        print(f"  Count: {latest_record.get('count', 'N/A')}")

        # Show stocks information with detailed nested structure analysis
        stocks = latest_record.get('stocks', [])
        print(f"\nStocks array analysis:")
        analyze_nested_structure(stocks, "stocks")

        # Look for any deeply nested technical analysis data
        print(f"\nAnalyzing technical analysis data in first few stocks:")
        for i, stock in enumerate(stocks[:3]):
            print(f"\n--- Stock {i+1} ({stock.get('code', 'N/A')}) ---")

            # Check for any nested technical analysis fields
            for key, value in stock.items():
                if key in ['tech_analysis', 'technical_analysis', 'technical_indicators', 'indicators']:
                    print(f"Found technical analysis field '{key}':")
                    analyze_nested_structure(value, key)
                elif isinstance(value, dict) and len(value) > 0:
                    # Check if this dict might be technical analysis data
                    if any(k in str(value.keys()).lower() for k in ['macd', 'rsi', 'ma', 'moving', 'average', 'trend']):
                        print(f"Potential technical analysis field '{key}':")
                        analyze_nested_structure(value, key)

        db_manager.close_connection()
        print("\n✓ Detailed analysis of latest pool stocks completed successfully")
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_latest_pool_stocks_detailed()
    sys.exit(0 if success else 1)

