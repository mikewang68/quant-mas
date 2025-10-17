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

def update_finance_data(db):
    """
    更新财务相关数据
    使用多个akshare函数获取财务数据，并更新到对应的MongoDB集合中
    清空集合后重新写入，使用股票代码作为_id
    """
    print("开始更新财务相关数据...")

    try:
        # 1. 更新业绩报表数据 (stock_yjbb_em -> fin_yjbb)
        print("获取业绩报表数据...")
        yjbb_data = ak.stock_yjbb_em()
        if not yjbb_data.empty:
            print(f"获取到 {len(yjbb_data)} 条业绩报表数据")
            yjbb_collection = db["fin_yjbb"]

            # 清空集合
            yjbb_collection.delete_many({})

            inserted_count = 0
            for _, row in yjbb_data.iterrows():
                stock_code = row.get("股票代码", "")
                if stock_code:
                    # 创建新文档，使用股票代码作为_id，同时保留股票代码字段
                    record_data = {"_id": stock_code, "股票代码": stock_code}

                    # 按dataframe列顺序添加字段，跳过"序号"字段
                    for col in yjbb_data.columns:
                        if col not in ["序号"]:
                            value = row[col]
                            if pd.notna(value):
                                # 转换datetime.date对象为字符串
                                if isinstance(value, datetime.date):
                                    value = value.strftime('%Y-%m-%d')
                                record_data[col] = value

                    # 插入数据
                    try:
                        yjbb_collection.insert_one(record_data)
                        inserted_count += 1
                    except Exception as e:
                        print(f"插入业绩报表数据失败 {stock_code}: {e}")

            print(f"成功插入 {inserted_count} 条业绩报表记录")
        else:
            print("未获取到业绩报表数据")

        # 2. 更新资产负债表数据 (stock_zcfz_em -> fin_zcfz)
        print("获取资产负债表数据...")
        zcfz_data = ak.stock_zcfz_em()
        if not zcfz_data.empty:
            print(f"获取到 {len(zcfz_data)} 条资产负债表数据")
            zcfz_collection = db["fin_zcfz"]

            # 清空集合
            zcfz_collection.delete_many({})

            inserted_count = 0
            for _, row in zcfz_data.iterrows():
                stock_code = row.get("股票代码", "")
                if stock_code:
                    # 创建新文档，使用股票代码作为_id，同时保留股票代码字段
                    record_data = {"_id": stock_code, "股票代码": stock_code}

                    # 按dataframe列顺序添加字段，跳过"序号"字段
                    for col in zcfz_data.columns:
                        if col not in ["序号"]:
                            value = row[col]
                            if pd.notna(value):
                                # 转换datetime.date对象为字符串
                                if isinstance(value, datetime.date):
                                    value = value.strftime('%Y-%m-%d')
                                record_data[col] = value

                    # 插入数据
                    try:
                        zcfz_collection.insert_one(record_data)
                        inserted_count += 1
                    except Exception as e:
                        print(f"插入资产负债表数据失败 {stock_code}: {e}")

            print(f"成功插入 {inserted_count} 条资产负债表记录")
        else:
            print("未获取到资产负债表数据")

        # 3. 更新利润表数据 (stock_lrb_em -> fin_lrb)
        print("获取利润表数据...")
        lrb_data = ak.stock_lrb_em()
        if not lrb_data.empty:
            print(f"获取到 {len(lrb_data)} 条利润表数据")
            lrb_collection = db["fin_lrb"]

            # 清空集合
            lrb_collection.delete_many({})

            inserted_count = 0
            for _, row in lrb_data.iterrows():
                stock_code = row.get("股票代码", "")
                if stock_code:
                    # 创建新文档，使用股票代码作为_id，同时保留股票代码字段
                    record_data = {"_id": stock_code, "股票代码": stock_code}

                    # 按dataframe列顺序添加字段，跳过"序号"字段
                    for col in lrb_data.columns:
                        if col not in ["序号"]:
                            value = row[col]
                            if pd.notna(value):
                                # 转换datetime.date对象为字符串
                                if isinstance(value, datetime.date):
                                    value = value.strftime('%Y-%m-%d')
                                record_data[col] = value

                    # 插入数据
                    try:
                        lrb_collection.insert_one(record_data)
                        inserted_count += 1
                    except Exception as e:
                        print(f"插入利润表数据失败 {stock_code}: {e}")

            print(f"成功插入 {inserted_count} 条利润表记录")
        else:
            print("未获取到利润表数据")

        # 4. 更新现金流量表数据 (stock_xjll_em -> fin_xjll)
        print("获取现金流量表数据...")
        xjll_data = ak.stock_xjll_em()
        if not xjll_data.empty:
            print(f"获取到 {len(xjll_data)} 条现金流量表数据")
            xjll_collection = db["fin_xjll"]

            # 清空集合
            xjll_collection.delete_many({})

            inserted_count = 0
            for _, row in xjll_data.iterrows():
                stock_code = row.get("股票代码", "")
                if stock_code:
                    # 创建新文档，使用股票代码作为_id
                    record_data = {"_id": stock_code}

                    # 按dataframe列顺序添加字段，跳过"序号"和"股票代码"字段
                    for col in xjll_data.columns:
                        if col not in ["序号", "股票代码"]:
                            value = row[col]
                            if pd.notna(value):
                                # 转换datetime.date对象为字符串
                                if isinstance(value, datetime.date):
                                    value = value.strftime('%Y-%m-%d')
                                record_data[col] = value

                    # 插入数据
                    try:
                        xjll_collection.insert_one(record_data)
                        inserted_count += 1
                    except Exception as e:
                        print(f"插入现金流量表数据失败 {stock_code}: {e}")

            print(f"成功插入 {inserted_count} 条现金流量表记录")
        else:
            print("未获取到现金流量表数据")

        # 5. 更新盈利预测数据 (stock_profit_forecast_em -> fin_forecast)
        print("获取盈利预测数据...")
        forecast_data = ak.stock_profit_forecast_em()
        if not forecast_data.empty:
            print(f"获取到 {len(forecast_data)} 条盈利预测数据")
            print(f"盈利预测数据列名: {list(forecast_data.columns)}")
            forecast_collection = db["fin_forecast"]

            # 清空集合
            forecast_collection.delete_many({})

            inserted_count = 0
            for _, row in forecast_data.iterrows():
                # 使用"代码"字段而不是"股票代码"
                stock_code = row.get("代码", "")
                if stock_code:
                    # 创建新文档，使用股票代码作为_id
                    record_data = {"_id": stock_code}

                    # 按dataframe列顺序添加字段，跳过"序号"和"代码"字段
                    for col in forecast_data.columns:
                        if col not in ["序号", "代码"]:
                            value = row[col]
                            if pd.notna(value):
                                # 转换datetime.date对象为字符串
                                if isinstance(value, datetime.date):
                                    value = value.strftime('%Y-%m-%d')
                                record_data[col] = value

                    # 插入数据
                    try:
                        forecast_collection.insert_one(record_data)
                        inserted_count += 1
                    except Exception as e:
                        print(f"插入盈利预测数据失败 {stock_code}: {e}")

            print(f"成功插入 {inserted_count} 条盈利预测记录")
        else:
            print("未获取到盈利预测数据")

        print("财务数据更新完成")

    except Exception as e:
        print(f"更新财务数据时发生错误: {str(e)}")

if __name__ == "__main__":
    print("=== 开始测试 update_finance_data 函数 ===")

    # Connect to database
    db = conn_mongo()

    # Run the function
    update_finance_data(db)

    print("=== 测试完成 ===")

