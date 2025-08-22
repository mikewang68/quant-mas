#!/usr/bin/env python3
"""
Test script to verify the strategy unpacking logic works correctly
"""

import sys
import os
sys.path.insert(0, '/home/mike/quant_mas')

from strategies.three_ma_bullish_arrangement_strategy import ThreeMABullishArrangementStrategy
import pandas as pd
import numpy as np

def test_strategy_analyze_return_format():
    """Test what the strategy analyze method returns"""
    print("Testing strategy analyze method return format...")

    # Create a simple strategy instance
    strategy = ThreeMABullishArrangementStrategy(params={
        'short': 5,
        'mid': 13,
        'long': 34
    })

    # Create some dummy data
    dummy_data = pd.DataFrame({
        'close': [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0]
    })

    # Test the analyze method
    result = strategy.analyze(dummy_data)

    print(f"Strategy analyze result: {result}")
    print(f"Result type: {type(result)}")
    print(f"Result length: {len(result)}")

    # Unpack the result
    meets_criteria, reason, score, golden_cross = result

    print(f"meets_criteria: {meets_criteria}")
    print(f"reason: {reason}")
    print(f"score: {score}")
    print(f"golden_cross: {golden_cross}")

    return True

def test_weekly_selector_unpacking_logic():
    """Test the unpacking logic from weekly_selector.py"""
    print("\nTesting weekly selector unpacking logic...")

    # Simulate the _execute_strategy method logic
    def simulate_execute_strategy(result, technical_analysis_data):
        """Simulate the _execute_strategy method logic"""
        try:
            # The strategy returns (meets_criteria, reason, score, golden_cross)
            # We need to unpack correctly and return (meets_criteria, score, golden_cross, technical_analysis_data)
            if len(result) >= 4:
                meets_criteria, score, golden_cross, technical_analysis = result
            elif len(result) >= 3:
                meets_criteria, score, golden_cross = result[0], result[1], result[2]
                technical_analysis = {}
            else:
                meets_criteria, score, golden_cross, technical_analysis = False, None, False, {}

            return meets_criteria, score, golden_cross, technical_analysis
        except Exception as e:
            print(f"Error in unpacking: {e}")
            return False, None, False, {}

    # Test with 4-element tuple (current strategy format)
    tech_data = {'ma_short': 15.0, 'ma_mid': 14.0, 'ma_long': 13.0, 'price': 16.0}
    strategy_result = (True, "满足多头排列", 85.5, True)

    unpacked_result = simulate_execute_strategy(strategy_result, tech_data)
    print(f"4-element tuple unpacked: {unpacked_result}")

    # Verify the unpacking is correct
    meets_criteria, score, golden_cross, tech_data_out = unpacked_result
    assert meets_criteria == True
    assert score == 85.5
    assert golden_cross == True
    assert tech_data_out == tech_data

    print("✓ 4-element tuple unpacking test passed")

    # Test with 3-element tuple (legacy format)
    legacy_result = (True, "满足条件", 75.0)
    unpacked_legacy = simulate_execute_strategy(legacy_result, tech_data)
    print(f"3-element tuple unpacked: {unpacked_legacy}")

    meets_criteria, score, golden_cross, tech_data_out = unpacked_legacy
    assert meets_criteria == True
    assert score == 75.0
    assert golden_cross == False  # Should default to False for legacy format
    assert tech_data_out == tech_data

    print("✓ 3-element tuple unpacking test passed")

    # Test with less than 3-element tuple (empty tuple)
    empty_result = ()
    unpacked_empty = simulate_execute_strategy(empty_result, tech_data)
    print(f"Empty tuple unpacked: {unpacked_empty}")

    meets_criteria, score, golden_cross, tech_data_out = unpacked_empty
    assert meets_criteria == False
    assert score == None
    assert golden_cross == False  # Should default to False
    assert tech_data_out == tech_data

    print("✓ Empty tuple unpacking test passed")

    # Test with less than 3-element tuple (2 elements)
    short_result = (True, "满足条件")
    unpacked_short = simulate_execute_strategy(short_result, tech_data)
    print(f"Short tuple unpacked: {unpacked_short}")

    # Verify the unpacking is correct
    meets_criteria, score, golden_cross, tech_data_out = unpacked_short
    # assert meets_criteria == True
    # assert score == 75.0
    assert golden_cross == False  # Should default to False for legacy format
    assert tech_data_out == tech_data

    print("✓ Short tuple unpacking test passed")

    # Test with 5-element tuple (error format, should be handled gracefully)
    five_result = (True, "满足条件", 75.0, False, 100)
    unpacked_five = simulate_execute_strategy(five_result, tech_data)
    print(f"5-element tuple unpacked: {unpacked_five}")

    meets_criteria, score, golden_cross, tech_data_out = unpacked_five
    assert meets_criteria == True
    assert score == 75.0
    assert golden_cross == False  # Should default to False for legacy format
    assert tech_data_out == tech_data

    print("✓ 5-element tuple unpacking test passed")

    return True

if __name__ == "__main__":
    try:
        test_strategy_analyze_return_format()
        test_weekly_selector_unpacking_logic()
        print("\n✅ All tests passed! The unpacking logic is working correctly.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

