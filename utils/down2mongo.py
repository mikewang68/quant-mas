#!/usr/bin/env python
# coding=utf-8

import akshare as ak
import pandas as pd
from pymongo import MongoClient
import time
import json
import sys
import os

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the MongoDB configuration from the project
from config.mongodb_config import MongoDBConfig

# Import the router control function
try:
    from utils.enhanced_router_control import TPLinkWAN2Controller

    ROUTER_CONTROL_AVAILABLE = True
except ImportError:
    print(
        "Warning: Router control module not available. IP switching will be disabled."
    )
    ROUTER_CONTROL_AVAILABLE = False

# Import the IP detection function
try:
    from utils.get_isp_ip import get_current_ip

    IP_DETECTION_AVAILABLE = True
except ImportError:
    print("Warning: IP detection module not available.")
    IP_DETECTION_AVAILABLE = False


# 连接mongodb中的stock数据库
def conn_mongo():
    # Use the project's MongoDB configuration
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


# 更新股票代码表
def update_code_name(db):
    df_code = ak.stock_info_a_code_name()
    data = json.loads(df_code.T.to_json()).values()

    my_coll = db["code"]
    for row in data:
        my_coll.update_one(
            {"_id": row["code"]},
            {"$set": {"code": row["code"], "name": row["name"]}},
            upsert=True,
        )


def get_code_name(db):
    my_coll = db["code"]
    cursor = my_coll.find({})
    df = pd.DataFrame(cursor)
    return df


def get_stocks_to_update(db):
    """
    获取需要更新的股票代码列表
    条件：last_updated字段小于update_date数据集中的latest，或是空的股票集合
    """
    # 获取最新的更新日期
    latest_date = get_lastest_date(db)

    # 查询条件：last_updated为空或者小于latest_date
    query = {
        "$or": [
            {"last_updated": {"$exists": False}},
            {"last_updated": {"$lt": latest_date}}
        ]
    }

    my_coll = db["code"]
    cursor = my_coll.find(query)
    df = pd.DataFrame(cursor)

    # 如果DataFrame为空，返回空的DataFrame但保持列结构
    if df.empty:
        return pd.DataFrame(columns=["_id", "code", "name", "last_updated"])

    return df


# 获取上次更新时间
def get_lastest_date(db):
    str_lastest = db.get_collection("update_date").find_one()
    return str_lastest["lastest"]


# 设置本次更新时间
def set_lastest_date(db):
    str_lastest = db.get_collection("update_date").find_one()
    last_date = str_lastest["lastest"]
    update_date = time.strftime("%Y%m%d", time.localtime(time.time()))
    db.get_collection("update_date").update_one(
        {"lastest": last_date}, {"$set": {"lastest": update_date}}
    )
    return


