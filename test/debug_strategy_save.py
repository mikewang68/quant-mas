"""
Debug script to check why only 68 stocks are being saved instead of 232
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.weekly_selector import WeeklyStockSelector

def debug_strategy_save():
    """Debug the strategy save issue"""

    # Initialize components
    db_manager = MongoDBManager()
    data_fetcher = AkshareClient()

    # Create weekly selector
    selector = WeeklyStockSelector(db_manager, data_fetcher)

    # Get all strategies from database
    strategies = db_manager.get_strategies()
    print(f"Total strategies in database: {len(strategies)}")

    # Find the specific strategies
    target_strategies = [
        "趋势-跟踪策略（稳健型）",
        "趋势-放量突破策略（强势股捕捉）",
        "趋势-回踩低吸型策略（抄底型）"
    ]

    strategy_ids = []
    for strategy in strategies:
        if strategy.get("name") in target_strategies:
            print(f"Found strategy: {strategy.get('name')} - ID: {strategy.get('_id')}")
            strategy_ids.append(str(strategy.get("_id")))

    print(f"Target strategy IDs: {strategy_ids}")

    # Create selector with specific strategies
    selector_with_target = WeeklyStockSelector(db_manager, data_fetcher, strategy_ids)

    print(f"Loaded strategies: {len(selector_with_target.strategies)}")
    for strategy_info in selector_with_target.strategies:
        print(f"  - {strategy_info['name']}")

    # Run selection
    print("\nRunning stock selection...")
    strategy_results = selector_with_target.select_stocks()

    print(f"\nStrategy results structure: {type(strategy_results)}")

    if isinstance(strategy_results, dict):
        print(f"Number of strategies in results: {len(strategy_results)}")
        for strategy_name, (selected_stocks, selection_reasons, scores, technical_analysis_data) in strategy_results.items():
            print(f"  {strategy_name}: {len(selected_stocks)} stocks")

            # Check if selection_reasons is properly populated
            if selection_reasons:
                print(f"    Selection reasons type: {type(selection_reasons)}")
                print(f"    Selection reasons count: {len(selection_reasons)}")
            else:
                print(f"    WARNING: No selection reasons found for {strategy_name}")

    # Save results
    print("\nSaving results to database...")
    save_result = selector_with_target.save_selected_stocks(strategy_results)
    print(f"Save result: {save_result}")

    # Check the pool data
    print("\nChecking pool data...")
    pool_collection = db_manager.get_collection("pool")
    latest_pool = pool_collection.find_one(sort=[("_id", -1)])

    if latest_pool:
        stocks = latest_pool.get("stocks", [])
        print(f"Total stocks in pool: {len(stocks)}")

        # Count stocks by strategy
        strategy_counts = {}
        for stock in stocks:
            trend_data = stock.get("trend", {})
            for strategy_name in trend_data.keys():
                strategy_counts[strategy_name] = strategy_counts.get(strategy_name, 0) + 1

        print(f"Stocks by strategy in pool:")
        for strategy, count in strategy_counts.items():
            print(f"  {strategy}: {count} stocks")

if __name__ == "__main__":
    debug_strategy_save()

