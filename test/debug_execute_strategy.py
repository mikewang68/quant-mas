#!/usr/bin/env python3
"""
Debug script to trace the _execute_strategy method in detail
"""

import sys
import os
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.weekly_selector import WeeklyStockSelector
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient

def debug_execute_strategy():
    """Debug the _execute_strategy method in detail"""
    print("Debugging _execute_strategy method...")

    # Create mock database manager
    mock_db_manager = Mock(spec=MongoDBManager)

    # Mock the get_strategies method to return a valid strategy
    mock_db_manager.get_strategies.return_value = [{
        'name': '三均线多头排列策略',
        'parameters': {
            'short': 5,
            'mid': 13,
            'long': 34
        },
        'file': 'strategies.three_ma_bullish_arrangement_strategy',
        'class_name': 'ThreeMABullishArrangementStrategy'
    }]

    # Create realistic test data
    def create_test_k_data():
        """Create test K-line data that should meet strategy criteria"""
        dates = pd.date_range('2024-01-01', periods=250, freq='D')
        close_prices = np.linspace(100, 150, 250)  # Strong upward trend

        data = pd.DataFrame({
            'date': dates,
            'open': close_prices * 0.99,
            'high': close_prices * 1.01,
            'low': close_prices * 0.99,
            'close': close_prices,
            'volume': np.full(250, 1500000),
            'amount': close_prices * 1500000
        })
        return data

    # Test the weekly selector
    with patch('agents.weekly_selector.importlib.import_module') as mock_import:
        # Mock the strategy module import
        import strategies.three_ma_bullish_arrangement_strategy as mock_strategy_module
        mock_import.return_value = mock_strategy_module

        print("Creating WeeklyStockSelector...")
        selector = WeeklyStockSelector(mock_db_manager, Mock(spec=AkshareClient))

        print(f"Strategy loaded: {selector.strategy_name}")
        print(f"Strategy params: {selector.strategy_params}")

        # Create test data
        test_data = create_test_k_data()
        weekly_data = selector._convert_daily_to_weekly(test_data)

        print(f"Weekly data shape: {weekly_data.shape}")
        print(f"Weekly data last few closes: {weekly_data['close'].tail().tolist()}")

        # Manually test the strategy's generate_signals method
        print(f"\n--- Testing strategy generate_signals ---")
        signals = selector.strategy_instance.generate_signals(weekly_data)
        print(f"Generated signals shape: {signals.shape}")
        print(f"Last few signals: {signals.tail()}")

        if len(signals) > 0:
            last_signal = signals.iloc[-1]['signal']
            print(f"Last signal: {last_signal}")
            print(f"Is BUY signal: {last_signal == 'BUY'}")

        # Now test the _execute_strategy method with detailed tracing
        print(f"\n--- Testing _execute_strategy method ---")
        result = selector._execute_strategy('000001', weekly_data)
        print(f"_execute_strategy result: {result}")

        # Let's also manually call the strategy analyze method to see full details
        print(f"\n--- Manual strategy analyze ---")
        from strategies.three_ma_bullish_arrangement_strategy import ThreeMABullishArrangementStrategy
        strategy = ThreeMABullishArrangementStrategy(params=selector.strategy_params)
        meets_criteria, reason, score, golden_cross = strategy.analyze(weekly_data)
        print(f"Analyze result:")
        print(f"  Meets criteria: {meets_criteria}")
        print(f"  Reason: {reason}")
        print(f"  Score: {score}")
        print(f"  Golden cross: {golden_cross}")

if __name__ == "__main__":
    try:
        debug_execute_strategy()
    except Exception as e:
        print(f"Debug failed with error: {e}")
        import traceback
        traceback.print_exc()

