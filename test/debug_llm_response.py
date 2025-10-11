"""
调试LLM响应脚本
用于查看增强舆情分析策略V2的完整LLM响应内容
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2

def debug_llm_response():
    """调试LLM响应"""
    try:
        print("=== 开始调试LLM响应 ===")

        # 初始化数据库管理器
        db_manager = MongoDBManager()

        # 创建策略实例
        strategy_params = {
            "data_sources": ["akshare", "firecrawl", "professional_sites", "guba"],
            "llm_name": "qwen3-4B",
            "news_count_threshold": 5,
            "sentiment_threshold": 0.6,
            "time_window_hours": 24
        }

        strategy = EnhancedPublicOpinionAnalysisStrategyV2(
            name="增强型舆情分析策略V2",
            params=strategy_params,
            db_manager=db_manager
        )

        print("策略实例化成功")

        # 测试股票数据
        stock_data = {
            "000001": None,  # 平安银行
            "600036": None   # 招商银行
        }

        print(f"开始执行策略，测试股票: {list(stock_data.keys())}")

        # 执行策略
        selected_stocks = strategy.execute(
            stock_data=stock_data,
            agent_name="舆情分析Agent",
            db_manager=db_manager
        )

        print(f"策略执行完成，选中股票数量: {len(selected_stocks)}")

        for stock in selected_stocks:
            print(f"股票: {stock['code']}, 评分: {stock['score']}")
            print(f"详细原因: {stock['value'][:500]}...")
            print("---")

        return True

    except Exception as e:
        print(f"调试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_llm_response()
    if success:
        print("=== 调试完成 ===")
    else:
        print("=== 调试失败 ===")

