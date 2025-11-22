#!/usr/bin/env python
# coding=utf-8

import akshare as ak
import pandas as pd
from pymongo import MongoClient
import time
import json
import sys
import os
from datetime import datetime
import requests

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the MongoDB configuration from the project
from config.mongodb_config import MongoDBConfig

# from utils.network_error_handler import handle_network_error  # Unused import
# from utils.enhanced_router_control import TPLinkWAN2Controller  # Unused import

# 全局IP使用记录数组，长度为50
ip_used = []
MAX_IP_HISTORY = 50


def get_current_ip():
    """获取当前ISP提供的IP地址"""
    try:
        # 使用最方便的IP查询服务 - 直接返回纯文本IP
        service = "https://ip.3322.net/"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(service, headers=headers, timeout=10)
        if response.status_code == 200:
            # 直接返回响应内容，不需要解析
            ip = response.text.strip()
            print(f"获取到当前IP: {ip}")
            return ip
        else:
            print(f"IP查询服务返回状态码: {response.status_code}")
            return "unknown"

    except Exception as e:
        print(f"获取IP地址失败: {e}")
        return "unknown"


def is_ip_used(ip):
    """检查IP是否已经在使用记录中"""
    global ip_used
    return ip in ip_used


def add_ip_to_history(ip):
    """将IP添加到使用记录中"""
    global ip_used

    # 如果IP已经在记录中，不需要重复添加
    if ip in ip_used:
        return

    # 如果数组已满，删除第一个元素
    if len(ip_used) >= MAX_IP_HISTORY:
        ip_used.pop(0)

    # 添加新IP到数组末尾
    ip_used.append(ip)
    print(f"IP {ip} 已添加到使用记录，当前记录数: {len(ip_used)}")


def switch_to_new_ip():
    """切换到新的IP地址，确保不使用重复的IP"""
    global ip_used

    print("开始IP轮换过程...")
    print(f"当前IP使用记录: {ip_used}")

    # 使用优化版路由器控制器
    from utils.optimized_router_control import OptimizedTPLinkWAN2Controller

    controller = OptimizedTPLinkWAN2Controller(
        router_ip="192.168.1.1",
        username="wangdg68",
        password="wap951020ZJL",
        headless=True,
        reuse_session=True
    )

    max_attempts = 10  # 最大尝试次数
    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        print(f"\n第 {attempt} 次尝试切换IP...")

        # 执行IP切换
        success = controller.switch_ip()
        if not success:
            print("IP切换失败，继续尝试...")
            continue

        # 等待网络稳定
        print("等待网络稳定...")
        time.sleep(15)

        # 获取新IP
        new_ip = get_current_ip()

        if new_ip == "unknown":
            print("无法获取新IP，继续尝试...")
            continue

        # 检查IP是否重复
        if not is_ip_used(new_ip):
            print(f"✅ 成功获取新IP: {new_ip} (未使用过)")
            add_ip_to_history(new_ip)
            print(f"✅ IP切换成功！当前IP使用记录数组: {ip_used}")
            # 注意：不关闭浏览器，保持会话
            return True
        else:
            print(f"⚠️ 获取的IP {new_ip} 已在使用记录中，继续尝试...")

    print(f"❌ 经过 {max_attempts} 次尝试后仍无法获取新IP")
    # 关闭会话
    controller.close()
    return False


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


def get_stocks_to_update(db, force_update_missing=False):
    """
    获取需要更新的股票代码列表
    条件：last_updated字段小于或等于update_date数据集中的latest，或是空的股票集合
    """
    # 获取最新的更新日期
    latest_date = get_lastest_date()

    # 查询条件：last_updated为空或者小于latest_date
    query = {
        "$or": [
            {"last_updated": {"$exists": False}},
            {"last_updated": {"$lt": latest_date}},
        ]
    }

    # 如果是强制更新缺失数据，则查找在k_data中没有数据的股票
    if force_update_missing:
        k_data_collection = db["k_data"]
        code_collection = db["code"]

        # 获取所有股票代码
        all_codes_cursor = code_collection.find({}, {"code": 1})
        all_codes = [doc["code"] for doc in all_codes_cursor]

        # 找出在k_data中没有数据的股票代码
        missing_codes = []
        for code in all_codes:
            if k_data_collection.count_documents({"代码": code}) == 0:
                missing_codes.append(code)

        # 如果有缺失的代码，只返回这些代码
        if missing_codes:
            query = {"code": {"$in": missing_codes}}
        else:
            # 如果没有缺失的代码，返回空DataFrame
            return pd.DataFrame(columns=["_id", "code", "name", "last_updated"])

    my_coll = db["code"]
    cursor = my_coll.find(query)
    df = pd.DataFrame(cursor)

    # 如果DataFrame为空，返回空的DataFrame但保持列结构
    if df.empty:
        return pd.DataFrame(columns=["_id", "code", "name", "last_updated"])

    return df


