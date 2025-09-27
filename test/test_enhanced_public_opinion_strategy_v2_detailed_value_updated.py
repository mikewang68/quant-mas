#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the enhanced public opinion strategy v2 detailed value output
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2
from data.mongodb_manager import MongoDBManager

def test_detailed_value_format():
    """Test that the detailed value format contains specific data rather than just counts"""

    # Create a mock database manager
    db_manager = MongoDBManager()

    # Create strategy instance
    strategy = EnhancedPublicOpinionAnalysisStrategyV2(db_manager=db_manager)

    # Mock data that would be collected by the strategy
    mock_all_data = {
        "stock_info": {"code": "000001", "name": "平安银行"},
        "akshare_news": [
            {"title": "平安银行发布业绩预增公告", "content": "业绩增长20%", "publishedAt": "2025-09-01T10:00:00", "source": "AkShare"},
            {"title": "银行业政策利好频出", "content": "监管层支持银行发展", "publishedAt": "2025-09-02T10:00:00", "source": "AkShare"},
            {"title": "市场对银行股关注度提升", "content": "资金流入银行板块", "publishedAt": "2025-09-03T10:00:00", "source": "AkShare"}
        ],
        "industry_info": {"industries": ["银行", "金融服务", "金融"]},
        "qian_gu_qian_ping_data": {
            "综合评分": "85",
            "市盈率": "8.5",
            "成长性": "良好"
        },
        "guba_data": {
            "consultations": [
                {"title": "利好消息推动股价上涨", "publishedAt": "2025-09-01T10:00:00"},
                {"title": "风险提示需关注", "publishedAt": "2025-09-02T10:00:00"}
            ],
            "research_reports": [
                {"title": "分析师给予买入评级", "publishedAt": "2025-09-01T10:00:00"}
            ],
            "announcements": [],
            "hot_posts": [
                {"title": "市场分析：银行股机会来临", "publishedAt": "2025-09-03T10:00:00"}
            ]
        },
        "professional_sites_data": [
            {"title": "同花顺分析报告", "source": "同花顺财经", "publishedAt": "2025-09-01T10:00:00"},
            {"title": "东方财富网点评", "source": "东方财富网", "publishedAt": "2025-09-02T10:00:00"}
        ],
        "firecrawl_data": [
            {"title": "银行业整体业绩改善", "publishedAt": "2025-09-01T10:00:00"},
            {"title": "政策支持银行发展", "publishedAt": "2025-09-02T10:00:00"}
        ],
        "detailed_guba_data": {
            "user关注指数": [
                {"date": "2025-09-01", "focus_index": "85.5"},
                {"date": "2025-09-02", "focus_index": "87.2"}
            ],
            "机构参与度": [
                {"date": "2025-09-01", "participation": "75.3"},
                {"date": "2025-09-02", "participation": "78.1"}
            ],
            "历史评分": [
                {"date": "2025-09-01", "rating": "8.5"},
                {"date": "2025-09-02", "rating": "8.7"}
            ],
            "日度市场参与意愿": [
                {"date": "2025-09-01", "daily_desire_rise": "5.2%", "avg_participation_change": "3.1%"},
                {"date": "2025-09-02", "daily_desire_rise": "6.1%", "avg_participation_change": "3.8%"}
            ]
        }
    }

    # Mock LLM analysis results
    mock_full_analysis = {
        "sentiment_trend": "上升",
        "market_impact": "高",
        "confidence_level": 0.85,
        "recommendation": "买入",
        "key_events": ["利好消息", "业绩预增", "政策支持"],
        "risk_factors": ["市场波动", "政策风险", "行业竞争"],
        "analysis_summary": "该股票近期受到积极舆情影响，市场关注度较高。业绩预增公告提升了投资者信心，同时银行业整体政策环境向好。但需关注市场波动风险和行业竞争加剧的可能性。"
    }

    # Call the _create_detailed_value method
    detailed_value = strategy._create_detailed_value(
        basic_reason="符合条件: 舆情 sentiment 分数(0.65) >= 阈值(0.0), 相关信息46条",
        sentiment_score=0.65,
        full_analysis=mock_full_analysis,
        all_data=mock_all_data
    )

    print("Generated detailed value:")
    print(detailed_value)
    print("\n" + "="*50 + "\n")

    # Verify that the detailed value contains specific information
    checks = [
        ("LLM分析摘要包含具体内容", "业绩预增公告" in detailed_value),
        ("数据源详情包含具体行业信息", "银行, 金融服务, 金融" in detailed_value),
        ("数据源详情包含千股千评具体数据", "综合评分85, 市盈率8.5, 成长性良好" in detailed_value),
        ("数据源详情包含Guba具体主题", ("利好" in detailed_value and "风险" in detailed_value and "分析" in detailed_value)),
        ("数据源详情包含专业网站来源", "同花顺财经, 东方财富网" in detailed_value),
        ("数据源详情包含FireCrawl具体主题", ("业绩" in detailed_value and "政策" in detailed_value)),
        ("东方财富股吧详细数据显示具体数值", "85.5, 87.2" in detailed_value),
        ("东方财富股吧详细数据显示参与度数值", "75.3, 78.1" in detailed_value),
        ("东方财富股吧详细数据显示评分数值", "8.5, 8.7" in detailed_value),
        ("东方财富股吧详细数据显示参与意愿数值", "5.2%, 6.1%" in detailed_value),
    ]

    print("Verification checks:")
    all_passed = True
    for check_name, check_result in checks:
        status = "✓ PASS" if check_result else "✗ FAIL"
        print(f"{status}: {check_name}")
        if not check_result:
            all_passed = False

    print(f"\nOverall result: {'All checks passed' if all_passed else 'Some checks failed'}")
    return all_passed

if __name__ == "__main__":
    test_detailed_value_format()

