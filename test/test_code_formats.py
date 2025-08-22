#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试akshare对股票代码的处理方式
"""

import akshare as ak
import pandas as pd
from datetime import datetime

def test_code_formats():
    """测试不同的股票代码格式"""
    print("=== 测试不同的股票代码格式 ===")

    # 测试股票代码
    test_codes = ["001216", "sz001216", "sh001216"]
    start_date = "20250701"
    end_date = "20250816"

    for code in test_codes:
        print(f"\n测试代码: {code}")
        try:
            data = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
            if data.empty:
                print(f"  未获取到数据")
            else:
                print(f"  成功获取 {len(data)} 条记录")
        except Exception as e:
            print(f"  出错: {e}")

    # 测试其他股票
    print("\n\n=== 测试其他股票代码 ===")
    other_codes = ["000001", "sz000001", "sh000001", "600000", "sh600000", "sz600000"]
    start_date = "20240101"
    end_date = "20240110"

    for code in other_codes:
        print(f"\n测试代码: {code}")
        try:
            data = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
            if data.empty:
                print(f"  未获取到数据")
            else:
                print(f"  成功获取 {len(data)} 条记录")
        except Exception as e:
            print(f"  出错: {e}")

if __name__ == "__main__":
    test_code_formats()

