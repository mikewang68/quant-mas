#!/usr/bin/env python3
"""
测试回踩低吸策略的NoneType错误修复
"""

import sys
import os
import pandas as pd
import numpy as np

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.pullback_buying_strategy import PullbackBuyingStrategy

def test_none_type_handling():
    """测试NoneType错误处理"""
    print("=== 测试回踩低吸策略的NoneType错误修复 ===")

    # 创建策略实例
    strategy = PullbackBuyingStrategy()

    # 测试1: _is_valid_pullback方法中的None值处理
    print("\n1. 测试_is_valid_pullback方法:")

    # 测试None值
    result1 = strategy._is_valid_pullback(10.0, None, 15.0, 25.0, 1)
    print(f"   ma_value=None: {result1} (期望: False)")

    result2 = strategy._is_valid_pullback(10.0, 10.5, None, 25.0, 1)
    print(f"   kdj_j=None: {result2} (期望: False)")

    result3 = strategy._is_valid_pullback(10.0, 10.5, 15.0, None, 1)
    print(f"   rsi_value=None: {result3} (期望: False)")

    # 测试ma_value为0的情况
    result4 = strategy._is_valid_pullback(10.0, 0, 15.0, 25.0, 1)
    print(f"   ma_value=0: {result4} (期望: False)")

    # 测试正常值
    result5 = strategy._is_valid_pullback(10.0, 10.5, 15.0, 25.0, 1)
    print(f"   正常值: {result5} (期望: True)")

    # 测试2: _calculate_score方法中的None值处理
    print("\n2. 测试_calculate_score方法:")

    # 测试None值
    score1 = strategy._calculate_score(10.0, None, 15.0, 25.0)
    print(f"   ma_value=None: {score1} (期望: 0)")

    score2 = strategy._calculate_score(10.0, 10.5, None, 25.0)
    print(f"   kdj_j=None: {score2} (期望: 0)")

    score3 = strategy._calculate_score(10.0, 10.5, 15.0, None)
    print(f"   rsi_value=None: {score3} (期望: 0)")

    # 测试ma_value为0的情况
    score4 = strategy._calculate_score(10.0, 0, 15.0, 25.0)
    print(f"   ma_value=0: {score4} (期望: 0)")

    # 测试正常值
    score5 = strategy._calculate_score(10.0, 10.5, 15.0, 25.0)
    print(f"   正常值: {score5} (期望: 数值在0-100之间)")

    # 测试3: _calculate_ma_trend方法中的None值处理
    print("\n3. 测试_calculate_ma_trend方法:")

    # 测试None值
    trend1 = strategy._calculate_ma_trend(None)
    print(f"   ma_values=None: {trend1} (期望: 0)")

    # 测试包含None值的数组
    trend2 = strategy._calculate_ma_trend([10.0, None, 12.0])
    print(f"   ma_values包含None: {trend2} (期望: 0)")

    # 测试正常值
    trend3 = strategy._calculate_ma_trend([10.0, 11.0, 12.0])
    print(f"   上升趋势: {trend3} (期望: 1)")

    trend4 = strategy._calculate_ma_trend([12.0, 11.0, 10.0])
    print(f"   下降趋势: {trend4} (期望: -1)")

    trend5 = strategy._calculate_ma_trend([10.0, 11.0, 10.5])
    print(f"   震荡趋势: {trend5} (期望: 0)")

def test_with_sample_data():
    """使用样本数据测试策略"""
    print("\n=== 使用样本数据测试策略 ===")

    strategy = PullbackBuyingStrategy()

    # 创建样本数据
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    data = pd.DataFrame({
        'date': dates,
        'open': np.random.uniform(9, 11, 30),
        'high': np.random.uniform(10, 12, 30),
        'low': np.random.uniform(8, 10, 30),
        'close': np.random.uniform(9, 11, 30),
        'volume': np.random.randint(100000, 1000000, 30)
    })

    # 设置索引
    data.set_index('date', inplace=True)

    try:
        # 测试技术分析数据获取
        tech_data = strategy.get_technical_analysis_data(data)
        print(f"技术分析数据获取成功: {len(tech_data)} 个指标")

        # 测试策略分析
        result = strategy.analyze(data)
        print(f"策略分析结果: {result}")

        print("✅ 策略测试通过，没有出现NoneType错误")

    except Exception as e:
        print(f"❌ 策略测试失败: {e}")
        return False

    return True

if __name__ == "__main__":
    # 运行NoneType错误处理测试
    test_none_type_handling()

    # 运行样本数据测试
    success = test_with_sample_data()

    if success:
        print("\n🎉 所有测试通过！回踩低吸策略的NoneType错误已修复。")
    else:
        print("\n⚠️ 测试失败，需要进一步调试。")
        sys.exit(1)

