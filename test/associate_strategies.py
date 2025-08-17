#!/usr/bin/env python3
"""
Script to associate strategies with the technical analysis agent
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pymongo import MongoClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def associate_strategies_with_technical_agent():
    """Associate existing technical strategies with the technical analysis agent"""
    try:
        # MongoDB connection details
        host = "192.168.1.2"
        port = 27017
        database_name = "stock"
        username = "stock"
        password = "681123"
        auth_database = "admin"
        
        # Create connection URI
        uri = f"mongodb://{username}:{password}@{host}:{port}/{database_name}?authSource={auth_database}"
        
        # Connect to MongoDB
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Get database
        db = client[database_name]
        
        # Find the technical analysis agent
        agents_collection = db['agents']
        technical_agent = agents_collection.find_one({'name': '技术分析Agent'})
        
        if not technical_agent:
            logger.error("Technical analysis agent not found")
            return False
            
        logger.info(f"Found technical analysis agent: {technical_agent.get('name')}")
        logger.info(f"Current strategies: {technical_agent.get('strategies', [])}")
        
        # Get all strategies
        strategies_collection = db['strategies']
        strategies = list(strategies_collection.find({}, {'_id': 1, 'name': 1, 'type': 1}))
        logger.info(f"Found {len(strategies)} strategies")
        
        # Filter for technical strategies
        technical_strategies = [s for s in strategies if s.get("type") in ["technical", "rsi", "macd", "bollinger"]]
        logger.info(f"Found {len(technical_strategies)} technical strategies")
        
        # Get strategy IDs
        strategy_ids = [str(s.get("_id")) for s in technical_strategies]
        logger.info(f"Strategy IDs to associate: {strategy_ids}")
        
        # Update the technical agent with these strategies
        agent_id = technical_agent.get("_id")
        result = agents_collection.update_one(
            {'_id': agent_id},
            {'$set': {'strategies': strategy_ids}}
        )
        
        if result.modified_count > 0:
            logger.info("Successfully updated technical analysis agent with strategies")
        else:
            logger.info("No changes needed for technical analysis agent")
            
        # Verify the update
        updated_agent = agents_collection.find_one({'_id': agent_id})
        logger.info(f"Updated strategies: {updated_agent.get('strategies', [])}")
        
        # Close connection
        client.close()
        logger.info("Database connection closed")
        return True
        
    except Exception as e:
        logger.error(f"Error associating strategies with technical agent: {e}")
        return False

if __name__ == "__main__":
    success = associate_strategies_with_technical_agent()
    if success:
        print("Successfully associated strategies with technical analysis agent")
    else:
        print("Failed to associate strategies with technical analysis agent")
        sys.exit(1)

