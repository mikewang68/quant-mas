"""
Debug script to capture the exact error in save_selected_stocks
"""
import sys
import os
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.weekly_selector import WeeklyStockSelector

def debug_save_error():
    """Debug the save error with detailed traceback"""

    # Initialize components
    db_manager = MongoDBManager()
    data_fetcher = AkshareClient()

    # Find the specific strategies
    strategies = db_manager.get_strategies()
    target_strategies = [
        "趋势-跟踪策略（稳健型）",
        "趋势-放量突破策略（强势股捕捉）",
        "趋势-回踩低吸型策略（抄底型）"
    ]

    strategy_ids = []
    for strategy in strategies:
        if strategy.get("name") in target_strategies:
            strategy_ids.append(str(strategy.get("_id")))

    # Create selector with specific strategies
    selector = WeeklyStockSelector(db_manager, data_fetcher, strategy_ids)

    # Run selection
    print("Running stock selection...")
    strategy_results = selector.select_stocks()

    print(f"\nStrategy results structure: {type(strategy_results)}")

    if isinstance(strategy_results, dict):
        print(f"Number of strategies in results: {len(strategy_results)}")
        for strategy_name, (selected_stocks, selection_reasons, scores, technical_analysis_data) in strategy_results.items():
            print(f"  {strategy_name}: {len(selected_stocks)} stocks")

    # Save results with detailed error handling
    print("\nSaving results to database...")
    try:
        save_result = selector.save_selected_stocks(strategy_results)
        print(f"Save result: {save_result}")
    except Exception as e:
        print(f"ERROR during save: {e}")
        print("\nFull traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_save_error()

