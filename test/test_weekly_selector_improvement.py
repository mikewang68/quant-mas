"""
测试程序：验证Weekly Selector写入程序的改进
"""

import sys
import os

# Add project root to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.weekly_selector import WeeklyStockSelector
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient


def test_weekly_selector_save_method():
    """
    测试Weekly Selector的保存方法
    """
    print("=== 测试Weekly Selector保存方法 ===")

    try:
        # 初始化数据库管理器和数据获取器
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # 创建Weekly Selector实例
        selector = WeeklyStockSelector(db_manager, data_fetcher)

        # 模拟策略结果数据
        mock_strategy_results = {
            "策略1": (
                ["000001", "000002"],  # 选中的股票代码
                {"000001": 0.85, "000002": 0.72},  # 分数
                {
                    "000001": '{"score": 0.85, "reason": "符合条件", "details": "技术指标良好"}',
                    "000002": '{"score": 0.72, "reason": "符合条件", "details": "基本面良好"}'
                }  # JSON值
            ),
            "策略2": (
                ["000001", "000003"],
                {"000001": 0.90, "000003": 0.68},
                {
                    "000001": '{"score": 0.90, "reason": "趋势向上", "details": "突破阻力位"}',
                    "000003": '{"score": 0.68, "reason": "符合条件", "details": "成交量放大"}'
                }
            )
        }

        # 测试保存方法
        print("\n测试保存方法...")
        result = selector.save_selected_stocks(mock_strategy_results, "2025-10-15")

        if result:
            print("✅ 保存方法执行成功")
        else:
            print("❌ 保存方法执行失败")

        # 验证保存的数据
        print("\n验证保存的数据...")
        pool_collection = db_manager.get_collection('pool')
        latest_doc = pool_collection.find_one(sort=[("_id", -1)])

        if latest_doc:
            print(f"最新文档ID: {latest_doc.get('_id')}")
            print(f"策略名称: {latest_doc.get('strategy_name')}")
            print(f"股票数量: {latest_doc.get('count')}")

            stocks = latest_doc.get('stocks', [])
            print(f"实际保存的股票数量: {len(stocks)}")

            # 检查股票数据结构
            for stock in stocks[:2]:  # 只检查前2个股票
                print(f"\n股票 {stock.get('code')}:")
                if 'trend' in stock:
                    print(f"  趋势策略数量: {len(stock['trend'])}")
                    for strategy_name, strategy_data in stock['trend'].items():
                        print(f"    策略 '{strategy_name}':")
                        print(f"      分数: {strategy_data.get('score')}")
                        print(f"      值类型: {type(strategy_data.get('value')).__name__}")

        else:
            print("❌ 未找到保存的文档")

    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


def analyze_current_implementation():
    """
    分析当前实现的问题
    """
    print("\n=== 分析当前实现的问题 ===")

    print("\n1. 当前实现的问题:")
    print("   - 缺少agent_name字段")
    print("   - 缺少strategy_id字段")
    print("   - 缺少selection_date字段")
    print("   - 缺少last_data_date字段")
    print("   - 缺少strategy_params字段")

    print("\n2. 建议的改进:")
    print("   - 添加缺失的字段以符合pool数据集的标准结构")
    print("   - 确保所有字段都有适当的默认值")
    print("   - 改进错误处理和日志记录")


