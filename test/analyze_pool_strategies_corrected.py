#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to analyze the actual pool data structure and count strategies correctly
"""

import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def analyze_pool_structure():
    """Analyze the pool data structure to count actual strategies"""
    db_manager = None
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()

        # Get the latest pool record
        pool_collection = db_manager.db['pool']
        latest_pool_record = pool_collection.find_one(sort=[("_id", -1)])

        if not latest_pool_record:
            print("No records found in pool collection")
            return

        # Get stocks from the latest pool record
        pool_stocks = latest_pool_record.get("stocks", [])

        if not pool_stocks:
            print("No stocks found in latest pool record")
            return

        print(f"Found {len(pool_stocks)} stocks in the latest pool record")

        # Analyze the first stock to understand the structure
        if pool_stocks:
            first_stock = pool_stocks[0]
            print(f"\nAnalyzing structure of stock {first_stock.get('code', 'Unknown')}:")

            # Count strategies by examining fields (excluding special fields)
            strategy_count = 0
            strategy_fields = []

            for field_name, field_value in first_stock.items():
                # Skip special fields
                if field_name in ['code', 'signal', 'signals']:
                    print(f"  Skipping field '{field_name}' (special field)")
                    continue

                # Count strategies in strategy fields
                if isinstance(field_value, dict):
                    field_strategy_count = 0
                    for strategy_name, strategy_info in field_value.items():
                        if isinstance(strategy_info, dict):
                            field_strategy_count += 1

                    print(f"  Field '{field_name}': {field_strategy_count} strategies")
                    strategy_count += field_strategy_count
                    strategy_fields.append((field_name, field_strategy_count))
                else:
                    print(f"  Skipping field '{field_name}' (not a strategy field)")

            print(f"\nTotal strategies found: {strategy_count}")
            print("Strategy field breakdown:")
            for field_name, count in strategy_fields:
                print(f"  {field_name}: {count} strategies")

            # Show some example strategies
            print("\nExample strategies found:")
            shown = 0
            for field_name, field_value in first_stock.items():
                if field_name in ['code', 'signal', 'signals'] or not isinstance(field_value, dict):
                    continue

                for strategy_name, strategy_info in field_value.items():
                    if isinstance(strategy_info, dict) and shown < 5:
                        score = strategy_info.get('score', 'N/A')
                        print(f"  {field_name}_{strategy_name}: score={score}")
                        shown += 1

            return strategy_count

    except Exception as e:
        print(f"Error analyzing pool structure: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # Close connection
        if db_manager:
            db_manager.close_connection()

def count_satisfied_strategies(stock_data):
    """Count how many strategies have actual scores (are satisfied)"""
    satisfied_count = 0
    satisfied_strategies = []

    # Process all fields except special fields
    for field_name, field_value in stock_data.items():
        # Skip special fields
        if field_name in ['code', 'signal', 'signals'] or not isinstance(field_value, dict):
            continue

        # Process each strategy in the field
        for strategy_name, strategy_info in field_value.items():
            if isinstance(strategy_info, dict):
                score = strategy_info.get('score')
                # Check if score exists and is not None/empty
                if score is not None and score != '':
                    try:
                        score_float = float(score)
                        if score_float > 0:
                            satisfied_count += 1
                            satisfied_strategies.append(f"{field_name}_{strategy_name}: {score}")
                    except (ValueError, TypeError):
                        # Score is not a valid number, but it exists
                        if score:
                            satisfied_count += 1
                            satisfied_strategies.append(f"{field_name}_{strategy_name}: {score}")

    return satisfied_count, satisfied_strategies

def analyze_002067_in_pool():
    """Analyze stock 002067 in the actual pool data"""
    db_manager = None
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()

        # Get the latest pool record
        pool_collection = db_manager.db['pool']
        latest_pool_record = pool_collection.find_one(sort=[("_id", -1)])

        if not latest_pool_record:
            print("No records found in pool collection")
            return

        # Get stocks from the latest pool record
        pool_stocks = latest_pool_record.get("stocks", [])

        # Find stock 002067
        stock_002067 = None
        for stock in pool_stocks:
            if stock.get('code') == '002067':
                stock_002067 = stock
                break

        if not stock_002067:
            print("Stock 002067 not found in pool data")
            return

        print(f"\n=== Analysis for Stock 002067 ===")

        # Count total strategies in pool (from first stock), excluding 'signals'
        first_stock = pool_stocks[0]
        total_strategies = 0
        for field_name, field_value in first_stock.items():
            if field_name in ['code', 'signal', 'signals'] or not isinstance(field_value, dict):
                continue
            for strategy_name, strategy_info in field_value.items():
                if isinstance(strategy_info, dict):
                    total_strategies += 1

        print(f"Total strategies in pool (excluding 'signals'): {total_strategies}")

        # Count satisfied strategies for 002067
        satisfied_count, satisfied_list = count_satisfied_strategies(stock_002067)
        print(f"Satisfied strategies for 002067: {satisfied_count}")

        print("\nSatisfied strategies:")
        for strategy in satisfied_list:
            print(f"  {strategy}")

        # Calculate score
        sum_scores = 0
        for field_name, field_value in stock_002067.items():
            if field_name in ['code', 'signal', 'signals'] or not isinstance(field_value, dict):
                continue
            for strategy_name, strategy_info in field_value.items():
                if isinstance(strategy_info, dict):
                    score = strategy_info.get('score', 0)
                    try:
                        score_float = float(score) if score is not None else 0.0
                        sum_scores += score_float
                    except (ValueError, TypeError):
                        sum_scores += 0.0

        average_score = sum_scores / total_strategies if total_strategies > 0 else 0
        print(f"\nScore calculation:")
        print(f"  Sum of all strategy scores: {sum_scores}")
        print(f"  Total strategies: {total_strategies}")
        print(f"  Average score: {sum_scores} / {total_strategies} = {average_score:.4f}")

        # Determine signal
        if average_score > 0.7:
            signal = "买入"
        elif 0.4 <= average_score <= 0.7:
            signal = "持有"
        else:
            signal = "卖出"

        print(f"  Signal: {signal} ({average_score:.4f})")

        return {
            'total_strategies': total_strategies,
            'satisfied_strategies': satisfied_count,
            'average_score': average_score,
            'signal': signal
        }

    except Exception as e:
        print(f"Error analyzing 002067: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # Close connection
        if db_manager:
            db_manager.close_connection()

if __name__ == "__main__":
    print("=== Pool Data Structure Analysis ===")
    analyze_pool_structure()

    print("\n" + "="*50)
    analyze_002067_in_pool()

