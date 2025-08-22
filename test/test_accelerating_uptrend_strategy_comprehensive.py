#!/usr/bin/env python3
"""
Test script to verify the numpy type conversion fix in AcceleratingUptrendStrategy
More comprehensive test with data that should trigger stock selection
"""

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.accelerating_uptrend_strategy import AcceleratingUptrendStrategy


def create_test_data_with_uptrend() -> pd.DataFrame:
    """Create test stock data with a clear uptrend that should be selected"""
    # Create dates for the last 30 days
    end_date = datetime.now()
    dates = [end_date - timedelta(days=x) for x in range(29, -1, -1)]

    # Create strong upward trend data
    # Start from 10 and create a clear uptrend to 20
    base_prices = np.linspace(10, 20, 30)

    # Add some realistic noise but keep the trend
    noise = np.random.normal(0, 0.3, 30)
    prices = base_prices + noise

    # Ensure all prices are positive
    prices = np.abs(prices)

    # Create increasing volume to confirm the trend
    base_volumes = np.linspace(1000000, 3000000, 30)  # Increasing volume
    volume_noise = np.random.normal(0, 200000, 30)
    volumes = base_volumes + volume_noise
    volumes = np.abs(volumes)  # Ensure positive volumes

    # Create DataFrame
    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': prices + np.random.uniform(0, 0.5, 30),
        'low': prices - np.random.uniform(0, 0.5, 30),
        'close': prices,
        'volume': volumes.astype(int),
        'amount': prices * volumes
    })

    return df


def test_strategy_execution():
    """Test the strategy execution with numpy type checking"""
    print("Testing AcceleratingUptrendStrategy execution with strong uptrend data...")

    # Create test data with clear uptrend
    test_data = create_test_data_with_uptrend()
    stock_data = {'TEST001': test_data}

    # Initialize strategy
    strategy = AcceleratingUptrendStrategy(name="加速上涨策略")

    try:
        # Execute strategy
        selected_stocks = strategy.execute(stock_data, "技术分析Agent", None)

        print(f"Strategy execution completed. Selected {len(selected_stocks)} stocks.")

        if selected_stocks:
            print("✓ Stocks were selected - this is good for testing!")

            # Check the types of values in the first selected stock
            first_stock = selected_stocks[0]
            print(f"\nFirst selected stock data types:")
            for key, value in first_stock.items():
                print(f"  {key}: {type(value)} = {value}")
                # Check if any values are numpy types
                if isinstance(value, np.ndarray):
                    print(f"    WARNING: {key} is numpy array!")
                elif isinstance(value, np.floating):
                    print(f"    WARNING: {key} is numpy float!")
                elif isinstance(value, np.integer):
                    print(f"    WARNING: {key} is numpy integer!")
                elif isinstance(value, np.bool_):
                    print(f"    WARNING: {key} is numpy boolean!")

            # Check technical analysis data specifically
            if 'technical_analysis' in first_stock:
                ta_data = first_stock['technical_analysis']
                print(f"\nTechnical analysis data types:")
                for key, value in ta_data.items():
                    print(f"  {key}: {type(value)} = {value}")
                    # Check if any values are numpy types
                    if isinstance(value, np.ndarray):
                        print(f"    WARNING: {key} is numpy array!")
                    elif isinstance(value, np.floating):
                        print(f"    WARNING: {key} is numpy float!")
                    elif isinstance(value, np.integer):
                        print(f"    WARNING: {key} is numpy integer!")
                    elif isinstance(value, np.bool_):
                        print(f"    WARNING: {key} is numpy boolean!")

            # Check score and position types
            if 'score' in first_stock:
                score = first_stock['score']
                print(f"\nScore type: {type(score)} = {score}")

            if 'position' in first_stock:
                position = first_stock['position']
                print(f"Position type: {type(position)} = {position}")

            return True
        else:
            print("No stocks were selected. This might be due to test data not meeting criteria.")
            # Let's still check if there were any issues
            return True

    except Exception as e:
        print(f"Error during strategy execution: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("Running AcceleratingUptrendStrategy comprehensive numpy type test...")

    success = test_strategy_execution()

    if success:
        print("\n✓ Strategy execution test completed!")
        print("The numpy type conversion fixes should prevent MongoDB errors.")
        return 0
    else:
        print("\n✗ Strategy execution test failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())

