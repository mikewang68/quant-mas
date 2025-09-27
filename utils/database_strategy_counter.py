#!/usr/bin/env python3
"""
Database Strategy Counter
Counts the actual number of strategies in the database and compares with agent assignments.
"""

import sys
import os
from pymongo import MongoClient
from typing import Dict, Any, List
import logging
from bson import ObjectId

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_to_mongodb():
    """Connect to MongoDB and return the database instance."""
    try:
        # Connection parameters from config/database.yaml
        MONGODB_URI = "mongodb://stock:681123@192.168.1.2:27017/admin"
        DATABASE_NAME = "stock"

        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        # Test connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        return db
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return None

def count_total_strategies(db) -> int:
    """
    Count total strategies in the strategies collection.

    Args:
        db: MongoDB database instance

    Returns:
        int: Total number of strategies
    """
    try:
        strategies_collection = db['strategies']
        total_strategies = strategies_collection.count_documents({})
        logger.info(f"Total strategies in database: {total_strategies}")
        return total_strategies
    except Exception as e:
        logger.error(f"Error counting total strategies: {e}")
        return 0

def count_unique_agent_strategies(db) -> int:
    """
    Count unique strategies assigned to agents.

    Args:
        db: MongoDB database instance

    Returns:
        int: Number of unique strategies assigned to agents
    """
    try:
        # Get agents collection
        agents_collection = db['agents']

        # Get all agents
        agents = list(agents_collection.find({}))

        # Count unique strategies across all agents
        unique_strategies = set()
        for agent in agents:
            strategy_ids = agent.get('strategies', [])
            for strategy_id in strategy_ids:
                unique_strategies.add(strategy_id)

        total_unique_strategies = len(unique_strategies)
        logger.info(f"Unique strategies assigned to agents: {total_unique_strategies}")
        return total_unique_strategies
    except Exception as e:
        logger.error(f"Error counting unique agent strategies: {e}")
        return 0

def list_agent_strategies(db):
    """
    List strategies assigned to each agent.

    Args:
        db: MongoDB database instance
    """
    try:
        # Get collections
        agents_collection = db['agents']
        strategies_collection = db['strategies']

        # Get all agents
        agents = list(agents_collection.find({}))

        print("\nAgent Strategy Assignments:")
        print("="*40)

        # Process each agent
        for agent in agents:
            agent_name = agent.get('name', 'Unknown')
            strategy_ids = agent.get('strategies', [])

            print(f"\n{agent_name}:")

            # Get strategy names for this agent
            strategy_names = []
            for strategy_id in strategy_ids:
                try:
                    strategy = strategies_collection.find_one({'_id': ObjectId(strategy_id)})
                    if strategy:
                        strategy_names.append(strategy.get('name', 'Unknown'))
                except Exception as e:
                    logger.warning(f"Error getting strategy {strategy_id}: {e}")

            print(f"  Strategies ({len(strategy_names)}): {strategy_names}")

    except Exception as e:
        logger.error(f"Error listing agent strategies: {e}")

def main():
    """Main function to run the database strategy counter."""
    print("Database Strategy Counter")
    print("="*22)

    # Connect to MongoDB
    db = connect_to_mongodb()
    if db is None:
        print("Failed to connect to database")
        return 1

    # Count total strategies
    total_strategies = count_total_strategies(db)

    # Count unique agent strategies
    unique_agent_strategies = count_unique_agent_strategies(db)

    print(f"\nStrategy Counts:")
    print("-"*15)
    print(f"Total strategies in database: {total_strategies}")
    print(f"Unique strategies assigned to agents: {unique_agent_strategies}")

    # List agent strategies
    list_agent_strategies(db)

    return 0

if __name__ == "__main__":
    sys.exit(main())

