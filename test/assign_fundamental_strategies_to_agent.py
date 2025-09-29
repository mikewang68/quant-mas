#!/usr/bin/env python3
"""
Script to assign fundamental strategies to the fundamental analysis agent in MongoDB.
"""

import sys
import os
import logging
from bson import ObjectId

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def assign_strategies_to_fundamental_agent():
    """Assign fundamental strategies to the fundamental analysis agent."""
    try:
        # Initialize MongoDB manager
        mongodb_manager = MongoDBManager()

        # Get the fundamental analysis agent
        agent = mongodb_manager.agents_collection.find_one(
            {"name": "基本面分析Agent"}
        )

        if not agent:
            logger.error("Fundamental analysis agent not found in database")
            return False

        # Get the fundamental strategies
        fundamental_strategy = mongodb_manager.strategies_collection.find_one(
            {"name": "基本面分析策略"}
        )

        llm_fundamental_strategy = mongodb_manager.strategies_collection.find_one(
            {"name": "LLM基本面分析策略"}
        )

        if not fundamental_strategy:
            logger.error("Fundamental strategy not found in database")
            return False

        if not llm_fundamental_strategy:
            logger.error("LLM Fundamental strategy not found in database")
            return False

        # Get strategy IDs
        fundamental_strategy_id = str(fundamental_strategy['_id'])
        llm_fundamental_strategy_id = str(llm_fundamental_strategy['_id'])

        # Update agent with strategy IDs
        strategy_ids = [fundamental_strategy_id, llm_fundamental_strategy_id]

        result = mongodb_manager.agents_collection.update_one(
            {"_id": agent['_id']},
            {"$set": {"strategies": strategy_ids}}
        )

        if result.modified_count > 0:
            logger.info("Successfully assigned fundamental strategies to fundamental analysis agent")
            logger.info(f"Assigned strategies: {strategy_ids}")
        else:
            logger.info("No changes needed - strategies already assigned to agent")

        # Close MongoDB connection
        mongodb_manager.close_connection()
        return True

    except Exception as e:
        logger.error(f"Error assigning strategies to fundamental agent: {e}")
        return False

def main():
    """Main function to assign fundamental strategies to the agent."""
    logger.info("Starting fundamental strategies assignment process")

    success = assign_strategies_to_fundamental_agent()

    if success:
        logger.info("Successfully assigned fundamental strategies to agent")
        print("Successfully assigned fundamental strategies to agent")
        return True
    else:
        logger.error("Failed to assign fundamental strategies to agent")
        print("Failed to assign fundamental strategies to agent")
        return False

if __name__ == "__main__":
    main()

