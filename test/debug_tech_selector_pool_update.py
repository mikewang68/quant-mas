#!/usr/bin/env python3
"""
Debug script for TechnicalStockSelector pool update issue
"""

import sys
import os
from datetime import datetime

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.technical_selector import TechnicalStockSelector

def debug_pool_update():
    """Debug the pool update process"""
    print("Debugging TechnicalStockSelector pool update...")

    # Initialize components
    db_manager = MongoDBManager()
    data_fetcher = AkshareClient()

    try:
        # Initialize selector
        selector = TechnicalStockSelector(db_manager, data_fetcher)

        print(f"Loaded {len(selector.strategy_instances)} strategy instances")
        for i, strategy in enumerate(selector.strategy_instances):
            print(f"  Strategy {i}: {strategy.name}")

        if not selector.strategy_instances:
            print("ERROR: No strategy instances loaded!")
            return False

        # Check pool collection
        pool_collection = db_manager.db["pool"]
        latest_pool_record = pool_collection.find_one(sort=[("selection_date", -1)])

        if not latest_pool_record:
            print("ERROR: No records found in pool collection")
            return False

        print(f"Found latest pool record with ID: {latest_pool_record.get('_id')}")
        print(f"Selection date: {latest_pool_record.get('selection_date')}")

        # Extract stock codes
        pool_stocks = latest_pool_record.get("stocks", [])
        stock_codes = [stock.get("code") for stock in pool_stocks if stock.get("code")]

        print(f"Pool contains {len(pool_stocks)} stocks")
        print(f"Stock codes: {stock_codes[:5]}...")  # Show first 5

        if not stock_codes:
            print("ERROR: No stock codes found in latest pool record")
            return False

        # Get standard format data
        print("Getting standard data...")
        stock_data = selector.get_standard_data(stock_codes)
        print(f"Retrieved data for {len(stock_data)} stocks")

        if not stock_data:
            print("ERROR: No stock data available for analysis")
            return False

        # Execute strategies
        print("Executing strategies...")
        all_selected_stocks = []
        for i, strategy_instance in enumerate(selector.strategy_instances):
            try:
                strategy_name = selector.strategy_names[i] if i < len(selector.strategy_names) else f"Strategy_{i}"
                print(f"Executing strategy: {strategy_name}")

                selected_stocks = strategy_instance.execute(
                    stock_data, "技术分析Agent", db_manager
                )

                print(f"Strategy {strategy_name} returned {len(selected_stocks)} stocks")

                # Add strategy identifier to each selected stock
                for stock in selected_stocks:
                    stock['strategy_name'] = strategy_name
                    all_selected_stocks.append(stock)

                    # Print sample data for debugging
                    if len(all_selected_stocks) <= 3:  # Show first 3 stocks
                        print(f"  Sample stock: {stock}")

            except Exception as e:
                strategy_name = selector.strategy_names[i] if i < len(selector.strategy_names) else f"Strategy_{i}"
                print(f"ERROR executing strategy {strategy_name}: {e}")
                import traceback
                traceback.print_exc()

        print(f"Total selected stocks: {len(all_selected_stocks)}")

        if not all_selected_stocks:
            print("WARNING: No stocks selected by any strategy")
            # Let's check what the strategies returned
            return False

        # Now test the update function
        print("Testing update_latest_pool_record...")
        success = selector.update_latest_pool_record(all_selected_stocks)

        if success:
            print("Pool update completed successfully")

            # Verify the update
            updated_pool_record = pool_collection.find_one({"_id": latest_pool_record["_id"]})
            if updated_pool_record:
                updated_stocks = updated_pool_record.get("stocks", [])
                print(f"Updated pool has {len(updated_stocks)} stocks")

                # Check if any stocks have tech data
                stocks_with_tech = [s for s in updated_stocks if "tech" in s and s["tech"]]
                print(f"Stocks with tech data: {len(stocks_with_tech)}")

                if stocks_with_tech:
                    print("Sample stocks with tech data:")
                    for i, stock in enumerate(stocks_with_tech[:3]):
                        print(f"  {i+1}. {stock['code']}: {stock['tech']}")
                else:
                    print("ERROR: No stocks have tech data after update!")
                    # Let's check what's in the all_selected_stocks
                    print("Selected stocks data:")
                    for i, stock in enumerate(all_selected_stocks[:5]):
                        print(f"  {i+1}. {stock}")
            else:
                print("ERROR: Could not retrieve updated pool record")
        else:
            print("ERROR: Pool update failed")

        return success

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db_manager.close_connection()

def main():
    """Main function"""
    print("Starting TechnicalStockSelector pool update debug...")

    success = debug_pool_update()

    if success:
        print("\n✓ Debug completed successfully")
    else:
        print("\n✗ Debug failed")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())

