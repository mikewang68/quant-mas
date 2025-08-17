#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试akshare功能
"""

import akshare as ak
import pandas as pd
from datetime import datetime

def test_akshare_directly():
    """直接测试akshare功能"""
    print("=== 直接测试akshare功能 ===")
    print(f"当前系统时间: {datetime.now().strftime('%Y-%m-%d')}")

    # 测试用户提到的股票和时间范围
    test_code = "001216"
    start_date = "20250617"
    end_date = "20250816"
    adjust_type = "qfq"

    print(f"\n测试股票: {test_code}")
    print(f"时间范围: {start_date} 到 {end_date}")
    print(f"复权类型: {adjust_type}")

    try:
        # 直接调用akshare
        print("\n1. 直接调用akshare.stock_zh_a_hist:")
        data = ak.stock_zh_a_hist(
            symbol=test_code,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust=adjust_type
        )
        if data.empty:
            print("  未获取到数据")
        else:
            print(f"  成功获取 {len(data)} 条记录")
            print(f"  列名: {list(data.columns)}")
            print(data.head())
    except Exception as e:
        print(f"  调用akshare时出错: {e}")

    # 测试获取历史数据（2024年）
    print("\n2. 测试获取2024年历史数据:")
    try:
        data = ak.stock_zh_a_hist(
            symbol=test_code,
            period="daily",
            start_date="20240101",
            end_date="20241231",
            adjust=adjust_type
        )
        if data.empty:
            print("  未获取到2024年数据")
        else:
            print(f"  成功获取2024年数据 {len(data)} 条记录")
            print(f"  数据日期范围: {data['日期'].min()} 到 {data['日期'].max()}")
    except Exception as e:
        print(f"  获取2024年数据时出错: {e}")

    # 测试获取近期历史数据
    print("\n3. 测试获取近期历史数据（最近3个月）:")
    try:
        end_date_recent = datetime.now().strftime('%Y%m%d')
        start_date_recent = (datetime.now() - pd.Timedelta(days=90)).strftime('%Y%m%d')
        print(f"  请求日期范围: {start_date_recent} 到 {end_date_recent}")

        data = ak.stock_zh_a_hist(
            symbol=test_code,
            period="daily",
            start_date=start_date_recent,
            end_date=end_date_recent,
            adjust=adjust_type
        )
        if data.empty:
            print("  未获取到近期数据")
        else:
            print(f"  成功获取近期数据 {len(data)} 条记录")
            print(f"  数据日期范围: {data['日期'].min()} 到 {data['日期'].max()}")
    except Exception as e:
        print(f"  获取近期数据时出错: {e}")

    # 测试股票代码格式化
    print("\n4. 测试股票代码格式化:")
    try:
        # 测试sz格式
        data_sz = ak.stock_zh_a_hist(
            symbol=f"sz{test_code}",
            period="daily",
            start_date="20240101",
            end_date="20241231",
            adjust=adjust_type
        )
        if data_sz.empty:
            print(f"  sz{test_code} 未获取到数据")
        else:
            print(f"  sz{test_code} 成功获取 {len(data_sz)} 条记录")
    except Exception as e:
        print(f"  测试sz{test_code}时出错: {e}")

    try:
        # 测试sh格式
        data_sh = ak.stock_zh_a_hist(
            symbol=f"sh{test_code}",
            period="daily",
            start_date="20240101",
            end_date="20241231",
            adjust=adjust_type
        )
        if data_sh.empty:
            print(f"  sh{test_code} 未获取到数据")
        else:
            print(f"  sh{test_code} 成功获取 {len(data_sh)} 条记录")
    except Exception as e:
        print(f"  测试sh{test_code}时出错: {e}")

if __name__ == "__main__":
    test_akshare_directly()

