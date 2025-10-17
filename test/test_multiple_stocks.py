#!/usr/bin/env python3
"""
测试多个股票的API数据
"""

import requests
import json

def test_multiple_stocks():
    """测试多个股票的API数据"""

    stocks = ["000006", "000001", "600036", "300339"]

    for stock in stocks:
        url = f"http://localhost:5000/api/stock-kline-realtime/{stock}"

        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and data:
                    first_item = data[0]
                    print(f"\n=== 股票 {stock} ===")
                    print(f"开盘价: {first_item.get('open')}")
                    print(f"最高价: {first_item.get('high')}")
                    print(f"最低价: {first_item.get('low')}")
                    print(f"收盘价: {first_item.get('close')}")

                    # 检查数据合理性
                    open_price = first_item.get('open', 0)
                    high_price = first_item.get('high', 0)
                    low_price = first_item.get('low', 0)
                    close_price = first_item.get('close', 0)

                    if high_price < low_price:
                        print("❌ 数据异常：最高价 < 最低价")
                    if open_price > 100 or close_price > 100:
                        print("❌ 数据异常：价格异常高")
                    if abs(open_price - close_price) > 10:
                        print("❌ 数据异常：开盘收盘价差过大")
                else:
                    print(f"股票 {stock}: 没有数据")
            else:
                print(f"股票 {stock}: API请求失败，状态码: {response.status_code}")

        except Exception as e:
            print(f"股票 {stock}: 测试失败: {e}")

if __name__ == "__main__":
    test_multiple_stocks()

