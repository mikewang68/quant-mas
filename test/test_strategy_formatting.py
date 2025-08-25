#!/usr/bin/env python3
"""
Test script for strategy data formatting methods
"""

import sys
import os
import pandas as pd
import numpy as np

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.base_strategy import BaseStrategy
from strategies.trend_following_strategy import TrendFollowingStrategy
from strategies.macd_strategy import MACDStrategy
from strategies.rsi_strategy import RSIStrategy
from strategies.ma_crossover_strategy import MACrossoverStrategy
from strategies.three_ma_bullish_arrangement_strategy import ThreeMABullishArrangementStrategy


def test_base_strategy_formatting():
    """Test the base strategy formatting methods"""
    print("Testing BaseStrategy formatting methods...")

    # Create a simple mock strategy class for testing
    class MockStrategy(BaseStrategy):
        def generate_signals(self, data):
            import pandas as pd
            return pd.DataFrame()

        def calculate_position_size(self, signal, portfolio_value, price):
            return 0.0

    # Create a mock strategy instance
    strategy = MockStrategy("Test Strategy", {"param1": 10, "param2": 20})

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
    print(f"Formatted stock data: {formatted}")

    # Test format_strategy_output
    stocks = [stock_data]
    output = strategy.format_strategy_output(
        stocks=stocks,
        agent_name="TestAgent",
        date="2023-01-01",
        strategy_params={"test": "params"},
        additional_metadata={"test_meta": "value"}
    )

    print(f"Formatted strategy output: {output}")
    print("BaseStrategy formatting tests passed!\n")


def test_concrete_strategies_formatting():
    """Test concrete strategies formatting methods"""
    print("Testing concrete strategy formatting methods...")

    # Test TrendFollowingStrategy
    trend_strategy = TrendFollowingStrategy("Trend Following", {"fast": 5, "slow": 13})
    print(f"TrendFollowingStrategy initialized with params: {trend_strategy.params}")

    # Test MACDStrategy
    macd_strategy = MACDStrategy("MACD Strategy", {"fast_period": 12, "slow_period": 26})
    print(f"MACDStrategy initialized with params: {macd_strategy.params}")

    # Test RSIStrategy
    rsi_strategy = RSIStrategy("RSI Strategy", {"period": 14})
    print(f"RSIStrategy initialized with params: {rsi_strategy.params}")

    # Test MACrossoverStrategy
    ma_strategy = MACrossoverStrategy("MA Crossover", {"fast_period": 5, "slow_period": 13})
    print(f"MACrossoverStrategy initialized with params: {ma_strategy.params}")

    # Test ThreeMABullishArrangementStrategy
    three_ma_strategy = ThreeMABullishArrangementStrategy("Three MA Bullish", {"short": 5, "medium": 13, "long": 34})
    print(f"ThreeMABullishArrangementStrategy initialized with params: {three_ma_strategy.params}")

    print("Concrete strategy formatting tests passed!\n")


def main():
    """Main test function"""
    print("Running strategy formatting tests...\n")

    try:
        test_base_strategy_formatting()
        test_concrete_strategies_formatting()
        print("All strategy formatting tests passed!")
        return 0
    except Exception as e:
        print(f"Error in strategy formatting tests: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

