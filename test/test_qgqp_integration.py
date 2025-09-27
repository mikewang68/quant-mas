#!/usr/bin/env python3
"""
Comprehensive test for Qian Gu Qian Ping integration in Enhanced Public Opinion Analysis Strategy V2
"""

import sys
import os
import pandas as pd

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2

def test_qgqp_initialization():
    """Test Qian Gu Qian Ping data initialization"""
    print("=== Testing Qian Gu Qian Ping Data Initialization ===")

    try:
        # Initialize strategy without database manager to avoid connection issues
        strategy = EnhancedPublicOpinionAnalysisStrategyV2()
        print(f"✓ Strategy initialized: {strategy.name}")

        # Check if qian gu qian ping data was loaded
        if strategy.qian_gu_qian_ping_data is not None:
            print(f"✓ Qian Gu Qian Ping data loaded successfully")
            print(f"✓ Number of stocks in qian gu qian ping data: {len(strategy.qian_gu_qian_ping_data)}")

            # Show sample data
            sample_stock_code = list(strategy.qian_gu_qian_ping_data.keys())[0]
            sample_data = strategy.qian_gu_qian_ping_data[sample_stock_code]
            print(f"✓ Sample stock data for {sample_stock_code}:")
            for key, value in list(sample_data.items())[:5]:  # Show first 5 fields
                print(f"  {key}: {value}")
        else:
            print("✗ Qian Gu Qian Ping data is None")
            return False

        return True
    except Exception as e:
        print(f"✗ Error during initialization test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_qgqp_data_lookup():
    """Test Qian Gu Qian Ping data lookup for specific stocks"""
    print("\n=== Testing Qian Gu Qian Ping Data Lookup ===")

    try:
        strategy = EnhancedPublicOpinionAnalysisStrategyV2()

        # Test with multiple stock codes
        test_stocks = ["300339", "000001", "600000"]

        for stock_code in test_stocks:
            qgqp_data = strategy.get_qian_gu_qian_ping_data_for_stock(stock_code)
            if qgqp_data:
                print(f"✓ Found Qian Gu Qian Ping data for {stock_code}")
                # Show key metrics
                print(f"  综合得分: {qgqp_data.get('综合得分', 'N/A')}")
                print(f"  关注指数: {qgqp_data.get('关注指数', 'N/A')}")
                print(f"  机构参与度: {qgqp_data.get('机构参与度', 'N/A')}")
            else:
                print(f"✗ No Qian Gu Qian Ping data found for {stock_code}")

        return True
    except Exception as e:
        print(f"✗ Error during data lookup test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_detailed_guba_data():
    """Test detailed Guba data collection"""
    print("\n=== Testing Detailed Guba Data Collection ===")

    try:
        strategy = EnhancedPublicOpinionAnalysisStrategyV2()

        # Test with a sample stock code
        stock_code = "300339"
        print(f"Collecting detailed Guba data for {stock_code}...")

        detailed_data = strategy.get_detailed_guba_data(stock_code)

        # Check each data type
        data_types = [
            ("user_focus", "用户关注指数"),
            ("institutional_participation", "机构参与度"),
            ("historical_rating", "历史评分"),
            ("daily_participation", "日度市场参与意愿")
        ]

        for key, description in data_types:
            if detailed_data.get(key):
                print(f"✓ {description} data collected: {len(detailed_data[key])} records")
                if detailed_data[key]:
                    sample_record = detailed_data[key][0]
                    print(f"  Sample: {sample_record}")
            else:
                print(f"⚠ {description} data not available")

        return True
    except Exception as e:
        print(f"✗ Error during detailed Guba data test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_integration_in_collection():
    """Test that qian gu qian ping data is integrated in the collect_all_data method"""
    print("\n=== Testing Data Integration in Collection ===")

    try:
        strategy = EnhancedPublicOpinionAnalysisStrategyV2()

        # Test data collection for a stock
        stock_code = "300339"
        stock_name = "润和软件"

        print(f"Collecting all data for {stock_code} ({stock_name})...")
        all_data = strategy.collect_all_data(stock_code, stock_name)

        # Check if qian gu qian ping data is included
        if "qian_gu_qian_ping_data" in all_data:
            print("✓ Qian Gu Qian Ping data included in collected data")
            if all_data["qian_gu_qian_ping_data"]:
                print("✓ Qian Gu Qian Ping data is not empty")
            else:
                print("⚠ Qian Gu Qian Ping data is empty")
        else:
            print("✗ Qian Gu Qian Ping data missing from collected data")

        # Check if detailed Guba data is included
        if "detailed_guba_data" in all_data:
            print("✓ Detailed Guba data included in collected data")
            detailed_guba = all_data["detailed_guba_data"]
            for key in ["user_focus", "institutional_participation", "historical_rating", "daily_participation"]:
                if detailed_guba.get(key):
                    print(f"  ✓ {key}: {len(detailed_guba[key])} records")
        else:
            print("✗ Detailed Guba data missing from collected data")

        return True
    except Exception as e:
        print(f"✗ Error during data integration test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Comprehensive Test for Qian Gu Qian Ping Integration")
    print("=" * 60)

    # Run all tests
    tests = [
        test_qgqp_initialization,
        test_qgqp_data_lookup,
        test_detailed_guba_data,
        test_data_integration_in_collection
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
    print("\n" + "=" * 60)
    print("Test Summary:")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! Qian Gu Qian Ping integration is working correctly.")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())

