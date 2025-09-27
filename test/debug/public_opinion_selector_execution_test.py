#!/usr/bin/env python3
"""
Test script to verify public opinion selector execution with enhanced logging
"""

import sys
import os
import logging

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.public_opinion_selector import PublicOpinionStockSelector
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient

# Configure logging to see detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main function to test public opinion selector execution with enhanced logging"""
    try:
        # Initialize components
        logger.info("Initializing components...")
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Initialize selector
        logger.info("Initializing public opinion stock selector...")
        selector = PublicOpinionStockSelector(db_manager, data_fetcher)

        # Check what strategies were loaded
        logger.info(f"Loaded strategies: {len(selector.strategy_names)}")
        for i, name in enumerate(selector.strategy_names):
            logger.info(f"  Strategy {i}: {name}")
            logger.info(f"    File: {selector.strategy_files[i] if i < len(selector.strategy_files) else 'N/A'}")
            logger.info(f"    Class: {selector.strategy_class_names[i] if i < len(selector.strategy_class_names) else 'N/A'}")

        # Check strategy instances
        logger.info(f"Strategy instances: {len(selector.strategy_instances)}")
        for i, instance in enumerate(selector.strategy_instances):
            logger.info(f"  Instance {i}: {type(instance).__name__}")

        # Run the selector to test execution
        logger.info("Running public opinion selector...")
        success = selector.run()

        if success:
            logger.info("Public opinion selector executed successfully")
        else:
            logger.error("Public opinion selector execution failed")

        # Close database connection
        db_manager.close_connection()
        logger.info("Public opinion selector execution test completed")

    except Exception as e:
        logger.error(f"Error testing public opinion selector execution: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()

