#!/usr/bin/env python3
"""
Test script for Enhanced Public Opinion Analysis Strategy V2 with qian gu qian ping data
"""

import sys
import os
import pandas as pd

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2
from data.mongodb_manager import MongoDBManager

def test_strategy_with_qgqp():
    """Test the enhanced public opinion analysis strategy with qian gu qian ping data"""
    print("Testing Enhanced Public Opinion Analysis Strategy V2 with qian gu qian ping data")

    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()
        print("MongoDB manager initialized")

        # Initialize strategy with database manager to load configuration
        strategy = EnhancedPublicOpinionAnalysisStrategyV2(
            name="增强型舆情分析策略V2",
            db_manager=db_manager
        )
        print(f"Strategy initialized: {strategy.name}")
        print(f"Qian gu qian ping data loaded: {strategy.qian_gu_qian_ping_data is not None}")
        if strategy.qian_gu_qian_ping_data:
            print(f"Number of stocks in qian gu qian ping data: {len(strategy.qian_gu_qian_ping_data)}")

        # Test getting qian gu qian ping data for a specific stock
        test_stock_code = "300339"  # Test stock
        qgqp_data = strategy.get_qian_gu_qian_ping_data_for_stock(test_stock_code)
        print(f"Qian gu qian ping data for {test_stock_code}: {qgqp_data}")

        # Test getting detailed Guba data for a specific stock
        print(f"Getting detailed Guba data for {test_stock_code}...")
        detailed_guba_data = strategy.get_detailed_guba_data(test_stock_code)
        print(f"Detailed Guba data keys: {list(detailed_guba_data.keys())}")

        # Print some sample data
        if detailed_guba_data.get("user_focus"):
            print(f"Sample user focus data: {detailed_guba_data['user_focus'][:2]}")
        if detailed_guba_data.get("institutional_participation"):
            print(f"Sample institutional participation data: {detailed_guba_data['institutional_participation'][:2]}")
        if detailed_guba_data.get("historical_rating"):
            print(f"Sample historical rating data: {detailed_guba_data['historical_rating'][:2]}")
        if detailed_guba_data.get("daily_participation"):
            print(f"Sample daily participation data: {detailed_guba_data['daily_participation'][:2]}")

        print("Test completed successfully!")

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Close database connection
        if 'db_manager' in locals():
            db_manager.close_connection()

if __name__ == "__main__":
    test_strategy_with_qgqp()

