#!/usr/bin/env python3
"""
Integration test for the weekly selector with the parameter mapping fix
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.three_ma_bullish_arrangement_strategy import ThreeMABullishArrangementStrategy

def mock_database_strategy_data():
    """Mock the strategy data as it would be stored in the database"""
    return {
        '_id': 'test_strategy_id',
        'name': '三均线多头排列策略',
        'file': 'strategies.three_ma_bullish_arrangement_strategy',
        'class_name': 'ThreeMABullishArrangementStrategy',
        'type': 'technical',
        'description': '基于三均线多头排列的选股策略',
        'parameters': {
            'ma_short': 5,
            'ma_mid': 13,
            'ma_long': 34,
            'rsi_period': 14,
            'rsi_min': 30,
            'rsi_max': 70
        }
    }

def test_weekly_selector_integration():
    """Test that simulates how the weekly selector loads and uses the strategy"""
    print("Testing weekly selector integration...")

    # Simulate how weekly selector loads strategy from database
    strategy_data = mock_database_strategy_data()
    print(f"Database strategy data: {strategy_data}")

    # Extract parameters as the weekly selector would
    strategy_params = strategy_data.get('parameters', {})
    print(f"Parameters from database: {strategy_params}")

    # Import the strategy module as the weekly selector would
    import importlib
    strategy_module = importlib.import_module(strategy_data['file'])
    strategy_class = getattr(strategy_module, strategy_data['class_name'])

    # Instantiate the strategy with database parameters
    strategy_instance = strategy_class(params=strategy_params)
    print(f"Strategy instance params: {strategy_instance.params}")

    # Verify that parameter mapping worked
    assert strategy_instance.params['short'] == 5, f"Expected short=5, got {strategy_instance.params['short']}"
    assert strategy_instance.params['mid'] == 13, f"Expected mid=13, got {strategy_instance.params['mid']}"
    assert strategy_instance.params['long'] == 34, f"Expected long=34, got {strategy_instance.params['long']}"

    # Test with sample data
    print("\nTesting strategy analysis with sample data...")

    # Create sample stock data with bullish arrangement
    dates = pd.date_range(datetime.now() - timedelta(days=365), periods=52, freq='W-FRI')
    # Create upward trending data
    close_prices = np.array([50 + i*0.8 + np.sin(i*0.2)*3 for i in range(52)])

    sample_data = pd.DataFrame({
        'date': dates,
        'open': close_prices * (0.98 + np.random.random(52) * 0.04),
        'high': close_prices * (1.01 + np.random.random(52) * 0.03),
        'low': close_prices * (0.97 - np.random.random(52) * 0.03),
        'close': close_prices,
        'volume': np.random.randint(100000, 1000000, 52),
        'amount': close_prices * np.random.randint(100000, 1000000, 52)
    })

    # Execute strategy analysis as the weekly selector would
    meets_criteria, reason, score, golden_cross = strategy_instance.analyze(sample_data)

    print(f"Analysis result:")
    print(f"  Meets criteria: {meets_criteria}")
    print(f"  Reason: {reason}")
    print(f"  Score: {score}")
    print(f"  Golden cross: {golden_cross}")

    print("\nWeekly selector integration test completed!")

def test_multiple_stock_simulation():
    """Simulate processing multiple stocks like the weekly selector does"""
    print("\nTesting multiple stock simulation...")

    # Load strategy as weekly selector would
    strategy_data = mock_database_strategy_data()
    import importlib
    strategy_module = importlib.import_module(strategy_data['file'])
    strategy_class = getattr(strategy_module, strategy_data['class_name'])
    strategy_instance = strategy_class(params=strategy_data['parameters'])

    # Create sample stock data for multiple stocks
    stock_codes = ['000001', '000002', '600000', '600036']
    selected_stocks = []

    for i, code in enumerate(stock_codes):
        # Create different patterns for different stocks
        dates = pd.date_range(datetime.now() - timedelta(days=365), periods=52, freq='W-FRI')

        # Stock 0 and 2: bullish arrangement (should be selected)
        # Stock 1 and 3: random/no pattern (should not be selected)
        if i % 2 == 0:
            # Upward trend with bullish arrangement
            close_prices = np.array([50 + j*0.8 + np.sin(j*0.2)*3 + i*5 for j in range(52)])
        else:
            # Random pattern (no clear trend)
            close_prices = 50 + np.random.random(52) * 20 + i*5

        sample_data = pd.DataFrame({
            'date': dates,
            'open': close_prices * (0.98 + np.random.random(52) * 0.04),
            'high': close_prices * (1.01 + np.random.random(52) * 0.03),
            'low': close_prices * (0.97 - np.random.random(52) * 0.03),
            'close': close_prices,
            'volume': np.random.randint(100000, 1000000, 52),
            'amount': close_prices * np.random.randint(100000, 1000000, 52)
        })

        # Analyze as weekly selector would
        meets_criteria, reason, score, golden_cross = strategy_instance.analyze(sample_data)

        print(f"Stock {code}: meets_criteria={meets_criteria}, score={score}")

        if meets_criteria:
            selected_stocks.append(code)

    print(f"\nSelected stocks: {selected_stocks}")
    print(f"Number of selected stocks: {len(selected_stocks)}")

    print("Multiple stock simulation completed!")

if __name__ == "__main__":
    test_weekly_selector_integration()
    test_multiple_stock_simulation()
    print("\nAll integration tests completed successfully!")

