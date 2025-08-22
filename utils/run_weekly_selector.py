#!/usr/bin/env python3
"""
Run the weekly stock selector to select stocks and save results to pool collection
"""

import sys
import os
import logging
import yaml
from datetime import datetime

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.weekly_selector import WeeklyStockSelector
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def get_strategy_params_from_db(db_manager):
    """Get strategy parameters directly from database"""
    try:
        # Try to get the first strategy from the database
        strategies = db_manager.get_strategies()
        if strategies and len(strategies) > 0:
            first_strategy = strategies[0]
            strategy_params = first_strategy.get('parameters', {})
            logger.info(f"Using strategy parameters from database: {strategy_params}")
            return strategy_params
        else:
            logger.info("No strategies found in database, using default parameters")
            return {}
    except Exception as strategy_error:
        logger.warning(f"Error loading strategy parameters from database: {strategy_error}")
        logger.info("Using default parameters")
        return {}


def main():
    """Main function to run the weekly stock selector"""
    try:
        # Initialize components
        logger.info("Initializing components...")
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Get strategy parameters directly from database
        strategy_params = get_strategy_params_from_db(db_manager)
        
        # Initialize selector
        logger.info("Initializing weekly stock selector...")
        selector = WeeklyStockSelector(db_manager, data_fetcher)
        
        # Select stocks
        logger.info("Selecting stocks...")
        selected_stocks, last_data_date, golden_cross_flags, selected_scores, technical_analysis_data = selector.select_stocks()
        logger.info(f"Selected {len(selected_stocks)} stocks: {selected_stocks}")

        # Save selection to pool collection
        if selected_stocks:
            logger.info("Saving selected stocks to pool collection...")
            success = selector.save_selected_stocks(selected_stocks, golden_cross_flags, date=datetime.now().strftime('%Y-%m-%d'), last_data_date=last_data_date, scores=selected_scores, technical_analysis_data=technical_analysis_data)
            if success:
                logger.info("Successfully saved selected stocks to pool collection")
            else:
                logger.error("Failed to save selected stocks to pool collection")
        else:
            logger.warning("No stocks selected")
            # Still save an empty selection to pool collection
            success = selector.save_selected_stocks(selected_stocks, golden_cross_flags, date=datetime.now().strftime('%Y-%m-%d'), last_data_date=last_data_date, scores=selected_scores, technical_analysis_data={})
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

