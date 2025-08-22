#!/usr/bin/env python3
"""
Comprehensive debug script that replicates the exact weekly selector process
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import importlib

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the strategy directly
from strategies.three_ma_bullish_arrangement_strategy import ThreeMABullishArrangementStrategy

def simulate_weekly_selector_complete_process():
    """Simulate the complete weekly selector process step by step"""
    print("=== Comprehensive Weekly Selector Process Debug ===\n")

    # Step 1: Simulate database strategy loading
    print("1. Simulating database strategy loading...")
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
    print(f"   Database strategy: {database_strategy}")

    # Step 2: Simulate weekly selector initialization
    print("\n2. Simulating weekly selector initialization...")
    try:
        # Load strategy module
        strategy_module = importlib.import_module(database_strategy['file'])
        strategy_class = getattr(strategy_module, database_strategy['class_name'])
        strategy_params = database_strategy['parameters']

        print(f"   Strategy module: {database_strategy['file']}")
        print(f"   Strategy class: {database_strategy['class_name']}")
        print(f"   Strategy params: {strategy_params}")

        # Create strategy instance (exactly as weekly selector does)
        strategy_instance = strategy_class(params=strategy_params)
        print(f"   Strategy instance created successfully!")
        print(f"   Strategy instance params: {strategy_instance.params}")

    except Exception as e:
        print(f"   ✗ Strategy initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 3: Simulate data processing for a stock
    print("\n3. Simulating data processing for a stock...")
    try:
        # Create realistic test data
        dates = pd.date_range(datetime.now() - timedelta(days=365), periods=52, freq='W-FRI')

        # Create strong bullish trend data
        base_price = 100.0
        close_prices = []
        for i in range(52):
            price = base_price + (i * 1.5) + (np.sin(i * 0.3) * 3)
            close_prices.append(price)
        close_prices = np.array(close_prices)

        # Create DataFrame with all required columns
        k_data = pd.DataFrame({
            'date': dates,
            'open': close_prices * (0.99 + np.random.random(52) * 0.02),
            'high': close_prices * (1.005 + np.random.random(52) * 0.02),
            'low': close_prices * (0.995 - np.random.random(52) * 0.02),
            'close': close_prices,
            'volume': np.random.randint(100000, 1000000, 52)
        })

        print(f"   K-line data shape: {k_data.shape}")
        print(f"   Data date range: {k_data['date'].min()} to {k_data['date'].max()}")
        print(f"   Last 3 closing prices: {k_data['close'].tail(3).values}")

        # Check data validity (as weekly selector does)
        if k_data.empty:
            print(f"   ✗ K-line data is empty!")
            return False
        else:
            print(f"   ✓ K-line data is valid")

    except Exception as e:
        print(f"   ✗ Data processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 4: Simulate strategy execution (exactly as weekly selector does)
    print("\n4. Simulating strategy execution...")
    try:
        # Check if strategy instance exists and data is valid
        if strategy_instance and k_data is not None and not k_data.empty:
            print(f"   ✓ Strategy instance and data are valid")

            # Execute strategy analyze method
            meets_criteria, reason, score, golden_cross = strategy_instance.analyze(k_data)

            print(f"   Analysis result:")
            print(f"     Meets criteria: {meets_criteria}")
            print(f"     Reason: {reason}")
            print(f"     Score: {score}")
            print(f"     Golden cross: {golden_cross}")

            # This is exactly what weekly selector does
            if meets_criteria:
                print(f"   ✓ Stock WOULD be selected by weekly selector!")
                return True
            else:
                print(f"   ⚠ Stock would NOT be selected by weekly selector")
                return False
        else:
            print(f"   ✗ Strategy instance or data invalid")
            return False

    except Exception as e:
        print(f"   ✗ Strategy execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 5: Debug any potential issues
    print("\n5. Additional debugging...")
    try:
        # Check parameter types
        print(f"   Strategy parameters:")
        for key, value in strategy_instance.params.items():
            print(f"     {key}: {value} (type: {type(value)})")

        # Check if required parameters are integers
        required_params = ['short', 'mid', 'long']
        for param in required_params:
            if param in strategy_instance.params:
                if isinstance(strategy_instance.params[param], int):
                    print(f"   ✓ {param} is integer: {strategy_instance.params[param]}")
                else:
                    print(f"   ⚠ {param} is not integer: {strategy_instance.params[param]} (type: {type(strategy_instance.params[param])})")
            else:
                print(f"   ✗ {param} is missing!")

        # Check data format
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col in k_data.columns:
                print(f"   ✓ Column '{col}' exists")
            else:
                print(f"   ✗ Column '{col}' missing!")

    except Exception as e:
        print(f"   ✗ Additional debugging failed: {e}")

    return True

def test_edge_cases():
    """Test edge cases that might cause issues"""
    print("\n=== Testing Edge Cases ===\n")

    # Test 1: Empty data
    print("1. Testing with empty data...")
    strategy = ThreeMABullishArrangementStrategy(params={'ma_short': 5, 'ma_mid': 13, 'ma_long': 34})
    empty_data = pd.DataFrame()
    result = strategy.analyze(empty_data)
    print(f"   Empty data result: {result}")

    # Test 2: Insufficient data
    print("\n2. Testing with insufficient data...")
    dates = pd.date_range('2023-01-01', periods=10, freq='W')  # Only 10 data points
    insufficient_data = pd.DataFrame({
        'date': dates,
        'open': np.random.random(10) * 100,
        'high': np.random.random(10) * 100,
        'low': np.random.random(10) * 100,
        'close': np.random.random(10) * 100,
        'volume': np.random.randint(1000, 10000, 10)
    })
    result = strategy.analyze(insufficient_data)
    print(f"   Insufficient data result: meets_criteria={result[0]}, reason={result[1]}")

    # Test 3: NaN values in data
    print("\n3. Testing with NaN values...")
    dates = pd.date_range('2023-01-01', periods=50, freq='W')
    close_prices = np.random.random(50) * 100
    close_prices[5] = np.nan  # Insert NaN
    nan_data = pd.DataFrame({
        'date': dates,
        'open': np.random.random(50) * 100,
        'high': np.random.random(50) * 100,
        'low': np.random.random(50) * 100,
        'close': close_prices,
        'volume': np.random.randint(1000, 10000, 50)
    })
    result = strategy.analyze(nan_data)
    print(f"   NaN data result: meets_criteria={result[0]}")

if __name__ == "__main__":
    print("Starting comprehensive debug of weekly selector process...\n")

    success = simulate_weekly_selector_complete_process()

    test_edge_cases()

    print(f"\n=== Final Summary ===")
    if success:
        print("✅ The weekly selector process should work correctly!")
        print("If it's still selecting 0 stocks, the issue might be:")
        print("1. Real market data doesn't meet the strategy criteria")
        print("2. Data quality issues in the actual database")
        print("3. Issues with how multiple stocks are processed")
    else:
        print("❌ There are still issues with the process!")

