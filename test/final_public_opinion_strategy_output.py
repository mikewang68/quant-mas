#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final test script to demonstrate the JSON output from Enhanced Public Opinion Analysis Strategy V2
"""

import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2
import pandas as pd


def main():
    """Main function to demonstrate the JSON output"""
    print("=== Final Public Opinion Strategy Output Demo ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        # Initialize database manager
        print("Initializing MongoDB manager...")
        db_manager = MongoDBManager()
        print("✓ MongoDB manager initialized")

        # Get strategy configuration from database
        print("Fetching strategy configuration from database...")
        strategy_config = db_manager.strategies_collection.find_one(
            {"name": "增强型舆情分析策略V2"}
        )

        if not strategy_config:
            print("✗ Enhanced Public Opinion Analysis Strategy V2 not found in database")
            return

        print("✓ Strategy configuration found")
        print()

        # Initialize the strategy
        print("Initializing Enhanced Public Opinion Analysis Strategy V2...")
        strategy = EnhancedPublicOpinionAnalysisStrategyV2(
            name=strategy_config.get('name', 'EnhancedPublicOpinionAnalysisStrategyV2'),
            params=strategy_config.get('parameters', {}),
            db_manager=db_manager
        )
        print("✓ Strategy initialized")
        print()

        # Create a sample analysis result that matches the actual output format
        sample_analysis_result = {
            "score": 0.515,
            "reason": "股价下跌，监管罚单增多，财务改善但情绪偏弱",
            "details": {
                "policy": {
                    "score": 0.45,
                    "reason": "近期银行罚单密集，监管风险上升"
                },
                "finance": {
                    "score": 0.70,
                    "reason": "零售贷款质量改善，分红稳定"
                },
                "industry": {
                    "score": 0.55,
                    "reason": "行业罚单增多，但零售业务改善"
                },
                "price_action": {
                    "score": 0.25,
                    "reason": "股价下跌，主力成本接近"
                },
                "sentiment": {
                    "score": 0.50,
                    "reason": "关注指数中等，情绪波动"
                }
            },
            "weights": {
                "finance": 0.30,
                "industry": 0.25,
                "policy": 0.15,
                "price_action": 0.20,
                "sentiment": 0.10
            },
            "sentiment_score": 0.50,
            "sentiment_trend": "震荡",
            "key_events": [
                "13家银行被罚7776万元",
                "平安银行零售客户增长0.9%",
                "上半年不良贷款生成率1.64%",
                "2025年半年度分红每10股派2.36元",
                "零售贷款质量改善",
                "股价创新低"
            ],
            "market_impact": "中",
            "confidence_level": 0.75,
            "analysis_summary": "平安银行近期股价下跌，监管罚单增多，但零售业务改善，情绪偏中性。",
            "recommendation": "观望",
            "risk_factors": [
                "监管处罚风险",
                "股价波动",
                "不良贷款率"
            ]
        }

        print("Creating sample analysis result...")
        print()

        # Test the _create_detailed_value method
        print("Testing _create_detailed_value method...")
        detailed_value = strategy._create_detailed_value(
            "符合条件: 舆情 sentiment 分数(0.52) >= 阈值(0.0), 相关信息15条",
            {},  # all_data - empty for this test
            sample_analysis_result
        )
        print("✓ _create_detailed_value method executed")
        print()

        # Display the JSON output format
        print("=== JSON Output Format ===")
        print("The Enhanced Public Opinion Analysis Strategy V2 returns the following JSON structure:")
        print()

        # Pretty print the sample JSON
        print(json.dumps(sample_analysis_result, ensure_ascii=False, indent=2))
        print()

        # Also show what gets stored in the value field
        print("=== Value Field Content ===")
        print("The 'value' field in the strategy output contains the full JSON as a string:")
        print()
        print(detailed_value[:200] + "..." if len(detailed_value) > 200 else detailed_value)
        print()

        # Show what gets stored in the score field
        print("=== Score Field Content ===")
        print(f"The 'score' field in the strategy output contains: {sample_analysis_result['score']}")
        print()

        # Show the complete structure that would be returned by the strategy
        print("=== Complete Strategy Output Structure ===")
        strategy_output = {
            "code": "000001",
            "score": sample_analysis_result["score"],
            "value": detailed_value
        }
        print(json.dumps(strategy_output, ensure_ascii=False, indent=2))
        print()

    except Exception as e:
        print(f"✗ Error during execution: {e}")
        import traceback
        traceback.print_exc()

    print("=== Demo Completed ===")


if __name__ == "__main__":
    main()

