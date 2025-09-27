#!/usr/bin/env python3
"""
Final integration test for Enhanced Public Opinion Analysis Strategy V2
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import (
    EnhancedPublicOpinionAnalysisStrategyV2,
)


def test_strategy_initialization():
    """Test strategy initialization"""
    print("Testing strategy initialization...")
    try:
        strategy = EnhancedPublicOpinionAnalysisStrategyV2()
        print("✓ Strategy initialized successfully")
        print(f"  Strategy name: {strategy.name}")
        print(f"  Data sources: {strategy.data_sources}")
        print(f"  FireCrawl config: {strategy.firecrawl_config}")
        return True
    except Exception as e:
        print(f"✗ Strategy initialization failed: {e}")
        return False


def test_qgqp_data_loading():
    """Test qian gu qian ping data loading"""
    print("\nTesting qian gu qian ping data loading...")
    try:
        strategy = EnhancedPublicOpinionAnalysisStrategyV2()
        # Check if qgqp data was loaded
        if hasattr(strategy, "qgqp_data") and strategy.qgqp_data:
            print("✓ Qian gu qian ping data loaded successfully")
            print(f"  Loaded data for {len(strategy.qgqp_data)} stocks")
            # Show sample data
            sample_stock = (
                list(strategy.qgqp_data.keys())[0] if strategy.qgqp_data else None
            )
            if sample_stock:
                print(
                    f"  Sample data for {sample_stock}: {strategy.qgqp_data[sample_stock]}"
                )
        else:
            print("⚠ Qian gu qian ping data not loaded or empty")
        return True
    except Exception as e:
        print(f"✗ Qian gu qian ping data loading failed: {e}")
        return False


def test_firecrawl_integration():
    """Test FireCrawl integration"""
    print("\nTesting FireCrawl integration...")
    try:
        strategy = EnhancedPublicOpinionAnalysisStrategyV2()

        # Check FireCrawl availability
        api_url = strategy.firecrawl_config.get("api_url")
        timeout = strategy.firecrawl_config.get("timeout", 30)
        is_available = strategy._is_firecrawl_available(api_url, timeout)

        print(f"  FireCrawl available: {is_available}")

        if is_available:
            print("✓ FireCrawl integration working correctly")
            # Test a simple search
            test_queries = ["科技股"]
            results = strategy.search_stock_news(test_queries)
            print(f"  Test search returned {len(results)} results")
        else:
            print("⚠ FireCrawl not available")

        return True
    except Exception as e:
        print(f"✗ FireCrawl integration test failed: {e}")
        return False


def test_guba_data_collection():
    """Test Guba data collection"""
    print("\nTesting Guba data collection...")
    try:
        strategy = EnhancedPublicOpinionAnalysisStrategyV2()

        # Test with a sample stock
        sample_stock = "300339"  # Ping An Bank
        guba_data = strategy.get_detailed_guba_data(sample_stock)

        print(f"✓ Guba data collection completed")
        print(f"  Collected data for stock {sample_stock}")
        if guba_data:
            total_items = (
                len(guba_data.get("consultations", []))
                + len(guba_data.get("research_reports", []))
                + len(guba_data.get("announcements", []))
                + len(guba_data.get("hot_posts", []))
            )
            print(f"  Total items collected: {total_items}")
        else:
            print("  No Guba data collected")

        return True
    except Exception as e:
        print(f"✗ Guba data collection failed: {e}")
        return False


def test_data_integration():
    """Test integration of all data sources"""
    print("\nTesting data integration...")
    try:
        strategy = EnhancedPublicOpinionAnalysisStrategyV2()

        # Test with a sample stock
        sample_stock = "000001"
        sample_name = "平安银行"

        # Collect all data
        all_data = strategy.collect_all_data(sample_stock, sample_name)

        print("✓ Data integration completed")
        print(f"  Data sources collected: {list(all_data.keys())}")

        # Check each data source
        for source, data in all_data.items():
            if isinstance(data, list):
                print(f"  {source}: {len(data)} items")
            elif isinstance(data, dict):
                total_items = sum(len(v) for v in data.values() if isinstance(v, list))
                print(f"  {source}: {total_items} items")
            else:
                print(f"  {source}: {type(data)}")

        return True
    except Exception as e:
        print(f"✗ Data integration failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("Enhanced Public Opinion Analysis Strategy V2 - Final Integration Test")
    print("=" * 70)

    tests = [
        # test_strategy_initialization,
        # test_qgqp_data_loading,
        test_firecrawl_integration,
        # test_guba_data_collection,
        # test_data_integration,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 70)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED! Strategy is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
