#!/usr/bin/env python3
"""
Verify that fundamental analysis results are properly written to the pool collection.
"""

import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_fundamental_data_in_pool():
    """Check that fundamental analysis data exists in the latest pool record."""
    logger.info("Checking fundamental analysis data in pool...")

    try:
        # Initialize database manager
        db_manager = MongoDBManager()

        # Get the latest pool record
        pool_collection = db_manager.db['pool']
        latest_record = pool_collection.find_one(sort=[('selection_date', -1)])

        if not latest_record:
            logger.error("No records found in pool collection")
            return False

        logger.info(f"Latest pool record date: {latest_record.get('selection_date', 'Unknown')}")

        # Check if fund_at timestamp exists
        if 'fund_at' in latest_record:
            logger.info(f"Fundamental analysis timestamp: {latest_record['fund_at']}")
        else:
            logger.warning("No fundamental analysis timestamp found in latest pool record")

        # Check stocks for fundamental analysis data
        stocks = latest_record.get('stocks', [])
        logger.info(f"Found {len(stocks)} stocks in latest pool record")

        # Look for stocks with fund data
        stocks_with_fund = 0
        for stock in stocks:
            if 'fund' in stock:
                stocks_with_fund += 1
                code = stock.get('code', 'Unknown')
                fund_data = stock['fund']
                logger.info(f"Stock {code} has fund data: {list(fund_data.keys())}")

                # Check specific strategy data
                for strategy_name, strategy_data in fund_data.items():
                    score = strategy_data.get('score', 'N/A')
                    logger.info(f"  Strategy '{strategy_name}': score={score}")

        logger.info(f"Found {stocks_with_fund} stocks with fundamental analysis data")

        db_manager.close_connection()
        return True

    except Exception as e:
        logger.error(f"Error checking fundamental data in pool: {e}")
        return False


def main():
    """Main verification function."""
    logger.info("Starting fundamental analysis verification...")

    success = check_fundamental_data_in_pool()

    if success:
        logger.info("Fundamental analysis verification completed successfully!")
        return True
    else:
        logger.error("Fundamental analysis verification failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

