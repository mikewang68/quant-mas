#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的增强型舆情分析策略V2 - 验证数据组合和LLM分析
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2
from data.mongodb_manager import MongoDBManager

def test_data_combination_and_llm_analysis():
    """测试数据组合和LLM分析功能"""
    print("=== 测试数据组合和LLM分析功能 ===")

    try:
        # 初始化数据库管理器
        db_manager = MongoDBManager()

        # 创建策略实例
        strategy = EnhancedPublicOpinionAnalysisStrategyV2(
            name="增强型舆情分析策略V2",
            params={
                "sentiment_threshold": 0.0,  # 设置为0以测试所有股票
                "news_count_threshold": 1,   # 降低阈值用于测试
                "search_depth": 5,
                "time_window_hours": 24,
                "data_sources": ["akshare", "guba"],  # 只使用akshare和guba数据源
                "llm_name": "qwen3-4b"  # 明确指定LLM配置
            },
            db_manager=db_manager
        )

        print("✅ 策略初始化成功")

        # 创建测试数据
        test_stock_data = {}
        test_stocks = ["000985", "001209"]  # 测试股票代码

        # 创建空的DataFrame作为测试数据
        for stock_code in test_stocks:
            # 创建空的DataFrame，策略会从k_data集合获取实际数据
            test_stock_data[stock_code] = pd.DataFrame()

        print(f"✅ 创建测试数据，股票数量: {len(test_stock_data)}")

        # 执行策略
        print("\n=== 开始执行策略 ===")
        selected_stocks = strategy.execute(
            stock_data=test_stock_data,
            agent_name="舆情分析Agent",
            db_manager=db_manager
        )

        print(f"\n=== 策略执行结果 ===")
        print(f"选中股票数量: {len(selected_stocks)}")

        for stock in selected_stocks:
            print(f"\n股票代码: {stock['code']}")
            print(f"评分: {stock['score']:.4f}")
            print(f"详细分析: {stock['value'][:300]}...")

        print("\n✅ 策略测试完成")

    except Exception as e:
        print(f"❌ 策略测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_llm_prompt_and_response():
    """测试LLM提示词和响应处理"""
    print("\n=== 测试LLM提示词和响应处理 ===")

    try:
        # 创建策略实例
        strategy = EnhancedPublicOpinionAnalysisStrategyV2(
            name="测试策略",
            params={
                "sentiment_threshold": 0.0,
                "news_count_threshold": 1,
                "search_depth": 5,
                "time_window_hours": 24,
                "data_sources": ["akshare", "guba"]
            }
        )

        # 模拟收集到的数据
        test_data = {
            "stock_info": {"code": "000985", "name": "大庆华科"},
            "industry_info": {"行业": "化工行业", "细分": "基础化工"},
            "qian_gu_qian_ping_data": {
                "最新价": 18.78,
                "涨跌幅": -9.84,
                "换手率": 17.61,
                "市盈率": 107.55,
                "综合得分": 58.33
            },
            "detailed_guba_data": {
                "user_focus": [
                    {"date": "2024-09-20", "focus_index": 61.2},
                    {"date": "2024-09-21", "focus_index": 60.0},
                    {"date": "2024-09-22", "focus_index": 68.0}
                ],
                "institutional_participation": [
                    {"date": "2024-09-04", "participation": 14.248},
                    {"date": "2024-09-08", "participation": 11.525}
                ]
            },
            "akshare_news": [
                {
                    "title": "大庆华科发布业绩预告",
                    "publishedAt": "2024-09-29",
                    "content": "公司预计前三季度净利润同比增长50%-70%",
                    "source": "公司公告"
                },
                {
                    "title": "化工行业政策利好",
                    "publishedAt": "2024-09-28",
                    "content": "国家出台支持化工行业转型升级政策",
                    "source": "行业新闻"
                }
            ],
            "guba_data": {
                "consultations": [
                    {"title": "请问公司未来发展前景如何", "publishedAt": "2024-09-30"},
                    {"title": "近期股价波动较大，是否正常", "publishedAt": "2024-09-29"}
                ]
            },
            "professional_sites_data": [
                {
                    "title": "专业机构分析报告",
                    "publishedAt": "2024-09-25",
                    "content": "机构认为公司基本面良好，但短期存在波动风险",
                    "source": "专业分析网站"
                }
            ],
            "firecrawl_data": [
                {
                    "title": "网络分析文章",
                    "publishedAt": "2024-09-26",
                    "content": "投资者对大庆华科关注度较高，市场情绪积极",
                    "source": "财经网站"
                }
            ]
        }

        # 测试数据格式化
        print("\n=== 测试数据格式化 ===")
        formatted_data = strategy._format_data_for_llm(test_data)
        print(f"格式化数据长度: {len(formatted_data)} 字符")
        print(f"格式化数据预览:\n{formatted_data[:800]}...")

        # 测试LLM提示词生成
        print("\n=== 测试LLM提示词生成 ===")
        prompt = strategy._create_llm_prompt("000985", "大庆华科", formatted_data)
        print(f"提示词长度: {len(prompt)} 字符")
        print(f"提示词预览:\n{prompt[:500]}...")

        print("\n✅ LLM提示词和响应处理测试完成")

    except Exception as e:
        print(f"❌ LLM提示词和响应处理测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_llm_response_extraction():
    """测试LLM响应提取功能"""
    print("\n=== 测试LLM响应提取功能 ===")

    try:
        # 创建策略实例
        strategy = EnhancedPublicOpinionAnalysisStrategyV2(
            name="测试策略",
            params={
                "sentiment_threshold": 0.0,
                "news_count_threshold": 1,
                "search_depth": 5,
                "time_window_hours": 24,
                "data_sources": ["akshare", "guba"]
            }
        )

        # 测试包含<think>标签的响应
        think_response = """<think>
首先，我需要根据提供的舆情信息进行 sentiment 分析。用户要求我输出一个特定的 JSON 格式，包含多个字段。我必须严格按照给定的结构和要求来填写。

回顾用户提供的 JSON 模板：
- sentiment_score: 0-1 之间的数值（0.75 已经给出作为示例，但我要基于分析计算）
- sentiment_trend: 字符串，如 "上升"（上升）
- key_events: 数组，例如 ["利好消息", "业绩预增"]
- market_impact: 字符串，如 "高"
- confidence_level: 数值，如 0.85
- analysis_summary: 字符串，详细的分析理由（字数控制在800字以内）
- recommendation: 字符串，如 "买入"
- risk_factors: 数组，如 ["市场波动", "政策风险"]

用户指定了要输出的 JSON，但实际分析需要我基于舆情信息。用户说："请根据提供的舆情信息进行 sentiment 分析"，并给出了详细的舆情数据。我需要从这些数据中提取关键点。

分析舆情信息：
- 股票代码000985（大庆华科）属于化工行业
- AkShare新闻数据：有业绩预告、行业政策利好、技术研发进展等正面消息
- 东方财富股吧数据：用户关注指数85.2，机构参与度78.5，历史评分82.1，日度市场参与意愿76.8，整体数据较好
- 专业网站数据：有专业分析文章
- 千股千评数据：综合评分80，技术面良好，基本面稳定

基于以上分析，我认为该股票舆情整体偏正面，sentiment_score应该在0.7-0.8之间。我选择0.75作为sentiment_score。

现在输出JSON：
{"sentiment_score": 0.75, "sentiment_trend": "上升", "key_events": ["业绩预告", "行业政策利好", "技术研发进展"], "market_impact": "中", "confidence_level": 0.8, "analysis_summary": "大庆华科近期舆情整体偏正面，业绩预告显示公司经营状况良好，化工行业政策利好为公司发展提供支持，技术研发进展表明公司创新能力。股吧数据显示用户和机构关注度较高，市场参与意愿积极。综合评分80分，技术面和基本面均表现稳定。", "recommendation": "持有", "risk_factors": ["行业周期性波动", "原材料价格波动", "环保政策风险"]}
</think>"""

        # 测试直接JSON响应
        json_response = """{"sentiment_score": 0.65, "sentiment_trend": "波动", "key_events": ["业绩预告", "行业政策"], "market_impact": "中", "confidence_level": 0.7, "analysis_summary": "舆情整体中性偏正面", "recommendation": "观望", "risk_factors": ["市场风险"]}"""

        # 测试提取功能
        print("测试包含<think>标签的响应:")
        score1 = strategy._extract_sentiment_score_robust(think_response)
        print(f"提取的分数: {score1}")

        print("\n测试直接JSON响应:")
        score2 = strategy._extract_sentiment_score_robust(json_response)
        print(f"提取的分数: {score2}")

        print("\n✅ LLM响应提取测试完成")

    except Exception as e:
        print(f"❌ LLM响应提取测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("开始测试修复后的增强型舆情分析策略V2...")

    # 测试LLM提示词和响应处理
    test_llm_prompt_and_response()

    # 测试LLM响应提取功能
    test_llm_response_extraction()

    # 测试完整策略功能
    test_data_combination_and_llm_analysis()

    print("\n=== 所有测试完成 ===")

