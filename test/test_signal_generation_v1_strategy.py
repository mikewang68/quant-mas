#!/usr/bin/env python3
"""
Test script for the Signal Generation V1 Strategy
"""

import sys
import os
import logging

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data.mongodb_manager import MongoDBManager
from strategies.signal_generation_v1_strategy import SignalGenerationV1Strategy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_signal_generation_v1_strategy():
    """Test the Signal Generation V1 Strategy"""
    db_manager = None
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()

        # Initialize strategy
        strategy = SignalGenerationV1Strategy()

        # Execute strategy (with empty stock_data as it's not used)
        logger.info("Executing Signal Generation V1 Strategy...")
        results = strategy.execute({}, "信号生成Agent", db_manager)

        logger.info(f"Strategy execution completed. Results: {len(results)} stocks analyzed")

        # Print some results
        for i, result in enumerate(results[:5]):  # Show first 5 results
            logger.info(f"Stock {i+1}: {result}")

        return True

    except Exception as e:
        logger.error(f"Error testing strategy: {e}")
        return False
    finally:
        # Close connection
        if db_manager:
            db_manager.close_connection()


if __name__ == "__main__":
    test_signal_generation_v1_strategy()

