#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Execute script to run the Enhanced Public Opinion Analysis Strategy V2
and display the actual JSON output from strategy execution.
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
from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2
import pandas as pd


def timeout_handler(signum, frame):
    """Timeout handler to prevent infinite execution"""
    raise TimeoutError("Execution timed out after 60 seconds")


def main():
    """Main function to run the strategy execution test"""
    print("=== Execute Enhanced Public Opinion Strategy ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Set timeout to prevent infinite execution
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(60)  # 60 seconds timeout

    try:
        # Initialize database manager
        print("Initializing MongoDB manager...")
        db_manager = MongoDBManager()
        print("✓ MongoDB manager initialized")

        # Initialize data fetcher
        print("Initializing Akshare client...")
        data_fetcher = AkshareClient()
        print("✓ Akshare client initialized")
        print()

        # Get strategy configuration from database
        print("Fetching strategy configuration from database...")
        strategy_config = db_manager.strategies_collection.find_one(
            {"name": "增强型舆情分析策略V2"}
        )

        if not strategy_config:
            print("✗ Enhanced Public Opinion Analysis Strategy V2 not found in database")
            return

        print("✓ Strategy configuration found")
        print(f"Strategy name: {strategy_config.get('name')}")
        print()

        # Initialize the strategy
        print("Initializing Enhanced Public Opinion Analysis Strategy V2...")
        strategy = EnhancedPublicOpinionAnalysisStrategyV2(
            name=strategy_config.get('name', 'EnhancedPublicOpinionAnalysisStrategyV2'),
            params=strategy_config.get('parameters', {}),
            db_manager=db_manager
        )
        print("✓ Strategy initialized")
        print()

        # Test with a single stock that is likely to have data
        test_stock_code = "000001"  # 上证指数作为测试
        test_stock_name = "上证指数"
        print(f"Testing with stock: {test_stock_code} ({test_stock_name})")
        print()

        # Create minimal stock data with empty DataFrame
        stock_data = {test_stock_code: pd.DataFrame()}
        print("Created empty stock data for testing")
        print()

        # Execute the strategy
        print("Executing strategy...")
        start_time = datetime.now()

        try:
            selected_stocks = strategy.execute(stock_data, "舆情分析Agent", db_manager)
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            print(f"✓ Strategy execution completed in {execution_time:.2f} seconds")
            print()

            # Display results
            print("=== Results ===")
            if not selected_stocks:
                print("No stocks were selected by the strategy.")
                return

            for i, stock in enumerate(selected_stocks):
                print(f"Stock {i+1}: {stock.get('code', 'Unknown')}")

                # Display the value (should be JSON string)
                value_str = stock.get('value', '')
                print("Value (JSON string):")
                if value_str:
                    try:
                        # Try to parse and pretty print the JSON
                        parsed_json = json.loads(value_str)
                        print(json.dumps(parsed_json, ensure_ascii=False, indent=2))
                    except json.JSONDecodeError as e:
                        # If not valid JSON, just print the string
                        print(f"JSON parsing error: {e}")
                        print(value_str)
                else:
                    print("(empty)")

                # Display the score
                score = stock.get('score', 0.0)
                print(f"Score: {score}")
                print("-" * 50)

        except Exception as e:
            print(f"✗ Error during strategy execution: {e}")
            import traceback
            traceback.print_exc()

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