# 写日k线
def write_k_daily(db):
    df_code = get_stocks_to_update(db)

    start_date = get_lastest_date(db)
    # start_date = ""
    end_date = time.strftime("%Y%m%d", time.localtime(time.time()))

    # Initialize the used IP list
    used_ip = []

    # Get the initial IP before starting data collection
    if IP_DETECTION_AVAILABLE:
        initial_ip = get_current_ip(max_retries=3, retry_delay=2)
        if initial_ip:
            used_ip.append(initial_ip)
            print(f"Initial IP added to used list: {initial_ip}")
        else:
            print("Failed to get initial IP - continuing without IP tracking")
            # We'll continue without IP tracking if detection fails

    # Counter for IP switching
    stock_counter = 0
    stocks_since_last_switch = 0

    for code in df_code["code"]:
        try:
            print("daily: " + code)
            df_n = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="",
            )
            df_h = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="hfq",
            )
            df_q = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq",
            )
            if not df_n.empty:
                df_h.rename(
                    columns={
                        "开盘": "开盘h",
                        "收盘": "收盘h",
                        "最高": "最高h",
                        "最低": "最低h",
                        "成交量": "成交量h",
                        "成交额": "成交额h",
                        "振幅": "振幅h",
                        "涨跌幅": "涨跌幅h",
                        "涨跌额": "涨跌额h",
                        "换手率": "换手率h",
                    },
                    inplace=True,
                )
                df_q.rename(
                    columns={
                        "开盘": "开盘q",
                        "收盘": "收盘q",
                        "最高": "最高q",
                        "最低": "最低q",
                        "成交量": "成交量q",
                        "成交额": "成交额q",
                        "振幅": "振幅q",
                        "涨跌幅": "涨跌幅q",
                        "涨跌额": "涨跌额q",
                        "换手率": "换手率q",
                    },
                    inplace=True,
                )
                df = pd.merge(df_n, df_h, on=["日期"])
                df = pd.merge(df, df_q, on=["日期"])
                df["日期"] = df["日期"].apply(lambda x: x.strftime("%Y-%m-%d"))
                df["代码"] = code

                data = json.loads(df.T.to_json()).values()
                for row in data:
                    db["k_data"].update_one(
                        {"_id": row["日期"] + ":" + row["代码"]},
                        {"$set": row},
                        upsert=True,
                    )

                # 更新code数据集，将当前日期写入last_updated字段
                current_date = time.strftime("%Y%m%d", time.localtime(time.time()))
                db["code"].update_one(
                    {"_id": code},
                    {"$set": {"last_updated": current_date}},
                    upsert=True,
                )
            else:
                print(f"Warning: No data found for code {code}. Skipping...")

                # 即使没有数据，也更新code数据集的日期
                current_date = time.strftime("%Y%m%d", time.localtime(time.time()))
                db["code"].update_one(
                    {"_id": code},
                    {"$set": {"last_updated": current_date}},
                    upsert=True,
                )

            # Increment counters
            stock_counter += 1
            stocks_since_last_switch += 1

            # Add a 1-second delay after processing each stock
            # time.sleep(1)

            # Switch IP every 100 stocks
            if ROUTER_CONTROL_AVAILABLE and stocks_since_last_switch >= 300:
                print(f"Switching IP after processing {stock_counter} stocks...")

                # Switch the IP
                controller = TPLinkWAN2Controller(
                    router_ip="192.168.1.1",
                    username="wangdg68",
                    password="wap951020ZJL",
                )
                success = controller.switch_ip()
                if success:
                    print("IP switch successful")

                    # If IP detection is available, check and manage IP addresses
                    if IP_DETECTION_AVAILABLE:
                        # Get the current IP with retry mechanism
                        current_ip = get_current_ip(max_retries=3, retry_delay=2)
                        if current_ip:
                            print(f"Current IP: {current_ip}")

                            # Check if this IP has been used before
                            while current_ip in used_ip:
                                print(
                                    f"IP {current_ip} has been used before, switching again..."
                                )
                                # Switch IP again
                                controller = TPLinkWAN2Controller(
                                    router_ip="192.168.1.1",
                                    username="wangdg68",
                                    password="wap951020ZJL",
                                )
                                controller.switch_ip()
                                time.sleep(5)  # Wait for IP to change
                                current_ip = get_current_ip(
                                    max_retries=3, retry_delay=2
                                )
                                if current_ip:
                                    print(f"New IP: {current_ip}")
                                else:
                                    print("Failed to get current IP after switching")
                                    break

                            # Add the new IP to the used list
                            if current_ip and current_ip not in used_ip:
                                used_ip.append(current_ip)
                                print(f"Added {current_ip} to used IP list")
                                print(f"Current used IP list: {used_ip}")
                        else:
                            print("Failed to get current IP after multiple attempts")
                else:
                    print("IP switch failed")
                stocks_since_last_switch = 0  # Reset the counter

        except KeyError as e:
            print(
                f"Error: Stock code {code} not found in the dictionary. Skipping this code."
            )


def find_missing_k_data(db):
    """
    对照code表中的代码，检查哪个代码在k_data中没有数据，将缺失的代码返回一个df或列表
    """
    code_df = get_code_name(db)
    k_data_collection = db["k_data"]
    missing_codes = []

    for code in code_df["code"]:
        # 检查k_data中是否有该代码的数据
        if k_data_collection.count_documents({"代码": code}) == 0:
            missing_codes.append(code)

    return pd.DataFrame(missing_codes, columns=["missing_codes"])


def get_k_data_by_code(db, code):
    """
    从k_data数据集中提取指定代码的股票数据

    :param db: MongoDB数据库连接
    :param code: 股票代码
    :return: 包含股票数据的Pandas DataFrame
    """
    my_coll = db["k_data"]
    cursor = my_coll.find({"代码": code})
    df = pd.DataFrame(cursor)
    return df


def main():
    db = conn_mongo()
    update_code_name(db)
    last_date = get_lastest_date(db)
    current_date = time.strftime("%Y%m%d", time.localtime(time.time()))
    if current_date > last_date:
        write_k_daily(db)
        set_lastest_date(db)
    else:
        print("no upgrade data")

    # print(find_missing_k_data(db))
    # print(get_k_data_by_code(db, "000011"))


if __name__ == "__main__":
    main()
