#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detailed test for Three Moving Average Bullish Arrangement Strategy signals
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.three_ma_bullish_arrangement_strategy import ThreeMABullishArrangementStrategy

def create_data_with_golden_cross():
    """Create test data that clearly shows a golden cross pattern"""
    # Create dates for the past 20 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=20)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    # Ensure we have exactly 20 data points
    n_points = len(dates)

    # Create prices that clearly show a golden cross
    # For the first 10 days: MA5 < MA13 (no golden cross)
    # For the last 10 days: MA5 > MA13 (golden cross occurs)
    prices = []

    # First 10 days - downtrend then uptrend but MA5 < MA13
    for i in range(n_points // 2):
        prices.append(100 + i * 0.1 + np.random.normal(0, 0.5))

    # Last 10 days - strong uptrend where MA5 crosses above MA13
    for i in range(n_points - len(prices)):
        prices.append(105 + i * 1.0 + np.random.normal(0, 0.5))

    # Ensure we have exactly n_points prices
    prices = prices[:n_points]

    # Create OHLC data with consistent lengths
    opens = [p * (1 + np.random.normal(0, 0.01)) for p in prices]
    highs = [p * (1 + abs(np.random.normal(0, 0.02))) for p in prices]
    lows = [p * (1 - abs(np.random.normal(0, 0.02))) for p in prices]
    volumes = np.random.randint(1000000, 5000000, n_points).tolist()

    df = pd.DataFrame({
        'date': dates,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': prices,
        'volume': volumes
    })

    return df

def test_golden_cross_signals():
    """Test the golden cross signal generation"""
    print("=== Testing Golden Cross Signal Generation ===")

    # Create test data with a clear golden cross
    test_data = create_data_with_golden_cross()
    print(f"Created test data with {len(test_data)} rows")

    # Initialize strategy
    strategy = ThreeMABullishArrangementStrategy()
    print(f"Initialized strategy with parameters: {strategy.params}")

    # Test generate_signals method
    signals = strategy.generate_signals(test_data)

    print(f"\nSignal Generation Results:")
    print(f"Total signals: {len(signals)}")

    # Check if we have any BUY signals
    buy_signals = signals[signals['signal'] == 'BUY']
    print(f"BUY signals: {len(buy_signals)}")

    if len(buy_signals) > 0:
        print("BUY signals found at indices:")
        for idx in buy_signals.index:
            print(f"  - Index {idx}: Date {test_data.loc[idx, 'date'] if idx < len(test_data) else 'N/A'}")

    # Print last few signals
    print(f"\nLast 5 signals:")
    for i in range(max(0, len(signals)-5), len(signals)):
        if i < len(test_data):
            signal_date = test_data.loc[i, 'date']
            print(f"  Index {i}: Date {signal_date}, Signal {signals.loc[i, 'signal']}, Position {signals.loc[i, 'position']}")

    return signals

def create_simple_upward_trend_data():
    """Create simple upward trend data to test moving average calculations"""
    dates = pd.date_range(start='2023-01-01', periods=20, freq='D')

    # Create a clear upward trend
    prices = [100 + i*0.5 for i in range(20)]

    # Create OHLC data
    opens = [p * (1 + np.random.normal(0, 0.005)) for p in prices]
    highs = [p * 1.01 for p in prices]
    lows = [p * 0.99 for p in prices]
    volumes = [1000000] * 20

    df = pd.DataFrame({
        'date': dates,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': prices,
        'volume': volumes
    })

    return df

def test_simple_signals():
    """Test signals with simple upward trend data"""
    print("\n=== Testing Simple Upward Trend Signal Generation ===")

    # Create simple test data
    test_data = create_simple_upward_trend_data()
    print(f"Created simple test data with {len(test_data)} rows")

    # Initialize strategy
    strategy = ThreeMABullishArrangementStrategy()

    # Test generate_signals method
    signals = strategy.generate_signals(test_data)

    print(f"\nSimple Signal Generation Results:")
    print(f"Total signals: {len(signals)}")

    # Print all signals
    for i in range(len(signals)):
        if i < len(test_data):
            signal_date = test_data.loc[i, 'date']
            print(f"  Date {signal_date}, Signal {signals.loc[i, 'signal']}, Position {signals.loc[i, 'position']}")

    return signals

def test_position_calculation():
    """Test position calculation functionality"""
    print("\n=== Testing Position Calculation ===")

    # Initialize strategy
    strategy = ThreeMABullishArrangementStrategy()

    # Test different signals
    portfolio_value = 100000.0  # 100k portfolio
    current_price = 50.0

    # Test BUY signal
    buy_position = strategy.calculate_position_size('BUY', portfolio_value, current_price)
    print(f"BUY signal position size: {buy_position} shares (for ${portfolio_value} portfolio at ${current_price} price)")

    # Test SELL signal
    sell_position = strategy.calculate_position_size('SELL', portfolio_value, current_price)
    print(f"SELL signal position size: {sell_position} shares")

    # Test HOLD signal
    hold_position = strategy.calculate_position_size('HOLD', portfolio_value, current_price)
    print(f"HOLD signal position size: {hold_position} shares")

    return buy_position, sell_position, hold_position

if __name__ == "__main__":
    print("Starting Detailed Three Moving Average Bullish Arrangement Strategy Signal Tests...")

    # Test golden cross signals
    golden_cross_signals = test_golden_cross_signals()

    # Test simple signals
    simple_signals = test_simple_signals()

    # Test position calculation
    test_position_calculation()

    print("\n=== Detailed Signal Test Completed ===")

