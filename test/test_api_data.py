#!/usr/bin/env python3
"""
测试API返回的数据格式
"""

import requests
import json

def test_api_data():
    """测试API返回的数据格式"""

    # 测试000006股票的K线数据
    url = "http://localhost:5000/api/stock-kline-realtime/000006"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print("=== API返回数据格式测试 ===")
            print(f"状态码: {response.status_code}")
            print(f"数据类型: {type(data)}")

            # 检查数据结构
            if isinstance(data, list):
                print(f"数据条数: {len(data)}")
                if data:
                    first_item = data[0]
                    print("\n第一条数据的字段:")
                    for key, value in first_item.items():
                        print(f"  {key}: {value}")

                    print("\n=== 字段映射验证 ===")
                    print(f"开盘价字段: 'open' = {first_item.get('open')}")
                    print(f"最高价字段: 'high' = {first_item.get('high')}")
                    print(f"最低价字段: 'low' = {first_item.get('low')}")
                    print(f"收盘价字段: 'close' = {first_item.get('close')}")

                    # 验证数据顺序
                    print("\n=== 数据顺序验证 ===")
                    print(f"数据数组: [{first_item.get('open')}, {first_item.get('high')}, {first_item.get('low')}, {first_item.get('close')}]")

            elif isinstance(data, dict):
                print(f"数据条数: {len(data.get('data', []))}")
                if data.get('data'):
                    first_item = data['data'][0]
                    print("\n第一条数据的字段:")
                    for key, value in first_item.items():
                        print(f"  {key}: {value}")

                    print("\n=== 字段映射验证 ===")
                    print(f"开盘价字段: 'open' = {first_item.get('open')}")
                    print(f"最高价字段: 'high' = {first_item.get('high')}")
                    print(f"最低价字段: 'low' = {first_item.get('low')}")
                    print(f"收盘价字段: 'close' = {first_item.get('close')}")

                    # 验证数据顺序
                    print("\n=== 数据顺序验证 ===")
                    print(f"数据数组: [{first_item.get('open')}, {first_item.get('high')}, {first_item.get('low')}, {first_item.get('close')}]")
            else:
                print(f"未知的数据类型: {type(data)}")
                return

        else:
            print(f"API请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")

    except Exception as e:
        print(f"测试失败: {e}")
        print("请确保Web服务正在运行 (http://localhost:5000)")

if __name__ == "__main__":
    test_api_data()

