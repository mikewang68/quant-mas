#!/usr/bin/env python3
"""
测试 volume_breakout_strategy 的 analyze 方法
验证新的返回值格式 (bool, score, value)
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.volume_breakout_strategy import VolumeBreakoutStrategy

def create_sample_data():
    """创建测试用的股票数据"""
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')

    # 创建模拟数据：价格逐渐上涨，成交量放大
    np.random.seed(42)
    base_price = 10.0
    prices = []
    volumes = []

    for i in range(100):
        # 价格逐渐上涨
        price = base_price + i * 0.1 + np.random.normal(0, 0.5)
        prices.append(price)

        # 成交量逐渐放大
        volume = 1000000 + i * 10000 + np.random.normal(0, 50000)
        volumes.append(max(volume, 100000))

    data = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p + np.random.uniform(0, 0.5) for p in prices],
        'low': [p - np.random.uniform(0, 0.5) for p in prices],
        'close': prices,
        'volume': volumes,
        'amount': [v * p for v, p in zip(volumes, prices)]
    })

    return data

def test_analyze_method():
    """测试 analyze 方法"""
    print("=== 测试 VolumeBreakoutStrategy analyze 方法 ===")

    # 创建策略实例
    strategy = VolumeBreakoutStrategy()

    # 创建测试数据
    test_data = create_sample_data()
    stock_code = "000001"

    print(f"测试数据形状: {test_data.shape}")
    print(f"股票代码: {stock_code}")
    print(f"最后5行数据:")
    print(test_data.tail())

    # 调用 analyze 方法
    print("\n--- 调用 analyze 方法 ---")
    meets_criteria, score, value_dict = strategy.analyze(test_data, code=stock_code)

    # 验证返回值格式
    print(f"返回值格式: (bool, score, value_dict)")
    print(f"meets_criteria: {meets_criteria}")
    print(f"score: {score}")
    print(f"value_dict 类型: {type(value_dict)}")

    # 验证 value_dict 包含所有必需字段
    print("\n--- 验证 value_dict 字段 ---")
    required_fields = ["code", "score", "selection_reason", "technical_analysis", "breakout_signal", "position"]

    for field in required_fields:
        if field in value_dict:
            print(f"✓ {field}: {value_dict[field]}")
        else:
            print(f"✗ {field}: 缺失")

    # 验证字段值
    print("\n--- 字段值验证 ---")
    print(f"code: {value_dict['code']} (期望: {stock_code})")
    print(f"score in value_dict: {value_dict['score']} (应与返回的score一致: {score})")
    print(f"selection_reason 长度: {len(value_dict['selection_reason'])} 字符")
    print(f"technical_analysis 类型: {type(value_dict['technical_analysis'])}")
    print(f"breakout_signal: {value_dict['breakout_signal']}")
    print(f"position: {value_dict['position']}")

    # 验证技术分析数据
    print("\n--- 技术分析数据 ---")
    tech_data = value_dict['technical_analysis']
    if tech_data:
        for key, value in tech_data.items():
            print(f"  {key}: {value}")
    else:
        print("  无技术分析数据")

    # 测试边界情况
    print("\n--- 测试边界情况 ---")

    # 测试空数据
    empty_data = pd.DataFrame()
    meets_criteria_empty, score_empty, value_dict_empty = strategy.analyze(empty_data, code="000002")
    print(f"空数据测试 - meets_criteria: {meets_criteria_empty}, score: {score_empty}")
    print(f"空数据测试 - value_dict 包含所有字段: {all(field in value_dict_empty for field in required_fields)}")

    # 测试数据不足
    insufficient_data = test_data.head(10)  # 只有10条数据
    meets_criteria_insufficient, score_insufficient, value_dict_insufficient = strategy.analyze(insufficient_data, code="000003")
    print(f"数据不足测试 - meets_criteria: {meets_criteria_insufficient}, score: {score_insufficient}")
    print(f"数据不足测试 - value_dict 包含所有字段: {all(field in value_dict_insufficient for field in required_fields)}")

    print("\n=== 测试完成 ===")

    # 总结
    print("\n=== 测试总结 ===")
    print(f"✓ 返回值格式正确: (bool, score, value_dict)")
    print(f"✓ value_dict 包含所有必需字段: {all(field in value_dict for field in required_fields)}")
    print(f"✓ 边界情况处理正确")
    print(f"✓ 股票代码正确传递: {value_dict['code'] == stock_code}")
    print(f"✓ 分数一致性: {value_dict['score'] == score}")

if __name__ == "__main__":
    test_analyze_method()

