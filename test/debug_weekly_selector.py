#!/usr/bin/env python3
"""
Debug script to test weekly selector and identify the unpacking error
"""

import sys
import os
import logging

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.weekly_selector import WeeklyStockSelector
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """Debug main function"""
    try:
        # Initialize components
        logger.info("Initializing components...")
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Initialize selector
        logger.info("Initializing weekly stock selector...")
        selector = WeeklyStockSelector(db_manager, data_fetcher)

        # Select stocks
        logger.info("Selecting stocks...")
        strategy_results = selector.select_stocks()

        logger.info("Strategy results structure:")
        logger.info(f"Type of strategy_results: {type(strategy_results)}")
        logger.info(f"Keys in strategy_results: {list(strategy_results.keys())}")

        # Check each strategy result
        for strategy_name, strategy_result in strategy_results.items():
            logger.info(f"Strategy: {strategy_name}")
            logger.info(f"  Type: {type(strategy_result)}")
            logger.info(f"  Length: {len(strategy_result)}")
            logger.info(f"  Content: {strategy_result}")

            # Try to unpack
            try:
                if len(strategy_result) >= 3:
                    selected_stocks = strategy_result[0]
                    selected_scores = strategy_result[1]
                    json_values = strategy_result[2]
                    logger.info(f"  Successfully unpacked 3 values")
                else:
                    logger.error(f"  Not enough values to unpack")
            except Exception as unpack_error:
                logger.error(f"  Error unpacking: {unpack_error}")

        logger.info("wdg..................")
        logger.info(strategy_results)

        # Save selection to pool collection
        logger.info("Saving selected stocks to pool collection...")
        success = selector.save_selected_stocks(strategy_results, date="2025-10-17")

        if success:
            logger.info("Successfully saved selected stocks to pool collection")
        else:
            logger.error("Failed to save selected stocks to pool collection")

        # Close database connection
        db_manager.close_connection()
        logger.info("Weekly stock selection completed")

    except Exception as e:
        logger.error(f"Error running weekly stock selector: {e}", exc_info=True)
        import traceback

        logger.error(f"Full traceback: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
