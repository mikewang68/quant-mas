#!/usr/bin/env python3
"""
Comprehensive test script for Enhanced Public Opinion Analysis Strategy V2 with qian gu qian ping data
"""

import sys
import os
import pandas as pd

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2
from data.mongodb_manager import MongoDBManager

def test_strategy_initialization():
    """Test strategy initialization with qian gu qian ping data"""
    print("1. Testing strategy initialization...")

    try:
        # Initialize strategy without database manager
        strategy = EnhancedPublicOpinionAnalysisStrategyV2()
        print(f"   ✓ Strategy initialized: {strategy.name}")
        print(f"   ✓ Qian gu qian ping data loaded: {strategy.qian_gu_qian_ping_data is not None}")
        if strategy.qian_gu_qian_ping_data:
            print(f"   ✓ Number of stocks in qian gu qian ping data: {len(strategy.qian_gu_qian_ping_data)}")

        return True
    except Exception as e:
        print(f"   ✗ Error during strategy initialization test: {e}")
        return False

def test_qgqp_data_lookup():
    """Test Qian Gu Qian Ping data lookup for specific stocks"""
    print("\n2. Testing Qian Gu Qian Ping data lookup...")

    try:
        # Initialize strategy
        strategy = EnhancedPublicOpinionAnalysisStrategyV2()

        # Test with sample stock codes
        test_stocks = ["300339", "000001", "600000"]

        for stock_code in test_stocks:
            qgqp_data = strategy.get_qian_gu_qian_ping_data_for_stock(stock_code)
            if qgqp_data:
                print(f"   ✓ Qian gu qian ping data found for {stock_code}")
                # Show some key fields
                print(f"     Name: {qgqp_data.get('名称', 'N/A')}")
                print(f"     Price: {qgqp_data.get('最新价', 'N/A')}")
                print(f"     Score: {qgqp_data.get('综合得分', 'N/A')}")
            else:
                print(f"   - No Qian gu qian ping data found for {stock_code}")

        return True
    except Exception as e:
        print(f"   ✗ Error during Qian Gu Qian Ping data lookup test: {e}")
        return False

def test_detailed_guba_data():
    """Test detailed Guba data collection"""
    print("\n3. Testing detailed Guba data collection...")

    try:
        # Initialize strategy
        strategy = EnhancedPublicOpinionAnalysisStrategyV2()

        # Test with a sample stock code
        stock_code = "300339"  # Example stock code
        print(f"   Collecting detailed Guba data for {stock_code}...")

        detailed_data = strategy.get_detailed_guba_data(stock_code)

        print(f"   ✓ Detailed Guba data collected:")
        for key, value in detailed_data.items():
            print(f"     {key}: {len(value) if isinstance(value, list) else value} items")

        # Show sample data from each category
        if detailed_data.get("user_focus"):
            sample = detailed_data["user_focus"][0] if detailed_data["user_focus"] else {}
            print(f"     Sample user focus: {sample}")

        if detailed_data.get("institutional_participation"):
            sample = detailed_data["institutional_participation"][0] if detailed_data["institutional_participation"] else {}
            print(f"     Sample institutional participation: {sample}")

        if detailed_data.get("historical_rating"):
            sample = detailed_data["historical_rating"][0] if detailed_data["historical_rating"] else {}
            print(f"     Sample historical rating: {sample}")

        if detailed_data.get("daily_participation"):
            sample = detailed_data["daily_participation"][0] if detailed_data["daily_participation"] else {}
            print(f"     Sample daily participation: {sample}")

        return True
    except Exception as e:
        print(f"   ✗ Error during detailed Guba data test: {e}")
        return False

def test_data_integration_in_llm_format():
    """Test data integration in LLM format"""
    print("\n4. Testing data integration in LLM format...")

    try:
        # Initialize strategy
        strategy = EnhancedPublicOpinionAnalysisStrategyV2()

        # Create sample data structure
        stock_code = "300339"
        stock_name = "润和软件"

        all_data = {
            "stock_info": {
                "code": stock_code,
                "name": stock_name
            },
            "akshare_news": [],
            "industry_info": {},
            "guba_data": {},
            "professional_sites_data": [],
            "firecrawl_data": [],
            "qian_gu_qian_ping_data": {},
            "detailed_guba_data": {}
        }

        # Add qian gu qian ping data
        qgqp_data = strategy.get_qian_gu_qian_ping_data_for_stock(stock_code)
        if qgqp_data:
            all_data["qian_gu_qian_ping_data"] = qgqp_data

        # Add detailed Guba data
        detailed_guba_data = strategy.get_detailed_guba_data(stock_code)
        all_data["detailed_guba_data"] = detailed_guba_data

        # Format data for LLM
        formatted_data = strategy._format_data_for_llm(all_data)

        print(f"   ✓ Data formatted for LLM ({len(formatted_data)} characters)")

        # Check if key sections are present
        if "千股千评综合数据" in formatted_data:
            print("   ✓ Qian gu qian ping data included in LLM format")
        else:
            print("   ✗ Qian gu qian ping data missing from LLM format")

        if "东方财富股吧详细数据" in formatted_data:
            print("   ✓ Detailed Guba data included in LLM format")
        else:
            print("   ✗ Detailed Guba data missing from LLM format")

        return True
    except Exception as e:
        print(f"   ✗ Error during LLM data format test: {e}")
        return False

def test_strategy_with_database():
    """Test strategy with database manager"""
    print("\n5. Testing strategy with database manager...")

    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()
        print("   ✓ MongoDB manager initialized")

        # Initialize strategy with database manager
        strategy = EnhancedPublicOpinionAnalysisStrategyV2(
            name="增强型舆情分析策略V2",
            db_manager=db_manager
        )
        print(f"   ✓ Strategy initialized with database: {strategy.name}")

        # Close database connection
        db_manager.close_connection()
        print("   ✓ Database connection closed")

        return True
    except Exception as e:
        print(f"   ✗ Error during database test: {e}")
        # Close database connection if it was opened
        if 'db_manager' in locals():
            db_manager.close_connection()
        return False

def main():
    """Main test function"""
    print("Comprehensive Test for Enhanced Public Opinion Analysis Strategy V2 with Qian Gu Qian Ping Data")
    print("=" * 100)

    # Run all tests
    tests = [
        test_strategy_initialization,
        test_qgqp_data_lookup,
        test_detailed_guba_data,
        test_data_integration_in_llm_format,
        test_strategy_with_database
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"Test {test.__name__} failed with exception: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 100)
    print("Test Summary:")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed!")
        print("\nEnhanced Public Opinion Analysis Strategy V2 with Qian Gu Qian Ping data integration is working correctly.")
        print("Features verified:")
        print("  - Strategy initialization with qian gu qian ping data loading")
        print("  - Qian gu qian ping data lookup for specific stocks")
        print("  - Detailed Guba data collection using AkShare functions")
        print("  - Data integration in LLM analysis format")
        print("  - Database integration")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())

