#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to debug the actual scores for stock 002067
"""

import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def debug_002067_scores():
    """Debug the actual scores for stock 002067"""
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

        print(f"=== Detailed Analysis for Stock 002067 ===")
        print(f"Stock code: {stock_002067.get('code')}")

        # Show all fields
        print("\nAll fields in stock data:")
        for field_name, field_value in stock_002067.items():
            if isinstance(field_value, dict):
                print(f"  {field_name}: [dict with {len(field_value)} items]")
            else:
                print(f"  {field_name}: {field_value}")

        # Analyze strategy fields in detail
        print("\nStrategy field details (excluding special fields):")
        sum_scores = 0
        total_strategies = 0

        for field_name, field_value in stock_002067.items():
            # Skip special fields
            if field_name in ['code', 'signal', 'signals']:
                continue

            if isinstance(field_value, dict):
                print(f"\n  Field '{field_name}':")
                field_strategy_count = 0
                field_score_sum = 0

                for strategy_name, strategy_info in field_value.items():
                    if isinstance(strategy_info, dict):
                        score = strategy_info.get('score', 'N/A')
                        value = strategy_info.get('value', 'N/A')
                        field_strategy_count += 1
                        total_strategies += 1

                        try:
                            score_float = float(score) if score is not None else 0.0
                            field_score_sum += score_float
                            sum_scores += score_float
                            print(f"    {strategy_name}: score={score} (value: {str(value)[:50]}...)")
                        except (ValueError, TypeError):
                            sum_scores += 0.0
                            print(f"    {strategy_name}: score={score} (INVALID SCORE)")

                print(f"    Field subtotal: {field_score_sum} from {field_strategy_count} strategies")

        print(f"\n=== Summary ===")
        print(f"Total strategies: {total_strategies}")
        print(f"Sum of all scores: {sum_scores}")
        if total_strategies > 0:
            average_score = sum_scores / total_strategies
            print(f"Average score: {sum_scores} / {total_strategies} = {average_score:.4f}")

            # Determine signal
            if average_score > 0.7:
                signal = "买入"
            elif 0.4 <= average_score <= 0.7:
                signal = "持有"
            else:
                signal = "卖出"

            print(f"Signal: {signal} ({average_score:.4f})")
        else:
            print("No strategies found!")

    except Exception as e:
        print(f"Error analyzing 002067: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close connection
        if db_manager:
            db_manager.close_connection()

if __name__ == "__main__":
    debug_002067_scores()

