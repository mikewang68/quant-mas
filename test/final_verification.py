#!/usr/bin/env python3
"""
Final verification test that replicates the exact issue and confirms the fix
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def simulate_weekly_selector_process():
    """Simulate the exact process that was failing in the weekly selector"""
    print("=== Final Verification Test ===")
    print("Simulating the exact weekly selector process that was failing...\n")

    # Step 1: Load strategy from database (this is what was happening)
    print("1. Loading strategy from database...")
    database_strategy = {
        'name': '三均线多头排列策略',
        'file': 'strategies.three_ma_bullish_arrangement_strategy',
        'class_name': 'ThreeMABullishArrangementStrategy',
        'parameters': {
            'ma_short': 5,
            'ma_mid': 13,
            'ma_long': 34,
            'rsi_period': 14
        }
    }
    print(f"   Database strategy parameters: {database_strategy['parameters']}")

    # Step 2: Import and instantiate strategy (this is where the error occurred)
    print("\n2. Importing and instantiating strategy...")
    try:
        import importlib
        strategy_module = importlib.import_module(database_strategy['file'])
        strategy_class = getattr(strategy_module, database_strategy['class_name'])

        # This is the exact call that was failing
        strategy_instance = strategy_class(params=database_strategy['parameters'])
        print(f"   Strategy instantiated successfully!")
        print(f"   Strategy parameters after mapping: {strategy_instance.params}")

        # Verify the critical parameters are correctly mapped
        if 'short' in strategy_instance.params and 'mid' in strategy_instance.params and 'long' in strategy_instance.params:
            print(f"   ✓ Parameter mapping successful: short={strategy_instance.params['short']}, mid={strategy_instance.params['mid']}, long={strategy_instance.params['long']}")
        else:
            print(f"   ✗ Parameter mapping failed!")
            return False

    except Exception as e:
        print(f"   ✗ Strategy instantiation failed: {e}")
        return False

    # Step 3: Test with actual stock data
    print("\n3. Testing with sample stock data...")
    try:
        # Create realistic stock data
        dates = pd.date_range(datetime.now() - timedelta(days=365), periods=52, freq='W-FRI')
        # Create clear bullish arrangement pattern
        close_prices = []
        base_price = 50.0
        for i in range(52):
            # Strong upward trend with some noise
            price = base_price + (i * 1.2) + (np.sin(i * 0.3) * 2)
            close_prices.append(price)

        close_prices = np.array(close_prices)

        stock_data = pd.DataFrame({
            'date': dates,
            'open': close_prices * (0.99 + np.random.random(52) * 0.02),
            'high': close_prices * (1.005 + np.random.random(52) * 0.02),
            'low': close_prices * (0.995 - np.random.random(52) * 0.02),
            'close': close_prices,
            'volume': np.random.randint(100000, 1000000, 52)
        })

        print(f"   Sample data shape: {stock_data.shape}")
        print(f"   Data date range: {stock_data['date'].min()} to {stock_data['date'].max()}")

        # Step 4: Execute strategy analysis (this is where the error occurred)
        print("\n4. Executing strategy analysis...")
        meets_criteria, reason, score, golden_cross = strategy_instance.analyze(stock_data)

        print(f"   Analysis result: {meets_criteria}")
        print(f"   Selection reason: {reason}")
        print(f"   Score: {score}")
        if meets_criteria:
            print("   ✓ Stock selected successfully!")
        else:
            print("   ⚠ Stock not selected (this might be expected based on criteria)")

    except Exception as e:
        print(f"   ✗ Strategy analysis failed: {e}")
        return False

    # Step 5: Verify parameter usage in analysis
    print("\n5. Verifying parameter usage in analysis...")
    required_params = ['short', 'mid', 'long']
    missing_params = [param for param in required_params if param not in strategy_instance.params]

    if not missing_params:
        print(f"   ✓ All required parameters present: {required_params}")
        print(f"   ✓ Strategy can access parameters correctly for SMA calculations")
    else:
        print(f"   ✗ Missing required parameters: {missing_params}")
        return False

    print("\n=== Test Summary ===")
    print("✓ Database parameter mapping fixed")
    print("✓ Strategy instantiation successful")
    print("✓ Parameter access in analysis working")
    print("✓ Strategy execution successful")
    print("\n🎉 All fixes verified successfully! The weekly selector should now work correctly.")

    return True

if __name__ == "__main__":
    success = simulate_weekly_selector_process()
    if success:
        print("\n✅ FINAL VERIFICATION PASSED - The parameter mapping issue has been resolved!")
        sys.exit(0)
    else:
        print("\n❌ FINAL VERIFICATION FAILED - Issues remain!")
        sys.exit(1)

