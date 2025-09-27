#!/usr/bin/env python3
"""
Simple test script for Enhanced Public Opinion Analysis Strategy V2
"""

import sys
import os
import pandas as pd

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import (
    EnhancedPublicOpinionAnalysisStrategyV2,
)
from data.mongodb_manager import MongoDBManager


def test_strategy_simple():
    """Simple test for the enhanced public opinion analysis strategy"""
    print("Testing Enhanced Public Opinion Analysis Strategy V2")

    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()
        print("MongoDB manager initialized")

        # Initialize strategy with database manager to load configuration
        strategy = EnhancedPublicOpinionAnalysisStrategyV2(
            name="增强型舆情分析策略V2", db_manager=db_manager
        )
        print(f"Strategy initialized: {strategy.name}")

        # Test the strategy with a sample stock
        test_stock_code = "000001"  # Ping An Bank
        test_stock_name = "平安银行"

        print(f"Testing with stock: {test_stock_code} ({test_stock_name})")

        # Test analyze_public_opinion method
        meets_criteria, reason, sentiment_score, full_analysis = (
            strategy.analyze_public_opinion(test_stock_code, test_stock_name)
        )

        print(f"Meets criteria: {meets_criteria}")
        print(f"Reason: {reason}")
        print(f"Sentiment score: {sentiment_score}")
        print(
            f"Full analysis keys: {list(full_analysis.keys()) if full_analysis else 'None'}"
        )

        # Test collect_all_data method
        print("Testing data collection...")
        all_data = strategy.collect_all_data(test_stock_code, test_stock_name)
        print(f"Collected data keys: {list(all_data.keys())}")

        # Show some sample data
        if all_data.get("akshare_news"):
            print(f"AkShare news count: {len(all_data['akshare_news'])}")
        if all_data.get("qian_gu_qian_ping_data"):
            print("Qian gu qian ping data available")
        if all_data.get("detailed_guba_data"):
            print(
                f"Detailed Guba data keys: {list(all_data['detailed_guba_data'].keys())}"
            )

        print("Test completed successfully!")

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Close database connection
        if "db_manager" in locals():
            db_manager.close_connection()


if __name__ == "__main__":
    test_strategy_simple()
