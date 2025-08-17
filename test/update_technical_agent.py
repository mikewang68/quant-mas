#!/usr/bin/env python3
"""
Update the technical analysis agent with strategies
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.mongodb_manager import MongoDBManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_technical_agent():
    """Update the technical analysis agent with strategies"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()
        
        # Get all strategies
        strategies = db_manager.get_strategies()
        strategy_ids = [strategy.get('_id') for strategy in strategies]
        
        logger.info(f"Found {len(strategy_ids)} strategies: {strategy_ids}")
        
        # Find the technical analysis agent
        agents_collection = db_manager.db['agents']
        technical_agent = agents_collection.find_one({'name': '技术分析Agent'})
        
        if technical_agent:
            agent_id = technical_agent.get('_id')
            logger.info(f"Found technical analysis agent with ID: {agent_id}")
            
            # Update the agent with all strategy IDs
            result = agents_collection.update_one(
                {'_id': agent_id},
                {'$set': {'strategies': strategy_ids}}
            )
            
            if result.modified_count > 0:
                logger.info(f"Successfully updated technical analysis agent with {len(strategy_ids)} strategies")
            else:
                logger.info("No changes made to technical analysis agent")
        else:
            logger.error("Technical analysis agent not found")
        
        # Close connection
        db_manager.close_connection()
        logger.info("Database connection closed")
        
    except Exception as e:
        logger.error(f"Error updating technical analysis agent: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_technical_agent()

