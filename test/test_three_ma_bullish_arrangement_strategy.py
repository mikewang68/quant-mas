#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Three Moving Average Bullish Arrangement Strategy
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.three_ma_bullish_arrangement_strategy import ThreeMABullishArrangementStrategy

def create_test_data():
    """Create test stock data with a bullish arrangement pattern"""
    # Create dates for the past 50 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=50)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    # Create a DataFrame with bullish arrangement pattern
    # We'll create data where MA5 > MA13 > MA34 and prices are above all MAs
    np.random.seed(42)  # For reproducible results

    # Create base prices with an upward trend
    base_prices = np.linspace(100, 130, len(dates))

    # Add some noise
    noise = np.random.normal(0, 1, len(dates))

    # Create prices with upward trend and noise
    prices = base_prices + noise

    # Ensure the latest prices show a bullish arrangement
    # Adjust the last few prices to ensure MA5 > MA13 > MA34
    prices[-5:] = np.linspace(125, 135, 5)  # Strong upward trend at the end

    # Create OHLC data
    df = pd.DataFrame({
        'date': dates,
        'open': prices * (1 + np.random.normal(0, 0.01, len(prices))),  # Small variation from close
        'high': prices * (1 + np.abs(np.random.normal(0, 0.02, len(prices)))),  # High is higher
        'low': prices * (1 - np.abs(np.random.normal(0, 0.02, len(prices)))),   # Low is lower
        'close': prices,
        'volume': np.random.randint(1000000, 5000000, len(prices))  # Random volume
    })

    return df

def create_test_data_with_golden_cross():
    """Create test stock data with a golden cross pattern"""
    # Create dates for the past 50 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=50)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    # Create a DataFrame with a golden cross pattern
    np.random.seed(42)  # For reproducible results

    # Create prices that show a crossover
    prices = []
    for i in range(len(dates)):
        if i < 30:
            # Before crossover - MA5 < MA13
            prices.append(100 + i * 0.2 + np.random.normal(0, 1))
        else:
            # After crossover - MA5 > MA13 (golden cross)
            prices.append(110 + (i - 30) * 0.5 + np.random.normal(0, 1))

    # Create OHLC data
    df = pd.DataFrame({
        'date': dates,
        'open': [p * (1 + np.random.normal(0, 0.01)) for p in prices],
        'high': [p * (1 + abs(np.random.normal(0, 0.02))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.02))) for p in prices],
        'close': prices,
        'volume': np.random.randint(1000000, 5000000, len(prices))
    })

    return df

def test_strategy_bullish_arrangement():
    """Test the strategy with bullish arrangement data"""
    print("=== Testing Three MA Bullish Arrangement Strategy ===")

    # Create test data
    test_data = create_test_data()
    print(f"Created test data with {len(test_data)} rows")

    # Initialize strategy
    strategy = ThreeMABullishArrangementStrategy()
    print(f"Initialized strategy with parameters: {strategy.params}")

    # Test analyze method
    meets_criteria, reason, score, golden_cross = strategy.analyze(test_data)

    print(f"\nAnalysis Results:")
    print(f"Meets Criteria: {meets_criteria}")
    print(f"Reason: {reason}")
    print(f"Score: {score}")
    print(f"Golden Cross Detected: {golden_cross}")

    # Test generate_signals method
    signals = strategy.generate_signals(test_data)
    print(f"\nSignal Generation:")
    print(f"Last signal: {signals.iloc[-1]['signal'] if not signals.empty else 'No signals'}")
    print(f"Position: {signals.iloc[-1]['position'] if not signals.empty else 'No position'}")

    return meets_criteria, reason, score, golden_cross

def test_strategy_golden_cross():
    """Test the strategy with golden cross data"""
    print("\n=== Testing Golden Cross Detection ===")

    # Create test data with golden cross
    test_data = create_test_data_with_golden_cross()
    print(f"Created test data with {len(test_data)} rows")

    # Initialize strategy
    strategy = ThreeMABullishArrangementStrategy()
    print(f"Initialized strategy with parameters: {strategy.params}")

    # Test analyze method
    meets_criteria, reason, score, golden_cross = strategy.analyze(test_data)

    print(f"\nAnalysis Results:")
    print(f"Meets Criteria: {meets_criteria}")
    print(f"Reason: {reason}")
    print(f"Score: {score}")
    print(f"Golden Cross Detected: {golden_cross}")

    return meets_criteria, reason, score, golden_cross

def test_strategy_execute():
    """Test the execute method"""
    print("\n=== Testing Execute Method ===")

    # Create multiple test datasets
    stock_data = {
        '000001.SZ': create_test_data(),
        '000002.SZ': create_test_data_with_golden_cross(),
        '000003.SZ': pd.DataFrame()  # Empty data to test error handling
    }

    # Initialize strategy
    strategy = ThreeMABullishArrangementStrategy()
    print(f"Initialized strategy with parameters: {strategy.params}")

    # Mock db_manager for testing (we won't actually save to database)
    class MockDBManager:
        def __init__(self):
            pass

    # Test execute method (without saving to database)
    try:
        selected_stocks = strategy.execute(stock_data, "TestAgent", MockDBManager())
        print(f"\nExecute Results:")
        print(f"Selected stocks count: {len(selected_stocks)}")
        for stock in selected_stocks:
            print(f"  - {stock['code']}: {stock['selection_reason']}")
    except Exception as e:
        print(f"Execute method error (expected due to mock DB): {e}")
        # This is expected since we're using a mock DB manager

    return len(selected_stocks) if 'selected_stocks' in locals() else 0

if __name__ == "__main__":
    print("Starting Three Moving Average Bullish Arrangement Strategy Tests...")

    # Test bullish arrangement
    test_strategy_bullish_arrangement()

    # Test golden cross
    test_strategy_golden_cross()

    # Test execute method
    test_strategy_execute()

    print("\n=== Test Completed ===")

