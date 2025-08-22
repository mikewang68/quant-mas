#!/usr/bin/env python3
"""
Test for the weekly selector stock selection functionality
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

def test_stock_selection():
    """Test the stock selection functionality"""
    print("=== Testing Stock Selection ===")

    try:
        # Initialize components
        logger.info("Initializing components...")
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Initialize selector
        logger.info("Initializing weekly stock selector...")
        selector = WeeklyStockSelector(db_manager, data_fetcher)

        # Test select_stocks method
        logger.info("Testing select_stocks method...")
        selected_stocks, last_data_date, golden_cross_flags, selected_scores, technical_analysis_data = selector.select_stocks()
        print(f"Selected stocks count: {len(selected_stocks)}")
        print(f"Last data date: {last_data_date}")
        print(f"Golden cross flags count: {len(golden_cross_flags)}")
        print(f"Selected scores count: {len(selected_scores)}")
        print(f"Technical analysis data count: {len(technical_analysis_data)}")

        # Close database connection
        db_manager.close_connection()
        logger.info("Test completed successfully")

    except Exception as e:
        logger.error(f"Error in test: {e}")
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    test_stock_selection()

