"""
测试程序：获取pool数据集结构
用于分析pool数据集的字段结构，以便准确修改写入程序
"""

import sys
import os
from datetime import datetime

# Add project root to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.mongodb_manager import MongoDBManager
from config.mongodb_config import mongodb_config


def analyze_pool_structure():
    """
    分析pool数据集的结构
    """
    print("=== 开始分析pool数据集结构 ===")

    try:
        # 初始化数据库管理器
        db_manager = MongoDBManager()

        # 获取pool集合
        pool_collection = db_manager.get_collection('pool')

        # 获取pool集合中的文档数量
        total_count = pool_collection.count_documents({})
        print(f"\n1. pool集合总文档数: {total_count}")

        # 获取最新的几个文档
        latest_docs = list(pool_collection.find().sort("_id", -1).limit(5))

        print(f"\n2. 最新5个文档的结构:")
        for i, doc in enumerate(latest_docs):
            print(f"\n--- 文档 {i+1} ---")
            print(f"文档ID: {doc.get('_id')}")
            print(f"创建时间: {doc.get('created_at')}")
            print(f"更新时间: {doc.get('updated_at')}")
            print(f"策略键: {doc.get('strategy_key')}")
            print(f"代理名称: {doc.get('agent_name')}")
            print(f"策略ID: {doc.get('strategy_id')}")
            print(f"策略名称: {doc.get('strategy_name')}")
            print(f"选择日期: {doc.get('selection_date')}")
            print(f"最后数据日期: {doc.get('last_data_date')}")

            # 分析字段结构
            print("\n字段结构:")
            for key, value in doc.items():
                if key not in ['_id', 'created_at', 'updated_at']:
                    if isinstance(value, dict):
                        print(f"  {key}: dict (包含 {len(value)} 个键)")
                        # 如果是code字段，显示详细信息
                        if key == 'code':
                            print(f"    股票代码: {value}")
                        # 如果是trend字段，显示策略信息
                        elif key == 'trend':
                            for trend_key, trend_value in value.items():
                                print(f"    趋势策略 '{trend_key}': {type(trend_value)}")
                                if isinstance(trend_value, dict):
                                    for sub_key in trend_value.keys():
                                        print(f"      - {sub_key}")
                        # 如果是tech字段，显示技术分析信息
                        elif key == 'tech':
                            for tech_key, tech_value in value.items():
                                print(f"    技术策略 '{tech_key}': {type(tech_value)}")
                                if isinstance(tech_value, dict):
                                    for sub_key in tech_value.keys():
                                        print(f"      - {sub_key}")
                        # 如果是fund字段，显示基本面分析信息
                        elif key == 'fund':
                            for fund_key, fund_value in value.items():
                                print(f"    基本面策略 '{fund_key}': {type(fund_value)}")
                                if isinstance(fund_value, dict):
                                    for sub_key in fund_value.keys():
                                        print(f"      - {sub_key}")
                        # 如果是pub字段，显示舆情分析信息
                        elif key == 'pub':
                            for pub_key, pub_value in value.items():
                                print(f"    舆情策略 '{pub_key}': {type(pub_value)}")
                                if isinstance(pub_value, dict):
                                    for sub_key in pub_value.keys():
                                        print(f"      - {sub_key}")
                    elif isinstance(value, list):
                        print(f"  {key}: list (包含 {len(value)} 个元素)")
                        if value and isinstance(value[0], dict):
                            print(f"    第一个元素字段: {list(value[0].keys())}")
                    else:
                        print(f"  {key}: {type(value).__name__} = {value}")

        # 分析字段分布
        print(f"\n3. 字段分布统计:")
        field_counts = {}
        sample_docs = list(pool_collection.find().limit(20))

        for doc in sample_docs:
            for key in doc.keys():
                field_counts[key] = field_counts.get(key, 0) + 1

        for field, count in sorted(field_counts.items()):
            percentage = (count / len(sample_docs)) * 100
            print(f"  {field}: {count}/{len(sample_docs)} ({percentage:.1f}%)")

        # 分析策略类型分布
        print(f"\n4. 策略类型分布:")
        strategy_types = {}
        for doc in sample_docs:
            agent_name = doc.get('agent_name', 'Unknown')
            strategy_types[agent_name] = strategy_types.get(agent_name, 0) + 1

        for agent, count in sorted(strategy_types.items()):
            print(f"  {agent}: {count} 个文档")

        # 分析数据字段类型
        print(f"\n5. 数据字段类型分析:")
        data_fields = ['trend', 'tech', 'fund', 'pub']
        for field in data_fields:
            field_presence = sum(1 for doc in sample_docs if field in doc)
            percentage = (field_presence / len(sample_docs)) * 100
            print(f"  {field}: {field_presence}/{len(sample_docs)} ({percentage:.1f}%)")

        # 分析股票代码字段
        print(f"\n6. 股票代码字段分析:")
        code_presence = sum(1 for doc in sample_docs if 'code' in doc)
        print(f"  包含code字段的文档: {code_presence}/{len(sample_docs)}")

        # 如果有code字段，显示一些示例
        code_docs = [doc for doc in sample_docs if 'code' in doc]
        if code_docs:
            print(f"  示例股票代码:")
            for doc in code_docs[:3]:
                print(f"    {doc.get('code')}")

        print("\n=== pool数据集结构分析完成 ===")

    except Exception as e:
        print(f"分析pool数据集结构时出错: {e}")
        import traceback
        traceback.print_exc()


def analyze_specific_strategy():
    """
    分析特定策略的数据结构
    """
    print("\n=== 分析特定策略数据结构 ===")

    try:
        db_manager = MongoDBManager()
        pool_collection = db_manager.get_collection('pool')

        # 分析WeeklySelector策略的数据结构
        weekly_docs = list(pool_collection.find({"agent_name": "WeeklySelector"}).limit(3))

        print(f"\nWeeklySelector策略文档数量: {len(weekly_docs)}")

        for i, doc in enumerate(weekly_docs):
            print(f"\n--- WeeklySelector文档 {i+1} ---")
            print(f"策略键: {doc.get('strategy_key')}")
            print(f"策略名称: {doc.get('strategy_name')}")

            # 分析trend字段结构
            if 'trend' in doc:
                trend_data = doc['trend']
                print(f"趋势策略数量: {len(trend_data)}")
                for strategy_name, strategy_data in trend_data.items():
                    print(f"  策略 '{strategy_name}':")
                    if isinstance(strategy_data, dict):
                        for key, value in strategy_data.items():
                            if key == 'score':
                                print(f"    分数: {value}")
                            elif key == 'value':
                                print(f"    值类型: {type(value).__name__}")
                                if isinstance(value, str) and len(value) > 100:
                                    print(f"    值内容(前100字符): {value[:100]}...")
                                else:
                                    print(f"    值内容: {value}")
                            else:
                                print(f"    {key}: {type(value).__name__}")

    except Exception as e:
        print(f"分析特定策略时出错: {e}")


if __name__ == "__main__":
    analyze_pool_structure()
    analyze_specific_strategy()