def create_improved_save_method():
    """
    创建改进的保存方法
    """
    print("\n=== 改进的保存方法代码 ===")

    improved_code = '''
def save_selected_stocks_improved(
    self,
    strategy_results: Dict[str, Tuple[List[str], Dict[str, float], Dict[str, str]]],
    date: Optional[str] = None,
) -> bool:
    """
    改进的保存方法 - 符合pool数据集标准结构
    """
    try:
        # Import here to avoid circular imports
        from data.database_operations import DatabaseOperations

        # Create database operations instance
        db_ops = DatabaseOperations(self.db_manager)

        # Ensure date is not None
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # 第一步：收集所有策略的所有股票数据
        all_stocks_data = []
        all_strategy_names = []
        total_stock_count = 0

        # Process each strategy's results
        for strategy_name, strategy_result in strategy_results.items():
            # Handle different tuple lengths gracefully
            if len(strategy_result) == 3:
                selected_stocks = strategy_result[0]
                scores = strategy_result[1]  # 这是分数字典
                json_values = strategy_result[2]  # 这是JSON值字典
            elif len(strategy_result) == 4:
                # Support 4-element format (selected_stocks, last_data_date, selected_scores, json_values)
                selected_stocks = strategy_result[0]
                scores = strategy_result[2]  # selected_scores is at index 2
                json_values = strategy_result[3]  # json_values is at index 3
            else:
                self.logger.error(
                    f"Unexpected strategy result format for {strategy_name}: {len(strategy_result)} elements"
                )
                continue

            if not selected_stocks:
                self.logger.info(
                    f"No stocks selected by strategy {strategy_name}, skipping save"
                )
                continue

            # 记录策略名称
            all_strategy_names.append(strategy_name)
            total_stock_count += len(selected_stocks)

            # Convert stocks list to the expected format (list of dicts)
            for stock_code in selected_stocks:
                # Get score from scores dictionary - use the original score directly
                score = 0.0
                if scores and isinstance(scores, dict):
                    score = scores.get(stock_code, 0.0)
                else:
                    self.logger.warning(
                        f"scores is not a dictionary for stock {stock_code}, using default score 0.0"
                    )

                # Get selection value from strategy results if available - use the JSON value directly
                value_text = ""
                if (
                    json_values
                    and isinstance(json_values, dict)
                    and stock_code in json_values
                ):
                    # Use the JSON value directly
                    value_text = json_values[stock_code]
                else:
                    # Default fallback
                    value_text = (
                        f"Strategy {strategy_name} selected stock {stock_code}"
                    )

                # Use the original score directly without normalization
                # Strategies should return scores in the appropriate range
                rounded_score = round(float(score), 2) if score is not None else 0.0

                # Create value data using the actual JSON value from strategy
                value_content = json_values.get(
                    stock_code, ""
                )  # Use the actual JSON value directly

                # 查找是否已经存在该股票的记录
                existing_stock = None
                for stock in all_stocks_data:
                    if stock.get("code") == stock_code:
                        existing_stock = stock
                        break

                if existing_stock:
                    # 如果股票已存在，在trend字段下添加新的策略数据
                    if "trend" not in existing_stock:
                        existing_stock["trend"] = {}
                    existing_stock["trend"][strategy_name] = {
                        "score": rounded_score,
                        "value": value_content,
                    }
                else:
                    # 如果股票不存在，创建新记录
                    stock_info = {
                        "code": stock_code,
                        "trend": {
                            strategy_name: {
                                "score": rounded_score,
                                "value": value_content,
                            }
                        },
                    }
                    all_stocks_data.append(stock_info)

        # 第二步：一次性保存所有策略的所有数据
        if all_stocks_data:
            # 获取策略ID（使用第一个策略的ID作为主策略ID）
            strategy_id = None
            strategies = self.db_manager.get_strategies()

            # Try to find the first strategy in the database
            for strategy in strategies:
                if (
                    strategy.get("name") == all_strategy_names[0]
                    if all_strategy_names
                    else ""
                ):
                    strategy_id = strategy.get("_id")
                    break

            # If we couldn't find the strategy, use a default
            if not strategy_id:
                strategy_id = f"weekly_selector_multi_strategy"

            # Use strategy_id as the strategy key
            strategy_key = strategy_id

            # 准备额外的元数据，包含所有策略名称和总股票数
            additional_metadata = {
                "strategy_name": ", ".join(
                    all_strategy_names
                ),  # 所有策略名称的字符串
                "count": total_stock_count,  # 所有策略选中的总股票数
                "strategies_count": len(all_strategy_names),  # 策略数量
            }

            # 使用save_trend_output_to_pool保存趋势数据，支持多策略结果累积
            save_result = db_ops.save_trend_output_to_pool(
                strategy_key=strategy_key,
                agent_name="WeeklySelector",  # 添加agent_name字段
                strategy_id=strategy_id,
                strategy_name="WeeklySelector_Multi",  # 使用统一的策略名称
                stocks=all_stocks_data,
                date=date,
                last_data_date=date,  # Use the selection date as last_data_date
                strategy_params={},  # 空参数，因为是多策略
                additional_metadata=additional_metadata,
            )

            if save_result:
                self.logger.info(
                    f"Successfully saved {len(all_stocks_data)} stocks from {len(all_strategy_names)} strategies"
                )
            else:
                self.logger.error(
                    f"Failed to save stocks from {len(all_strategy_names)} strategies"
                )

        return True
    except Exception as e:
        self.logger.error(f"Error saving selected stocks: {e}")
        return False
'''

    print(improved_code)


if __name__ == "__main__":
    test_weekly_selector_save_method()
    analyze_current_implementation()
    create_improved_save_method()

