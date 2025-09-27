#!/usr/bin/env python3
"""
Final comprehensive test for Qian Gu Qian Ping integration in Enhanced Public Opinion Analysis Strategy V2
"""

import sys
import os
import pandas as pd

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import (
    EnhancedPublicOpinionAnalysisStrategyV2,
)


def test_complete_integration():
    """Test complete integration of Qian Gu Qian Ping data"""
    print("=== Final Comprehensive Test for Qian Gu Qian Ping Integration ===")

    try:
        # Test 1: Strategy initialization
        print("\n1. Testing strategy initialization...")
        strategy = EnhancedPublicOpinionAnalysisStrategyV2()
        assert strategy.qian_gu_qian_ping_data is not None, (
            "Qian Gu Qian Ping data should be loaded"
        )
        assert len(strategy.qian_gu_qian_ping_data) > 0, (
            "Qian Gu Qian Ping data should not be empty"
        )
        print(
            f"   ✓ Strategy initialized with {len(strategy.qian_gu_qian_ping_data)} stocks data"
        )

        # Test 2: Data lookup functionality
        print("\n2. Testing Qian Gu Qian Ping data lookup...")
        test_stock = "300339"
        qgqp_data = strategy.get_qian_gu_qian_ping_data_for_stock(test_stock)
        assert qgqp_data is not None, f"Should find data for stock {test_stock}"
        assert "综合得分" in qgqp_data, "Should contain composite score"
        assert "关注指数" in qgqp_data, "Should contain focus index"
        assert "机构参与度" in qgqp_data, "Should contain institutional participation"
        print(f"   ✓ Found Qian Gu Qian Ping data for {test_stock}")
        print(f"     Composite Score: {qgqp_data['综合得分']}")
        print(f"     Focus Index: {qgqp_data['关注指数']}")
        print(f"     Institutional Participation: {qgqp_data['机构参与度']}")

        # Test 3: Detailed Guba data collection
        print("\n3. Testing detailed Guba data collection...")
        detailed_data = strategy.get_detailed_guba_data(test_stock)
        required_keys = [
            "user_focus",
            "institutional_participation",
            "historical_rating",
            "daily_participation",
        ]
        for key in required_keys:
            assert key in detailed_data, f"Should contain {key}"
            assert isinstance(detailed_data[key], list), f"{key} should be a list"
            print(f"   ✓ {key}: {len(detailed_data[key])} records")

        # Test 4: Data integration in collection process
        print("\n4. Testing data integration in collection process...")
        collected_data = strategy.collect_all_data(test_stock, "测试股票")
        assert "qian_gu_qian_ping_data" in collected_data, (
            "Should include Qian Gu Qian Ping data"
        )
        assert "detailed_guba_data" in collected_data, (
            "Should include detailed Guba data"
        )
        print("   ✓ Qian Gu Qian Ping data integrated in collection")
        print("   ✓ Detailed Guba data integrated in collection")

        # Test 5: Data formatting for LLM
        print("\n5. Testing data formatting for LLM...")
        formatted_data = strategy._format_data_for_llm(collected_data)
        assert isinstance(formatted_data, str), "Formatted data should be a string"
        assert len(formatted_data) > 0, "Formatted data should not be empty"
        assert "千股千评综合数据" in formatted_data, (
            "Should include Qian Gu Qian Ping data in LLM format"
        )
        assert "东方财富股吧详细数据" in formatted_data, (
            "Should include detailed Guba data in LLM format"
        )
        print(f"   ✓ Data formatted for LLM ({len(formatted_data)} characters)")
        print("   ✓ Qian Gu Qian Ping data included in LLM format")
        print("   ✓ Detailed Guba data included in LLM format")

        # Test 6: Multiple stock lookup
        print("\n6. Testing multiple stock lookups...")
        test_stocks = ["000692", "300339"]
        for stock in test_stocks:
            data = strategy.get_qian_gu_qian_ping_data_for_stock(stock)
            assert data is not None, f"Should find data for stock {stock}"
            assert "名称" in data, f"Should contain name for stock {stock}"
            print(f"   ✓ Found data for {stock}: {data['名称']}")

        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("\nIntegration Summary:")
        print("  ✓ Strategy initialization with Qian Gu Qian Ping data loading")
        print("  ✓ Data lookup for specific stocks")
        print("  ✓ Detailed Guba data collection")
        print("  ✓ Data integration in collection process")
        print("  ✓ Data formatting for LLM analysis")
        print("  ✓ Multiple stock data access")
        print("\nThe Enhanced Public Opinion Analysis Strategy V2")
        print("is successfully integrated with Qian Gu Qian Ping data!")

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("Final Test for Enhanced Public Opinion Analysis Strategy V2")
    print("with Qian Gu Qian Ping Data Integration")

    success = test_complete_integration()

    if success:
        print("\n🎉 Integration test completed successfully!")
        return 0
    else:
        print("\n❌ Integration test failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
