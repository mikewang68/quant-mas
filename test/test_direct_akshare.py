#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试akshare获取指定股票和时间的数据
"""

import akshare as ak
import pandas as pd
from datetime import datetime

def test_direct_akshare():
    """直接测试akshare"""
    print("=== 直接测试akshare ===")
    print(f"当前系统时间: {datetime.now().strftime('%Y-%m-%d')}")

    # 测试指定的股票和时间范围
    code = "001216"
    start_date = "2025-06-17"
    end_date = "2025-08-16"

    print(f"\n测试股票: {code}")
    print(f"请求日期范围: {start_date} 到 {end_date}")

    # 格式化代码（sz或sh前缀）
    if code.startswith('6'):
        formatted_code = f"sh{code}"
    else:
        formatted_code = f"sz{code}"

    print(f"格式化代码: {formatted_code}")

    try:
        # 直接调用akshare
        print("调用 ak.stock_zh_a_hist...")
        k_data = ak.stock_zh_a_hist(
            symbol=formatted_code,
            period="daily",
            start_date=start_date.replace("-", ""),
            end_date=end_date.replace("-", ""),
            adjust="qfq"
        )

        if k_data.empty:
            print("  未获取到数据")
            print("  DataFrame为空")
        else:
            print(f"  成功获取 {len(k_data)} 条记录")
            print(f"  列名: {list(k_data.columns)}")
            print("  前几行数据:")
            print(k_data.head())

    except Exception as e:
        print(f"  调用akshare时出错: {e}")
        import traceback
        traceback.print_exc()

    # 再测试一个历史时间范围
    print("\n\n测试历史时间范围（2024年）:")
    try:
        k_data_hist = ak.stock_zh_a_hist(
            symbol="sz001216",
            period="daily",
            start_date="20240101",
            end_date="20241231",
            adjust="qfq"
        )

        if k_data_hist.empty:
            print("  未获取到2024年历史数据")
        else:
            print(f"  成功获取2024年数据 {len(k_data_hist)} 条记录")
            print("  前几行数据:")
            print(k_data_hist.head())

    except Exception as e:
        print(f"  获取2024年历史数据时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_akshare()

