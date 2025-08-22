#!/usr/bin/env python3
"""
Debug the actual weekly selector process to see why it selects 0 stocks
when 2100+ should qualify
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import importlib

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def simulate_weekly_selector_process():
    """Simulate the exact weekly selector process step by step"""
    print("=== Simulating Weekly Selector Process ===\n")

    # Step 1: Load strategy exactly as weekly selector does
    print("1. Loading strategy...")
    database_strategy = {
        'name': '三均线多头排列策略（基本型）',
        'file': 'strategies.three_ma_bullish_arrangement_strategy',
        'class_name': 'ThreeMABullishArrangementStrategy',
        'parameters': {
            'ma_short': 5,
            'ma_mid': 13,
            'ma_long': 34
        }
    }

    print(f"Database strategy: {database_strategy}")

    try:
        # Load strategy module and class
        strategy_module = importlib.import_module(database_strategy['file'])
        strategy_class = getattr(strategy_module, database_strategy['class_name'])
        strategy_params = database_strategy['parameters']

        print(f"✓ Strategy module loaded: {database_strategy['file']}")
        print(f"✓ Strategy class loaded: {database_strategy['class_name']}")
        print(f"✓ Strategy params: {strategy_params}")

        # Create strategy instance
        strategy_instance = strategy_class(params=strategy_params)
        print(f"✓ Strategy instance created")
        print(f"  Instance params: {strategy_instance.params}")

    except Exception as e:
        print(f"✗ Strategy loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 2: Test strategy with data that should qualify
    print("\n2. Testing with qualifying data...")

    # Create strong bullish data that should definitely qualify
    dates = pd.date_range(datetime.now() - timedelta(days=365), periods=52, freq='W-FRI')

    # Create very strong bullish trend
    close_prices = []
    base_price = 50.0
    for i in range(52):
        # Very strong upward trend
        price = base_price + (i * 3.0)  # +3 per week = very strong trend
        close_prices.append(price)
    close_prices = np.array(close_prices)

    test_data = pd.DataFrame({
        'date': dates,
        'open': close_prices * 0.99,
        'high': close_prices * 1.01,
        'low': close_prices * 0.99,
        'close': close_prices,
        'volume': np.ones(52) * 1000000
    })

    print(f"Test data shape: {test_data.shape}")
    print(f"Price range: {close_prices.min():.2f} to {close_prices.max():.2f}")
    print(f"Last 3 prices: {close_prices[-3:]}")

    # Step 3: Execute strategy exactly as weekly selector does
    print("\n3. Executing strategy...")
    try:
        if strategy_instance and test_data is not None and not test_data.empty:
            print("✓ Strategy instance and data valid")

            # This is exactly what weekly selector does
            meets_criteria, reason, score, golden_cross = strategy_instance.analyze(test_data)

            print(f"Analysis result:")
            print(f"  Meets criteria: {meets_criteria}")
            print(f"  Reason: {reason}")
            print(f"  Score: {score}")
            print(f"  Golden cross: {golden_cross}")

            if meets_criteria:
                print("✓ SUCCESS: Stock would be selected!")
                return True
            else:
                print("✗ FAILURE: Stock would NOT be selected!")
                return False
        else:
            print("✗ Strategy instance or data invalid")
            return False

    except Exception as e:
        print(f"✗ Strategy execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_strategy_logic():
    """Check the actual strategy logic to see what might be wrong"""
    print("\n=== Checking Strategy Logic ===")

    from strategies.three_ma_bullish_arrangement_strategy import ThreeMABullishArrangementStrategy

    # Create strategy
    strategy = ThreeMABullishArrangementStrategy(params={'ma_short': 5, 'ma_mid': 13, 'ma_long': 34})

    # Create perfect bullish data
    close_prices = np.array([i for i in range(50, 150)])  # 50 to 149 - perfect upward trend

    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    perfect_data = pd.DataFrame({
        'date': dates,
        'open': close_prices * 0.99,
        'high': close_prices * 1.01,
        'low': close_prices * 0.99,
        'close': close_prices,
        'volume': np.ones(100) * 1000000
    })

    print(f"Perfect data - close prices: {close_prices[:5]} ... {close_prices[-5:]}")

    # Manual calculation to verify what should happen
    print("\nManual calculation of expected moving averages:")
    ma5 = np.mean(close_prices[-5:])
    ma13 = np.mean(close_prices[-13:])
    ma34 = np.mean(close_prices[-34:])

    current_price = close_prices[-1]

    print(f"Current price: {current_price}")
    print(f"MA5: {ma5:.2f}")
    print(f"MA13: {ma13:.2f}")
    print(f"MA34: {ma34:.2f}")

    price_condition = current_price > ma5 > ma13 > ma34
    print(f"Price condition (current > MA5 > MA13 > MA34): {price_condition}")

    # Execute strategy
    meets_criteria, reason, score, golden_cross = strategy.analyze(perfect_data)

    print(f"\nStrategy result:")
    print(f"  Meets criteria: {meets_criteria}")
    print(f"  Reason: {reason}")

if __name__ == "__main__":
    print("Debugging why weekly selector selects 0 stocks when 2100+ should qualify...\n")

    success = simulate_weekly_selector_process()
    check_strategy_logic()

    print(f"\n=== Summary ===")
    if success:
        print("The strategy works correctly in isolation.")
        print("If weekly selector still selects 0 stocks, the issue must be:")
        print("1. Data processing issues in weekly selector")
        print("2. How multiple stocks are processed")
        print("3. Issues with real database data format")
    else:
        print("There's still an issue with the strategy itself.")