# 获取上次更新时间
def get_lastest_date():
    # 原来的语句保留，注释掉
    # str_lastest = db.get_collection("update_date").find_one()
    # last_date = str_lastest["lastest"]
    # return last_date

    # 返回当前日期，格式为"20250930"
    return time.strftime("%Y%m%d", time.localtime(time.time()))


# 获取数据库中存储的上次更新时间
def get_db_lastest_date(db):
    str_lastest = db.get_collection("update_date").find_one()
    if str_lastest and "lastest" in str_lastest:
        return str_lastest["lastest"]
    else:
        # 如果没有记录，返回一个较早的日期
        return "20200101"


# 设置本次更新时间
def set_lastest_date(db):
    str_lastest = db.get_collection("update_date").find_one()
    last_date = str_lastest["lastest"]
    update_date = time.strftime("%Y%m%d", time.localtime(time.time()))
    db.get_collection("update_date").update_one(
        {"lastest": last_date}, {"$set": {"lastest": update_date}}
    )
    return


# 写日k线 - 仅负责从akshare获取数据并写入k_data集合
def write_k_daily(db, code, start_date="") -> bool:
    """
    从akshare获取指定股票代码的日K线数据并写入k_data集合

    :param db: MongoDB数据库连接
    :param code: 股票代码
    :param start_date: 开始日期，格式为"YYYYMMDD"，如果为空则获取全部数据
    :return: 成功返回True，失败返回False
    """
    end_date = datetime.now().strftime("%Y%m%d")

    try:
        print(f"daily: {code}")
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

            print(f"Successfully downloaded data for code: {code}")
            return True
        else:
            print(f"Warning: No data found for code {code}")
            return True

    except Exception as e:
        print(f"Error downloading data for code {code}: {str(e)}")

        # 使用公共网络错误重试函数
        from utils.network_retry_handler import handle_network_error_with_retry

        if not handle_network_error_with_retry(e, max_retries=3, retry_delay=2):
            print(f"经过重试后仍然失败，跳过股票{code}")
        return False


def should_update_data(db):
    """
    判断是否需要更新数据
    使用 ak.tool_trade_date_hist_sina() 获取交易日历，
    如果当前日期与 update_date 数据集中的 lastest 日期之间有交易日，则返回 True，否则返回 False
    """
    # 获取数据库中存储的上次更新时间
    last_update_date = get_db_lastest_date(db)

    # 获取当前日期
    current_date = datetime.now().strftime("%Y%m%d")

    try:
        # 获取交易日历
        trade_dates_df = ak.tool_trade_date_hist_sina()

        # 确保日期列是 datetime 类型
        trade_dates_df["trade_date"] = pd.to_datetime(trade_dates_df["trade_date"])

        # 转换日期格式用于比较
        last_update_dt = pd.to_datetime(last_update_date)
        current_dt = pd.to_datetime(current_date)

        # 筛选出在上次更新日期和当前日期之间的交易日
        mask = (trade_dates_df["trade_date"] > last_update_dt) & (
            trade_dates_df["trade_date"] <= current_dt
        )
        trade_dates_in_range = trade_dates_df[mask]

        # 如果有交易日，则需要更新
        return not trade_dates_in_range.empty
    except Exception as e:
        print(f"Error checking trade dates: {e}")
        # 出错时默认需要更新
        return True


def is_first_trading_day_of_month():
    """
    判断今天是否是当月的第一个交易日
    """
    try:
        # 获取当前日期
        current_date = time.strftime("%Y%m%d", time.localtime(time.time()))
        current_dt = pd.to_datetime(current_date)

        # 获取交易日历
        trade_dates_df = ak.tool_trade_date_hist_sina()
        trade_dates_df["trade_date"] = pd.to_datetime(trade_dates_df["trade_date"])

        # 获取当前年份和月份
        current_year = current_dt.year
        current_month = current_dt.month

        # 筛选出当前月份的交易日
        month_trade_dates = trade_dates_df[
            (trade_dates_df["trade_date"].dt.year == current_year)
            & (trade_dates_df["trade_date"].dt.month == current_month)
        ]

        # 如果当前月份没有交易日，返回False
        if month_trade_dates.empty:
            return False

        # 获取当前月份的第一个交易日
        first_trading_day = month_trade_dates["trade_date"].min()

        # 判断今天是否是第一个交易日
        return current_dt.date() == first_trading_day.date()

    except Exception as e:
        print(f"Error checking first trading day: {e}")
        # 出错时默认返回False，不执行行业更新
        return False


