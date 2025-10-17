#!/usr/bin/env python3
"""
测试API返回的原始数据
"""

import requests
import json

def test_api_raw_data():
    """测试API返回的原始数据"""

    # 测试600036股票的K线数据
    url = "http://localhost:5000/api/stock-kline-realtime/600036"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print("=== API返回的原始数据 ===")
            print(f"状态码: {response.status_code}")
            print(f"数据条数: {len(data)}")

            if data:
                # 显示第一条数据的完整内容
                first_item = data[0]
                print("\n第一条数据的完整内容:")
                print(json.dumps(first_item, indent=2, ensure_ascii=False))

                # 检查字段类型
                print("\n=== 字段类型检查 ===")
                for key, value in first_item.items():
                    print(f"  {key}: {value} (类型: {type(value)})")

                # 检查是否有异常值
                print("\n=== 异常值检查 ===")
                open_price = first_item.get('open', 0)
                high_price = first_item.get('high', 0)
                low_price = first_item.get('low', 0)
                close_price = first_item.get('close', 0)

                print(f"开盘价: {open_price}")
                print(f"最高价: {high_price}")
                print(f"最低价: {low_price}")
                print(f"收盘价: {close_price}")

                if open_price > 100:
                    print("❌ 开盘价异常高")
                if high_price < low_price:
                    print("❌ 最高价 < 最低价")

            else:
                print("没有获取到数据")
        else:
            print(f"API请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")

    except Exception as e:
        print(f"测试失败: {e}")
        print("请确保Web服务正在运行 (http://localhost:5000)")

if __name__ == "__main__":
    test_api_raw_data()

