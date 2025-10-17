"""
Direct test of Weekly Selector to verify it can filter 508 stocks
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.weekly_selector import WeeklyStockSelector
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient

# Initialize components
db_manager = MongoDBManager()
data_fetcher = AkshareClient()

print("初始化Weekly Stock Selector...")

# Create weekly selector instance
try:
    weekly_selector = WeeklyStockSelector(db_manager, data_fetcher)
    print("Weekly Selector初始化成功")

    # Check if strategies are loaded
    if weekly_selector.strategies:
        print(f"已加载 {len(weekly_selector.strategies)} 个策略:")
        for strategy in weekly_selector.strategies:
            print(f"  - {strategy.get('name', 'Unknown')}")
    else:
        print("未加载任何策略")

    # Run stock selection
    print("\n开始执行股票筛选...")
    selected_stocks, last_data_date, golden_cross_flags, scores, technical_analysis_data, strategy_results = weekly_selector.select_stocks()

    print(f"\n筛选结果:")
    print(f"筛选出的股票数量: {len(selected_stocks)}")
    print(f"最后数据日期: {last_data_date}")

    # Show first 10 stocks
    if selected_stocks:
        print(f"前10只股票: {selected_stocks[:10]}")

    # Show strategy results
    if strategy_results:
        print(f"\n各策略筛选结果:")
        for strategy_name, results in strategy_results.items():
            print(f"策略 '{strategy_name}': 筛选出 {len(results['selected_stocks'])} 只股票")
            if results['selected_stocks']:
                print(f"  股票代码: {', '.join(results['selected_stocks'][:5])}" +
                      ("..." if len(results['selected_stocks']) > 5 else ""))

    # Save results to database
    print(f"\n保存筛选结果到数据库...")
    save_result = weekly_selector.save_selected_stocks(
        stocks=selected_stocks,
        golden_cross_flags=golden_cross_flags,
        scores=scores,
        technical_analysis_data=technical_analysis_data,
        strategy_results=strategy_results
    )

    if save_result:
        print("筛选结果保存成功")
    else:
        print("筛选结果保存失败")

    print(f"\n总共筛选出 {len(selected_stocks)} 只股票")

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

print("\n测试完成")

