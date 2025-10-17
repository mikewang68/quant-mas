"""
Check pool data to verify multiple strategies are correctly saved
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def check_pool_data():
    """Check pool data for multiple strategy verification"""

    print("Checking Pool Data for Multiple Strategies...")

    # Initialize MongoDB manager
    db_manager = MongoDBManager()
    pool_collection = db_manager.db["pool"]

    # Get the latest pool record
    latest_record = pool_collection.find_one(sort=[("_id", -1)])

    if not latest_record:
        print("No pool record found")
        return False

    print(f"Latest pool record _id: {latest_record.get('_id')}")
    print(f"Strategy keys count: {len(latest_record.get('strategy_key', []))}")
    print(f"Strategy names count: {len(latest_record.get('strategy_name', []))}")
    print(f"Total stocks: {latest_record.get('count', 0)}")

    strategy_names = latest_record.get('strategy_name', [])
    print(f"\nStrategy names in pool: {strategy_names}")

    # Check stocks data
    stocks = latest_record.get('stocks', [])
    print(f"\nTotal stocks in record: {len(stocks)}")

    # Analyze strategy distribution across stocks
    strategy_distribution = {}
    for stock in stocks:
        trend_data = stock.get('trend', {})
        for strategy_name in trend_data.keys():
            strategy_distribution[strategy_name] = strategy_distribution.get(strategy_name, 0) + 1

    print(f"\nStrategy Distribution (number of stocks per strategy):")
    for strategy_name, count in strategy_distribution.items():
        print(f"  {strategy_name}: {count} stocks")

    # Check if any stock has multiple strategies
    multi_strategy_stocks = []
    for stock in stocks:
        trend_data = stock.get('trend', {})
        if len(trend_data) > 1:
            multi_strategy_stocks.append(stock.get('code'))

    print(f"\nStocks with multiple strategies: {len(multi_strategy_stocks)}")
    if multi_strategy_stocks:
        print(f"  Sample: {multi_strategy_stocks[:5]}")

    # Show detailed example of a stock with multiple strategies
    if multi_strategy_stocks:
        sample_stock_code = multi_strategy_stocks[0]
        for stock in stocks:
            if stock.get('code') == sample_stock_code:
                print(f"\nDetailed example - Stock {sample_stock_code}:")
                trend_data = stock.get('trend', {})
                for strategy_name, strategy_data in trend_data.items():
                    print(f"  {strategy_name}: score={strategy_data.get('score')}")
                break

    return True

if __name__ == "__main__":
    try:
        success = check_pool_data()
        if success:
            print("\n✓ Pool data check completed successfully")
        else:
            print("\n✗ Pool data check failed")
    except Exception as e:
        print(f"\n✗ Error checking pool data: {e}")
        import traceback
        traceback.print_exc()

