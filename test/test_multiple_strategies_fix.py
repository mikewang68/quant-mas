"""
Test script to verify that multiple strategies' data is properly saved to database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.weekly_selector import WeeklyStockSelector
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_multiple_strategies_save():
    """Test that multiple strategies' data is properly saved to database"""

    try:
        # Initialize components
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Create weekly selector instance
        weekly_selector = WeeklyStockSelector(db_manager, data_fetcher)

        # Check how many strategies are loaded
        logger.info(f"Loaded {len(weekly_selector.strategies)} strategies")

        # Execute stock selection
        logger.info("Executing stock selection with multiple strategies...")
        strategy_results = weekly_selector.select_stocks()

        # Check strategy results
        logger.info(f"Strategy results keys: {list(strategy_results.keys())}")

        # Save selected stocks to database
        logger.info("Saving selected stocks to database...")
        save_result = weekly_selector.save_selected_stocks(strategy_results)

        if save_result:
            logger.info("✓ Successfully saved multiple strategies' data to database")

            # Verify the data in database
            logger.info("Verifying database data...")

            # Get the latest pool record
            pool_collection = db_manager.get_collection('pool')
            latest_pool_record = pool_collection.find_one(sort=[('_id', -1)])

            if latest_pool_record:
                logger.info(f"✓ Found latest pool record with ID: {latest_pool_record.get('_id')}")

                # Check if all strategies' data is present
                stocks = latest_pool_record.get('stocks', [])
                logger.info(f"✓ Found {len(stocks)} stocks in pool record")

                # Check the structure of the first stock to see if multiple strategies are present
                if stocks:
                    first_stock = stocks[0]
                    logger.info(f"First stock code: {first_stock.get('code')}")

                    # Check trend field
                    trend_data = first_stock.get('trend', {})
                    logger.info(f"Trend field keys: {list(trend_data.keys())}")

                    # Check if multiple strategies are present
                    if len(trend_data) > 1:
                        logger.info("✓ SUCCESS: Multiple strategies' data found in database!")
                        for strategy_name, strategy_data in trend_data.items():
                            logger.info(f"  - {strategy_name}: score={strategy_data.get('score')}")
                    else:
                        logger.warning("⚠ Only one strategy found in database - this might indicate the issue persists")

                else:
                    logger.warning("⚠ No stocks found in pool record")

            else:
                logger.error("✗ No pool record found in database")

        else:
            logger.error("✗ Failed to save selected stocks to database")

    except Exception as e:
        logger.error(f"✗ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_multiple_strategies_save()

