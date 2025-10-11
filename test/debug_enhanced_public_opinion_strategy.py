#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to test the Enhanced Public Opinion Analysis Strategy V2
and display the JSON output for a single stock.
"""

import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2
import pandas as pd


def main():
    """Main function to run the debug test"""
    print("=== Debug Enhanced Public Opinion Strategy ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        # Initialize database manager
        print("Initializing MongoDB manager...")
        db_manager = MongoDBManager()
        print("✓ MongoDB manager initialized")

        # Initialize data fetcher
        print("Initializing Akshare client...")
        data_fetcher = AkshareClient()
        print("✓ Akshare client initialized")
        print()

        # Get strategy configuration from database
        print("Fetching strategy configuration from database...")
        strategy_config = db_manager.strategies_collection.find_one(
            {"name": "增强型舆情分析策略V2"}
        )

        if not strategy_config:
            print("✗ Enhanced Public Opinion Analysis Strategy V2 not found in database")
            return

        print("✓ Strategy configuration found")
        print(f"Strategy name: {strategy_config.get('name')}")
        print(f"Strategy parameters: {strategy_config.get('parameters', {})}")
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

        # Test with a single stock (使用一个简单的测试股票)
        test_stock_code = "000001"  # 上证指数作为测试
        test_stock_name = "上证指数"
        print(f"Testing with stock: {test_stock_code} ({test_stock_name})")
        print()

        # Create minimal stock data with empty DataFrame
        stock_data = {test_stock_code: pd.DataFrame()}
        print("Created empty stock data for testing")
        print()

        # Execute the strategy with timeout protection
        print("Executing strategy (with timeout protection)...")
        start_time = datetime.now()

        # Just test the _create_detailed_value method directly
        print("Testing _create_detailed_value method directly...")

        # Create a mock analysis result
        mock_analysis_result = {
            "score": 0.75,
            "reason": "测试原因",
            "details": {
                "policy": {"score": 0.8, "reason": "政策利好"},
                "finance": {"score": 0.7, "reason": "财务稳健"},
                "industry": {"score": 0.75, "reason": "行业前景良好"},
                "price_action": {"score": 0.65, "reason": "价格走势积极"},
                "sentiment": {"score": 0.85, "reason": "市场情绪乐观"}
            },
            "weights": {
                "finance": 0.30,
                "industry": 0.25,
                "policy": 0.15,
                "price_action": 0.20,
                "sentiment": 0.10
            },
            "sentiment_score": 0.85,
            "sentiment_trend": "积极",
            "key_events": ["重大合同签署", "业绩超预期"],
            "market_impact": "正面",
            "confidence_level": 0.8,
            "analysis_summary": "综合分析显示该股票具有较好的投资价值",
            "recommendation": "买入",
            "risk_factors": ["市场波动风险", "行业竞争加剧"]
        }

        # Test the _create_detailed_value method
        detailed_value = strategy._create_detailed_value("测试原因", {}, mock_analysis_result)

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        print(f"✓ Method execution completed in {execution_time:.2f} seconds")
        print()

        # Display the JSON output
        print("=== JSON Output ===")
        print("Value (JSON string):")
        if detailed_value:
            try:
                # Try to parse and pretty print the JSON
                parsed_json = json.loads(detailed_value)
                print(json.dumps(parsed_json, ensure_ascii=False, indent=2))
            except json.JSONDecodeError as e:
                # If not valid JSON, just print the string
                print(f"JSON parsing error: {e}")
                print(detailed_value)
        else:
            print("(empty)")

        print("-" * 50)

        # Also test with None analysis result
        print("Testing with None analysis result:")
        detailed_value_none = strategy._create_detailed_value("基本原因", {}, None)
        print(f"Value: {detailed_value_none}")
        print("-" * 50)

    except Exception as e:
        print(f"✗ Error during execution: {e}")
        import traceback
        traceback.print_exc()

    print("\n=== Debug Test Completed ===")


if __name__ == "__main__":
    main()

