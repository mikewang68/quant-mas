"""
Debug script to check which strategy is being loaded and test its logic
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient

# Initialize components
db_manager = MongoDBManager()
data_fetcher = AkshareClient()

print("检查策略加载情况...")

# Check agent configuration
agents_collection = db_manager.db['agents']
agent_config = agents_collection.find_one({"name": "趋势选股Agent"})
if agent_config:
    print(f"Agent配置: {agent_config}")
    if 'strategies' in agent_config:
        strategy_ids = agent_config['strategies']
        print(f"配置的策略ID: {strategy_ids}")

        # Load all strategies for this agent
        strategies = []
        strategies_collection = db_manager.db['strategies']
        for strategy_id in strategy_ids:
            strategy = strategies_collection.find_one({"_id": strategy_id})
            if strategy:
                strategies.append(strategy)
                print(f"加载策略: {strategy.get('name', 'Unknown')}")
                print(f"  文件: {strategy.get('file', 'N/A')}")
                print(f"  类名: {strategy.get('class_name', 'N/A')}")
                print(f"  参数: {strategy.get('parameters', {})}")
            else:
                print(f"策略ID {strategy_id} 未找到")

        print(f"成功加载 {len(strategies)} 个策略")
else:
    print("未找到趋势选股Agent配置")

# Check what strategy files exist
print("\n检查策略文件是否存在...")
import glob
strategy_files = glob.glob("strategies/*.py")
print(f"找到的策略文件: {len(strategy_files)}")
for file in strategy_files[:10]:  # Show first 10
    print(f"  {file}")

print("\n调试完成")

