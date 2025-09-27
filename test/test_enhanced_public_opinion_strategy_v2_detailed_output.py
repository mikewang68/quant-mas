#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the Enhanced Public Opinion Analysis Strategy V2 with detailed output
"""

import sys
import os
import pandas as pd

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2
from config.mongodb_config import MongoDBConfig
from data.mongodb_manager import MongoDBManager

def test_detailed_output():
    """Test the strategy with detailed output"""
    print("Testing Enhanced Public Opinion Analysis Strategy V2 with detailed output...")

    # Initialize database manager
    try:
        mongodb_config = MongoDBConfig()
        config = mongodb_config.get_mongodb_config()
        db_manager = MongoDBManager(config)
        print("Successfully connected to MongoDB")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return

    # Create strategy instance
    strategy = EnhancedPublicOpinionAnalysisStrategyV2(
        name="增强型舆情分析策略V2测试",
        db_manager=db_manager
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

    # Test the execute method with a small dataset
    stock_data = {
        test_stock_code: mock_data
    }

    print(f"\nExecuting strategy on {len(stock_data)} stocks...")
    results = strategy.execute(stock_data, "舆情分析Agent", db_manager)

    print(f"Number of selected stocks: {len(results)}")

    # Print detailed information for each selected stock
    for i, stock in enumerate(results):
        print(f"\nStock {i+1}:")
        print(f"  Code: {stock.get('code')}")
        print(f"  Score: {stock.get('score')}")
        print(f"  Value: {stock.get('value')}")

        # Check if pub data is included
        pub_data = stock.get('pub', {})
        if pub_data:
            print("  Public Opinion Analysis Details:")
            print(f"    Sentiment Score: {pub_data.get('sentiment_score')}")
            print(f"    Sentiment Trend: {pub_data.get('sentiment_trend')}")
            print(f"    Market Impact: {pub_data.get('market_impact')}")
            print(f"    Confidence Level: {pub_data.get('confidence_level')}")
            print(f"    Recommendation: {pub_data.get('recommendation')}")

            # Print key events and risk factors
            key_events = pub_data.get('key_events', [])
            if key_events:
                print(f"    Key Events: {', '.join(key_events[:3])}")  # Limit to first 3

            risk_factors = pub_data.get('risk_factors', [])
            if risk_factors:
                print(f"    Risk Factors: {', '.join(risk_factors[:3])}")  # Limit to first 3

            # Print analysis details
            analysis_details = pub_data.get('analysis_details', {})
            if analysis_details:
                print("    Analysis Details:")
                for key, value in analysis_details.items():
                    print(f"      {key}: {value}")
        else:
            print("  No public opinion data found")

if __name__ == "__main__":
    test_detailed_output()

