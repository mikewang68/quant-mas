#!/usr/bin/env python3
"""
Data quality check to see why real data isn't meeting strategy criteria
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.three_ma_bullish_arrangement_strategy import ThreeMABullishArrangementStrategy

def create_debug_data_analysis():
    """Create analysis to understand what real data looks like"""
    print("=== Data Quality Analysis ===\n")

    # Create different types of data to see which ones meet criteria
    test_cases = [
        ("Strong Bullish Trend", create_bullish_data),
        ("Sideways Movement", create_sideways_data),
        ("Bearish Trend", create_bearish_data),
        ("Volatile Data", create_volatile_data),
        ("Realistic Stock Data", create_realistic_data)
    ]

    # Strategy with parameters
    strategy = ThreeMABullishArrangementStrategy(params={'ma_short': 5, 'ma_mid': 13, 'ma_long': 34})

    for test_name, data_func in test_cases:
        print(f"--- {test_name} ---")
        try:
            test_data = data_func()
            meets_criteria, reason, score, golden_cross = strategy.analyze(test_data)

            print(f"Meets criteria: {meets_criteria}")
            if not meets_criteria:
                print(f"Reason: {reason}")
            else:
                print(f"Score: {score:.3f}")

            # Show last few data points
            if not test_data.empty:
                print(f"Last 3 closes: {test_data['close'].tail(3).values}")
                print(f"Data points: {len(test_data)}")

        except Exception as e:
            print(f"Error: {e}")
        print()

def create_bullish_data():
    """Create strongly bullish data"""
    dates = pd.date_range(datetime.now() - timedelta(days=365), periods=52, freq='W-FRI')
    base_price = 100.0
    close_prices = []
    for i in range(52):
        price = base_price + (i * 2.0) + (np.sin(i * 0.2) * 2)
        close_prices.append(price)
    close_prices = np.array(close_prices)

    return pd.DataFrame({
        'date': dates,
        'open': close_prices * (0.99 + np.random.random(52) * 0.02),
        'high': close_prices * (1.005 + np.random.random(52) * 0.02),
        'low': close_prices * (0.995 - np.random.random(52) * 0.02),
        'close': close_prices,
        'volume': np.random.randint(100000, 1000000, 52)
    })

def create_sideways_data():
    """Create sideways moving data"""
    dates = pd.date_range(datetime.now() - timedelta(days=365), periods=52, freq='W-FRI')
    base_price = 100.0
    close_prices = []
    for i in range(52):
        # Small oscillations around base price
        price = base_price + (np.sin(i * 0.5) * 5)
        close_prices.append(price)
    close_prices = np.array(close_prices)

    return pd.DataFrame({
        'date': dates,
        'open': close_prices * (0.99 + np.random.random(52) * 0.02),
        'high': close_prices * (1.005 + np.random.random(52) * 0.02),
        'low': close_prices * (0.995 - np.random.random(52) * 0.02),
        'close': close_prices,
        'volume': np.random.randint(100000, 1000000, 52)
    })

def create_bearish_data():
    """Create bearish data"""
    dates = pd.date_range(datetime.now() - timedelta(days=365), periods=52, freq='W-FRI')
    base_price = 100.0
    close_prices = []
    for i in range(52):
        # Decreasing price
        price = base_price - (i * 1.0) + (np.sin(i * 0.2) * 2)
        close_prices.append(price)
    close_prices = np.array(close_prices)

    return pd.DataFrame({
        'date': dates,
        'open': close_prices * (0.99 + np.random.random(52) * 0.02),
        'high': close_prices * (1.005 + np.random.random(52) * 0.02),
        'low': close_prices * (0.995 - np.random.random(52) * 0.02),
        'close': close_prices,
        'volume': np.random.randint(100000, 1000000, 52)
    })

def create_volatile_data():
    """Create highly volatile data"""
    dates = pd.date_range(datetime.now() - timedelta(days=365), periods=52, freq='W-FRI')
    close_prices = 100 + np.cumsum(np.random.randn(52) * 3)

    return pd.DataFrame({
        'date': dates,
        'open': close_prices * (0.99 + np.random.random(52) * 0.02),
        'high': close_prices * (1.005 + np.random.random(52) * 0.02),
        'low': close_prices * (0.995 - np.random.random(52) * 0.02),
        'close': close_prices,
        'volume': np.random.randint(100000, 1000000, 52)
    })

def create_realistic_data():
    """Create more realistic stock-like data"""
    dates = pd.date_range(datetime.now() - timedelta(days=365), periods=52, freq='W-FRI')

    # Simulate more realistic stock behavior
    returns = np.random.normal(0.001, 0.02, 52)  # Small positive drift
    prices = [100]
    for ret in returns:
        prices.append(prices[-1] * (1 + ret))
    prices = np.array(prices[1:])  # Remove initial price

    return pd.DataFrame({
        'date': dates,
        'open': prices * (0.99 + np.random.random(52) * 0.02),
        'high': prices * (1.005 + np.random.random(52) * 0.02),
        'low': prices * (0.995 - np.random.random(52) * 0.02),
        'close': prices,
        'volume': np.random.randint(100000, 1000000, 52)
    })

def analyze_strategy_sensitivity():
    """Analyze how sensitive the strategy is to different conditions"""
    print("=== Strategy Sensitivity Analysis ===\n")

    strategy = ThreeMABullishArrangementStrategy(params={'ma_short': 5, 'ma_mid': 13, 'ma_long': 34})

    # Test different bullish arrangements
    print("Testing different bullish arrangement strengths:")

    for strength in [0.5, 1.0, 1.5, 2.0, 2.5]:
        dates = pd.date_range(datetime.now() - timedelta(days=365), periods=52, freq='W-FRI')
        base_price = 100.0
        close_prices = []
        for i in range(52):
            price = base_price + (i * strength) + (np.sin(i * 0.2) * 2)
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

        meets_criteria, reason, score, golden_cross = strategy.analyze(test_data)
        print(f"Strength {strength}: {'✓' if meets_criteria else '✗'} ({reason[:50]}...)")

if __name__ == "__main__":
    create_debug_data_analysis()
    print()
    analyze_strategy_sensitivity()
    print("\n=== Key Insights ===")
    print("1. The strategy requires a clear bullish trend")
    print("2. Sideways or bearish data won't meet criteria")
    print("3. Volatility alone isn't enough - need upward momentum")
    print("4. Real market data may not show strong enough trends")
    print("5. The strategy might be too selective for current market conditions")

