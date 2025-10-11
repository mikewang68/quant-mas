"""
测试舆情分析智能体pub字段写入功能
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.public_opinion_selector import PublicOpinionStockSelector
from config.mongodb_config import MongoDBConfig
from pymongo import MongoClient
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_pub_field_writing():
    """测试pub字段写入功能"""

    try:
        # 创建舆情分析智能体实例
        from data.mongodb_manager import MongoDBManager
        from utils.akshare_client import AkshareClient

        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()
        selector = PublicOpinionStockSelector(db_manager, data_fetcher)

        # 创建测试数据
        test_stocks = [
            {
                'code': '000001',
                'strategy_name': '增强型舆情分析策略V2',
                'score': 0.85,
                'value': '测试舆情分析数据1'
            },
            {
                'code': '000002',
                'strategy_name': '增强型舆情分析策略V2',
                'score': 0.72,
                'value': '测试舆情分析数据2'
            }
        ]

        logger.info("=== 开始测试pub字段写入 ===")
        logger.info(f"测试股票数量: {len(test_stocks)}")

        # 调用update_latest_pool_record方法
        result = selector.update_latest_pool_record(test_stocks)

        logger.info(f"写入结果: {result}")

        # 检查数据库中的结果
        mongodb_config = MongoDBConfig()
        config = mongodb_config.get_mongodb_config()

        # Connect to MongoDB
        if config.get("username") and config.get("password"):
            uri = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?authSource={config.get('auth_database', 'admin')}"
        else:
            uri = f"mongodb://{config['host']}:{config['port']}/"

        client = MongoClient(uri)
        db = client[config["database"]]
        pool_collection = db["pool"]

        # 获取最新的pool记录
        latest_record = pool_collection.find_one(sort=[("_id", -1)])

        if latest_record:
            logger.info(f"最新记录ID: {latest_record['_id']}")
            logger.info(f"pub_at时间: {latest_record.get('pub_at', 'N/A')}")

            stocks = latest_record.get('stocks', [])
            logger.info(f"股票数量: {len(stocks)}")

            # 检查测试股票的pub字段
            for test_stock in test_stocks:
                code = test_stock['code']
                found = False
                for stock in stocks:
                    if stock.get('code') == code:
                        found = True
                        if 'pub' in stock:
                            pub_data = stock['pub']
                            logger.info(f"股票 {code}: pub字段存在，包含策略: {list(pub_data.keys())}")
                            for strategy_name, strategy_data in pub_data.items():
                                logger.info(f"  策略 {strategy_name}: score={strategy_data.get('score', 'N/A')}, value={strategy_data.get('value', 'N/A')}")
                        else:
                            logger.info(f"股票 {code}: 无pub字段")
                        break

                if not found:
                    logger.info(f"股票 {code}: 未在最新记录中找到")
        else:
            logger.error("未找到pool记录")

        return result

    except Exception as e:
        logger.error(f"测试过程中出错: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def debug_update_latest_pool_record():
    """调试update_latest_pool_record方法"""

    try:
        # 创建舆情分析智能体实例
        selector = PublicOpinionStockSelector()

        # 创建测试数据
        test_stocks = [
            {
                'code': '000001',
                'strategy_name': '增强型舆情分析策略V2',
                'score': 0.85,
                'value': '测试舆情分析数据1'
            }
        ]

        logger.info("=== 调试update_latest_pool_record方法 ===")

        # 获取pool集合
        collection = selector.db_manager.db["pool"]

        # 查找最新的pool记录
        latest_pool_record = collection.find_one(sort=[("_id", -1)])

        if not latest_pool_record:
            logger.error("No records found in pool collection")
            return False

        logger.info(f"找到最新记录: ID={latest_pool_record['_id']}")

        # 获取现有股票
        existing_stocks = latest_pool_record.get("stocks", [])
        logger.info(f"现有股票数量: {len(existing_stocks)}")

        # 创建股票映射
        existing_stock_map = {stock.get("code"): stock for stock in existing_stocks}
        logger.info(f"股票映射大小: {len(existing_stock_map)}")

        # 检查测试股票是否在现有股票中
        for test_stock in test_stocks:
            code = test_stock['code']
            if code in existing_stock_map:
                logger.info(f"股票 {code} 在现有股票中")

                # 更新pub字段
                strategy_name = test_stock.get('strategy_name', 'unknown_strategy')

                if 'pub' not in existing_stock_map[code]:
                    existing_stock_map[code]['pub'] = {}
                    logger.info(f"为股票 {code} 创建pub字段")

                existing_stock_map[code]['pub'][strategy_name] = {
                    'score': test_stock.get('score', 0.0),
                    'value': test_stock.get('value', ''),
                }
                logger.info(f"更新股票 {code} 的pub字段: {existing_stock_map[code]['pub']}")
            else:
                logger.info(f"股票 {code} 不在现有股票中")

        # 准备清理后的股票
        cleaned_stocks = []
        for stock in existing_stocks:
            # 获取更新后的股票
            updated_stock = existing_stock_map.get(stock.get('code'))
            if updated_stock:
                clean_stock = updated_stock.copy()
                logger.info(f"使用更新后的股票 {stock.get('code')}: pub字段={clean_stock.get('pub', 'N/A')}")
            else:
                clean_stock = stock.copy()
                logger.info(f"使用原始股票 {stock.get('code')}: pub字段={clean_stock.get('pub', 'N/A')}")

            cleaned_stocks.append(clean_stock)

        logger.info(f"清理后股票数量: {len(cleaned_stocks)}")

        # 更新数据库
        result = collection.update_one(
            {"_id": latest_pool_record["_id"]},
            {
                "$set": {
                    "stocks": cleaned_stocks,
                    "pub_at": datetime.now(),
                },
                "$unset": {
                    "selected_stocks_count": "",
                    "strategy_execution_time": ""
                }
            },
        )

        logger.info(f"数据库更新结果: modified_count={result.modified_count}")

        return result.modified_count > 0

    except Exception as e:
        logger.error(f"调试过程中出错: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("=== 开始测试pub字段写入功能 ===")

    # 运行测试
    result = test_pub_field_writing()

    if result:
        logger.info("测试成功: pub字段写入功能正常")
    else:
        logger.error("测试失败: pub字段写入功能异常")

    # 运行调试
    logger.info("\n=== 开始调试update_latest_pool_record方法 ===")
    debug_result = debug_update_latest_pool_record()

    if debug_result:
        logger.info("调试成功: update_latest_pool_record方法正常")
    else:
        logger.error("调试失败: update_latest_pool_record方法异常")

    logger.info("=== 测试完成 ===")

