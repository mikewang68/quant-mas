#!/usr/bin/env python3
"""
Debug script to diagnose why the three MA bullish arrangement strategy selects 0 stocks
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.three_ma_bullish_arrangement_strategy import ThreeMABullishArrangementStrategy

def create_debug_data():
    """Create debug data that should satisfy the strategy criteria"""
    # Create dates for about a year of data
    dates = pd.date_range('2024-08-01', periods=50, freq='D')

    # Create price data with a clear bullish arrangement pattern
    # We'll create data where the price is clearly above all moving averages
    # and the moving averages are in the correct order and trending upward

    # Start with a base price and create upward trending data
    base_price = 100
    trend = np.linspace(0, 20, 50)  # Upward trend of 20 points
    noise = np.random.normal(0, 1, 50)  # Some noise

    close_prices = base_price + trend + noise

    # Ensure the last few prices are higher to create clear bullish arrangement
    close_prices[-5:] = np.linspace(125, 130, 5)  # Higher closing prices at the end

    # Create DataFrame
    data = pd.DataFrame({
        'date': dates,
        'open': close_prices * (0.98 + np.random.uniform(-0.01, 0.01, 50)),
        'high': close_prices * (1.02 + np.random.uniform(-0.01, 0.01, 50)),
        'low': close_prices * (0.98 + np.random.uniform(-0.01, 0.01, 50)),
        'close': close_prices,
        'volume': np.random.randint(1000000, 2000000, 50),
        'amount': close_prices * np.random.randint(1000000, 2000000, 50)
    })

    return data

def debug_strategy():
    """Debug the three MA bullish arrangement strategy"""
    print("Debugging Three MA Bullish Arrangement Strategy...")

    # Create strategy instance with default parameters
    strategy_params = {
        'short': 5,
        'mid': 13,
        'long': 34
    }
    strategy = ThreeMABullishArrangementStrategy(params=strategy_params)

    # Create debug data
    debug_data = create_debug_data()
    print(f"Created debug data with {len(debug_data)} rows")
    print(f"First few close prices: {debug_data['close'].head().tolist()}")
    print(f"Last few close prices: {debug_data['close'].tail().tolist()}")

    # Manually calculate moving averages to verify our expectations
    close_prices = debug_data['close'].values
    ma5 = pd.Series(close_prices).rolling(window=5).mean().iloc[-1]
    ma13 = pd.Series(close_prices).rolling(window=13).mean().iloc[-1]
    ma34 = pd.Series(close_prices).rolling(window=34).mean().iloc[-1] if len(close_prices) >= 34 else None

    print(f"Manual calculation:")
    print(f"  Last close price: {close_prices[-1]:.2f}")
    print(f"  MA5: {ma5:.2f}")
    print(f"  MA13: {ma13:.2f}")
    print(f"  MA34: {ma34:.2f}" if ma34 else "  MA34: Not enough data")

    # Check price arrangement
    if ma34:
        print(f"Price arrangement check:")
        print(f"  Close > MA5: {close_prices[-1] > ma5}")
        print(f"  MA5 > MA13: {ma5 > ma13}")
        print(f"  MA13 > MA34: {ma13 > ma34}")
        print(f"  Bullish arrangement: {close_prices[-1] > ma5 > ma13 > ma34}")

    # Test the analyze method with detailed debugging
    meets_criteria, reason, score, golden_cross = strategy.analyze(debug_data)

    print(f"\nStrategy analysis results:")
    print(f"  Meets criteria: {meets_criteria}")
    print(f"  Reason: {reason}")
    print(f"  Score: {score}")
    print(f"  Golden cross detected: {golden_cross}")

    # Let's also test with more realistic data that should definitely meet criteria
    print(f"\n--- Testing with ideal bullish data ---")

    # Create ideal bullish data
    ideal_dates = pd.date_range('2024-01-01', periods=100, freq='D')
    # Create clearly upward trending prices
    ideal_close = np.linspace(100, 150, 100)  # Strong upward trend

    ideal_data = pd.DataFrame({
        'date': ideal_dates,
        'open': ideal_close * 0.99,
        'high': ideal_close * 1.01,
        'low': ideal_close * 0.99,
        'close': ideal_close,
        'volume': np.full(100, 1500000),
        'amount': ideal_close * 1500000
    })

    print(f"Ideal data last 10 close prices: {ideal_data['close'].tail(10).tolist()}")

    # Manual calculation for ideal data
    ideal_close_prices = ideal_data['close'].values
    ideal_ma5 = pd.Series(ideal_close_prices).rolling(window=5).mean().iloc[-1]
    ideal_ma13 = pd.Series(ideal_close_prices).rolling(window=13).mean().iloc[-1]
    ideal_ma34 = pd.Series(ideal_close_prices).rolling(window=34).mean().iloc[-1]

    print(f"Ideal data manual calculation:")
    print(f"  Last close price: {ideal_close_prices[-1]:.2f}")
    print(f"  MA5: {ideal_ma5:.2f}")
    print(f"  MA13: {ideal_ma13:.2f}")
    print(f"  MA34: {ideal_ma34:.2f}")
    print(f"  Close > MA5 > MA13 > MA34: {ideal_close_prices[-1] > ideal_ma5 > ideal_ma13 > ideal_ma34}")

    # Test with ideal data
    ideal_meets_criteria, ideal_reason, ideal_score, ideal_golden_cross = strategy.analyze(ideal_data)

    print(f"\nIdeal data strategy analysis:")
    print(f"  Meets criteria: {ideal_meets_criteria}")
    print(f"  Reason: {ideal_reason}")
    print(f"  Score: {ideal_score}")
    print(f"  Golden cross detected: {ideal_golden_cross}")

if __name__ == "__main__":
    try:
        debug_strategy()
    except Exception as e:
        print(f"Debug failed with error: {e}")
        import traceback
        traceback.print_exc()

