"""
Debug script to check all_stocks_data building process
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.weekly_selector import WeeklyStockSelector

def debug_all_stocks_data():
    """Debug the all_stocks_data building process"""

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

    print(f"\nStrategy results:")
    total_stocks = 0
    for strategy_name, (selected_stocks, selection_reasons, scores, technical_analysis_data) in strategy_results.items():
        print(f"  {strategy_name}: {len(selected_stocks)} stocks")
        total_stocks += len(selected_stocks)
    print(f"Total stocks across all strategies: {total_stocks}")

    # Now let's manually trace the all_stocks_data building process
    print("\n=== Tracing all_stocks_data building ===")

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
            print(f"No stocks selected by strategy {strategy_name}, skipping")
            continue

        # 记录策略名称
        all_strategy_names.append(strategy_name)
        total_stock_count += len(selected_stocks)

        print(f"\nProcessing strategy: {strategy_name}")
        print(f"  Selected stocks: {len(selected_stocks)}")

        # Convert stocks list to the expected format (list of dicts)
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
                print(f"  Updated existing stock {stock_code} with {strategy_name}")
            else:
                # 如果股票不存在，创建新记录
                stock_info = {
                    "code": stock_code,
                    "trend": {
                        strategy_name: {"score": rounded_score, "value": value_json}
                    },
                }
                all_stocks_data.append(stock_info)
                print(f"  Added new stock {stock_code} for {strategy_name}")

    print(f"\n=== Final all_stocks_data ===")
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

    # Check if there are any stocks with multiple strategies
    multi_strategy_stocks = 0
    for stock in all_stocks_data:
        trend_data = stock.get("trend", {})
        if len(trend_data) > 1:
            multi_strategy_stocks += 1
            print(f"  Stock {stock['code']} has {len(trend_data)} strategies: {list(trend_data.keys())}")

    print(f"\nStocks with multiple strategies: {multi_strategy_stocks}")

if __name__ == "__main__":
    debug_all_stocks_data()

