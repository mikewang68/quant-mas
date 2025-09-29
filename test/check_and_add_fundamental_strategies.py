#!/usr/bin/env python3
"""
Script to check if fundamental strategies exist in MongoDB and add them if they don't.
"""

import sys
import os
import json
import logging

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_and_add_fundamental_strategies():
    """Check if fundamental strategies exist and add them if they don't."""
    try:
        # Initialize MongoDB manager
        mongodb_manager = MongoDBManager()

        # Check if standard fundamental strategy exists
        fundamental_strategy = mongodb_manager.get_strategy_by_name("基本面分析策略")
        if not fundamental_strategy:
            logger.info("Standard fundamental strategy not found, creating it...")
            create_standard_fundamental_strategy(mongodb_manager)
        else:
            logger.info("Standard fundamental strategy already exists")

        # Check if LLM fundamental strategy exists
        llm_fundamental_strategy = mongodb_manager.get_strategy_by_name("LLM基本面分析策略")
        if not llm_fundamental_strategy:
            logger.info("LLM fundamental strategy not found, creating it...")
            create_llm_fundamental_strategy(mongodb_manager)
        else:
            logger.info("LLM fundamental strategy already exists")

        # Close MongoDB connection
        mongodb_manager.close_connection()
        return True

    except Exception as e:
        logger.error(f"Error checking and adding fundamental strategies: {e}")
        return False

def create_standard_fundamental_strategy(mongodb_manager):
    """Create the standard fundamental strategy in MongoDB."""
    try:
        strategy_config = {
            "name": "基本面分析策略",
            "type": "fundamental",
            "description": "基于财务报表和财务比率的传统基本面分析策略",
            "file": "fundamental_strategy",
            "class_name": "FundamentalStrategy",
            "parameters": {
                "min_roe": 0.1,
                "max_pe": 20,
                "min_current_ratio": 1.5,
                "max_debt_equity": 0.5,
                "min_revenue_growth": 0.1
            },
            "program": {
                "file": "fundamental_strategy",
                "class": "FundamentalStrategy"
            }
        }

        result = mongodb_manager.create_strategy(strategy_config)
        if result:
            logger.info(f"Created standard fundamental strategy with ID: {result}")
        else:
            logger.error("Failed to create standard fundamental strategy")

    except Exception as e:
        logger.error(f"Error creating standard fundamental strategy: {e}")

def create_llm_fundamental_strategy(mongodb_manager):
    """Create the LLM fundamental strategy in MongoDB."""
    try:
        strategy_config = {
            "name": "LLM基本面分析策略",
            "type": "fundamental",
            "description": "基于大语言模型的智能基本面分析策略",
            "file": "llm_fundamental_strategy",
            "class_name": "LLMFundamentalStrategy",
            "parameters": {
                "llm_config": {
                    "api_url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-pro:generateContent",
                    "model": "gemini-2.0-pro",
                    "timeout": 60
                }
            },
            "program": {
                "file": "llm_fundamental_strategy",
                "class": "LLMFundamentalStrategy"
            }
        }

        result = mongodb_manager.create_strategy(strategy_config)
        if result:
            logger.info(f"Created LLM fundamental strategy with ID: {result}")
        else:
            logger.error("Failed to create LLM fundamental strategy")

    except Exception as e:
        logger.error(f"Error creating LLM fundamental strategy: {e}")

def main():
    """Main function to check and add fundamental strategies."""
    logger.info("Starting fundamental strategies check and addition process")

    success = check_and_add_fundamental_strategies()

    if success:
        logger.info("Successfully processed fundamental strategies")
        print("Successfully processed fundamental strategies")
        return True
    else:
        logger.error("Failed to process fundamental strategies")
        print("Failed to process fundamental strategies")
        return False

if __name__ == "__main__":
    main()

