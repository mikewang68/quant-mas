#!/usr/bin/env python3
"""
测试000006股票的K线数据
"""

import requests
import json

def test_000006_data():
    """测试000006股票的K线数据"""

    # 测试000006股票的K线数据
    url = "http://localhost:5000/api/stock-kline-realtime/000006"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print("=== 000006股票K线数据测试 ===")
            print(f"状态码: {response.status_code}")
            print(f"数据条数: {len(data)}")

            if data:
                # 显示最新的几条数据
                print("\n最新5条数据:")
                for i, item in enumerate(data[:5]):
                    print(f"\n第{i+1}条数据:")
                    print(f"  日期: {item.get('date')}")
                    print(f"  开: {item.get('open')}")
                    print(f"  高: {item.get('high')}")
                    print(f"  低: {item.get('low')}")
                    print(f"  收: {item.get('close')}")
                    print(f"  成交量: {item.get('volume')}")

                # 检查是否有异常数据
                print("\n=== 数据异常检查 ===")
                abnormal_data = []
                for item in data:
                    open_price = item.get('open', 0)
                    high_price = item.get('high', 0)
                    low_price = item.get('low', 0)
                    close_price = item.get('close', 0)

                    # 检查价格是否异常
                    if open_price > 100 or high_price > 100 or low_price > 100 or close_price > 100:
                        abnormal_data.append({
                            'date': item.get('date'),
                            'open': open_price,
                            'high': high_price,
                            'low': low_price,
                            'close': close_price
                        })

                if abnormal_data:
                    print(f"发现{len(abnormal_data)}条异常数据:")
                    for abnormal in abnormal_data:
                        print(f"  日期: {abnormal['date']}, 开: {abnormal['open']}, 高: {abnormal['high']}, 低: {abnormal['low']}, 收: {abnormal['close']}")
                else:
                    print("未发现异常数据")

            else:
                print("没有获取到数据")
        else:
            print(f"API请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")

    except Exception as e:
        print(f"测试失败: {e}")
        print("请确保Web服务正在运行 (http://localhost:5000)")

if __name__ == "__main__":
    test_000006_data()

