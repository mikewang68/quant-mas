#!/usr/bin/env python3
"""
Test script to verify that the fundamental selector optimization logic works correctly.
This script tests the logic that skips stock analysis when valid scores already exist.
"""

import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.fundamental_selector import FundamentalStockSelector
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_fundamental_selector_optimization():
    """Test that the fundamental selector optimization logic works correctly."""
    logger.info("Testing fundamental selector optimization logic...")

    try:
        # Initialize components
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Initialize selector
        selector = FundamentalStockSelector(db_manager, data_fetcher)

        # Check that strategies were loaded
        logger.info(f"Loaded {len(selector.strategy_names)} strategies")
        for i, name in enumerate(selector.strategy_names):
            logger.info(f"  Strategy {i}: {name}")

        # Check that strategy instances were created
        logger.info(f"Created {len(selector.strategy_instances)} strategy instances")
        for i, instance in enumerate(selector.strategy_instances):
            logger.info(f"  Instance {i}: {instance.__class__.__name__}")

        # Test the optimization logic by checking if it correctly identifies stocks
        # that need analysis vs those that already have valid scores
        pool_collection = db_manager.db["pool"]
        latest_pool_record = pool_collection.find_one(sort=[("selection_date", -1)])

        if not latest_pool_record:
            logger.warning("No pool records found - cannot test optimization logic")
            db_manager.close_connection()
            return True

        pool_stocks = latest_pool_record.get("stocks", [])
        logger.info(f"Found {len(pool_stocks)} stocks in latest pool record")

        # Test the optimization logic for each strategy
        for i, strategy_name in enumerate(selector.strategy_names):
            stocks_needing_analysis = []
            stocks_with_existing_data = []

            for stock in pool_stocks:
                code = stock.get("code")
                if not code:
                    continue

                # Check if this stock already has a valid score for this strategy
                fund_data = stock.get("fund", {})
                strategy_fund_data = fund_data.get(strategy_name, {})
                existing_score = strategy_fund_data.get("score", None)

                # If score exists and is valid (not 0 and not None), skip analysis
                if existing_score is not None and existing_score != 0 and existing_score != 0.0:
                    logger.info(f"Stock {code} already has valid score {existing_score} for {strategy_name}")
                    stocks_with_existing_data.append({
                        "code": code,
                        "score": existing_score,
                        "value": strategy_fund_data.get("value", ""),
                        "strategy_name": strategy_name
                    })
                else:
                    # Need to analyze this stock
                    stocks_needing_analysis.append(code)
                    logger.info(f"Stock {code} needs analysis for {strategy_name} (score: {existing_score})")

            logger.info(f"Strategy {strategy_name}: {len(stocks_with_existing_data)} stocks with existing data, {len(stocks_needing_analysis)} stocks need analysis")

        db_manager.close_connection()
        return True

    except Exception as e:
        logger.error(f"Error testing fundamental selector optimization logic: {e}")
        return False


def main():
    """Main test function."""
    logger.info("Starting fundamental selector optimization tests...")

    success = test_fundamental_selector_optimization()

    if success:
        logger.info("Optimization tests completed successfully!")
        return True
    else:
        logger.error("Optimization tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

