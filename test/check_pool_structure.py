"""
检查pool数据集的记录结构和_id格式
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def check_pool_structure():
    """检查pool数据集的记录结构"""

    # Initialize MongoDB manager
    db_manager = MongoDBManager()
    pool_collection = db_manager.get_collection("pool")

    # 获取所有pool记录
    pool_records = list(pool_collection.find().sort("_id", -1).limit(10))

    print(f"Total pool records: {len(pool_records)}")
    print("\n=== Pool Records Structure ===")

    for i, record in enumerate(pool_records):
        print(f"\nRecord {i+1}:")
        print(f"  _id: {record.get('_id')}")
        print(f"  _id type: {type(record.get('_id'))}")
        print(f"  stocks count: {len(record.get('stocks', []))}")

        # 检查是否有其他关键字段
        for key in ['selection_date', 'date', 'updated_at', 'metadata']:
            if key in record:
                print(f"  {key}: {record[key]}")

    # 检查最新的记录
    if pool_records:
        latest_record = pool_records[0]
        print(f"\n=== Latest Record Details ===")
        print(f"_id: {latest_record.get('_id')}")

        # 检查stocks字段中的策略分布
        stocks = latest_record.get("stocks", [])
        strategy_counts = {}
        for stock in stocks:
            trend_data = stock.get("trend", {})
            for strategy_name in trend_data.keys():
                strategy_counts[strategy_name] = strategy_counts.get(strategy_name, 0) + 1

        print(f"Strategies in latest record:")
        for strategy, count in strategy_counts.items():
            print(f"  {strategy}: {count} stocks")

if __name__ == "__main__":
    check_pool_structure()

