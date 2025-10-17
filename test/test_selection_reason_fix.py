"""
测试修复selection_reason字段写入问题的脚本
"""

import sys
import os
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategies.volume_breakout_strategy import VolumeBreakoutStrategy

def test_volume_breakout_strategy():
    """测试VolumeBreakoutStrategy的analyze方法是否返回selection_reason"""
    print("=== 测试VolumeBreakoutStrategy的analyze方法 ===")

    # 创建策略实例
    strategy = VolumeBreakoutStrategy()

    # 创建测试数据
    dates = pd.date_range("2023-01-01", periods=50, freq="D")
    sample_data = pd.DataFrame({
        "date": dates,
        "open": np.random.uniform(100, 110, 50),
        "high": np.random.uniform(110, 120, 50),
        "low": np.random.uniform(90, 100, 50),
        "close": np.random.uniform(100, 110, 50),
        "volume": np.random.uniform(1000000, 2000000, 50),
    })

    # 测试analyze方法
    meets_criteria, reason, score, breakout_signal = strategy.analyze(sample_data)

    print(f"meets_criteria: {meets_criteria}")
    print(f"reason: {reason}")
    print(f"score: {score}")
    print(f"breakout_signal: {breakout_signal}")

    # 验证reason字段不为空
    assert reason is not None, "selection_reason字段不应该为None"
    assert isinstance(reason, str), "selection_reason字段应该是字符串类型"
    print("✓ selection_reason字段正确返回")

def test_strategy_execution():
    """测试策略执行是否包含selection_reason"""
    print("\n=== 测试策略执行 ===")

    # 创建策略实例
    strategy = VolumeBreakoutStrategy()

    # 创建测试数据
    dates = pd.date_range("2023-01-01", periods=50, freq="D")
    sample_data = pd.DataFrame({
        "date": dates,
        "open": np.random.uniform(100, 110, 50),
        "high": np.random.uniform(110, 120, 50),
        "low": np.random.uniform(90, 100, 50),
        "close": np.random.uniform(100, 110, 50),
        "volume": np.random.uniform(1000000, 2000000, 50),
    })

    # 模拟Weekly Selector的执行方式
    stock_data = {"000001": sample_data}

    # 使用analyze方法（Weekly Selector实际调用的方法）
    meets_criteria, reason, score, breakout_signal = strategy.analyze(sample_data)

    print(f"股票代码: 000001")
    print(f"满足条件: {meets_criteria}")
    print(f"选择原因: {reason}")
    print(f"得分: {score}")
    print(f"突破信号: {breakout_signal}")

    # 验证所有字段都存在
    assert reason is not None, "selection_reason字段不应该为None"
    print("✓ 策略执行包含selection_reason字段")

if __name__ == "__main__":
    print("开始测试selection_reason字段修复...")

    try:
        test_volume_breakout_strategy()
        test_strategy_execution()
        print("\n🎉 所有测试通过！selection_reason字段修复成功")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

