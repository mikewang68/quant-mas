#!/usr/bin/env python3
"""
Debug script to verify that LLM fundamental scores are correctly stored in the database.
"""

import sys
import os
import logging

# Add project root to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from config.mongodb_config import MongoDBConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_fundamental_scores_in_pool():
    """Check if fundamental scores are correctly stored in pool records."""
    try:
        # Initialize MongoDB manager
        mongodb_config = MongoDBConfig()
        db_manager = MongoDBManager(mongodb_config)

        # Get pool collection
        pool_collection = db_manager.db["pool"]

        # Find the latest pool record
        latest_pool_record = pool_collection.find_one(sort=[("selection_date", -1)])

        if not latest_pool_record:
            logger.error("No records found in pool collection")
            return False

        logger.info(f"Found latest pool record with selection date: {latest_pool_record.get('selection_date')}")

        # Extract stock data
        stocks = latest_pool_record.get("stocks", [])
        logger.info(f"Found {len(stocks)} stocks in latest pool record")

        # Check for fundamental analysis data
        fund_analysis_count = 0
        scores_found = 0
        scores_with_values = 0

        for stock in stocks:
            code = stock.get("code")
            fund_data = stock.get("fund", {})

            if fund_data:
                fund_analysis_count += 1
                logger.info(f"Stock {code} has fundamental analysis data")

                # Check each strategy in fund data
                for strategy_name, strategy_data in fund_data.items():
                    score = strategy_data.get("score")
                    value = strategy_data.get("value")

                    logger.info(f"  Strategy: {strategy_name}")
                    logger.info(f"    Score: {score} (type: {type(score)})")
                    logger.info(f"    Value: {value[:100] if value else 'None'}...")

                    if score is not None:
                        scores_found += 1
                        if isinstance(score, (int, float)) and score > 0:
                            scores_with_values += 1
                            logger.info(f"    Score is valid: {score}")
                        elif isinstance(score, str):
                            try:
                                float_score = float(score)
                                logger.info(f"    Score is string but convertible: {float_score}")
                            except ValueError:
                                logger.warning(f"    Score is string and not convertible: {score}")
                        else:
                            logger.warning(f"    Score is {type(score)}: {score}")
                    else:
                        logger.warning(f"    No score found for strategy {strategy_name}")

        logger.info(f"Summary:")
        logger.info(f"  - Stocks with fundamental analysis: {fund_analysis_count}")
        logger.info(f"  - Total scores found: {scores_found}")
        logger.info(f"  - Scores with actual values > 0: {scores_with_values}")

        return True

    except Exception as e:
        logger.error(f"Error checking fundamental scores: {e}")
        return False

def check_sample_strategy_config():
    """Check the LLM strategy configuration in the database."""
    try:
        # Initialize MongoDB manager
        mongodb_config = MongoDBConfig()
        db_manager = MongoDBManager(mongodb_config)

        # Get strategies collection
        strategies_collection = db_manager.db["strategies"]

        # Find LLM fundamental strategy
        llm_strategy = strategies_collection.find_one(
            {"name": "基于LLM的基本面分析策略"}
        )

        if not llm_strategy:
            logger.error("LLM fundamental strategy not found in database")
            return False

        logger.info("Found LLM fundamental strategy in database")
        logger.info(f"Strategy name: {llm_strategy.get('name')}")
        logger.info(f"Strategy parameters: {llm_strategy.get('parameters', {})}")

        # Check if it's assigned to the fundamental analysis agent
        agents_collection = db_manager.db["agents"]
        fundamental_agent = agents_collection.find_one(
            {"name": "基本面分析Agent"}
        )

        if fundamental_agent:
            logger.info("Found 基本面分析Agent in database")
            strategy_ids = fundamental_agent.get("strategies", [])
            logger.info(f"Assigned strategy IDs: {strategy_ids}")

            if str(llm_strategy.get("_id")) in strategy_ids:
                logger.info("LLM fundamental strategy is assigned to 基本面分析Agent")
            else:
                logger.warning("LLM fundamental strategy is NOT assigned to 基本面分析Agent")
        else:
            logger.warning("基本面分析Agent not found in database")

        return True

    except Exception as e:
        logger.error(f"Error checking strategy config: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting fundamental score storage verification...")

    # Check strategy configuration
    logger.info("\n=== Checking Strategy Configuration ===")
    check_sample_strategy_config()

    # Check pool data
    logger.info("\n=== Checking Pool Data ===")
    check_fundamental_scores_in_pool()

    logger.info("Verification completed.")

