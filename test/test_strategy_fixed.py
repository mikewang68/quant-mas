#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证修复后的增强型舆情分析策略V2
"""

import sys
import os
import pandas as pd

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2

def test_strategy_execution():
    """测试策略执行"""

    # 创建策略实例
    strategy = EnhancedPublicOpinionAnalysisStrategyV2(
        "增强型舆情分析策略V2",
        {"sentiment_threshold": 0.0, "news_count_threshold": 1}
    )

    # 模拟股票数据
    stock_data = {
        "000001": pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=10),
            'open': [10.0, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9],
            'close': [10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 11.0],
            'volume': [1000000, 1100000, 1200000, 1300000, 1400000, 1500000, 1600000, 1700000, 1800000, 1900000]
        })
    }

    print("开始测试策略执行...")

    try:
        # 执行策略
        selected_stocks = strategy.execute(stock_data)

        print(f"策略执行成功！")
        print(f"选中股票数量: {len(selected_stocks)}")

        for stock in selected_stocks:
            print(f"股票代码: {stock['code']}, 评分: {stock['score']:.4f}")

    except Exception as e:
        print(f"策略执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_strategy_execution()

