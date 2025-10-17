"""
Debug script to check save_trend_output_to_pool method
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.weekly_selector import WeeklyStockSelector
from data.database_operations import DatabaseOperations

def debug_save_trend_output():
    """Debug the save_trend_output_to_pool method"""

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

    # Build all_stocks_data manually
    all_stocks_data = []
    all_strategy_names = []
    total_stock_count = 0

    # Process each strategy's results
    for strategy_name, (
        selected_stocks,
        selection_reasons,
        scores,
        technical_analysis_data,
    ) in strategy_results.items():
        if not selected_stocks:
            continue

        all_strategy_names.append(strategy_name)
        total_stock_count += len(selected_stocks)

        for stock_code in selected_stocks:
            # Get score from scores dictionary
            score = 0.0
            if scores and isinstance(scores, dict):
                score = scores.get(stock_code, 0.0)

            # Normalize score
            if score is not None:
                score_float = float(score)
                if score_float > 1.0:
                    normalized_score = max(0.0, min(1.0, score_float / 100.0))
                else:
                    normalized_score = max(0.0, min(1.0, score_float))
            else:
                normalized_score = 0.0

            rounded_score = round(normalized_score, 2)

            # Create value JSON
            value_content = {
                "code": stock_code,
                "score": rounded_score,
                "selection_reason": selection_reasons.get(stock_code, ""),
                "technical_analysis": {},
                "breakout_signal": False,
                "position": 0.0,
                "signal": "观望"
            }

            import json
            value_json = json.dumps(value_content, ensure_ascii=False)

            # 查找是否已经存在该股票的记录
            existing_stock = None
            for stock in all_stocks_data:
                if stock.get('code') == stock_code:
                    existing_stock = stock
                    break

            if existing_stock:
                # 如果股票已存在，在trend字段下添加新的策略数据
                if 'trend' not in existing_stock:
                    existing_stock['trend'] = {}
                existing_stock['trend'][strategy_name] = {"score": rounded_score, "value": value_json}
            else:
                # 如果股票不存在，创建新记录
                stock_info = {
                    "code": stock_code,
                    "trend": {
                        strategy_name: {"score": rounded_score, "value": value_json}
                    },
                }
                all_stocks_data.append(stock_info)

    print(f"\n=== Before saving to database ===")
    print(f"Total stocks in all_stocks_data: {len(all_stocks_data)}")

    # Count stocks by strategy in all_stocks_data
    strategy_counts = {}
    for stock in all_stocks_data:
        trend_data = stock.get("trend", {})
        for strategy_name in trend_data.keys():
            strategy_counts[strategy_name] = strategy_counts.get(strategy_name, 0) + 1

    print(f"Stocks by strategy in all_stocks_data:")
    for strategy, count in strategy_counts.items():
        print(f"  {strategy}: {count} stocks")

    # Now let's manually trace the save_trend_output_to_pool process
    print(f"\n=== Tracing save_trend_output_to_pool ===")

    # Create DatabaseOperations instance
    db_ops = DatabaseOperations(db_manager)

    # Get the latest pool record
    pool_collection = db_manager.get_collection("pool")
    latest_pool_record = pool_collection.find_one(sort=[("_id", -1)])

    if not latest_pool_record:
        print("No existing pool record found")
        return

    print(f"Latest pool record ID: {latest_pool_record.get('_id')}")
    existing_stocks = latest_pool_record.get("stocks", [])
    print(f"Existing stocks in pool: {len(existing_stocks)}")

    # Create a map of existing stocks by code for quick lookup
    existing_stock_map = {
        stock.get("code"): i
        for i, stock in enumerate(existing_stocks)
        if stock.get("code")
    }

    print(f"Existing stock map size: {len(existing_stock_map)}")

    # Update or add trend data to existing stocks
    updated_stocks = existing_stocks[:]  # Create a copy of existing stocks
    print(f"Initial updated_stocks size: {len(updated_stocks)}")

    for new_stock in all_stocks_data:
        stock_code = new_stock.get("code")
        if stock_code in existing_stock_map:
            # Update existing stock with new trend data
            existing_index = existing_stock_map[stock_code]
            existing_stock = updated_stocks[existing_index]

            # Handle trend data merging to preserve data from multiple strategies
            if "trend" in new_stock:
                if "trend" not in existing_stock:
                    existing_stock["trend"] = {}

                # Merge trend data instead of replacing it
                for strategy_name_key, strategy_data in new_stock["trend"].items():
                    existing_stock["trend"][strategy_name_key] = strategy_data
                    print(f"  Updated existing stock {stock_code} with {strategy_name_key}")
        else:
            # Add new stock if it doesn't exist in the pool
            updated_stocks.append(new_stock)
            print(f"  Added new stock {stock_code}")

    print(f"Final updated_stocks size: {len(updated_stocks)}")

    # Count stocks by strategy in updated_stocks
    final_strategy_counts = {}
    for stock in updated_stocks:
        trend_data = stock.get("trend", {})
        for strategy_name in trend_data.keys():
            final_strategy_counts[strategy_name] = final_strategy_counts.get(strategy_name, 0) + 1

    print(f"\nStocks by strategy in updated_stocks:")
    for strategy, count in final_strategy_counts.items():
        print(f"  {strategy}: {count} stocks")

    # Now actually save to database
    print(f"\n=== Saving to database ===")

    # Get strategy ID for the first strategy
    strategy_id = None
    for strategy in strategies:
        if strategy.get("name") == all_strategy_names[0]:
            strategy_id = strategy.get("_id")
            break

    if not strategy_id:
        strategy_id = "weekly_selector_multi_strategy"

    strategy_key = strategy_id

    # Prepare additional metadata
    additional_metadata = {
        'strategy_name': ', '.join(all_strategy_names),
        'count': total_stock_count,
        'strategies_count': len(all_strategy_names),
    }

    # Save to database
    save_result = db_ops.save_trend_output_to_pool(
        strategy_key=strategy_key,
        agent_name="WeeklySelector",
        strategy_id=strategy_id,
        strategy_name="WeeklySelector_Multi",
        stocks=all_stocks_data,
        date="2024-01-01",  # Use a test date
        last_data_date="2024-01-01",
        strategy_params={},
        additional_metadata=additional_metadata,
    )

    print(f"Save result: {save_result}")

    # Check the pool data after saving
    print(f"\n=== After saving to database ===")
    latest_pool_after = pool_collection.find_one(sort=[("_id", -1)])

    if latest_pool_after:
        stocks_after = latest_pool_after.get("stocks", [])
        print(f"Total stocks in pool after save: {len(stocks_after)}")

        # Count stocks by strategy
        strategy_counts_after = {}
        for stock in stocks_after:
            trend_data = stock.get("trend", {})
            for strategy_name in trend_data.keys():
                strategy_counts_after[strategy_name] = strategy_counts_after.get(strategy_name, 0) + 1

        print(f"Stocks by strategy in pool after save:")
        for strategy, count in strategy_counts_after.items():
            print(f"  {strategy}: {count} stocks")

if __name__ == "__main__":
    debug_save_trend_output()

