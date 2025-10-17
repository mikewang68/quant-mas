#!/usr/bin/env python
# coding=utf-8

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, '/home/mike/quant_mas')

# Import the MongoDB configuration
from config.mongodb_config import MongoDBConfig
from pymongo import MongoClient
import akshare as ak
import pandas as pd
import datetime

def conn_mongo():
    config_loader = MongoDBConfig()
    mongo_config = config_loader.get_mongodb_config()

    uri = "mongodb://%s:%s@%s" % (
        mongo_config.get("username", "stock"),
        mongo_config.get("password", "681123"),
        mongo_config.get("host", "192.168.1.2")
        + ":"
        + str(mongo_config.get("port", 27017))
        + "/"
        + mongo_config.get("auth_database", "admin"),
    )
    client = MongoClient(uri)
    db = client[mongo_config.get("database", "stock")]
    return db

def debug_forecast_fix():
    """
    调试盈利预测数据去重问题
    """
    print("=== 调试盈利预测数据去重问题 ===")

    # 获取盈利预测数据
    print("获取盈利预测数据...")
    forecast_data = ak.stock_profit_forecast_em()

    if not forecast_data.empty:
        print(f"获取到 {len(forecast_data)} 条盈利预测数据")

        # 检查重复的股票代码
        stock_codes = forecast_data['代码'].tolist()
        print(f"股票代码总数: {len(stock_codes)}")

        # 检查重复的股票代码
        from collections import Counter
        code_counts = Counter(stock_codes)
        duplicates = {code: count for code, count in code_counts.items() if count > 1}

        if duplicates:
            print(f"发现 {len(duplicates)} 个重复的股票代码:")
            for code, count in list(duplicates.items())[:10]:  # 只显示前10个
                print(f"  {code}: {count} 次")
        else:
            print("没有发现重复的股票代码")

        # 去重处理
        print("\n=== 去重处理 ===")
        unique_forecast_data = forecast_data.sort_values('序号', ascending=False).drop_duplicates(subset=['代码'], keep='first')
        print(f"去重后保留 {len(unique_forecast_data)} 条唯一股票记录")

        # 验证去重结果
        unique_codes = unique_forecast_data['代码'].tolist()
        unique_code_counts = Counter(unique_codes)
        unique_duplicates = {code: count for code, count in unique_code_counts.items() if count > 1}

        if unique_duplicates:
            print(f"去重后仍有 {len(unique_duplicates)} 个重复的股票代码:")
            for code, count in list(unique_duplicates.items())[:5]:
                print(f"  {code}: {count} 次")
        else:
            print("去重后没有重复的股票代码")

        # 显示去重前后的差异
        print(f"\n去重前: {len(forecast_data)} 条记录")
        print(f"去重后: {len(unique_forecast_data)} 条记录")
        print(f"去重数量: {len(forecast_data) - len(unique_forecast_data)} 条")

    else:
        print("未获取到盈利预测数据")

if __name__ == "__main__":
    debug_forecast_fix()

