"""
调试程序：检查Weekly Selector中value字段为空的原因
"""

import sys
import os

# Add project root to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.weekly_selector import WeeklyStockSelector
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient


def debug_value_field_issue():
    """
    调试value字段为空的问题
    """
    print("=== 调试value字段为空的问题 ===")

    try:
        # 初始化数据库管理器和数据获取器
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # 创建Weekly Selector实例
        selector = WeeklyStockSelector(db_manager, data_fetcher)

        print(f"加载的策略数量: {len(selector.strategies)}")
        for strategy_info in selector.strategies:
            print(f"策略: {strategy_info['name']}")
            print(f"  参数: {strategy_info['params']}")

        # 测试选择股票
        print("\n执行股票选择...")
        strategy_results = selector.select_stocks("2025-10-15")

        print(f"\n策略结果数量: {len(strategy_results)}")

        # 分析策略结果中的value字段
        for strategy_name, strategy_result in strategy_results.items():
            print(f"\n策略: {strategy_name}")

            if len(strategy_result) >= 3:
                selected_stocks = strategy_result[0]
                scores = strategy_result[1]
                json_values = strategy_result[2]

                print(f"  选中的股票数量: {len(selected_stocks)}")
                print(f"  分数字典大小: {len(scores) if scores else 0}")
                print(f"  JSON值字典大小: {len(json_values) if json_values else 0}")

                # 检查前几个股票的value字段
                for i, stock_code in enumerate(selected_stocks[:3]):
                    score = scores.get(stock_code, "N/A") if scores else "N/A"
                    json_value = json_values.get(stock_code, "N/A") if json_values else "N/A"

                    print(f"    股票 {stock_code}:")
                    print(f"      分数: {score}")
                    print(f"      JSON值类型: {type(json_value).__name__}")
                    print(f"      JSON值长度: {len(json_value) if isinstance(json_value, str) else 'N/A'}")
                    if isinstance(json_value, str) and len(json_value) > 0:
                        print(f"      JSON值内容(前100字符): {json_value[:100]}...")
                    else:
                        print(f"      JSON值内容: {json_value}")

        # 测试保存方法
        print("\n测试保存方法...")
        save_result = selector.save_selected_stocks(strategy_results, "2025-10-15")
        print(f"保存结果: {save_result}")

        # 检查保存后的数据
        print("\n检查保存后的数据...")
        pool_collection = db_manager.get_collection('pool')
        latest_doc = pool_collection.find_one(sort=[("_id", -1)])

        if latest_doc:
            print(f"最新文档ID: {latest_doc.get('_id')}")
            stocks = latest_doc.get('stocks', [])
            print(f"保存的股票数量: {len(stocks)}")

            # 检查前几个股票的value字段
            for i, stock in enumerate(stocks[:3]):
                print(f"\n股票 {stock.get('code')}:")
                if 'trend' in stock:
                    for strategy_name, strategy_data in stock['trend'].items():
                        print(f"  策略 '{strategy_name}':")
                        print(f"    分数: {strategy_data.get('score')}")
                        value = strategy_data.get('value', '')
                        print(f"    值类型: {type(value).__name__}")
                        print(f"    值长度: {len(value) if isinstance(value, str) else 'N/A'}")
                        if isinstance(value, str) and len(value) > 0:
                            print(f"    值内容(前100字符): {value[:100]}...")
                        else:
                            print(f"    值内容: {value}")

    except Exception as e:
        print(f"调试过程中出错: {e}")
        import traceback
        traceback.print_exc()


def check_strategy_execution():
    """
    检查策略执行过程
    """
    print("\n=== 检查策略执行过程 ===")

    try:
        # 初始化数据库管理器和数据获取器
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # 创建Weekly Selector实例
        selector = WeeklyStockSelector(db_manager, data_fetcher)

        # 获取一些股票数据
        all_codes = db_manager.get_stock_codes()
        if not all_codes:
            all_codes = data_fetcher.get_stock_list()

        test_codes = all_codes[:10]  # 只测试前10个股票
        stock_data = selector.get_standard_data(test_codes)

        print(f"获取到 {len(stock_data)} 个股票的数据")

        # 测试第一个策略的执行
        if selector.strategies:
            strategy_info = selector.strategies[0]
            strategy_instance = strategy_info['instance']
            strategy_name = strategy_info['name']

            print(f"\n测试策略: {strategy_name}")

            # 测试第一个股票
            for code, k_data in list(stock_data.items())[:3]:
                print(f"\n测试股票 {code}:")
                try:
                    # 直接调用策略的analyze方法
                    result = strategy_instance.analyze(k_data, code=code)
                    print(f"  策略执行结果: {result}")
                    print(f"  结果类型: {type(result)}")
                    print(f"  结果长度: {len(result) if hasattr(result, '__len__') else 'N/A'}")

                    if isinstance(result, tuple) and len(result) >= 3:
                        meets_criteria, score, value = result
                        print(f"  符合条件: {meets_criteria}")
                        print(f"  分数: {score}")
                        print(f"  值类型: {type(value).__name__}")
                        print(f"  值长度: {len(value) if isinstance(value, str) else 'N/A'}")
                        if isinstance(value, str) and len(value) > 0:
                            print(f"  值内容(前100字符): {value[:100]}...")
                        else:
                            print(f"  值内容: {value}")
                    else:
                        print(f"  意外的结果格式: {result}")

                except Exception as e:
                    print(f"  策略执行出错: {e}")

    except Exception as e:
        print(f"检查策略执行过程时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_value_field_issue()
    check_strategy_execution()

