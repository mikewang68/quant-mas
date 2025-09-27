#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to find and display the Signal Generation V1 Strategy results for stock 002067
"""

import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def find_002067_results():
    """Find and display results for stock 002067"""
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

        print(f"=== Signal Generation V1 Strategy Results for Stock 002067 ===")
        print(f"Stock code: {stock_002067.get('code')}")

        # Check if signals field exists
        if 'signals' in stock_002067:
            signals = stock_002067['signals']
            print(f"\nSignals field exists with {len(signals)} entries")

            # Look for our strategy specifically
            if '信号生成V1' in signals:
                strategy_result = signals['信号生成V1']
                print(f"\n--- 信号生成V1 Strategy Result ---")
                print(f"Score: {strategy_result.get('score', 'N/A')}")
                print(f"Value: {strategy_result.get('value', 'N/A')}")

                value_details = strategy_result.get('value', {})
                if value_details:
                    print(f"Count: {value_details.get('count', 'N/A')}")
                    print(f"Score Calculation: {value_details.get('score_calc', 'N/A')}")
                    print(f"Signal Calculation: {value_details.get('signal_calc', 'N/A')}")
                    print(f"AI Score: {value_details.get('score_ai', 'N/A')}")
                    print(f"AI Signal: {value_details.get('signal_ai', 'N/A')}")
            else:
                print("信号生成V1 strategy result not found in signals field")
        else:
            print("No signals field found in stock data")

        # Show all strategy scores for context
        print(f"\n--- All Strategy Scores for Context ---")
        total_score = 0
        strategy_count = 0

        for field_name, field_value in stock_002067.items():
            if field_name in ['code', 'signal', 'signals'] or not isinstance(field_value, dict):
                continue

            print(f"\nField '{field_name}':")
            for strategy_name, strategy_info in field_value.items():
                if isinstance(strategy_info, dict):
                    score = strategy_info.get('score', 'N/A')
                    try:
                        score_float = float(score) if score != 'N/A' else 0
                        total_score += score_float
                        strategy_count += 1
                        print(f"  {strategy_name}: {score}")
                    except (ValueError, TypeError):
                        strategy_count += 1
                        print(f"  {strategy_name}: {score} (Invalid)")

        print(f"\n--- Summary ---")
        print(f"Total strategies counted: {strategy_count}")
        if strategy_count > 0:
            average_score = total_score / strategy_count
            print(f"Sum of scores: {total_score}")
            print(f"Average score: {average_score:.4f}")

            # Determine signal
            if average_score > 0.7:
                signal = "买入"
            elif 0.4 <= average_score <= 0.7:
                signal = "持有"
            else:
                signal = "卖出"

            print(f"Calculated signal: {signal}")

    except Exception as e:
        print(f"Error finding 002067 results: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close connection
        if db_manager:
            db_manager.close_connection()

if __name__ == "__main__":
    find_002067_results()

