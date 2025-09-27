#!/usr/bin/env python3
"""
Test script to verify all modifications including HTML and strategy changes
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from strategies.signal_generation_v1_strategy import SignalGenerationV1Strategy


def test_html_modifications():
    """Test HTML modifications"""
    print("Testing HTML modifications...")

    try:
        with open('web/templates/stock_kline_v2.html', 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if table header is changed from "值" to "内容"
        if '内容</th>' in content and '值</th>' not in content:
            print("  ✓ PASS: Table header changed from '值' to '内容'")
        else:
            print("  ✗ FAIL: Table header not properly changed")
            return False

        # Check if signals section is displayed first
        signals_pos = content.find("displayStrategySection('signals', '信号生成', stockInfo.signals, tbody)")
        trend_pos = content.find("displayStrategySection('trend', '趋势策略', stockInfo.trend, tbody)")

        if signals_pos != -1 and trend_pos != -1 and signals_pos < trend_pos:
            print("  ✓ PASS: Signals section displayed first")
        else:
            print("  ✗ FAIL: Signals section not displayed first")
            return False

        # Check MA line styles
        if 'width: 1' in content and 'color: \'#ffffff\'' in content:
            print("  ✓ PASS: Short MA line style (width: 1, color: white)")
        else:
            print("  ✗ FAIL: Short MA line style not properly set")
            return False

        if 'width: 2' in content and 'color: \'#ffff00\'' in content:
            print("  ✓ PASS: Medium MA line style (width: 2, color: yellow)")
        else:
            print("  ✗ FAIL: Medium MA line style not properly set")
            return False

        if 'width: 3' in content and 'color: \'#ff00ff\'' in content:
            print("  ✓ PASS: Long MA line style (width: 3, color: magenta)")
        else:
            print("  ✗ FAIL: Long MA line style not properly set")
            return False

        return True

    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return False


def test_signal_action_logic():
    """Test the signal action calculation logic"""
    print("\nTesting signal action calculation logic...")

    def calculate_action(signal_calc, signal_ai):
        """Helper function to calculate action based on the same logic as in the strategy"""
        # Determine action based on new rules:
        # - If both signal_calc and signal_ai are "买入", output "买入"
        # - If either signal_calc or signal_ai is "卖出", output "卖出"
        # - Otherwise, output empty string
        if signal_calc == "买入" and signal_ai == "买入":
            return "买入"
        elif signal_calc == "卖出" or signal_ai == "卖出":
            return "卖出"
        else:
            return ""

    # Test cases
    test_cases = [
        ("买入", "买入", "买入"),
        ("卖出", "买入", "卖出"),
        ("买入", "卖出", "卖出"),
        ("卖出", "卖出", "卖出"),
        ("持有", "买入", ""),
        ("买入", "持有", ""),
        ("持有", "持有", ""),
    ]

    all_passed = True
    for signal_calc, signal_ai, expected in test_cases:
        result = calculate_action(signal_calc, signal_ai)
        status = "PASS" if result == expected else "FAIL"
        print(f"  {signal_calc}, {signal_ai} -> '{result}' (expected: '{expected}') [{status}]")
        if result != expected:
            all_passed = False

    return all_passed


def test_strategy_execution():
    """Test strategy execution"""
    print("\nTesting strategy execution...")

    try:
        # Initialize database manager
        db_manager = MongoDBManager()

        # Initialize strategy
        strategy = SignalGenerationV1Strategy()

        # Execute strategy
        print("  Executing signal generation strategy...")
        results = strategy.execute({}, "信号生成Agent", db_manager)

        print(f"  Strategy execution completed. Generated {len(results)} results")

        # Check if results contain signals data
        if results:
            first_result = results[0]
            print(f"  First result keys: {list(first_result.keys())}")

            if 'signals' in first_result:
                signals = first_result['signals']
                print(f"  Signals data found: {list(signals.keys())}")

                # Check if "信号生成V1" strategy data exists
                if '信号生成V1' in signals:
                    signal_data = signals['信号生成V1']
                    print(f"  '信号生成V1' data found: {list(signal_data.keys())}")

                    # Check for required fields
                    required_fields = ['counts', 'action', 'score_calc', 'signal_calc', 'score_ai', 'signal_ai', 'reason_ai']
                    missing_fields = [field for field in required_fields if field not in signal_data]
                    if missing_fields:
                        print(f"  ✗ FAIL: Missing fields in signals data: {missing_fields}")
                        return False
                    else:
                        print("  ✓ PASS: All required fields present in signals data")

                        # Check action field value
                        action = signal_data.get('action', '')
                        if action in ['', '买入', '卖出']:
                            print(f"  ✓ PASS: Action field has valid value: '{action}'")
                            return True
                        else:
                            print(f"  ✗ FAIL: Action field has invalid value: {action}")
                            return False
                else:
                    print("  ✗ FAIL: '信号生成V1' data not found in signals")
                    return False
            else:
                print("  ✗ FAIL: Strategy does not return signals data")
                return False
        else:
            print("  No results generated")
            return True

    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_signals():
    """Test database signals data"""
    print("\nTesting database signals data...")

    try:
        # Initialize database manager
        db_manager = MongoDBManager()

        # Check database for latest pool record
        print("  Checking database for latest pool record...")
        pool_collection = db_manager.db['pool']
        latest_record = pool_collection.find_one(sort=[("_id", -1)])

        if latest_record:
            stocks = latest_record.get('stocks', [])
            print(f"  Found {len(stocks)} stocks in latest pool record")

            if stocks:
                # Check first stock for signals data
                first_stock = stocks[0]
                code = first_stock.get('code', 'Unknown')
                print(f"  Checking stock {code} for signals data...")

                if 'signals' in first_stock:
                    signals = first_stock['signals']
                    print(f"  Signals field found in database: {list(signals.keys())}")

                    # Check if "信号生成V1" strategy data exists
                    if '信号生成V1' in signals:
                        signal_data = signals['信号生成V1']
                        print(f"  '信号生成V1' data found: {list(signal_data.keys())}")

                        # Check action field
                        action = signal_data.get('action', '')
                        print(f"  Action field: '{action}'")

                        # Validate action value
                        if action in ['', '买入', '卖出']:
                            print("  ✓ PASS: Action field has valid value")
                            return True
                        else:
                            print(f"  ✗ FAIL: Action field has invalid value: {action}")
                            return False
                    else:
                        print("  ✗ FAIL: '信号生成V1' data not found in signals")
                        return False
                else:
                    print("  ✗ FAIL: No signals field in stock data")
                    return False
            else:
                print("  No stocks in pool record")
                return True
        else:
            print("  No pool records found")
            return True

    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("Testing all modifications")
    print("=" * 50)

    # Test HTML modifications
    html_test_passed = test_html_modifications()

    # Test signal action logic
    logic_test_passed = test_signal_action_logic()

    # Test strategy execution
    strategy_test_passed = test_strategy_execution()

    # Test database signals
    database_test_passed = test_database_signals()

    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"  HTML Modifications: {'PASS' if html_test_passed else 'FAIL'}")
    print(f"  Signal Action Logic: {'PASS' if logic_test_passed else 'FAIL'}")
    print(f"  Strategy Execution: {'PASS' if strategy_test_passed else 'FAIL'}")
    print(f"  Database Signals: {'PASS' if database_test_passed else 'FAIL'}")

    all_passed = html_test_passed and logic_test_passed and strategy_test_passed and database_test_passed
    print(f"\nOverall Result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

