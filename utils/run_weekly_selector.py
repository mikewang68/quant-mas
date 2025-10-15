#!/usr/bin/env python3
"""
Run the weekly stock selector to select stocks and save results to pool collection
"""

import sys
import os
import logging
from numpy import log
import yaml
from datetime import datetime

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.weekly_selector import WeeklyStockSelector
from data.mongodb_manager import MongoDBManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def get_strategy_params_from_db(db_manager):
    """Get strategy parameters directly from database"""
    try:
        # Try to get the first strategy from the database
        strategies = db_manager.get_strategies()
        if strategies and len(strategies) > 0:
            first_strategy = strategies[0]
            strategy_params = first_strategy.get("parameters", {})
            logger.info(f"Using strategy parameters from database: {strategy_params}")
            return strategy_params
        else:
            logger.info("No strategies found in database, using default parameters")
            return {}
    except Exception as strategy_error:
        logger.warning(
            f"Error loading strategy parameters from database: {strategy_error}"
        )
        logger.info("Using default parameters")
        return {}


def main():
    """Main function to run the weekly stock selector"""
    try:
        # Initialize components
        logger.info("Initializing components...")
        db_manager = MongoDBManager()

        # Get strategy parameters directly from database
        strategy_params = get_strategy_params_from_db(db_manager)

        # Initialize selector
        logger.info("Initializing weekly stock selector...")
        selector = WeeklyStockSelector(db_manager)

        # Select stocks
        logger.info("Selecting stocks...")
        logger.info("wdg..................")
        strategy_results = selector.select_stocks()
        logger.info("wdg..................")
        logger.info(strategy_results)

        # Log results for each strategy
        total_selected = 0
        for strategy_name, strategy_result in strategy_results.items():
            # Handle different tuple lengths gracefully
            if len(strategy_result) >= 3:
                selected_stocks = strategy_result[0]
                selected_scores = strategy_result[1]
                json_values = strategy_result[2]
            else:
                logger.error(
                    f"Unexpected strategy result format for {strategy_name}: {len(strategy_result)} elements"
                )
                continue

            # Alternative unpacking approach (commented out but kept for reference)
            # selected_stocks, selected_scores, json_values = strategy_result
            logger.info(
                f"Strategy {strategy_name} selected {len(selected_stocks)} stocks"
            )
            total_selected += len(selected_stocks)
            if selected_stocks:
                logger.info(f"Selected stocks by {strategy_name}: {selected_stocks}")

        logger.info(f"Total selected {total_selected} stocks across all strategies")

        # Save selection to pool collection
        if total_selected > 0:
            logger.info("Saving selected stocks to pool collection...")
            success = selector.save_selected_stocks(
                strategy_results, date=datetime.now().strftime("%Y-%m-%d")
            )
            logger.info("right1")
            if success:
                logger.info("Successfully saved selected stocks to pool collection")
            else:
                logger.error("Failed to save selected stocks to pool collection")
        else:
            logger.warning("No stocks selected by any strategy")
            # Still save an empty selection to pool collection
            success = selector.save_selected_stocks(
                strategy_results, date=datetime.now().strftime("%Y-%m-%d")
            )
            if success:
                logger.info("Successfully saved empty selection to pool collection")
            else:
                logger.error("Failed to save empty selection to pool collection")

        # Close database connection
        db_manager.close_connection()
        logger.info("Weekly stock selection completed")

    except Exception as e:
        logger.error(f"Error running weekly stock selector: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
