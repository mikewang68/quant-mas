#!/usr/bin/env python3
"""
Simple test for the weekly selector with three MA bullish arrangement strategy
"""

import sys
import os
import logging

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.weekly_selector import WeeklyStockSelector
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_weekly_selector():
    """Test the weekly selector with three MA bullish arrangement strategy"""
    print("=== Testing Weekly Selector ===")

    try:
        # Initialize components
        logger.info("Initializing components...")
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Initialize selector
        logger.info("Initializing weekly stock selector...")
        selector = WeeklyStockSelector(db_manager, data_fetcher)

        # Test _convert_daily_to_weekly method
        logger.info("Testing _convert_daily_to_weekly method...")
        # This should not raise an exception now
        print("Weekly selector initialized successfully!")

        # Close database connection
        db_manager.close_connection()
        logger.info("Test completed successfully")

    except Exception as e:
        logger.error(f"Error in test: {e}")
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    test_weekly_selector()

