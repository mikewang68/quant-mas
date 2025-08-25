#!/usr/bin/env python3
"""
Test script for the unified database write interface
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.base_strategy import BaseStrategy
from strategies.trend_following_strategy import TrendFollowingStrategy
from strategies.macd_strategy import MACDStrategy
from strategies.rsi_strategy import RSIStrategy
from strategies.ma_crossover_strategy import MACrossoverStrategy
from strategies.three_ma_bullish_arrangement_strategy import ThreeMABullishArrangementStrategy


def test_strategy_data_formatting():
    """Test that all strategies format data consistently"""
    print("Testing strategy data formatting consistency...")

    # Create mock stock data
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    mock_data = pd.DataFrame({
        'date': dates,
        'open': np.random.uniform(100, 110, 100),
        'high': np.random.uniform(110, 120, 100),
        'low': np.random.uniform(90, 100, 100),
        'close': np.random.uniform(100, 110, 100),
        'volume': np.random.uniform(1000000, 2000000, 100)
    })

    stock_data = {'000001': mock_data}

    # Test each strategy
    strategies = [
        ("Trend Following", TrendFollowingStrategy("Trend Following", {"fast": 5, "slow": 13})),
        ("MACD", MACDStrategy("MACD", {"fast_period": 12, "slow_period": 26})),
        ("RSI", RSIStrategy("RSI", {"period": 14})),
        ("MA Crossover", MACrossoverStrategy("MA Crossover", {"fast_period": 5, "slow_period": 13})),
        ("Three MA Bullish", ThreeMABullishArrangementStrategy("Three MA Bullish", {"short": 5, "mid": 13, "long": 34}))
    ]

    for strategy_name, strategy in strategies:
        try:
            # Test that the strategy has the required formatting methods
            assert hasattr(strategy, 'format_stock_data_for_pool'), f"{strategy_name} missing format_stock_data_for_pool method"
            assert hasattr(strategy, 'format_strategy_output'), f"{strategy_name} missing format_strategy_output method"

            print(f"✓ {strategy_name} has required formatting methods")
        except Exception as e:
            print(f"✗ {strategy_name} failed: {e}")
            return False

    print("Strategy data formatting consistency tests passed!\n")
    return True


def test_formatted_data_structure():
    """Test that formatted data has consistent structure"""
    print("Testing formatted data structure...")

    # Create a mock strategy for testing
    class MockStrategy(BaseStrategy):
        def generate_signals(self, data):
            return pd.DataFrame()

        def calculate_position_size(self, signal, portfolio_value, price):
            return 0.0

    strategy = MockStrategy("Test Strategy", {"param1": 10})

    # Test format_stock_data_for_pool
    stock_data = {
        'code': '000001',
        'selection_reason': 'Test reason',
        'score': 0.85,
        'position': 0.1,
        'technical_analysis': {'rsi': 30.5},
        'signals': {'signal': 'BUY'},
        'metadata': {'test': 'data'}
    }

    formatted = strategy.format_stock_data_for_pool(stock_data)

    # Check required fields
    required_fields = ['code', 'selection_reason', 'score', 'position', 'strategy_name', 'strategy_key', 'technical_analysis', 'signals', 'metadata']
    for field in required_fields:
        assert field in formatted, f"Missing required field: {field}"

    # Check data types
    assert isinstance(formatted['code'], str), "code should be string"
    assert isinstance(formatted['score'], float), "score should be float"
    assert isinstance(formatted['position'], float), "position should be float"
    assert isinstance(formatted['technical_analysis'], dict), "technical_analysis should be dict"
    assert isinstance(formatted['signals'], dict), "signals should be dict"
    assert isinstance(formatted['metadata'], dict), "metadata should be dict"

    print("✓ Formatted stock data has correct structure and types")

    # Test format_strategy_output
    stocks = [stock_data]
    output = strategy.format_strategy_output(
        stocks=stocks,
        agent_name="TestAgent",
        date="2023-01-01",
        strategy_params={"test": "params"},
        additional_metadata={"test_meta": "value"}
    )

    # Check required fields in strategy output
    required_output_fields = ['strategy_key', 'agent_name', 'strategy_id', 'strategy_name', 'stocks', 'date', 'count', 'strategy_params', 'metadata']
    for field in required_output_fields:
        assert field in output, f"Missing required output field: {field}"

    # Check stocks array structure
    assert isinstance(output['stocks'], list), "stocks should be list"
    assert len(output['stocks']) == 1, "stocks should contain one item"
    assert output['stocks'][0] == formatted, "stocks should contain formatted stock data"

    print("✓ Formatted strategy output has correct structure and types")
    print("Formatted data structure tests passed!\n")
    return True


def test_strategy_key_generation():
    """Test that strategy keys are generated consistently"""
    print("Testing strategy key generation...")

    # Create a mock strategy for testing
    class MockStrategy(BaseStrategy):
        def generate_signals(self, data):
            return pd.DataFrame()

        def calculate_position_size(self, signal, portfolio_value, price):
            return 0.0

    strategy1 = MockStrategy("Test Strategy 1", {})
    strategy2 = MockStrategy("Test Strategy 2", {})

    # Test format_stock_data_for_pool generates consistent strategy keys
    stock_data1 = {'code': '000001', 'selection_reason': 'Test', 'score': 0.8, 'position': 0.1}
    stock_data2 = {'code': '000002', 'selection_reason': 'Test', 'score': 0.9, 'position': 0.15}

    formatted1 = strategy1.format_stock_data_for_pool(stock_data1)
    formatted2 = strategy1.format_stock_data_for_pool(stock_data2)
    formatted3 = strategy2.format_stock_data_for_pool(stock_data1)

    # Same strategy should generate same strategy_key prefix
    assert formatted1['strategy_key'] == formatted2['strategy_key'], "Same strategy should generate same strategy_key"
    assert formatted1['strategy_key'] != formatted3['strategy_key'], "Different strategies should generate different strategy_keys"

    print("✓ Strategy keys are generated consistently")
    print("Strategy key generation tests passed!\n")
    return True


def main():
    """Main test function"""
    print("Running unified database interface tests...\n")

    try:
        # Run all tests
        test_strategy_data_formatting()
        test_formatted_data_structure()
        test_strategy_key_generation()

        print("All unified database interface tests passed!")
        return 0
    except Exception as e:
        print(f"Error in unified database interface tests: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

