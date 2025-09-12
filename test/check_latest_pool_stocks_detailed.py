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

def check_latest_pool_stocks_detailed(stock_code="603381"):
    """Detailed check of stocks in the latest pool record"""
    print(f"Checking stocks in the latest pool record with detailed nested structure analysis for stock {stock_code}...")

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

        # Look for the specific stock
        target_stock = None
        for stock in stocks:
            if stock.get('code') == stock_code:
                target_stock = stock
                break

        if target_stock:
            print(f"\n--- Target Stock {stock_code} ---")
            analyze_nested_structure(target_stock, f"stock_{stock_code}")

            # Check for fundamental analysis data
            if 'fund' in target_stock:
                print(f"\nFundamental analysis data for {stock_code}:")
                fund_data = target_stock['fund']
                print(json.dumps(fund_data, indent=2, ensure_ascii=False))

                # Check for LLM基本面分析 data specifically
                for strategy_name, strategy_data in fund_data.items():
                    if 'LLM' in strategy_name or '基本面' in strategy_name:
                        score = strategy_data.get('score', 'N/A')
                        value = strategy_data.get('value', 'N/A')
                        print(f"\n{strategy_name}:")
                        print(f"  Score in DB: {score}")
                        print(f"  Value: {str(value)[:200]}...")

                        # Try to extract score from value
                        import re
                        if isinstance(value, str):
                            # Look for patterns like "评分: 0.65" or "score: 0.65"
                            score_matches = re.findall(r'[评评分分][:：]?\s*(\d+\.?\d*)', value)
                            if score_matches:
                                extracted_score = float(score_matches[0])
                                print(f"  Score extracted from value: {extracted_score}")
                                if isinstance(score, (int, float)) and abs(score - extracted_score) > 0.001:
                                    print(f"  ⚠️  SCORE MISMATCH: DB score={score}, Extracted score={extracted_score}")
                            else:
                                # Try general pattern for any decimal number
                                general_matches = re.findall(r'\b(\d\.\d+)\b', value)
                                for match in general_matches:
                                    try:
                                        general_score = float(match)
                                        if 0 <= general_score <= 1:  # Check if it's in 0-1 range
                                            print(f"  Potential score found in value: {general_score}")
                                            if isinstance(score, (int, float)) and abs(score - general_score) > 0.001:
                                                print(f"  ⚠️  POSSIBLE SCORE MISMATCH: DB score={score}, Found score={general_score}")
                                            break
                                    except ValueError:
                                        continue
            else:
                print(f"\nNo fundamental analysis data found for {stock_code}")
        else:
            print(f"\nTarget stock {stock_code} not found in latest pool record")

        db_manager.close_connection()
        print("\n✓ Detailed analysis of latest pool stocks completed successfully")
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    stock_code = "603381"
    if len(sys.argv) > 1:
        stock_code = sys.argv[1]

    success = check_latest_pool_stocks_detailed(stock_code)
    sys.exit(0 if success else 1)

