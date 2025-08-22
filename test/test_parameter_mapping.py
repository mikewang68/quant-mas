#!/usr/bin/env python3
"""
Test script to verify parameter mapping fix for ThreeMABullishArrangementStrategy
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.three_ma_bullish_arrangement_strategy import ThreeMABullishArrangementStrategy

def test_parameter_mapping():
    """Test that parameter mapping works correctly"""
    print("Testing parameter mapping...")

    # Test 1: Database-style parameters (ma_short, ma_mid, ma_long)
    db_params = {
        'ma_short': 5,
        'ma_mid': 13,
        'ma_long': 34,
        'rsi_period': 14,
        'rsi_min': 30,
        'rsi_max': 70
    }

    strategy1 = ThreeMABullishArrangementStrategy(params=db_params)
    print(f"Database-style params: {db_params}")
    print(f"Mapped strategy params: {strategy1.params}")

    # Verify that the mapping worked
    assert strategy1.params['short'] == 5, f"Expected short=5, got {strategy1.params['short']}"
    assert strategy1.params['mid'] == 13, f"Expected mid=13, got {strategy1.params['mid']}"
    assert strategy1.params['long'] == 34, f"Expected long=34, got {strategy1.params['long']}"
    assert strategy1.params['rsi_period'] == 14, f"Expected rsi_period=14, got {strategy1.params['rsi_period']}"

    # Test 2: Strategy-style parameters (short, mid, long)
    strategy_params = {
        'short': 5,
        'mid': 13,
        'long': 34,
        'rsi_period': 14,
        'rsi_min': 30,
        'rsi_max': 70
    }

    strategy2 = ThreeMABullishArrangementStrategy(params=strategy_params)
    print(f"Strategy-style params: {strategy_params}")
    print(f"Strategy params: {strategy2.params}")

    # Verify that the parameters are preserved
    assert strategy2.params['short'] == 5, f"Expected short=5, got {strategy2.params['short']}"
    assert strategy2.params['mid'] == 13, f"Expected mid=13, got {strategy2.params['mid']}"
    assert strategy2.params['long'] == 34, f"Expected long=34, got {strategy2.params['long']}"
    assert strategy2.params['rsi_period'] == 14, f"Expected rsi_period=14, got {strategy2.params['rsi_period']}"

    # Test 3: Mixed parameters (should prioritize strategy-style)
    mixed_params = {
        'ma_short': 10,  # Should be ignored
        'ma_mid': 20,    # Should be ignored
        'ma_long': 50,   # Should be ignored
        'short': 5,      # Should be used
        'mid': 13,       # Should be used
        'long': 34,      # Should be used
        'rsi_period': 14
    }

    strategy3 = ThreeMABullishArrangementStrategy(params=mixed_params)
    print(f"Mixed params: {mixed_params}")
    print(f"Mapped strategy params: {strategy3.params}")

    # Verify that strategy-style parameters take precedence
    assert strategy3.params['short'] == 5, f"Expected short=5, got {strategy3.params['short']}"
    assert strategy3.params['mid'] == 13, f"Expected mid=13, got {strategy3.params['mid']}"
    assert strategy3.params['long'] == 34, f"Expected long=34, got {strategy3.params['long']}"

    print("All parameter mapping tests passed!")

def test_strategy_analysis():
    """Test that the strategy works with the mapped parameters"""
    print("\nTesting strategy analysis with mapped parameters...")

    # Create test data
    dates = pd.date_range('2023-01-01', periods=50, freq='D')
    # Create data with clear bullish arrangement
    close_prices = np.array([100 + i*0.5 + np.sin(i*0.1)*2 for i in range(50)])

    test_data = pd.DataFrame({
        'date': dates,
        'open': close_prices * 0.99,
        'high': close_prices * 1.02,
        'low': close_prices * 0.98,
        'close': close_prices,
        'volume': np.random.randint(1000, 10000, 50)
    })

    # Test with database-style parameters
    db_params = {
        'ma_short': 5,
        'ma_mid': 13,
        'ma_long': 34
    }

    strategy = ThreeMABullishArrangementStrategy(params=db_params)
    meets_criteria, reason, score, golden_cross = strategy.analyze(test_data)

    print(f"Analysis result: meets_criteria={meets_criteria}, reason={reason}")
    print(f"Score: {score}, Golden cross: {golden_cross}")

    print("Strategy analysis test completed!")

if __name__ == "__main__":
    test_parameter_mapping()
    test_strategy_analysis()
    print("\nAll tests completed successfully!")

