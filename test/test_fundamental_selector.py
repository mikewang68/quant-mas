#!/usr/bin/env python3
"""
Test script to verify that the fundamental selector works correctly.
"""

import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.fundamental_selector import FundamentalStockSelector
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_fundamental_selector_initialization():
    """Test that the fundamental selector initializes correctly."""
    logger.info("Testing fundamental selector initialization...")

    try:
        # Initialize components
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Initialize selector
        selector = FundamentalStockSelector(db_manager, data_fetcher)

        # Check that strategies were loaded
        logger.info(f"Loaded {len(selector.strategy_names)} strategies")
        for i, name in enumerate(selector.strategy_names):
            logger.info(f"  Strategy {i}: {name}")

        # Check that strategy instances were created
        logger.info(f"Created {len(selector.strategy_instances)} strategy instances")
        for i, instance in enumerate(selector.strategy_instances):
            logger.info(f"  Instance {i}: {instance.__class__.__name__}")

        db_manager.close_connection()
        return True

    except Exception as e:
        logger.error(f"Error testing fundamental selector initialization: {e}")
        return False


def test_fundamental_selector_execution():
    """Test that the fundamental selector can execute strategies."""
    logger.info("Testing fundamental selector execution...")

    try:
        # Initialize components
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Initialize selector
        selector = FundamentalStockSelector(db_manager, data_fetcher)

        # Check if any strategies were loaded
        if not selector.strategy_instances:
            logger.warning("No strategies loaded - skipping execution test")
            db_manager.close_connection()
            return True

        # Test the run method (this will execute strategies but not save to database in test mode)
        result = selector.run()
        logger.info(f"Selector run result: {result}")

        db_manager.close_connection()
        return True

    except Exception as e:
        logger.error(f"Error testing fundamental selector execution: {e}")
        return False


def main():
    """Main test function."""
    logger.info("Starting fundamental selector tests...")

    # Test initialization
    init_success = test_fundamental_selector_initialization()

    # Test execution
    exec_success = test_fundamental_selector_execution()

    if init_success and exec_success:
        logger.info("All tests passed!")
        return True
    else:
        logger.error("Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

