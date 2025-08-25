#!/usr/bin/env python3
"""
Test script for the Volume Breakout strategy.
"""

import sys
import os
import logging
import pandas as pd
import numpy as np

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.volume_breakout_strategy import VolumeBreakoutStrategy

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_sample_data():
    """Create sample stock data for testing."""
    # Create dates
    dates = pd.date_range('2023-01-01', periods=100, freq='D')

    # Create sample data with a breakout pattern
    np.random.seed(42)  # For reproducible results

    # Create base prices with an upward trend
    base_prices = 100 + np.cumsum(np.random.normal(0.1, 1, 100))

    # Create a breakout around day 80
    breakout_point = 80
    base_prices[breakout_point:] += 5  # Price breakout

    # Create volumes with a spike at breakout point
    base_volumes = np.random.uniform(1000000, 2000000, 100)
    base_volumes[breakout_point] *= 3  # Volume spike

    # Create the DataFrame
    sample_data = pd.DataFrame({
        'date': dates,
        'open': base_prices + np.random.uniform(-1, 1, 100),
        'high': base_prices + np.random.uniform(0, 2, 100),
        'low': base_prices + np.random.uniform(-2, 0, 100),
        'close': base_prices,
        'volume': base_volumes
    })

    return sample_data

def test_volume_breakout_strategy():
    """Test the Volume Breakout strategy."""
    logger.info("Testing Volume Breakout Strategy")

    try:
        # Create sample data
        sample_data = create_sample_data()
        logger.info(f"Created sample data with {len(sample_data)} rows")

        # Initialize strategy
        strategy = VolumeBreakoutStrategy()
        logger.info("Initialized Volume Breakout Strategy")

        # Test analyze method
        meets_criteria, reason, score, breakout_signal = strategy.analyze(sample_data)
        logger.info(f"Analysis result - Meets criteria: {meets_criteria}")
        logger.info(f"Reason: {reason}")
        logger.info(f"Score: {score}")
        logger.info(f"Breakout signal: {breakout_signal}")

        # Test get_technical_analysis_data method
        technical_data = strategy.get_technical_analysis_data(sample_data)
        logger.info(f"Technical analysis data: {technical_data}")

        # Test generate_signals method
        signals = strategy.generate_signals(sample_data)
        buy_signals = len(signals[signals['signal'] == 'BUY'])
        logger.info(f"Generated {buy_signals} BUY signals")
        logger.info(f"Last 5 signals:\n{signals.tail()}")

        # Test execute method (mock database manager)
        class MockDBManager:
            def __init__(self):
                pass

            class db_operations:
                @staticmethod
                def save_strategy_output_to_pool(**kwargs):
                    logger.info(f"Mock save to pool called with args: {list(kwargs.keys())}")
                    return True

        mock_db_manager = MockDBManager()
        stock_data_dict = {"000001": sample_data}
        selected_stocks = strategy.execute(stock_data_dict, "TestAgent", mock_db_manager)
        logger.info(f"Execute method returned {len(selected_stocks)} selected stocks")

        return True

    except Exception as e:
        logger.error(f"Error testing Volume Breakout Strategy: {e}")
        return False

def main():
    """Main function to run tests."""
    logger.info("Starting Volume Breakout Strategy test")

    success = test_volume_breakout_strategy()

    if success:
        logger.info("Volume Breakout Strategy test completed successfully")
        print("Volume Breakout Strategy test completed successfully")
    else:
        logger.error("Volume Breakout Strategy test failed")
        print("Volume Breakout Strategy test failed")

if __name__ == "__main__":
    main()

