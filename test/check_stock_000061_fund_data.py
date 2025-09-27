#!/usr/bin/env python3
"""
Test program to check fund data for stock 000061
This will help us understand the data structure and identify any issues with score/value fields.
"""

import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_stock_fund_data(stock_code="000061"):
    """Check fund data for a specific stock code"""
    try:
        # Initialize database manager
        db_manager = MongoDBManager()

        # Get pool collection
        pool_collection = db_manager.db["pool"]

        # Find the latest pool record
        latest_pool_record = pool_collection.find_one(sort=[("selection_date", -1)])

        if not latest_pool_record:
            logger.error("No records found in pool collection")
            return False

        logger.info(f"Latest pool record date: {latest_pool_record.get('selection_date', 'Unknown')}")

        # Extract stocks from the latest record
        stocks = latest_pool_record.get("stocks", [])

        # Find the specific stock
        target_stock = None
        for stock in stocks:
            if stock.get("code") == stock_code:
                target_stock = stock
                break

        if not target_stock:
            logger.error(f"Stock {stock_code} not found in latest pool record")
            return False

        logger.info(f"Found stock {stock_code}")
        logger.info(f"Basic stock info: code={target_stock.get('code')}, score={target_stock.get('score')}")

        # Check if fund data exists
        if "fund" not in target_stock:
            logger.warning("No fund data found for this stock")
            return True

        fund_data = target_stock["fund"]
        logger.info(f"Fund data found with {len(fund_data)} strategies")

        # Display fund data for each strategy
        for strategy_name, strategy_data in fund_data.items():
            logger.info(f"Strategy: {strategy_name}")
            logger.info(f"  Score: {strategy_data.get('score', 'N/A')}")
            logger.info(f"  Value: {strategy_data.get('value', 'N/A')}")

            # Check if value contains score information (which would indicate the issue)
            value_field = strategy_data.get('value', '')
            score_field = strategy_data.get('score', '')

            if str(score_field) in str(value_field):
                logger.warning(f"  *** ISSUE DETECTED: Score {score_field} found in value field ***")

        return True

    except Exception as e:
        logger.error(f"Error checking stock fund data: {e}")
        return False

def check_multiple_pool_records(stock_code="000061", limit=5):
    """Check fund data for a specific stock across multiple pool records"""
    try:
        # Initialize database manager
        db_manager = MongoDBManager()

        # Get pool collection
        pool_collection = db_manager.db["pool"]

        # Find multiple pool records sorted by date
        pool_records = list(pool_collection.find().sort([("selection_date", -1)]).limit(limit))

        if not pool_records:
            logger.error("No records found in pool collection")
            return False

        logger.info(f"Checking {len(pool_records)} latest pool records for stock {stock_code}")

        for i, record in enumerate(pool_records):
            selection_date = record.get('selection_date', 'Unknown')
            logger.info(f"\n--- Record {i+1} (Date: {selection_date}) ---")

            # Extract stocks from this record
            stocks = record.get("stocks", [])

            # Find the specific stock
            target_stock = None
            for stock in stocks:
                if stock.get("code") == stock_code:
                    target_stock = stock
                    break

            if not target_stock:
                logger.info(f"Stock {stock_code} not found in this pool record")
                continue

            # Check if fund data exists
            if "fund" not in target_stock:
                logger.info("No fund data found for this stock in this record")
                continue

            fund_data = target_stock["fund"]
            logger.info(f"Fund data found with {len(fund_data)} strategies")

            # Display fund data for each strategy
            for strategy_name, strategy_data in fund_data.items():
                logger.info(f"  Strategy: {strategy_name}")
                logger.info(f"    Score: {strategy_data.get('score', 'N/A')}")
                logger.info(f"    Value: {strategy_data.get('value', 'N/A')}")

        return True

    except Exception as e:
        logger.error(f"Error checking multiple pool records: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting stock fund data check for stock 000061")

    # Check current fund data
    success = check_stock_fund_data("000061")

    if success:
        logger.info("\n" + "="*50)
        logger.info("Checking multiple pool records for comparison")
        logger.info("="*50)

        # Check multiple records for pattern analysis
        check_multiple_pool_records("000061", 3)

    logger.info("Stock fund data check completed")

