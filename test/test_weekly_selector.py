#!/usr/bin/env python3
"""
Test program for weekly selector
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock classes to simulate the real dependencies
class MockMongoDBManager:
    def get_strategies(self):
        return [{
            'name': '三均线多头排列策略（基本型）',
            'parameters': {
                'short': 5,
                'mid': 13,
                'long': 34
            },
            'program': {
                'file': 'three_ma_bullish_arrangement_strategy',
                'class': 'ThreeMABullishArrangementStrategy'
            }
        }]

    def get_stock_codes(self):
        # Return a small list of stock codes for testing
        return ['000001', '000002', '600000', '600036']

    def get_adjusted_k_data(self, code, start_date, end_date, frequency='daily'):
        # Return empty DataFrame to force data fetching
        return pd.DataFrame()

class MockAkshareClient:
    def get_stock_list(self):
        return ['000001', '000002', '600000', '600036']

    def get_daily_k_data(self, code, start_date, end_date):
        # Generate mock K-line data
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        # Remove weekends
        dates = dates[dates.weekday < 5]

        # Generate mock price data with some trend
        n = len(dates)
        open_prices = 100 + np.cumsum(np.random.randn(n) * 0.5)
        close_prices = open_prices + np.random.randn(n) * 0.5
        high_prices = np.maximum(open_prices, close_prices) + np.abs(np.random.randn(n) * 0.3)
        low_prices = np.minimum(open_prices, close_prices) - np.abs(np.random.randn(n) * 0.3)
        volumes = np.random.randint(1000000, 10000000, n)
        amounts = close_prices * volumes

        df = pd.DataFrame({
            'date': dates,
            'open': open_prices,
            'high': high_prices,
            'low': low_prices,
            'close': close_prices,
            'volume': volumes,
            'amount': amounts
        })

        return df

# Import the WeeklyStockSelector class
from agents.weekly_selector import WeeklyStockSelector

def test_weekly_selector():
    """Test the weekly selector functionality"""
    print("Testing WeeklyStockSelector...")

    # Create mock dependencies
    db_manager = MockMongoDBManager()
    data_fetcher = MockAkshareClient()

    # Create the selector
    selector = WeeklyStockSelector(db_manager, data_fetcher)

    # Test stock selection
    today = datetime.now().strftime('%Y-%m-%d')
    selected_stocks, last_data_date, golden_cross_flags, scores, technical_analysis_data = selector.select_stocks(today)

    print(f"Selected stocks: {selected_stocks}")
    print(f"Last data date: {last_data_date}")
    print(f"Golden cross flags: {golden_cross_flags}")
    print(f"Scores: {scores}")
    print(f"Technical analysis data: {technical_analysis_data}")

    # Test saving selected stocks
    result = selector.save_selected_stocks(
        stocks=selected_stocks,
        golden_cross_flags=golden_cross_flags,
        date=today,
        last_data_date=last_data_date,
        scores=scores
    )

    print(f"Save result: {result}")
    print("Test completed successfully!")

if __name__ == "__main__":
    test_weekly_selector()

