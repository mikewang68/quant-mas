#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试脚本：验证延时功能
"""

import time

def test_delay_function():
    """测试延时功能"""
    print("🔍 测试延时功能")
    print("="*50)

    # 模拟处理多只股票
    stock_codes = ["000001", "000002", "000003", "000004", "000005"]

    print("开始处理股票数据...")
    start_time = time.time()

    for i, code in enumerate(stock_codes, 1):
        print(f"处理第 {i} 只股票: {code}")

        # 模拟数据处理
        # 这里可以是实际的数据获取和处理逻辑
        time.sleep(0.1)  # 模拟数据处理时间

        # 添加1秒延时（模拟修改后的功能）
        print(f"  -> 股票 {code} 处理完成，延时1秒...")
        delay_start = time.time()
        time.sleep(1)
        delay_end = time.time()
        actual_delay = delay_end - delay_start
        print(f"  -> 实际延时: {actual_delay:.2f} 秒")

        print()

    end_time = time.time()
    total_time = end_time - start_time

    print(f"✅ 总处理时间: {total_time:.2f} 秒")
    expected_time = len(stock_codes) * 1.1 + (len(stock_codes) - 1) * 1  # 处理时间 + 延时时间
    print(f"⏱️  预期时间: {expected_time:.2f} 秒")

    if abs(total_time - expected_time) < 1:
        print("✅ 延时功能工作正常")
    else:
        print("⚠️  延时功能可能存在问题")

if __name__ == "__main__":
    test_delay_function()

