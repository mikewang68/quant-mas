"""
详细分析pool数据集中stocks字段的结构
"""

import sys
import os

# Add project root to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.mongodb_manager import MongoDBManager


def analyze_stocks_structure():
    """
    详细分析stocks字段的结构
    """
    print("=== 详细分析stocks字段结构 ===")

    try:
        db_manager = MongoDBManager()
        pool_collection = db_manager.get_collection('pool')

        # 获取包含stocks字段的文档
        docs_with_stocks = list(pool_collection.find({"stocks": {"$exists": True, "$ne": []}}).limit(5))

        print(f"包含stocks字段的文档数量: {len(docs_with_stocks)}")

        for i, doc in enumerate(docs_with_stocks):
            print(f"\n--- 文档 {i+1} ---")
            print(f"策略键: {doc.get('strategy_key')}")
            print(f"策略名称: {doc.get('strategy_name')}")
            print(f"stocks数量: {len(doc.get('stocks', []))}")

            # 分析stocks中的第一个股票
            stocks = doc.get('stocks', [])
            if stocks:
                first_stock = stocks[0]
                print(f"\n第一个股票的结构:")
                for key, value in first_stock.items():
                    if isinstance(value, dict):
                        print(f"  {key}: dict (包含 {len(value)} 个键)")
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, dict):
                                print(f"    {sub_key}: dict (包含 {len(sub_value)} 个键)")
                                for sub_sub_key in sub_value.keys():
                                    print(f"      - {sub_sub_key}")
                            else:
                                print(f"    {sub_key}: {type(sub_value).__name__} = {sub_value}")
                    else:
                        print(f"  {key}: {type(value).__name__} = {value}")

                # 特别分析trend字段
                if 'trend' in first_stock:
                    print(f"\n  trend字段详细分析:")
                    trend_data = first_stock['trend']
                    for strategy_name, strategy_info in trend_data.items():
                        print(f"    策略 '{strategy_name}':")
                        if isinstance(strategy_info, dict):
                            for field, field_value in strategy_info.items():
                                print(f"      {field}: {type(field_value).__name__}")
                                if field == 'value' and isinstance(field_value, str):
                                    if len(field_value) > 100:
                                        print(f"        值内容(前100字符): {field_value[:100]}...")
                                    else:
                                        print(f"        值内容: {field_value}")

                # 特别分析tech字段
                if 'tech' in first_stock:
                    print(f"\n  tech字段详细分析:")
                    tech_data = first_stock['tech']
                    for strategy_name, strategy_info in tech_data.items():
                        print(f"    策略 '{strategy_name}':")
                        if isinstance(strategy_info, dict):
                            for field, field_value in strategy_info.items():
                                print(f"      {field}: {type(field_value).__name__}")
                                if field == 'value' and isinstance(field_value, str):
                                    if len(field_value) > 100:
                                        print(f"        值内容(前100字符): {field_value[:100]}...")
                                    else:
                                        print(f"        值内容: {field_value}")

                # 特别分析fund字段
                if 'fund' in first_stock:
                    print(f"\n  fund字段详细分析:")
                    fund_data = first_stock['fund']
                    for strategy_name, strategy_info in fund_data.items():
                        print(f"    策略 '{strategy_name}':")
                        if isinstance(strategy_info, dict):
                            for field, field_value in strategy_info.items():
                                print(f"      {field}: {type(field_value).__name__}")
                                if field == 'value' and isinstance(field_value, str):
                                    if len(field_value) > 100:
                                        print(f"        值内容(前100字符): {field_value[:100]}...")
                                    else:
                                        print(f"        值内容: {field_value}")

                # 特别分析pub字段
                if 'pub' in first_stock:
                    print(f"\n  pub字段详细分析:")
                    pub_data = first_stock['pub']
                    for strategy_name, strategy_info in pub_data.items():
                        print(f"    策略 '{strategy_name}':")
                        if isinstance(strategy_info, dict):
                            for field, field_value in strategy_info.items():
                                print(f"      {field}: {type(field_value).__name__}")
                                if field == 'value' and isinstance(field_value, str):
                                    if len(field_value) > 100:
                                        print(f"        值内容(前100字符): {field_value[:100]}...")
                                    else:
                                        print(f"        值内容: {field_value}")

                # 特别分析signals字段
                if 'signals' in first_stock:
                    print(f"\n  signals字段详细分析:")
                    signals_data = first_stock['signals']
                    for strategy_name, strategy_info in signals_data.items():
                        print(f"    策略 '{strategy_name}':")
                        if isinstance(strategy_info, dict):
                            for field, field_value in strategy_info.items():
                                print(f"      {field}: {type(field_value).__name__}")
                                if field == 'value' and isinstance(field_value, str):
                                    if len(field_value) > 100:
                                        print(f"        值内容(前100字符): {field_value[:100]}...")
                                    else:
                                        print(f"        值内容: {field_value}")

    except Exception as e:
        print(f"分析stocks字段结构时出错: {e}")
        import traceback
        traceback.print_exc()


def analyze_database_operations():
    """
    分析database_operations.py中的写入方法
    """
    print("\n=== 分析database_operations.py中的写入方法 ===")

    try:
        from data.database_operations import DatabaseOperations

        # 查看DatabaseOperations类的save_trend_output_to_pool方法
        print("DatabaseOperations类包含的方法:")
        methods = [method for method in dir(DatabaseOperations) if not method.startswith('_')]
        for method in methods:
            print(f"  - {method}")

    except Exception as e:
        print(f"分析database_operations时出错: {e}")


if __name__ == "__main__":
    analyze_stocks_structure()
    analyze_database_operations()