def update_industry(db):
    """
    更新股票代码表中的行业、市盈率、市净率信息

    :param db: MongoDB数据库连接
    """
    print("开始更新行业、市盈率、市净率信息...")

    try:
        # 获取所有行业板块
        industry_boards = ak.stock_board_industry_name_em()

        all_stocks = []
        for industry in industry_boards["板块名称"]:
            try:
                stocks = ak.stock_board_industry_cons_em(symbol=industry)
                stocks["industry"] = industry
                all_stocks.append(stocks)
            except Exception as e:
                print(f"获取行业 {industry} 的成分股失败: {str(e)}")
                continue

        if not all_stocks:
            print("未能获取任何行业数据")
            return

        result_df = pd.concat(all_stocks, ignore_index=True)

        # 确保必要的字段存在
        required_columns = ["代码", "industry", "市盈率-动态", "市净率"]
        for col in required_columns:
            if col not in result_df.columns:
                print(f"警告: 结果数据中缺少字段 '{col}'")
                return

        # 更新code数据集
        my_coll = db["code"]
        updated_count = 0

        for _, row in result_df.iterrows():
            stock_code = row["代码"]
            industry = row["industry"]
            pe = row["市盈率-动态"]
            pb = row["市净率"]

            # 更新或插入行业、PE、PB信息
            update_data = {"industry": industry, "PE": pe, "PB": pb}

            # 移除空值
            update_data = {k: v for k, v in update_data.items() if pd.notna(v)}

            if update_data:
                result = my_coll.update_one(
                    {"_id": stock_code},
                    {"$set": update_data},
                    upsert=False,  # 只更新已存在的文档，不创建新文档
                )

                if result.modified_count > 0:
                    updated_count += 1

        print(f"成功更新 {updated_count} 只股票的行业、市盈率、市净率信息")

    except Exception as e:
        print(f"更新行业信息时发生错误: {str(e)}")


def build_concept_index():
    """
    建立概念板块索引，提高查询效率
    """
    # 获取所有概念板块
    all_concepts = ak.stock_board_concept_name_em()

    concept_index = {}
    stock_concept_map = {}

    print("正在构建概念索引...")
    for concept in all_concepts["板块名称"]:
        try:
            # 获取概念成分股
            concept_stocks = ak.stock_board_concept_cons_em(symbol=concept)
            concept_index[concept] = concept_stocks["代码"].tolist()

            # 建立股票到概念的映射
            for stock_code in concept_stocks["代码"]:
                if stock_code not in stock_concept_map:
                    stock_concept_map[stock_code] = []
                stock_concept_map[stock_code].append(concept)

        except Exception as e:
            print(f"获取概念{concept}失败: {e}")
            # 使用公共网络错误重试函数
            from utils.network_retry_handler import handle_network_error_with_retry

            handle_network_error_with_retry(e)
            print(f"跳过概念{concept}，继续处理其他概念")
            continue

    return concept_index, stock_concept_map


