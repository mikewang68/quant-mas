#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the Enhanced Public Opinion Analysis Strategy V2 with detailed value output
"""

import sys
import os
import pandas as pd

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2

def test_detailed_value():
    """Test the strategy with detailed value output"""
    print("Testing Enhanced Public Opinion Analysis Strategy V2 with detailed value output...")

    # Create strategy instance without database manager for testing
    strategy = EnhancedPublicOpinionAnalysisStrategyV2(
        name="增强型舆情分析策略V2测试"
    )

    # Test with a single stock
    test_stock_code = "000001"  # Ping An Bank
    test_stock_name = "平安银行"

    # Create mock stock data (empty DataFrame is fine for this strategy)
    mock_data = pd.DataFrame()

    # Test the analyze method
    print(f"\nAnalyzing stock {test_stock_code} ({test_stock_name})...")
    meets_criteria, reason, score = strategy.analyze(mock_data, test_stock_code, test_stock_name)

    print(f"Meets criteria: {meets_criteria}")
    print(f"Reason: {reason}")
    print(f"Score: {score}")

    # Create mock data for testing _create_detailed_value method
    mock_full_analysis = {
        "sentiment_score": 0.75,
        "sentiment_trend": "上升",
        "key_events": ["利好消息", "业绩预增", "政策支持"],
        "market_impact": "高",
        "confidence_level": 0.85,
        "analysis_summary": "该股票近期受到积极舆情影响，市场关注度较高。",
        "recommendation": "买入",
        "risk_factors": ["市场波动", "政策风险", "行业竞争"]
    }

    mock_all_data = {
        "stock_info": {"code": test_stock_code, "name": test_stock_name},
        "akshare_news": ["news1", "news2", "news3"],
        "industry_info": {"sector": "金融"},
        "guba_data": {
            "consultations": ["consult1", "consult2"],
            "research_reports": ["report1"],
            "announcements": ["announce1", "announce2", "announce3"],
            "hot_posts": ["post1", "post2"]
        },
        "professional_sites_data": ["data1", "data2"],
        "firecrawl_data": ["crawl1", "crawl2", "crawl3", "crawl4"],
        "qian_gu_qian_ping_data": {"rating": "积极"},
        "detailed_guba_data": {
            "user_focus": [{"date": "2023-01-01", "focus_index": 85}],
            "institutional_participation": [{"date": "2023-01-01", "participation": 75}],
            "historical_rating": [{"date": "2023-01-01", "rating": 4.5}],
            "daily_participation": [{"date": "2023-01-01", "daily_desire_rise": 10, "avg_participation_change": 5}]
        }
    }

    # Test the _create_detailed_value method
    print(f"\nTesting _create_detailed_value method...")
    detailed_value = strategy._create_detailed_value(
        "符合条件: 舆情 sentiment 分数(0.75) >= 阈值(0.0), 相关信息20条",
        0.75,
        mock_full_analysis,
        mock_all_data
    )

    print(f"Detailed value length: {len(detailed_value)} characters")
    print(f"Detailed value (first 1000 chars):\n{detailed_value[:1000]}...")

    # Check if the value contains detailed information
    if "LLM分析详情" in detailed_value:
        print("✓ Contains LLM analysis details")
    if "数据源详情" in detailed_value:
        print("✓ Contains data source details")
    if "东方财富股吧详细数据" in detailed_value:
        print("✓ Contains detailed Guba data")

if __name__ == "__main__":
    test_detailed_value()

