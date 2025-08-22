#!/usr/bin/env python3
"""
Debug script to replicate the exact real execution and see what's going wrong
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the strategy directly
from strategies.three_ma_bullish_arrangement_strategy import ThreeMABullishArrangementStrategy

def debug_real_execution():
    """Debug the exact real execution process"""
    print("=== Debugging Real Execution Process ===\n")

    # Step 1: Simulate exactly how the weekly selector gets parameters from database
    print("1. Simulating database strategy parameters (as they come from MongoDB)...")
    database_strategy_params = {
        'ma_short': 5,
        'ma_mid': 13,
        'ma_long': 34,
        'rsi_period': 14
    }
    print(f"   Database parameters: {database_strategy_params}")

    # Step 2: Simulate how weekly selector passes these to strategy constructor
    print("\n2. Simulating weekly selector strategy instantiation...")
    try:
        strategy = ThreeMABullishArrangementStrategy(params=database_strategy_params)
        print(f"   Strategy instantiated successfully!")
        print(f"   Strategy params after constructor: {strategy.params}")

        # Check if mapping worked
        if 'short' in strategy.params and 'mid' in strategy.params and 'long' in strategy.params:
            print(f"   ✓ Parameter mapping successful!")
            print(f"     short: {strategy.params['short']}")
            print(f"     mid: {strategy.params['mid']}")
            print(f"     long: {strategy.params['long']}")
        else:
            print(f"   ✗ Parameter mapping failed!")
            missing = [p for p in ['short', 'mid', 'long'] if p not in strategy.params]
            print(f"     Missing parameters: {missing}")
            return False

    except Exception as e:
        print(f"   ✗ Strategy instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 3: Create realistic test data that should meet criteria
    print("\n3. Creating realistic test data...")
    try:
        # Create 52 weeks of data (about a year)
        dates = pd.date_range(datetime.now() - timedelta(days=365), periods=52, freq='W-FRI')

        # Create data with clear bullish trend
        base_price = 100.0
        close_prices = []
        for i in range(52):
            # Strong upward trend with some noise
            price = base_price + (i * 1.5) + (np.sin(i * 0.3) * 3)
            close_prices.append(price)

        close_prices = np.array(close_prices)

        # Create DataFrame with all required columns
        test_data = pd.DataFrame({
            'date': dates,
            'open': close_prices * (0.99 + np.random.random(52) * 0.02),
            'high': close_prices * (1.005 + np.random.random(52) * 0.02),
            'low': close_prices * (0.995 - np.random.random(52) * 0.02),
            'close': close_prices,
            'volume': np.random.randint(100000, 1000000, 52)
        })

        print(f"   Test data shape: {test_data.shape}")
        print(f"   Data range: {test_data['close'].min():.2f} to {test_data['close'].max():.2f}")
        print(f"   Last 5 closing prices: {test_data['close'].tail().values}")

    except Exception as e:
        print(f"   ✗ Test data creation failed: {e}")
        return False

    # Step 4: Execute strategy analysis exactly as weekly selector would
    print("\n4. Executing strategy analysis...")
    try:
        meets_criteria, reason, score, golden_cross = strategy.analyze(test_data)

        print(f"   Analysis result:")
        print(f"     Meets criteria: {meets_criteria}")
        print(f"     Reason: {reason}")
        print(f"     Score: {score}")
        print(f"     Golden cross: {golden_cross}")

        if meets_criteria:
            print(f"   ✓ Stock would be SELECTED!")
        else:
            print(f"   ⚠ Stock would NOT be selected")

    except Exception as e:
        print(f"   ✗ Strategy analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 5: Debug detailed parameter access
    print("\n5. Debugging parameter access in analysis...")
    try:
        required_params = ['short', 'mid', 'long']
        for param in required_params:
            if param in strategy.params:
                print(f"   ✓ {param}: {strategy.params[param]} (type: {type(strategy.params[param])})")
            else:
                print(f"   ✗ {param}: MISSING")

        # Check if they're integers
        if all(isinstance(strategy.params.get(p), int) for p in required_params):
            print(f"   ✓ All parameters are integers")
        else:
            print(f"   ⚠ Some parameters are not integers:")
            for param in required_params:
                if param in strategy.params:
                    print(f"     {param}: {strategy.params[param]} (type: {type(strategy.params[param])})")

    except Exception as e:
        print(f"   ✗ Parameter access debugging failed: {e}")
        return False

    print("\n=== Debug Summary ===")
    print("If all steps above show success, the strategy should work in the weekly selector.")
    print("If stocks are still not being selected, the issue might be:")
    print("1. Data quality issues (not enough data points, wrong data format)")
    print("2. Strategy criteria still too strict")
    print("3. Issues with how the weekly selector processes the results")

    return True

if __name__ == "__main__":
    debug_real_execution()

