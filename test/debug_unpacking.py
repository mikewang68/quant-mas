#!/usr/bin/env python3
"""
Debug script to identify the exact unpacking error in weekly_selector.py
"""

import sys
import os
import traceback

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from strategies.three_ma_bullish_arrangement_strategy import ThreeMABullishArrangementStrategy
import pandas as pd
import numpy as np

def test_strategy_analyze():
    """Test the strategy's analyze method to see what it returns"""
    print("Testing strategy analyze method...")

    # Create a mock strategy instance
    strategy = ThreeMABullishArrangementStrategy()

    # Create mock data with enough points
    dates = pd.date_range('2023-01-01', periods=50, freq='D')
    data = pd.DataFrame({
        'date': dates,
        'open': np.random.rand(50) * 10 + 20,
        'high': np.random.rand(50) * 10 + 25,
        'low': np.random.rand(50) * 10 + 15,
        'close': np.random.rand(50) * 10 + 20,
        'volume': np.random.rand(50) * 1000000,
        'amount': np.random.rand(50) * 10000000
    })

    # Make sure we have a bullish arrangement for testing
    # Set close prices in ascending order to simulate bullish trend
    data['close'] = np.linspace(20, 30, 50) + np.random.rand(50) * 0.5

    print("Mock data created with shape:", data.shape)
    print("Last few close prices:", data['close'].tail())

    try:
        # Call the analyze method
        result = strategy.analyze(data)
        print("Strategy analyze method returned:")
        print(f"Type: {type(result)}")
        print(f"Length: {len(result)}")
        print(f"Values: {result}")

        # Try to unpack it
        print("\nTrying to unpack result...")
        meets_criteria, reason, score, golden_cross = result
        print(f"Successfully unpacked:")
        print(f"  meets_criteria: {meets_criteria}")
        print(f"  reason: {reason}")
        print(f"  score: {score}")
        print(f"  golden_cross: {golden_cross}")

    except Exception as e:
        print(f"Error during strategy analyze test: {e}")
        traceback.print_exc()

def test_execute_strategy_unpacking():
    """Test the unpacking logic in weekly_selector's _execute_strategy method"""
    print("\n" + "="*50)
    print("Testing _execute_strategy unpacking logic...")

    # Simulate what _execute_strategy returns
    # Based on the code, it should return: (meets_criteria, score, golden_cross, technical_analysis_data)

    # Test case 1: Normal case with 4 values
    print("\nTest case 1: Normal 4-value result")
    result1 = (True, 85.5, False, {'ma_short': 25.5, 'ma_mid': 24.8, 'ma_long': 23.9})
    print(f"Result: {result1}")

    try:
        meets_criteria, score, golden_cross, technical_analysis = result1
        print("Successfully unpacked 4 values:")
        print(f"  meets_criteria: {meets_criteria}")
        print(f"  score: {score}")
        print(f"  golden_cross: {golden_cross}")
        print(f"  technical_analysis: {technical_analysis}")
    except Exception as e:
        print(f"Error unpacking 4 values: {e}")
        traceback.print_exc()

    # Test case 2: Try to unpack with wrong number of variables
    print("\nTest case 2: Wrong unpacking (trying 3 variables for 4 values)")
    try:
        meets_criteria, score, golden_cross = result1  # This should fail
        print("Unexpectedly succeeded in unpacking")
    except Exception as e:
        print(f"Expected error when unpacking 4 values into 3 variables: {e}")

    # Test case 3: What if strategy returns different number of values?
    print("\nTest case 3: What if strategy analyze returns different format?")
    mock_strategy_result = (True, "Some reason", 90.5, True)  # 4 values
    print(f"Mock strategy result: {mock_strategy_result}")

    # This is what _execute_strategy does:
    if len(mock_strategy_result) >= 4:
        meets_criteria, reason, score, golden_cross = mock_strategy_result
        result_to_return = (meets_criteria, score, golden_cross, {})
        print(f"_execute_strategy would return: {result_to_return}")

        # Now test unpacking this in select_stocks
        try:
            meets_criteria, score, golden_cross, technical_analysis = result_to_return
            print("Successfully unpacked in select_stocks context")
        except Exception as e:
            print(f"Error unpacking in select_stocks context: {e}")

if __name__ == "__main__":
    print("Debugging unpacking errors in weekly selector")
    print("="*50)

    test_strategy_analyze()
    test_execute_strategy_unpacking()

    print("\n" + "="*50)
    print("Debug script completed")

