#!/usr/bin/env python3
"""
直接测试Akshare数据源
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.akshare_client import AkshareClient
import datetime

def test_akshare_direct():
    """直接测试Akshare数据源"""

    try:
        akshare_client = AkshareClient()

        # 测试几个股票
        stocks = ["000006", "600036", "000001"]

        for stock in stocks:
            print(f"\n=== 测试股票 {stock} ===")

            # 计算日期范围（最近1年）
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=365)

            # 获取前复权数据
            data = akshare_client.get_daily_k_data(
                code=stock,
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
                adjust_type="q"  # 前复权
            )

            if data is not None and not data.empty:
                print(f"数据条数: {len(data)}")
                print("数据列名:", list(data.columns))

                # 显示最新几条数据
                print("\n最新5条数据:")
                for i in range(min(5, len(data))):
                    row = data.iloc[i]
                    print(f"  第{i+1}条: 日期={row.get('date', 'N/A')}, 开盘={row.get('open', 'N/A')}, 最高={row.get('high', 'N/A')}, 最低={row.get('low', 'N/A')}, 收盘={row.get('close', 'N/A')}")

                # 检查是否有异常数据
                print("\n数据异常检查:")
                for i in range(min(10, len(data))):
                    row = data.iloc[i]
                    open_price = row.get('open', 0)
                    if open_price > 100:
                        print(f"  ❌ 异常数据: 日期={row.get('date', 'N/A')}, 开盘价={open_price}")

            else:
                print("没有获取到数据")

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_akshare_direct()

