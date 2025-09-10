#!/usr/bin/env python3
"""
Script to assign the Signal Generation V1 Strategy to the Signal Generator Agent
"""

import sys
import os
import logging
from bson import ObjectId

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data.mongodb_manager import MongoDBManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def assign_strategy_to_agent():
    """Assign the Signal Generation V1 Strategy to the Signal Generator Agent"""
    db_manager = None
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()

        # Get the strategy
        strategy = db_manager.strategies_collection.find_one({"name": "信号生成V1"})
        if not strategy:
            logger.error("Signal Generation V1 Strategy not found")
            return False

        strategy_id = strategy['_id']
        logger.info(f"Found strategy with ID: {strategy_id}")

        # Get the agent
        agent = db_manager.agents_collection.find_one({"name": "信号生成Agent"})
        if not agent:
            logger.error("Signal Generator Agent not found")
            return False

        agent_id = agent['_id']
        current_strategies = agent.get("strategies", [])
        logger.info(f"Found agent with ID: {agent_id}")
        logger.info(f"Current strategies assigned to agent: {current_strategies}")

        # Check if strategy is already assigned
        if str(strategy_id) in current_strategies:
            logger.info("Strategy already assigned to agent")
            return True

        # Add strategy to agent
        current_strategies.append(str(strategy_id))

        # Update agent
        result = db_manager.agents_collection.update_one(
            {"_id": agent_id},
            {"$set": {"strategies": current_strategies}}
        )

        if result.modified_count > 0:
            logger.info("Successfully assigned strategy to agent")
        else:
            logger.info("No changes made to agent")

        # Verify the assignment
        updated_agent = db_manager.agents_collection.find_one({"_id": agent_id})
        if updated_agent:
            updated_strategies = updated_agent.get("strategies", [])
            logger.info(f"Updated strategies assigned to agent: {updated_strategies}")
        else:
            logger.error("Failed to verify agent update")

        return True

    except Exception as e:
        logger.error(f"Error assigning strategy to agent: {e}")
        return False
    finally:
        # Close connection
        if db_manager:
            db_manager.close_connection()


if __name__ == "__main__":
    assign_strategy_to_agent()