def update_conception(db):
    """
    更新股票代码表中的概念信息

    :param db: MongoDB数据库连接
    """
    print("开始更新概念信息...")

    try:
        # 构建概念索引
        concept_index, stock_concept_map = build_concept_index()

        if not stock_concept_map:
            print("未能获取任何概念数据")
            return

        # 更新code数据集
        my_coll = db["code"]
        updated_count = 0

        # 遍历股票概念映射，更新每个股票的概念信息
        for stock_code, concepts in stock_concept_map.items():
            # 更新概念信息
            update_data = {"conception": concepts}

            result = my_coll.update_one(
                {"_id": stock_code},
                {"$set": update_data},
                upsert=False,  # 只更新已存在的文档，不创建新文档
            )

            if result.modified_count > 0:
                updated_count += 1

        print(f"成功更新 {updated_count} 只股票的概念信息")

    except Exception as e:
        print(f"更新概念信息时发生错误: {str(e)}")
        # 使用公共网络错误重试函数
        from utils.network_retry_handler import handle_network_error_with_retry

        if handle_network_error_with_retry(e):
            print("网络错误处理成功，建议重新运行更新")
        else:
            print("网络错误处理失败")


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
                                    value = value.strftime("%Y-%m-%d")
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
                                    value = value.strftime("%Y-%m-%d")
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
                                    value = value.strftime("%Y-%m-%d")
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
                    # 创建新文档，使用股票代码作为_id，同时保留股票代码字段
                    record_data = {"_id": stock_code, "股票代码": stock_code}

                    # 按dataframe列顺序添加字段，跳过"序号"字段
                    for col in xjll_data.columns:
                        if col not in ["序号"]:
                            value = row[col]
                            if pd.notna(value):
                                # 转换datetime.date对象为字符串
                                if isinstance(value, datetime.date):
                                    value = value.strftime("%Y-%m-%d")
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
            # print(f"盈利预测数据列名: {list(forecast_data.columns)}")
            forecast_collection = db["fin_forecast"]

            # 清空集合
            forecast_collection.delete_many({})

            # 去重处理：按股票代码分组，保留每个股票的最新记录（假设序号较大的记录较新）
            unique_forecast_data = forecast_data.sort_values(
                "序号", ascending=False
            ).drop_duplicates(subset=["代码"], keep="first")
            print(f"去重后保留 {len(unique_forecast_data)} 条唯一股票记录")

            inserted_count = 0
            for _, row in unique_forecast_data.iterrows():
                # 使用"代码"字段作为股票代码
                stock_code = row.get("代码", "")
                if stock_code:
                    # 创建新文档，使用股票代码作为_id，同时保留股票代码字段
                    record_data = {"_id": stock_code, "股票代码": stock_code}

                    # 按dataframe列顺序添加字段，跳过"序号"字段，但保留"代码"字段作为"股票代码"
                    for col in unique_forecast_data.columns:
                        if col not in ["序号"]:
                            value = row[col]
                            if pd.notna(value):
                                # 转换datetime.date对象为字符串
                                if isinstance(value, datetime.date):
                                    value = value.strftime("%Y-%m-%d")
                                # 将"名称"字段重命名为"股票简称"
                                if col == "名称":
                                    record_data["股票简称"] = value
                                # 将"代码"字段重命名为"股票代码"（已在上面的record_data中设置）
                                elif col == "代码":
                                    record_data["股票代码"] = value
                                else:
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


# 获取需要更新的股票列表
def get_should_update_code(db):
    """
    获取需要更新的股票代码
    逻辑：
    1. 如果update_date的lastest字段的日期与当前日期之间有交易日，则返回code中所有股票代码
    2. 如果没有交易日，则检查code数据集中的last_updated字段的日期小于update_date数据集中lastest的股票代码
    """
    # 检查是否有交易日需要更新
    # 有交易日，返回没有更新的所有股票代码
    latest_date = datetime.now().strftime("%Y%m%d")

    if not should_update_data(db):
        # 没有交易日，返回last_updated小于lastest的股票代码
        latest_date = get_db_lastest_date(db)
    query = {
        "$or": [
            {"last_updated": {"$exists": False}},
            {"last_updated": {"$lt": latest_date}},
        ]
    }
    my_coll = db["code"]
    cursor = my_coll.find(query)
    df = pd.DataFrame(cursor)
    return df


def main():
    db = conn_mongo()
    update_code_name(db)

    # 检查是否是当月第一个交易日，如果是则更新行业信息、概念和财务数据
    if is_first_trading_day_of_month():
        print(
            "Today is the first trading day of the month. Updating industry, conception, PE, and PB information..."
        )
        update_industry(db)
        update_conception(db)
        print("Updating finance data...")
        update_finance_data(db)
    else:
        print(
            "Today is not the first trading day of the month. Skipping industry and finance data update."
        )

    # 获取需要更新的股票列表
    df = get_should_update_code(db)
    # 下载df中所有股票的日线数据
    while not df.empty:
        for _, row in df.iterrows():
            code = row["code"]
            start_date = row.get("last_updated", "")
            is_success = write_k_daily(db, code, start_date)
            if is_success:
                current_date = datetime.now().strftime("%Y%m%d")
                db["code"].update_one(
                    {"_id": code},
                    {"$set": {"last_updated": current_date}},
                    upsert=True,
                )
        df = get_should_update_code(db)
    set_lastest_date(db)


if __name__ == "__main__":
    main()
