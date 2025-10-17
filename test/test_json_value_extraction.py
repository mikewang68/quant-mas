"""
测试JSON值提取和传递流程
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.weekly_selector import WeeklyStockSelector
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_json_value_extraction():
    """测试JSON值提取和传递流程"""
    try:
        # 创建数据库管理器和数据获取器
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # 创建Weekly Selector实例
        weekly_selector = WeeklyStockSelector(db_manager, data_fetcher)

        # 检查策略配置
        print("=== 检查策略配置 ===")
        print(f"加载的策略数量: {len(weekly_selector.strategies)}")
        for strategy_info in weekly_selector.strategies:
            print(f"策略名称: {strategy_info['name']}")
            print(f"策略参数: {strategy_info['params']}")

        # 测试少量股票
        test_stocks = ['000001', '000002', '000858']  # 平安银行, 万科A, 五粮液

        print(f"\n=== 测试股票数据获取 ===")
        stock_data = weekly_selector.get_standard_data(test_stocks)
        print(f"成功获取数据的股票数量: {len(stock_data)}")

        # 测试策略执行
        print(f"\n=== 测试策略执行 ===")
        for strategy_info in weekly_selector.strategies:
            strategy_name = strategy_info['name']
            strategy_instance = strategy_info['instance']

            print(f"\n测试策略: {strategy_name}")

            for code in test_stocks:
                if code in stock_data:
                    k_data = stock_data[code]
                    if not k_data.empty:
                        try:
                            # 执行策略
                            result = weekly_selector._execute_strategy_for_instance(
                                code, k_data, strategy_instance, strategy_name
                            )

                            if result:
                                print(f"  股票 {code}:")
                                print(f"    是否满足条件: {result.get('meets_criteria', False)}")
                                print(f"    分数: {result.get('score', 0.0)}")
                                print(f"    JSON值类型: {type(result.get('json_value', ''))}")
                                print(f"    JSON值长度: {len(str(result.get('json_value', '')))}")

                                # 检查JSON值内容
                                json_value = result.get('json_value', '')
                                if json_value:
                                    print(f"    JSON值预览: {json_value[:100]}...")
                            else:
                                print(f"  股票 {code}: 无结果")

                        except Exception as e:
                            print(f"  股票 {code}: 执行错误 - {e}")
                    else:
                        print(f"  股票 {code}: 无数据")
                else:
                    print(f"  股票 {code}: 未找到数据")

        # 测试完整的选择流程
        print(f"\n=== 测试完整选择流程 ===")
        strategy_results = weekly_selector.select_stocks()

        print(f"策略结果数量: {len(strategy_results)}")
        for strategy_name, result in strategy_results.items():
            selected_stocks = result[0]
            scores = result[1]
            json_values = result[2]

            print(f"\n策略: {strategy_name}")
            print(f"  选中股票数量: {len(selected_stocks)}")
            print(f"  分数字典大小: {len(scores)}")
            print(f"  JSON值字典大小: {len(json_values)}")

            # 检查JSON值
            if json_values:
                for code, json_value in list(json_values.items())[:3]:  # 只显示前3个
                    print(f"    股票 {code}:")
                    print(f"      分数: {scores.get(code, 0.0)}")
                    print(f"      JSON值类型: {type(json_value)}")
                    print(f"      JSON值长度: {len(str(json_value))}")
                    if json_value:
                        print(f"      JSON值预览: {json_value[:100]}...")

        # 测试保存到数据库
        print(f"\n=== 测试保存到数据库 ===")
        save_result = weekly_selector.save_selected_stocks(strategy_results)
        print(f"保存结果: {save_result}")

        if save_result:
            # 检查数据库中的记录
            pool_data = db_manager.find("pool", {})
            print(f"\n数据库pool集合记录数量: {len(pool_data)}")

            # 查找最新的记录
            if pool_data:
                latest_record = max(pool_data, key=lambda x: x.get('_id'))
                print(f"最新记录ID: {latest_record.get('_id')}")
                print(f"策略键: {latest_record.get('strategy_key')}")

                # 检查trend字段
                if 'trend' in latest_record:
                    trend_data = latest_record['trend']
                    print(f"趋势数据股票数量: {len(trend_data)}")

                    # 检查前几个股票的JSON值
                    for code, strategy_data in list(trend_data.items())[:3]:
                        print(f"\n股票 {code}:")
                        for strategy_name, data in strategy_data.items():
                            print(f"  策略 {strategy_name}:")
                            print(f"    分数: {data.get('score', 0.0)}")
                            print(f"    值类型: {type(data.get('value', ''))}")
                            value = data.get('value', '')
                            if value:
                                print(f"    值长度: {len(str(value))}")
                                print(f"    值预览: {str(value)[:100]}...")

        print(f"\n=== 测试完成 ===")
        return True

    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_json_value_extraction()
    print(f"\n测试结果: {'成功' if success else '失败'}")

