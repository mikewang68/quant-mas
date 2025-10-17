"""
Test script to verify Weekly Selector can filter 508 stocks
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient

# Initialize components
db_manager = MongoDBManager()
data_fetcher = AkshareClient()

# Check if we can get stock codes
print("获取股票代码列表...")
all_codes = db_manager.get_stock_codes()
print(f"数据库中的股票代码数量: {len(all_codes) if all_codes else 0}")

# If no codes in DB, fetch from data source
if not all_codes:
    print("从数据源获取股票代码...")
    all_codes = data_fetcher.get_stock_list()
    print(f"从数据源获取的股票代码数量: {len(all_codes) if all_codes else 0}")

    # Save to DB for future use
    if all_codes:
        db_manager.save_stock_codes(all_codes)
        print("股票代码已保存到数据库")

# Check agent configuration from database
print("\n检查数据库中的Agent配置...")
agents_collection = db_manager.db['agents']
agent_config = agents_collection.find_one({"name": "趋势选股Agent"})
if agent_config:
    print(f"Agent配置: {agent_config}")
    if 'strategies' in agent_config:
        strategy_ids = agent_config['strategies']
        print(f"配置的策略ID: {strategy_ids}")

        # Load strategies
        strategies = []
        for strategy_id in strategy_ids:
            strategy = db_manager.get_strategy_by_name(strategy_id)  # Try by name first
            if not strategy:
                # If not found by name, try by ID
                strategies_collection = db_manager.db['strategies']
                strategy = strategies_collection.find_one({"_id": strategy_id})
            if strategy:
                strategies.append(strategy)
                print(f"加载策略: {strategy.get('name', 'Unknown')}")

        print(f"成功加载 {len(strategies)} 个策略")
else:
    print("未找到趋势选股Agent配置")

# Check pool data to see current state
print("\n检查当前pool数据...")
pool_data = db_manager.get_pool_data()
if pool_data:
    print(f"当前pool数据中的记录数量: {len(pool_data)}")

    # Check latest pool record
    latest_pool = db_manager.get_latest_pool_record()
    if latest_pool:
        print(f"最新pool记录的策略: {latest_pool.get('strategy_name', 'Unknown')}")
        stocks = latest_pool.get('stocks', [])
        print(f"最新pool记录中的股票数量: {len(stocks)}")
        if stocks:
            print(f"前5只股票: {[stock.get('code') for stock in stocks[:5]]}")
else:
    print("当前没有pool数据")

# Check strategies collection
print("\n检查策略配置...")
strategies_collection = db_manager.db['strategies']
strategies = list(strategies_collection.find())
print(f"数据库中的策略数量: {len(strategies)}")

for strategy in strategies[:5]:  # Show first 5 strategies
    print(f"策略: {strategy.get('name', 'Unknown')} - ID: {strategy.get('_id')}")

print("\n测试完成")

