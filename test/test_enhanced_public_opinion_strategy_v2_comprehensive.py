#!/usr/bin/env python3
"""
Comprehensive test script for Enhanced Public Opinion Analysis Strategy V2
"""

import sys
import os
import pandas as pd

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2
from data.mongodb_manager import MongoDBManager

def test_strategy_comprehensive():
    """Comprehensive test for the enhanced public opinion analysis strategy"""
    print("Comprehensive Testing Enhanced Public Opinion Analysis Strategy V2")

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

        # Check strategy parameters
        print(f"Sentiment threshold: {strategy.sentiment_threshold}")
        print(f"News count threshold: {strategy.news_count_threshold}")
        print(f"Time window hours: {strategy.time_window_hours}")
        print(f"Data sources: {strategy.data_sources}")

        # Test with multiple stocks
        test_stocks = [
            ("000001", "平安银行"),
            ("000002", "万科A"),
            ("600036", "招商银行")
        ]

        for stock_code, stock_name in test_stocks:
            print(f"\n--- Testing with stock: {stock_code} ({stock_name}) ---")

            # Test analyze_public_opinion method
            meets_criteria, reason, sentiment_score, full_analysis = strategy.analyze_public_opinion(
                stock_code, stock_name
            )

            print(f"Meets criteria: {meets_criteria}")
            print(f"Reason: {reason}")
            print(f"Sentiment score: {sentiment_score}")
            if full_analysis:
                print(f"Full analysis keys: {list(full_analysis.keys())}")
                if 'sentiment_trend' in full_analysis:
                    print(f"Sentiment trend: {full_analysis['sentiment_trend']}")
                if 'market_impact' in full_analysis:
                    print(f"Market impact: {full_analysis['market_impact']}")
                if 'confidence_level' in full_analysis:
                    print(f"Confidence level: {full_analysis['confidence_level']}")

            # Test collect_all_data method
            print("Testing data collection...")
            all_data = strategy.collect_all_data(stock_code, stock_name)
            print(f"Collected data keys: {list(all_data.keys())}")

            # Show data collection details
            if all_data.get("akshare_news"):
                print(f"AkShare news count: {len(all_data['akshare_news'])}")
            if all_data.get("qian_gu_qian_ping_data"):
                print("Qian gu qian ping data available")
            if all_data.get("detailed_guba_data"):
                guba_data = all_data['detailed_guba_data']
                print(f"Detailed Guba data keys: {list(guba_data.keys())}")
                for key in guba_data.keys():
                    print(f"  {key}: {len(guba_data[key])} items")
            if all_data.get("firecrawl_data"):
                print(f"FireCrawl data count: {len(all_data['firecrawl_data'])}")

            # Test specific Guba data methods
            print("Testing specific Guba data methods...")
            detailed_guba = strategy.get_detailed_guba_data(stock_code)
            print(f"Detailed Guba data keys: {list(detailed_guba.keys())}")

            qgqp_data = strategy.get_qian_gu_qian_ping_data_for_stock(stock_code)
            print(f"Qian gu qian ping data available: {qgqp_data is not None}")

        # Test the execute method
        print("\n--- Testing execute method ---")
        # Create mock stock data (empty DataFrames since the strategy doesn't use them)
        stock_data = {
            "000001": pd.DataFrame(),
            "000002": pd.DataFrame()
        }

        results = strategy.execute(stock_data, "TestAgent", db_manager)
        print(f"Execute method returned {len(results)} results")
        for result in results[:3]:  # Show first 3 results
            print(f"  Code: {result['code']}, Score: {result['score']:.4f}, Reason: {result['value'][:50]}...")

        print("Comprehensive test completed successfully!")

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Close database connection
        if 'db_manager' in locals():
            db_manager.close_connection()

if __name__ == "__main__":
    test_strategy_comprehensive()

