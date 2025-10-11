#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to run the Public Opinion Selector agent and display the JSON output
from the Enhanced Public Opinion Analysis Strategy V2.
"""

import sys
import os
import json
import signal
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.public_opinion_selector import PublicOpinionStockSelector


def timeout_handler(signum, frame):
    """Timeout handler to prevent infinite execution"""
    raise TimeoutError("Execution timed out after 30 seconds")


def main():
    """Main function to run the public opinion selector test"""
    print("=== Public Opinion Selector JSON Output Test ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Set timeout to prevent infinite execution
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # 30 seconds timeout

    try:
        # Initialize database manager
        print("Initializing MongoDB manager...")
        db_manager = MongoDBManager()
        print("✓ MongoDB manager initialized")

        # Initialize data fetcher
        print("Initializing Akshare client...")
        data_fetcher = AkshareClient()
        print("✓ Akshare client initialized")

        # Initialize the public opinion selector
        print("Initializing Public Opinion Stock Selector...")
        selector = PublicOpinionStockSelector(
            db_manager=db_manager,
            data_fetcher=data_fetcher,
            name="TestPublicOpinionSelector"
        )
        print("✓ Public Opinion Stock Selector initialized")
        print()

        # Show loaded strategies
        print("Loaded strategies:")
        for i, (name, file, class_name) in enumerate(zip(
            selector.strategy_names,
            selector.strategy_files,
            selector.strategy_class_names
        )):
            print(f"  {i+1}. Name: {name}")
            print(f"     File: {file}")
            print(f"     Class: {class_name}")
        print()

        # Get stock codes from the latest pool record
        print("Fetching stock codes from latest pool record...")
        pool_collection = db_manager.db["pool"]
        latest_pool_record = pool_collection.find_one(sort=[("_id", -1)])

        if not latest_pool_record:
            print("✗ No records found in pool collection")
            return

        pool_stocks = latest_pool_record.get("stocks", [])
        stock_codes = [stock.get("code") for stock in pool_stocks if stock.get("code")]

        if not stock_codes:
            print("✗ No stock codes found in latest pool record")
            return

        print(f"✓ Found {len(stock_codes)} stocks in pool")
        print(f"Stock codes: {', '.join(stock_codes[:5])}{'...' if len(stock_codes) > 5 else ''}")
        print()

        # Get standard format data
        print("Getting standard format data...")
        stock_data = selector.get_standard_data(stock_codes)
        print(f"✓ Retrieved data for {len(stock_data)} stocks")
        print()

        # Execute all dynamically loaded strategies
        print("Executing strategies...")
        all_selected_stocks = []
        for i, strategy_instance in enumerate(selector.strategy_instances):
            try:
                strategy_name = selector.strategy_names[i] if i < len(selector.strategy_names) else f"Strategy_{i}"
                print(f"  Executing strategy: {strategy_name}")

                selected_stocks = strategy_instance.execute(
                    stock_data, "舆情分析Agent", db_manager
                )

                # Add strategy identifier to each selected stock
                for stock in selected_stocks:
                    stock['strategy_name'] = strategy_name
                    all_selected_stocks.append(stock)

                print(f"    Selected {len(selected_stocks)} stocks")

            except Exception as e:
                strategy_name = selector.strategy_names[i] if i < len(selector.strategy_names) else f"Strategy_{i}"
                print(f"    ✗ Error executing strategy {strategy_name}: {e}")

        print(f"✓ Strategies execution completed. Total selected stocks: {len(all_selected_stocks)}")
        print()

        # Display JSON outputs
        print("=== JSON Output Display ===")
        if not all_selected_stocks:
            print("No stocks were selected by the strategies.")
            return

        for i, stock in enumerate(all_selected_stocks):
            print(f"Stock {i+1}: {stock.get('code', 'Unknown')}")
            print(f"Strategy: {stock.get('strategy_name', 'Unknown')}")

            # Display the value (should be JSON string)
            value_str = stock.get('value', '')
            print("Value (JSON string):")
            if value_str:
                try:
                    # Try to parse and pretty print the JSON
                    parsed_json = json.loads(value_str)
                    print(json.dumps(parsed_json, ensure_ascii=False, indent=2))
                except json.JSONDecodeError:
                    # If not valid JSON, just print the string
                    print(value_str)
            else:
                print("(empty)")

            # Display the score
            score = stock.get('score', 0.0)
            print(f"Score: {score}")
            print("-" * 50)

    except TimeoutError:
        print("✗ Execution timed out")
    except Exception as e:
        print(f"✗ Error during execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cancel the alarm
        signal.alarm(0)

    print("\n=== Test Completed ===")


if __name__ == "__main__":
    main()

