#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试akshare数据获取功能
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.akshare_client import akshare_client

def test_akshare_data():
    """测试akshare数据获取"""
    print("=== akshare数据获取测试 ===")
    print(f"当前系统时间: {datetime.now().strftime('%Y-%m-%d')}")

    # 测试股票代码
    test_codes = ["000001", "000002", "600000"]

    # 1. 测试获取近期历史数据（应该能获取到）
    print("\n1. 测试获取近期历史数据（3个月前到现在）:")
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    print(f"请求日期范围: {start_date} 到 {end_date}")

    for code in test_codes[:1]:  # 只测试一个代码
        print(f"\n测试股票: {code}")
        try:
            data = akshare_client.get_daily_k_data(
                code=code,
                start_date=start_date,
                end_date=end_date,
                adjust_type="qfq"
            )
            if data.empty:
                print(f"  未获取到数据")
            else:
                print(f"  成功获取 {len(data)} 条记录")
                print(f"  数据日期范围: {data['date'].min()} 到 {data['date'].max()}")
        except Exception as e:
            print(f"  获取数据时出错: {e}")

    # 2. 测试获取2024年数据（应该能获取到）
    print("\n2. 测试获取2024年数据:")
    try:
        data = akshare_client.get_daily_k_data(
            code="000001",
            start_date="2024-01-01",
            end_date="2024-12-31",
            adjust_type="qfq"
        )
        if data.empty:
            print("  未获取到2024年数据")
        else:
            print(f"  成功获取2024年数据 {len(data)} 条记录")
            print(f"  数据日期范围: {data['date'].min()} 到 {data['date'].max()}")
    except Exception as e:
        print(f"  获取2024年数据时出错: {e}")

    # 3. 测试获取2025年数据（应该获取不到）
    print("\n3. 测试获取2025年数据:")
    try:
        data = akshare_client.get_daily_k_data(
            code="000001",
            start_date="2025-01-01",
            end_date="2025-12-31",
            adjust_type="qfq"
        )
        if data.empty:
            print("  未获取到2025年数据（正常，因为2025年还没到）")
        else:
            print(f"  成功获取2025年数据 {len(data)} 条记录")
            print(f"  数据日期范围: {data['date'].min()} 到 {data['date'].max()}")
    except Exception as e:
        print(f"  获取2025年数据时出错: {e}")

    # 4. 测试获取跨年数据（2023-2024）
    print("\n4. 测试获取跨年数据（2023-2024）:")
    try:
        data = akshare_client.get_daily_k_data(
            code="000001",
            start_date="2023-01-01",
            end_date="2024-12-31",
            adjust_type="qfq"
        )
        if data.empty:
            print("  未获取到跨年数据")
        else:
            print(f"  成功获取跨年数据 {len(data)} 条记录")
            print(f"  数据日期范围: {data['date'].min()} 到 {data['date'].max()}")
    except Exception as e:
        print(f"  获取跨年数据时出错: {e}")

if __name__ == "__main__":
    test_akshare_data()

