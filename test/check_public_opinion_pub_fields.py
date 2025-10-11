"""
检查舆情分析智能体数据库pub字段写入情况
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.mongodb_config import MongoDBConfig
from pymongo import MongoClient
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def check_pub_fields_in_database():
    """检查数据库中pool记录的pub字段情况"""

    try:
        # Load MongoDB configuration
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

        # 获取最新的5条pool记录
        latest_records = list(pool_collection.find().sort("_id", -1).limit(5))

        logger.info(f"检查最新的{len(latest_records)}条pool记录")

        for i, record in enumerate(latest_records):
            logger.info(f"\n=== 记录 {i+1} (ID: {record['_id']}) ===")
            logger.info(f"创建时间: {record.get('created_at', 'N/A')}")
            logger.info(f"更新时间: {record.get('updated_at', 'N/A')}")
            logger.info(f"pub_at时间: {record.get('pub_at', 'N/A')}")

            stocks = record.get('stocks', [])
            logger.info(f"股票数量: {len(stocks)}")

            # 检查每个股票的pub字段
            stocks_with_pub = 0
            for stock in stocks:
                code = stock.get('code', 'N/A')
                if 'pub' in stock:
                    stocks_with_pub += 1
                    pub_data = stock['pub']
                    logger.info(f"  股票 {code}: pub字段存在，包含策略: {list(pub_data.keys())}")
                    for strategy_name, strategy_data in pub_data.items():
                        logger.info(f"    策略 {strategy_name}: score={strategy_data.get('score', 'N/A')}, value长度={len(str(strategy_data.get('value', '')))}")
                else:
                    logger.info(f"  股票 {code}: 无pub字段")

            logger.info(f"有pub字段的股票数量: {stocks_with_pub}/{len(stocks)}")

        # 检查舆情分析策略是否在数据库中配置
        strategies_collection = db["strategies"]
        public_opinion_strategies = list(strategies_collection.find({"name": {"$regex": "舆情", "$options": "i"}}))

        logger.info(f"\n=== 舆情分析策略配置 ===")
        logger.info(f"找到 {len(public_opinion_strategies)} 个舆情分析策略")

        for strategy in public_opinion_strategies:
            logger.info(f"策略名称: {strategy.get('name')}")
            logger.info(f"策略文件: {strategy.get('file', strategy.get('program', {}).get('file', 'N/A'))}")
            logger.info(f"策略类名: {strategy.get('class_name', strategy.get('program', {}).get('class', 'N/A'))}")

        # 检查舆情分析Agent配置
        agents_collection = db["agents"]
        public_opinion_agent = agents_collection.find_one({"name": "舆情分析Agent"})

        logger.info(f"\n=== 舆情分析Agent配置 ===")
        if public_opinion_agent:
            logger.info(f"Agent名称: {public_opinion_agent.get('name')}")
            logger.info(f"策略数量: {len(public_opinion_agent.get('strategies', []))}")
            logger.info(f"策略ID列表: {public_opinion_agent.get('strategies', [])}")
        else:
            logger.error("舆情分析Agent未在数据库中配置")

    except Exception as e:
        logger.error(f"检查数据库时出错: {e}")
        import traceback
        logger.error(traceback.format_exc())

def check_recent_public_opinion_execution():
    """检查最近的舆情分析执行情况"""

    try:
        # Load MongoDB configuration
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

        # 查找有pub_at字段的记录
        records_with_pub_at = list(pool_collection.find({"pub_at": {"$exists": True}}).sort("pub_at", -1).limit(3))

        logger.info(f"\n=== 有pub_at字段的记录 ===")
        logger.info(f"找到 {len(records_with_pub_at)} 条有pub_at字段的记录")

        for i, record in enumerate(records_with_pub_at):
            logger.info(f"\n记录 {i+1}:")
            logger.info(f"ID: {record['_id']}")
            logger.info(f"pub_at: {record.get('pub_at')}")

            stocks = record.get('stocks', [])
            stocks_with_pub = sum(1 for stock in stocks if 'pub' in stock)
            logger.info(f"有pub字段的股票: {stocks_with_pub}/{len(stocks)}")

    except Exception as e:
        logger.error(f"检查舆情分析执行情况时出错: {e}")

if __name__ == "__main__":
    logger.info("=== 开始检查舆情分析智能体数据库pub字段 ===")
    check_pub_fields_in_database()
    check_recent_public_opinion_execution()
    logger.info("\n=== 检查完成 ===")

