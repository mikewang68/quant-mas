#!/usr/bin/env python3
"""
Debug script to check how LLM scores are stored in the pool collection
"""

import sys
import os

# Add project root to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_pool_scores():
    """Check how scores are stored in the pool collection"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()

        # Get pool collection
        pool_collection = db_manager.db["pool"]

        # Find the latest pool record
        latest_pool_record = pool_collection.find_one(sort=[("selection_date", -1)])

        if not latest_pool_record:
            logger.error("No records found in pool collection")
            return

        logger.info(f"Latest pool record date: {latest_pool_record.get('selection_date')}")

        # Extract stock data
        stocks = latest_pool_record.get("stocks", [])
        logger.info(f"Total stocks in pool: {len(stocks)}")

        # Check for fundamental analysis data
        fund_analysis_count = 0
        scores_found = []

        for i, stock in enumerate(stocks[:10]):  # Check first 10 stocks
            code = stock.get("code", "Unknown")
            if "fund" in stock:
                fund_analysis_count += 1
                fund_data = stock["fund"]
                logger.info(f"Stock {code} has fundamental analysis data:")

                for strategy_name, strategy_data in fund_data.items():
                    score = strategy_data.get("score", "N/A")
                    value = strategy_data.get("value", "N/A")
                    logger.info(f"  - Strategy: {strategy_name}")
                    logger.info(f"    Score: {score} (type: {type(score)})")
                    logger.info(f"    Value length: {len(str(value)) if value != 'N/A' else 'N/A'} chars")
                    if score != "N/A":
                        scores_found.append((code, strategy_name, score))
            else:
                logger.info(f"Stock {code} has no fundamental analysis data")

        logger.info(f"\nSummary:")
        logger.info(f"Stocks with fundamental analysis: {fund_analysis_count}/{min(10, len(stocks))}")
        logger.info(f"Scores found: {len(scores_found)}")

        # Show some actual score values
        if scores_found:
            logger.info("\nSample scores:")
            for code, strategy, score in scores_found[:5]:
                logger.info(f"  {code} - {strategy}: {score}")

        # Check fund_at timestamp
        fund_at = latest_pool_record.get("fund_at", "Not set")
        logger.info(f"\nFundamental analysis timestamp: {fund_at}")

    except Exception as e:
        logger.error(f"Error checking pool scores: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    check_pool_scores()

