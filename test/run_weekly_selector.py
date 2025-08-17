#!/usr/bin/env python3
"""
Run the weekly stock selector to select stocks and save results to pool collection
"""

import sys
import os
import logging
import yaml
import yaml

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


def load_strategy_params():
    """Load strategy parameters from configuration file"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'strategy_params.yaml')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                strategy_params = yaml.safe_load(f)
            logger.info(f"Loaded strategy parameters from config file: {strategy_params}")
            return strategy_params
        else:
            logger.warning(f"Strategy config file not found at {config_path}")
            return {}
    except Exception as e:
        logger.error(f"Error loading strategy parameters from config file: {e}")
        return {}


def main():
    """Main function to run the weekly stock selector"""
    try:
        # Initialize components
        logger.info("Initializing components...")
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()
        
        # Try to get strategy parameters from configuration file first
        strategy_params = load_strategy_params()
        
        # If no parameters from config file, try to get from database
        if not strategy_params:
            try:
                # Try to get the first strategy from the database
                strategies = db_manager.get_strategies()
                if strategies and len(strategies) > 0:
                    first_strategy = strategies[0]
                    strategy_params = first_strategy.get('parameters', {})
                    logger.info(f"Using strategy parameters from database: {strategy_params}")
                else:
                    logger.info("No strategies found in database, using default parameters")
            except Exception as strategy_error:
                logger.warning(f"Error loading strategy parameters from database: {strategy_error}")
                logger.info("Using default parameters")
        else:
            logger.info("Using strategy parameters from config file")
        
        # Initialize selector with strategy parameters
        logger.info("Initializing weekly stock selector...")
        selector = WeeklyStockSelector(db_manager, data_fetcher, strategy_params)
        
        # Select stocks
        logger.info("Selecting stocks...")
        selected_stocks = selector.select_stocks()
        logger.info(f"Selected {len(selected_stocks)} stocks: {selected_stocks}")
        
        # Save selection to pool collection
        if selected_stocks:
            logger.info("Saving selected stocks to pool collection...")
            success = selector.save_selected_stocks(selected_stocks)
            if success:
                logger.info("Successfully saved selected stocks to pool collection")
            else:
                logger.error("Failed to save selected stocks to pool collection")
        else:
            logger.warning("No stocks selected")
            # Still save an empty selection to pool collection
            success = selector.save_selected_stocks(selected_stocks)
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

