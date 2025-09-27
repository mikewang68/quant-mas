#!/usr/bin/env python3
"""
Test script to run the technical selector with the accelerating strategy
"""

import sys
import os
import logging

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.technical_selector import TechnicalStockSelector

def test_technical_selector_with_accelerating_strategy():
    """Test the technical selector with the accelerating strategy"""
    print("Testing technical selector with accelerating strategy...")

    try:
        # Initialize components
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()
        selector = TechnicalStockSelector(db_manager, data_fetcher)

        # Run the technical selector
        success = selector.update_pool_with_technical_analysis()

        if success:
            print("Technical selector executed successfully with accelerating strategy")
            return True
        else:
            print("Technical selector failed to execute")
            return False

    except Exception as e:
        print(f"Error running technical selector: {e}")
        return False

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Run the test
    success = test_technical_selector_with_accelerating_strategy()
    if success:
        print("Test completed successfully")
        sys.exit(0)
    else:
        print("Test failed")
        sys.exit(1)

