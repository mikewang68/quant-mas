#!/usr/bin/env python3
"""
Test script to verify the three MA bullish arrangement strategy fix
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.three_ma_bullish_arrangement_strategy import ThreeMABullishArrangementStrategy
from data.mongodb_manager import MongoDBManager

def create_test_data():
    """Create test data that satisfies the strategy criteria"""
    # Create dates
    dates = pd.date_range('2023-01-01', periods=50, freq='D')

    # Create price data with bullish arrangement pattern
    # Start with lower prices and gradually increase to create upward trends
    open_prices = np.linspace(100, 120, 50) + np.random.normal(0, 1, 50)
    high_prices = open_prices + np.random.uniform(0, 2, 50)
    low_prices = open_prices - np.random.uniform(0, 2, 50)
    close_prices = (open_prices + high_prices + low_prices) / 3 + np.random.normal(0, 0.5, 50)

    # Ensure the last few prices are higher to create the bullish arrangement
    close_prices[-10:] = np.linspace(115, 125, 10)

    # Create DataFrame
    data = pd.DataFrame({
        'date': dates,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': np.random.randint(1000000, 2000000, 50),
        'amount': close_prices * np.random.randint(1000000, 2000000, 50)
    })

    return data

def test_strategy():
    """Test the three MA bullish arrangement strategy"""
    print("Testing Three MA Bullish Arrangement Strategy...")

    # Create strategy instance with default parameters
    strategy_params = {
        'short': 5,
        'mid': 13,
        'long': 34
    }
    strategy = ThreeMABullishArrangementStrategy(params=strategy_params)

    # Create test data
    test_data = create_test_data()
    print(f"Created test data with {len(test_data)} rows")

    # Test the analyze method
    meets_criteria, reason, score, golden_cross = strategy.analyze(test_data)

    print(f"Meets criteria: {meets_criteria}")
    print(f"Reason: {reason}")
    print(f"Score: {score}")
    print(f"Golden cross detected: {golden_cross}")

    # Test the execute method with a mock database manager
    class MockDBManager:
        def __init__(self):
            self.pool_collection = None

        def save_to_pool(self, *args, **kwargs):
            print("Mock save_to_pool called")
            return True

    mock_db = MockDBManager()

    # Create stock data dictionary
    stock_data = {
        '000001': test_data,
        '000002': test_data.copy()
    }

    # Test execute method
    results = strategy.execute(stock_data, "TestAgent", mock_db)
    print(f"Execute method returned {len(results)} results")

    # Test generate_signals method
    signals = strategy.generate_signals(test_data)
    print(f"Generated {len(signals)} signals")
    if len(signals) > 0:
        print(f"Last signal: {signals.iloc[-1]['signal']}")

    return meets_criteria, results

if __name__ == "__main__":
    try:
        meets_criteria, results = test_strategy()
        print("\nTest completed successfully!")
        print(f"Strategy meets criteria: {meets_criteria}")
        print(f"Number of results: {len(results)}")
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

