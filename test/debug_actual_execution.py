#!/usr/bin/env python3
"""
Debug script to see actual execution with real parameters and data
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.three_ma_bullish_arrangement_strategy import ThreeMABullishArrangementStrategy

def debug_with_actual_params():
    """Debug with actual parameters from the system"""
    print("=== Debugging with Actual Parameters ===\n")

    # These are the actual parameters from your database
    actual_params = {
        'ma_short': 5,
        'ma_mid': 13,
        'ma_long': 34
    }

    print(f"Actual parameters from database: {actual_params}")

    # Create strategy with actual parameters
    strategy = ThreeMABullishArrangementStrategy(params=actual_params)

    print(f"Strategy parameters after mapping: {strategy.params}")

    # Check if all required parameters exist
    required_params = ['short', 'mid', 'long']
    for param in required_params:
        if param in strategy.params:
            print(f"✓ {param}: {strategy.params[param]} (type: {type(strategy.params[param])})")
        else:
            print(f"✗ {param}: MISSING")

    # Test with sample data
    print("\n=== Testing with Sample Data ===")

    # Create sample data similar to what would come from database
    dates = pd.date_range('2023-01-01', periods=50, freq='D')
    close_prices = np.array([100 + i*0.5 + np.sin(i*0.1)*2 for i in range(50)])

    sample_data = pd.DataFrame({
        'date': dates,
        'open': close_prices * 0.99,
        'high': close_prices * 1.02,
        'low': close_prices * 0.98,
        'close': close_prices,
        'volume': np.random.randint(1000, 10000, 50)
    })

    print(f"Sample data shape: {sample_data.shape}")
    print(f"Sample data columns: {list(sample_data.columns)}")
    print(f"Last 5 closing prices: {sample_data['close'].tail().values}")

    # Execute analysis
    print("\n=== Strategy Analysis ===")
    try:
        meets_criteria, reason, score, golden_cross = strategy.analyze(sample_data)
        print(f"Meets criteria: {meets_criteria}")
        print(f"Reason: {reason}")
        print(f"Score: {score}")
        print(f"Golden cross: {golden_cross}")
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

def debug_parameter_access():
    """Debug parameter access in the analyze method"""
    print("\n=== Debugging Parameter Access ===")

    strategy = ThreeMABullishArrangementStrategy(params={'ma_short': 5, 'ma_mid': 13, 'ma_long': 34})

    # Simulate what happens in the analyze method
    print("Simulating analyze method parameter access:")

    try:
        short_val = strategy.params['short']
        mid_val = strategy.params['mid']
        long_val = strategy.params['long']

        print(f"✓ Successfully accessed parameters:")
        print(f"  ma_short (short): {short_val}")
        print(f"  ma_mid (mid): {mid_val}")
        print(f"  ma_long (long): {long_val}")

        # Test max calculation
        max_val = max(short_val, mid_val, long_val)
        print(f"✓ Max value: {max_val}")

    except Exception as e:
        print(f"✗ Error accessing parameters: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_with_actual_params()
    debug_parameter_access()

