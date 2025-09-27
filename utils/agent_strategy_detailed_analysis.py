#!/usr/bin/env python3
"""
Agent Strategy Detailed Analysis
Analyzes agent strategy assignments in detail.
"""

import sys
import os
from pymongo import MongoClient
from typing import Dict, Any, Set
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

def analyze_agent_strategies(db) -> Dict[str, Any]:
    """
    Analyze agent strategy assignments in detail.

    Args:
        db: MongoDB database instance

    Returns:
        Dict with analysis results
    """
    try:
        # Get collections
        agents_collection = db['agents']
        strategies_collection = db['strategies']

        # Get all agents
        agents = list(agents_collection.find({}))

        # Track all unique strategies assigned to agents
        unique_strategies: Set[str] = set()
        agent_strategy_mapping = {}

        # Process each agent
        for agent in agents:
            agent_name = agent.get('name', 'Unknown')
            strategy_ids = agent.get('strategies', [])

            # Get strategy names for this agent
            strategy_names = []
            for strategy_id in strategy_ids:
                try:
                    strategy = strategies_collection.find_one({'_id': ObjectId(strategy_id)})
                    if strategy:
                        strategy_name = strategy.get('name', 'Unknown')
                        strategy_names.append(strategy_name)
                        unique_strategies.add(strategy_name)
                except Exception as e:
                    logger.warning(f"Error getting strategy {strategy_id}: {e}")

            agent_strategy_mapping[agent_name] = strategy_names

        # Detailed information
        results = {
            'agent_strategy_mapping': agent_strategy_mapping,
            'unique_strategies': list(unique_strategies),
            'total_unique_strategies': len(unique_strategies)
        }

        return results

    except Exception as e:
        logger.error(f"Error analyzing agent strategies: {e}")
        return {}

def main():
    """Main function to run the agent strategy analysis."""
    print("Agent Strategy Detailed Analysis")
    print("="*30)

    # Connect to MongoDB
    db = connect_to_mongodb()
    if db is None:
        print("Failed to connect to database")
        return 1

    # Analyze agent strategies
    results = analyze_agent_strategies(db)

    if not results:
        print("No results to display")
        return 1

    # Display results
    print(f"\nAgent Strategy Assignments:")
    print("-"*30)
    agent_mapping = results['agent_strategy_mapping']
    for agent, strategies in agent_mapping.items():
        print(f"{agent}: {len(strategies)} strategies")
        for strategy in strategies:
            print(f"  - {strategy}")

    print(f"\nUnique Strategies Assigned to Agents:")
    print("-"*40)
    unique_strategies = results['unique_strategies']
    print(f"Total unique strategies: {results['total_unique_strategies']}")
    for strategy in sorted(unique_strategies):
        print(f"  - {strategy}")

    return 0

if __name__ == "__main__":
    sys.exit(main())

