#!/usr/bin/env python3
"""
Test script to verify the weekly selector fix
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

def test_weekly_selector():
    """Test the weekly selector"""
    print("Testing Weekly Selector...")

    # Create mock database manager
    mock_db_manager = Mock(spec=MongoDBManager)

    # Mock the db attribute
    mock_db_manager.db = Mock()
    mock_pool_collection = Mock()
    mock_db_manager.db.__getitem__ = Mock(return_value=mock_pool_collection)
    mock_pool_collection.replace_one.return_value = Mock(upserted_id=None)

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

    # Mock the get_stock_codes method
    mock_db_manager.get_stock_codes.return_value = ['000001', '000002']

    # Mock the get_adjusted_k_data method
    def mock_get_adjusted_k_data(code, start_date, end_date, frequency):
        # Create test data
        dates = pd.date_range(start_date, end_date, freq='D')
        close_prices = np.linspace(100, 120, len(dates)) + np.random.normal(0, 1, len(dates))

        data = pd.DataFrame({
            'date': dates,
            'open': close_prices * 0.99,
            'high': close_prices * 1.02,
            'low': close_prices * 0.98,
            'close': close_prices,
            'volume': np.random.randint(1000000, 2000000, len(dates)),
            'amount': close_prices * np.random.randint(1000000, 2000000, len(dates))
        })
        return data

    mock_db_manager.get_adjusted_k_data = mock_get_adjusted_k_data

    # Create mock data fetcher
    mock_data_fetcher = Mock(spec=AkshareClient)

    # Test the weekly selector
    with patch('agents.weekly_selector.importlib.import_module') as mock_import:
        # Mock the strategy module import
        import strategies.three_ma_bullish_arrangement_strategy as mock_strategy_module
        mock_import.return_value = mock_strategy_module

        selector = WeeklyStockSelector(mock_db_manager, mock_data_fetcher)

        # Test select_stocks method
        selected_stocks, last_data_date, golden_cross_flags, selected_scores, technical_analysis_data = selector.select_stocks()

        print(f"Selected stocks: {selected_stocks}")
        print(f"Last data date: {last_data_date}")
        print(f"Golden cross flags: {golden_cross_flags}")
        print(f"Selected scores: {selected_scores}")
        print(f"Technical analysis data: {technical_analysis_data}")

        # Test save_selected_stocks method
        save_result = selector.save_selected_stocks(
            stocks=selected_stocks,
            golden_cross_flags=golden_cross_flags,
            date='2023-01-01'
        )

        print(f"Save result: {save_result}")

        return selected_stocks, save_result

if __name__ == "__main__":
    try:
        selected_stocks, save_result = test_weekly_selector()
        print("\nTest completed successfully!")
        print(f"Number of selected stocks: {len(selected_stocks)}")
        print(f"Save successful: {save_result}")
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

