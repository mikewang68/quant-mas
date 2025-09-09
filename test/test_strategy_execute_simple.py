#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test to verify the execute method structure
"""

import sys
import os
import pandas as pd
from unittest.mock import Mock, patch

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2

def test_execute_structure():
    """Test the execute method structure"""
    print("Testing Enhanced Public Opinion Analysis Strategy V2 execute method structure...")

    # Create strategy instance
    strategy = EnhancedPublicOpinionAnalysisStrategyV2(
        name="增强型舆情分析策略V2测试"
    )

    # Mock the analyze_public_opinion method to return predefined results
    def mock_analyze_public_opinion(stock_code, stock_name):
        # Return mock results
        return (
            True,  # meets_criteria
            f"符合条件: 舆情 sentiment 分数(0.65) >= 阈值(0.0), 相关信息46条",  # reason
            0.65,  # sentiment_score
            {  # full_analysis
                "sentiment_score": 0.65,
                "sentiment_trend": "稳定",
                "key_events": ["行业利好", "政策支持"],
                "market_impact": "中等",
                "confidence_level": 0.78,
                "analysis_summary": "该股票舆情分析结果较为积极。",
                "recommendation": "持有",
                "risk_factors": ["市场波动", "行业风险"]
            }
        )

    # Mock the collect_all_data method to return predefined results
    def mock_collect_all_data(stock_code, stock_name):
        # Return mock data
        return {
            "stock_info": {"code": stock_code, "name": stock_name},
            "akshare_news": ["news1", "news2"] * 10,  # 20 items
            "industry_info": {"sector": "科技"},
            "guba_data": {
                "consultations": ["consult1"] * 5,
                "research_reports": ["report1"] * 3,
                "announcements": ["announce1"] * 2,
                "hot_posts": ["post1"] * 5
            },
            "professional_sites_data": ["data1"] * 3,
            "firecrawl_data": ["crawl1"] * 2,
            "qian_gu_qian_ping_data": {"综合评分": 7.5},
            "detailed_guba_data": {
                "user_focus": [{"date": "2023-01-01", "focus_index": 80}] * 2,
                "institutional_participation": [{"date": "2023-01-01", "participation": 70}] * 2,
                "historical_rating": [{"date": "2023-01-01", "rating": 4.0}] * 2,
                "daily_participation": [{"date": "2023-01-01", "daily_desire_rise": 5, "avg_participation_change": 3}] * 2
            }
        }

    # Mock the save_to_pool method
    def mock_save_to_pool(*args, **kwargs):
        return True

    # Patch the methods
    strategy.analyze_public_opinion = mock_analyze_public_opinion
    strategy.collect_all_data = mock_collect_all_data
    strategy.save_to_pool = mock_save_to_pool

    # Create mock stock data
    stock_data = {
        "000001": pd.DataFrame(),
        "000002": pd.DataFrame()
    }

    # Mock database manager
    mock_db_manager = Mock()

    # Test the execute method
    print(f"\nExecuting strategy on {len(stock_data)} stocks...")
    with patch.object(strategy, 'log_info'), patch.object(strategy, 'log_warning'):
        results = strategy.execute(stock_data, "舆情分析Agent", mock_db_manager)

    print(f"Number of selected stocks: {len(results)}")

    # Print detailed information for each selected stock
    for i, stock in enumerate(results):
        print(f"\nStock {i+1}:")
        print(f"  Code: {stock.get('code')}")
        print(f"  Score: {stock.get('score')}")
        print(f"  Value length: {len(stock.get('value', ''))} characters")

        # Show first 300 characters of the value
        value = stock.get('value', '')
        if value:
            print(f"  Value (first 300 chars): {value[:300]}...")
        else:
            print("  No value data found")

        # Check if the value contains detailed information
        checks = [
            ("LLM分析详情", "LLM analysis details"),
            ("数据源详情", "Data source details"),
            ("东方财富股吧详细数据", "Detailed Guba data")
        ]

        for keyword, description in checks:
            if keyword in value:
                print(f"  ✓ Contains {description}")
            else:
                print(f"  ✗ Missing {description}")

if __name__ == "__main__":
    test_execute_structure()

