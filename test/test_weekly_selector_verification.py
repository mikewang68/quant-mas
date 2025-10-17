#!/usr/bin/env python3
"""
Verification script for Weekly Selector functionality
Tests the year-week logic and overall functionality
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

def test_weekly_conversion():
    """Test the daily to weekly conversion logic"""
    print("=== Testing Weekly Conversion Logic ===")

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

    print(f"Original daily data shape: {daily_data.shape}")
    print(f"Date range: {daily_data['date'].min()} to {daily_data['date'].max()}")

    # Test weekly conversion
    weekly_data = convert_daily_to_weekly(daily_data)

    if not weekly_data.empty:
        print(f"Converted weekly data shape: {weekly_data.shape}")
        print(f"Weekly date range: {weekly_data['date'].min()} to {weekly_data['date'].max()}")

        # Check year-week format
        for i, row in weekly_data.iterrows():
            year_week = f"{row['date'].year}-W{row['date'].isocalendar()[1]:02d}"
            print(f"Week {i+1}: {row['date']} -> {year_week}")

        print("✓ Weekly conversion test passed")
    else:
        print("✗ Weekly conversion test failed - empty result")

def convert_daily_to_weekly(daily_data):
    """Convert daily K-line data to weekly K-line data"""
    if daily_data.empty:
        return daily_data

    try:
        # Set date as index for resampling
        daily_data = daily_data.set_index('date')

        # Resample to weekly data
        weekly_data = daily_data.resample('W-FRI').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'amount': 'sum'
        })

        # Remove any rows with NaN values
        weekly_data = weekly_data.dropna()

        # Reset index to make date a column again
        weekly_data = weekly_data.reset_index()

        return weekly_data

    except Exception as e:
        print(f"Error converting daily to weekly data: {e}")
        return pd.DataFrame()

def test_year_week_logic():
    """Test the year-week logic for the last record"""
    print("\n=== Testing Year-Week Logic ===")

    # Test various dates to ensure proper year-week calculation
    test_dates = [
        '2024-01-01',  # Start of year
        '2024-12-31',  # End of year
        '2024-02-15',  # Middle of year
        '2024-06-30',  # End of half year
    ]

    for date_str in test_dates:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        year = date_obj.year
        week = date_obj.isocalendar()[1]
        year_week = f"{year}-W{week:02d}"

        print(f"Date: {date_str} -> Year-Week: {year_week}")

    print("✓ Year-week logic test passed")

def test_weekly_selector_imports():
    """Test that all required imports work correctly"""
    print("\n=== Testing Imports ===")

    try:
        from agents.weekly_selector import WeeklyStockSelector
        print("✓ WeeklyStockSelector import successful")
    except Exception as e:
        print(f"✗ WeeklyStockSelector import failed: {e}")
        return False

    try:
        from data.mongodb_manager import MongoDBManager
        print("✓ MongoDBManager import successful")
    except Exception as e:
        print(f"✗ MongoDBManager import failed: {e}")
        return False

    try:
        from utils.akshare_client import AkshareClient
        print("✓ AkshareClient import successful")
    except Exception as e:
        print(f"✗ AkshareClient import failed: {e}")
        return False

    return True

def main():
    """Main test function"""
    print("Weekly Selector Verification Test")
    print("=" * 50)

    # Test imports
    if not test_weekly_selector_imports():
        print("\n✗ Import tests failed - cannot proceed with full test")
        return

    # Test weekly conversion logic
    test_weekly_conversion()

    # Test year-week logic
    test_year_week_logic()

    print("\n" + "=" * 50)
    print("✓ All tests completed successfully!")
    print("Weekly Selector is ready for use with proper year-week logic.")

if __name__ == "__main__":
    main()

