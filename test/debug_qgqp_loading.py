#!/usr/bin/env python3
"""
Test script to debug qian gu qian ping data loading issue
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2

def test_qgqp_data_loading():
    """Test qian gu qian ping data loading in detail"""
    print("Testing qian gu qian ping data loading...")

    try:
        strategy = EnhancedPublicOpinionAnalysisStrategyV2()
        print("✓ Strategy initialized")

        # Check if qgqp data was loaded
        print(f"Qian gu qian ping data attribute exists: {hasattr(strategy, 'qian_gu_qian_ping_data')}")

        if hasattr(strategy, 'qian_gu_qian_ping_data'):
            qgqp_data = strategy.qian_gu_qian_ping_data
            print(f"Qian gu qian ping data value: {qgqp_data}")

            if qgqp_data is None:
                print("⚠ Qian gu qian ping data is None")
            elif isinstance(qgqp_data, dict):
                print(f"✓ Qian gu qian ping data is a dictionary with {len(qgqp_data)} entries")
                if qgqp_data:
                    # Show sample data
                    sample_stock = list(qgqp_data.keys())[0]
                    print(f"  Sample data for {sample_stock}: {qgqp_data[sample_stock]}")
            else:
                print(f"? Qian gu qian ping data is {type(qgqp_data)}: {qgqp_data}")

        # Test getting data for a specific stock
        sample_stock = "000001"
        stock_data = strategy.get_qian_gu_qian_ping_data_for_stock(sample_stock)
        print(f"Data for stock {sample_stock}: {stock_data}")

        return True
    except Exception as e:
        print(f"✗ Qian gu qian ping data loading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_akshare_qgqp_directly():
    """Test AkShare qian gu qian ping function directly"""
    print("\nTesting AkShare qian gu qian ping function directly...")

    try:
        import akshare as ak

        print("Calling ak.stock_comment_em()...")
        qgqp_df = ak.stock_comment_em()

        print(f"Returned data type: {type(qgqp_df)}")
        print(f"Is DataFrame empty: {qgqp_df.empty}")

        if not qgqp_df.empty:
            print(f"DataFrame shape: {qgqp_df.shape}")
            print("First few rows:")
            print(qgqp_df.head())
            print("\nColumn names:")
            print(list(qgqp_df.columns))
        else:
            print("DataFrame is empty")

        return True
    except Exception as e:
        print(f"✗ AkShare qian gu qian ping test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Qian Gu Qian Ping Data Loading Debug Test")
    print("=" * 50)

    tests = [
        test_akshare_qgqp_directly,
        test_qgqp_data_loading,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("❌ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

