#!/usr/bin/env python3
"""
Debug script to trace the weekly selector process and see why it selects 0 stocks
"""

import sys
import os
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.weekly_selector import WeeklyStockSelector
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient

def debug_weekly_selector():
    """Debug the weekly selector process"""
    print("Debugging Weekly Selector Process...")

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

    # Mock the get_stock_codes method with just a few test codes
    test_codes = ['000001', '000002', '000003']
    mock_db_manager.get_stock_codes.return_value = test_codes

    # Create realistic test data that should meet criteria
    def create_test_k_data():
        """Create test K-line data that should meet strategy criteria"""
        # Create enough data points to ensure we have sufficient weekly data
        # For 34 weeks, we need about 34 * 7 = 238 days of data
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

    # Mock the get_adjusted_k_data method
    def mock_get_adjusted_k_data(code, start_date, end_date, frequency):
        print(f"  Getting data for {code} from {start_date} to {end_date}")
        # Return the same test data for all codes
        return create_test_k_data()

    mock_db_manager.get_adjusted_k_data = mock_get_adjusted_k_data

    # Create mock data fetcher
    mock_data_fetcher = Mock(spec=AkshareClient)

    # Test the weekly selector
    with patch('agents.weekly_selector.importlib.import_module') as mock_import:
        # Mock the strategy module import
        import strategies.three_ma_bullish_arrangement_strategy as mock_strategy_module
        mock_import.return_value = mock_strategy_module

        print("Creating WeeklyStockSelector...")
        selector = WeeklyStockSelector(mock_db_manager, mock_data_fetcher)

        print(f"Strategy loaded: {selector.strategy_name}")
        print(f"Strategy params: {selector.strategy_params}")

        # Test select_stocks method with detailed tracing
        print("\nCalling select_stocks...")
        selected_stocks, last_data_date, golden_cross_flags, selected_scores, technical_analysis_data = selector.select_stocks()

        print(f"\nResults:")
        print(f"  Selected stocks: {selected_stocks}")
        print(f"  Last data date: {last_data_date}")
        print(f"  Golden cross flags: {golden_cross_flags}")
        print(f"  Number of selected stocks: {len(selected_stocks)}")
        print(f"  Technical analysis data: {len(technical_analysis_data)}")

        # Let's also manually test the strategy on one stock to see what happens
        print(f"\n--- Manual strategy test ---")
        test_data = create_test_k_data()

        # Convert to weekly data like the selector does
        weekly_data = selector._convert_daily_to_weekly(test_data)
        print(f"  Daily data shape: {test_data.shape}")
        print(f"  Weekly data shape: {weekly_data.shape}")

        if not weekly_data.empty:
            print(f"  Weekly data last few closes: {weekly_data['close'].tail().tolist()}")

            # Test strategy on weekly data
            meets_criteria = selector._execute_strategy('000001', weekly_data)
            print(f"  Strategy result on weekly data: {meets_criteria}")

            # Let's also manually call the strategy analyze method
            from strategies.three_ma_bullish_arrangement_strategy import ThreeMABullishArrangementStrategy
            strategy = ThreeMABullishArrangementStrategy(params=selector.strategy_params)
            meets_criteria, reason, score, golden_cross = strategy.analyze(weekly_data)
            print(f"  Manual analyze result:")
            print(f"    Meets criteria: {meets_criteria}")
            print(f"    Reason: {reason}")
            print(f"    Score: {score}")

if __name__ == "__main__":
    try:
        debug_weekly_selector()
    except Exception as e:
        print(f"Debug failed with error: {e}")
        import traceback
        traceback.print_exc()

