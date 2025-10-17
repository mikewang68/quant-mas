"""
Run Volume Breakout Strategy Only
Execute only the volume breakout strategy and ignore other strategies
"""

import sys
import os
import logging
from datetime import datetime

# Add project root to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.weekly_selector import WeeklyStockSelector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_volume_breakout_only():
    """
    Run only the volume breakout strategy
    """
    try:
        logger.info("Starting Volume Breakout Strategy Only Execution")

        # Initialize database manager and data fetcher
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Get the volume breakout strategy ID
        volume_breakout_strategy = db_manager.get_strategy_by_name("趋势-放量突破策略（强势股捕捉）")

        if not volume_breakout_strategy:
            logger.error("Volume breakout strategy not found in database")
            return False

        strategy_id = str(volume_breakout_strategy['_id'])
        logger.info(f"Found volume breakout strategy with ID: {strategy_id}")

        # Initialize weekly selector with only the volume breakout strategy
        weekly_selector = WeeklyStockSelector(
            db_manager=db_manager,
            data_fetcher=data_fetcher,
            strategy_ids=[strategy_id]  # Only load this specific strategy
        )

        logger.info(f"Weekly Selector initialized with {len(weekly_selector.strategies)} strategy(s)")

        # Execute stock selection
        strategy_results = weekly_selector.select_stocks()

        logger.info(f"Strategy execution completed. Results: {len(strategy_results)} strategy(s)")

        # Save results to database
        if strategy_results:
            save_success = weekly_selector.save_selected_stocks(strategy_results)
            if save_success:
                logger.info("Successfully saved volume breakout strategy results to database")

                # Print summary
                for strategy_name, result in strategy_results.items():
                    selected_stocks = result[0]
                    logger.info(f"Strategy '{strategy_name}' selected {len(selected_stocks)} stocks")
                    if selected_stocks:
                        logger.info(f"Selected stocks: {selected_stocks}")

                        # Print scores for each stock
                        scores = result[1]
                        for stock_code in selected_stocks:
                            score = scores.get(stock_code, 0.0)
                            logger.info(f"  {stock_code}: score = {score}")
            else:
                logger.error("Failed to save strategy results to database")
                return False
        else:
            logger.warning("No strategy results to save")

        return True

    except Exception as e:
        logger.error(f"Error running volume breakout strategy: {e}")
        return False

if __name__ == "__main__":
    success = run_volume_breakout_only()
    if success:
        logger.info("Volume breakout strategy execution completed successfully")
    else:
        logger.error("Volume breakout strategy execution failed")
        sys.exit(1)

