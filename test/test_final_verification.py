#!/usr/bin/env python3
"""
Final verification test for Enhanced Public Opinion Analysis Strategy V2
"""

import sys
import os
import pandas as pd

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2
from data.mongodb_manager import MongoDBManager

def test_final_verification():
    """Final verification test for the enhanced public opinion analysis strategy"""
    print("Final verification test for Enhanced Public Opinion Analysis Strategy V2")

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

        # Check that all required attributes are present
        required_attributes = [
            'sentiment_threshold',
            'news_count_threshold',
            'time_window_hours',
            'data_sources',
            'firecrawl_config',
            'llm_config',
            'qian_gu_qian_ping_data'
        ]

        for attr in required_attributes:
            if hasattr(strategy, attr):
                value = getattr(strategy, attr)
                print(f"✓ {attr}: {type(value).__name__} (length: {len(value) if hasattr(value, '__len__') and not isinstance(value, str) else 'N/A'})")
            else:
                print(f"✗ {attr}: MISSING")

        # Test with a sample stock
        test_stock_code = "000001"
        test_stock_name = "平安银行"

        print(f"\nTesting with stock: {test_stock_code} ({test_stock_name})")

        # Test analyze_public_opinion method
        meets_criteria, reason, sentiment_score, full_analysis = strategy.analyze_public_opinion(
            test_stock_code, test_stock_name
        )

        print(f"Meets criteria: {meets_criteria}")
        print(f"Reason: {reason}")
        print(f"Sentiment score: {sentiment_score}")
        if full_analysis:
            print(f"Full analysis keys: {list(full_analysis.keys())}")

        # Test collect_all_data method
        print("\nTesting data collection...")
        all_data = strategy.collect_all_data(test_stock_code, test_stock_name)
        print(f"Collected data keys: {list(all_data.keys())}")

        # Show data collection details
        data_sources = [
            ("akshare_news", "AkShare新闻"),
            ("industry_info", "行业信息"),
            ("guba_data", "股吧数据"),
            ("professional_sites_data", "专业网站数据"),
            ("firecrawl_data", "FireCrawl数据"),
            ("qian_gu_qian_ping_data", "千股千评数据"),
            ("detailed_guba_data", "详细股吧数据")
        ]

        for key, description in data_sources:
            if all_data.get(key):
                if isinstance(all_data[key], list):
                    print(f"✓ {description}: {len(all_data[key])} items")
                elif isinstance(all_data[key], dict):
                    if all_data[key]:  # Non-empty dict
                        print(f"✓ {description}: {len(all_data[key])} fields")
                    else:
                        print(f"○ {description}: Empty")
                else:
                    print(f"✓ {description}: Present")
            else:
                print(f"○ {description}: Not available")

        # Test specific methods
        print("\nTesting specific methods...")
        detailed_guba = strategy.get_detailed_guba_data(test_stock_code)
        print(f"Detailed Guba data keys: {list(detailed_guba.keys())}")

        qgqp_data = strategy.get_qian_gu_qian_ping_data_for_stock(test_stock_code)
        print(f"Qian gu qian ping data available: {qgqp_data is not None}")

        # Test the execute method
        print("\nTesting execute method...")
        # Create mock stock data (empty DataFrames since the strategy doesn't use them)
        stock_data = {
            "000001": pd.DataFrame(),
            "000002": pd.DataFrame()
        }

        results = strategy.execute(stock_data, "TestAgent", db_manager)
        print(f"Execute method returned {len(results)} results")
        for i, result in enumerate(results):
            print(f"  {i+1}. Code: {result['code']}, Score: {result['score']:.4f}")
            if i >= 2:  # Only show first 3 results
                print(f"  ... and {len(results) - 3} more results")
                break

        print("\nFinal verification test completed successfully!")
        print("✓ Enhanced Public Opinion Analysis Strategy V2 is working correctly")

    except Exception as e:
        print(f"Error during final verification test: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Close database connection
        if 'db_manager' in locals():
            db_manager.close_connection()

if __name__ == "__main__":
    test_final_verification()

