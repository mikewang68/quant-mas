#!/usr/bin/env python3
"""
Agent Strategy Counter
Counts the number of strategies assigned to each agent by checking the database configuration.
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

def count_strategies_by_agent(db) -> Dict[str, int]:
    """
    Count strategies assigned to each agent by checking database configuration.

    Args:
        db: MongoDB database instance

    Returns:
        Dictionary with strategy counts by agent
    """
    try:
        # Get collections
        agents_collection = db['agents']
        strategies_collection = db['strategies']

        # Get all agents
        agents = list(agents_collection.find({}))

        agent_strategy_counts = {}

        # Process each agent
        for agent in agents:
            agent_name = agent.get('name', 'Unknown')
            strategy_ids = agent.get('strategies', [])

            # Count strategies for this agent
            count = len(strategy_ids)
            agent_strategy_counts[agent_name] = count

            # Also get strategy names for more detailed information
            strategy_names = []
            for strategy_id in strategy_ids:
                try:
                    strategy = strategies_collection.find_one({'_id': ObjectId(strategy_id)})
                    if strategy:
                        strategy_names.append(strategy.get('name', 'Unknown'))
                except Exception as e:
                    logger.warning(f"Error getting strategy {strategy_id}: {e}")

            logger.info(f"Agent '{agent_name}' has {count} strategies: {strategy_names}")

        return agent_strategy_counts

    except Exception as e:
        logger.error(f"Error counting strategies by agent: {e}")
        return {}

def count_strategies_by_field_from_pool(db) -> Dict[str, int]:
    """
    Count unique strategies in each field (trend, tech, fund, pub) from pool data.

    Args:
        db: MongoDB database instance

    Returns:
        Dictionary with strategy counts by field
    """
    try:
        # Get the pool collection
        pool_collection = db['pool']

        # Find the latest pool record
        latest_pool_record = pool_collection.find_one(sort=[("_id", -1)])

        if not latest_pool_record:
            logger.error("No records found in pool collection")
            return {}

        # Get stocks from the latest pool record
        pool_stocks = latest_pool_record.get("stocks", [])

        if not pool_stocks:
            logger.error("No stocks found in latest pool record")
            return {}

        logger.info(f"Analyzing {len(pool_stocks)} stocks from pool")

        # Initialize sets to store unique strategies for each field
        field_strategies = {
            'trend': set(),
            'tech': set(),
            'fund': set(),
            'pub': set()
        }

        # Process each stock
        for stock in pool_stocks:
            # Process all fields in the stock
            for field_name, field_value in stock.items():
                # Only process the specified fields and ensure field_value is a dict
                if field_name in field_strategies and isinstance(field_value, dict):
                    # Add strategy names to the set for this field
                    for strategy_name in field_value.keys():
                        field_strategies[field_name].add(strategy_name)

        # Convert sets to counts
        field_strategy_counts = {
            field: len(strategies) for field, strategies in field_strategies.items()
        }

        # Log detailed information
        for field, strategies in field_strategies.items():
            logger.info(f"Field '{field}' has {len(strategies)} unique strategies: {list(strategies)}")

        return field_strategy_counts

    except Exception as e:
        logger.error(f"Error counting strategies by field from pool: {e}")
        return {}

def main():
    """Main function to run the agent strategy counter."""
    print("Agent Strategy Counter")
    print("="*20)

    # Connect to MongoDB
    db = connect_to_mongodb()
    if db is None:
        print("Failed to connect to database")
        return 1

    print("\n1. Strategy Counts by Agent:")
    print("-"*30)

    # Count strategies by agent
    agent_counts = count_strategies_by_agent(db)

    for agent, count in agent_counts.items():
        print(f"{agent}: {count} strategies")

    print("\n2. Unique Strategy Counts by Field (from pool data):")
    print("-"*50)

    # Count unique strategies by field from pool data
    field_counts = count_strategies_by_field_from_pool(db)

    total_unique_strategies = 0
    for field, count in field_counts.items():
        print(f"{field.upper():>5}: {count} unique strategies")
        total_unique_strategies += count

    print("-"*50)
    print(f"TOTAL: {total_unique_strategies} unique strategies")

    return 0

if __name__ == "__main__":
    sys.exit(main())

