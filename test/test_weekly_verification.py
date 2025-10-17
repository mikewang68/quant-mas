#!/usr/bin/env python3
"""
Verification script for Weekly Selector functionality
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_weekly_date_format():
    """Test if weekly date format follows year-week logic"""

    # Create sample daily data
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
    daily_data = pd.DataFrame({
        'date': dates,
        'open': [100 + i for i in range(len(dates))],
        'high': [105 + i for i in range(len(dates))],
        'low': [95 + i for i in range(len(dates))],
        'close': [102 + i for i in range(len(dates))],
        'volume': [1000000 + i * 10000 for i in range(len(dates))],
        'amount': [50000000 + i * 500000 for i in range(len(dates))]
    })

    print("Original daily data:")
    print(f"Date range: {daily_data['date'].min()} to {daily_data['date'].max()}")
    print(f"Number of days: {len(daily_data)}")

    # Convert to weekly using the same logic as Weekly Selector
    daily_data = daily_data.set_index('date')
    weekly_data = daily_data.resample('W').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum',
        'amount': 'sum'
    })

    weekly_data = weekly_data.dropna()
    weekly_data = weekly_data.reset_index()

    print("\nConverted weekly data:")
    print(f"Date range: {weekly_data['date'].min()} to {weekly_data['date'].max()}")
    print(f"Number of weeks: {len(weekly_data)}")

    # Check if dates follow year-week format
    for i, row in weekly_data.iterrows():
        date = row['date']
        year_week = f"{date.year}-W{date.isocalendar()[1]:02d}"
        print(f"Week {i+1}: {date.strftime('%Y-%m-%d')} -> {year_week}")

    return weekly_data

if __name__ == "__main__":
    print("=== Weekly Selector Date Format Verification ===")
    weekly_data = test_weekly_date_format()
    print("\n✓ Weekly date format verification completed")

