#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强型舆情分析策略V2的LLM配置加载
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2
from data.mongodb_manager import MongoDBManager

def test_llm_config_loading():
    """测试LLM配置加载"""

    # 创建数据库管理器
    db_manager = MongoDBManager()

    # 创建策略实例
    strategy = EnhancedPublicOpinionAnalysisStrategyV2(
        "增强型舆情分析策略V2",
        {"sentiment_threshold": 0.0, "news_count_threshold": 1},
        db_manager
    )

    print("=== 测试LLM配置加载 ===")

    try:
        # 测试获取LLM配置
        llm_config = strategy._get_llm_config()

        print(f"✅ 成功获取LLM配置")
        print(f"API URL: {llm_config.get('api_url')}")
        print(f"模型: {llm_config.get('model')}")
        print(f"提供商: {llm_config.get('provider')}")
        print(f"超时时间: {llm_config.get('timeout')}")

        # 验证配置是否正确
        expected_model = "qwen3-4B"
        actual_model = llm_config.get('model')

        if actual_model == expected_model:
            print(f"✅ 模型名称正确: {actual_model}")
        else:
            print(f"❌ 模型名称不匹配，期望: {expected_model}, 实际: {actual_model}")

        # 测试默认配置
        print("\n=== 测试默认LLM配置 ===")
        default_config = strategy._get_default_llm_config()
        print(f"默认API URL: {default_config.get('api_url')}")
        print(f"默认模型: {default_config.get('model')}")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm_config_loading()

