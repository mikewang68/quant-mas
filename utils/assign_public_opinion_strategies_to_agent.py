#!/usr/bin/env python3
"""
Utility script to assign public opinion analysis strategies to the 舆情分析Agent in MongoDB
"""

import sys
import os

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from bson import ObjectId


def assign_strategies_to_public_opinion_agent():
    """
    Assign public opinion analysis strategies to the 舆情分析Agent
    """
    try:
        # Initialize database manager
        db_manager = MongoDBManager()

        # Get the 舆情分析Agent
        public_opinion_agent = db_manager.agents_collection.find_one(
            {"name": "舆情分析Agent"}
        )

        if not public_opinion_agent:
            print("舆情分析Agent not found in database")
            return False

        # Find all strategies that should be assigned to public opinion analysis
        # In a real implementation, you would specify which strategies to assign
        public_opinion_strategies = list(db_manager.strategies_collection.find({
            "category": "public_opinion"  # This is an example filter
        }))

        if not public_opinion_strategies:
            print("No public opinion strategies found in database")
            return False

        # Get strategy IDs
        strategy_ids = [str(strategy["_id"]) for strategy in public_opinion_strategies]

        # Update the agent with the strategy IDs
        result = db_manager.agents_collection.update_one(
            {"_id": public_opinion_agent["_id"]},
            {"$set": {"strategies": strategy_ids}}
        )

        if result.modified_count > 0:
            print(f"Successfully assigned {len(strategy_ids)} strategies to 舆情分析Agent")
            for strategy in public_opinion_strategies:
                print(f"  - {strategy.get('name', 'Unknown Strategy')}")
            return True
        else:
            print("No changes made to 舆情分析Agent")
            return False

    except Exception as e:
        print(f"Error assigning strategies to public opinion agent: {e}")
        return False
    finally:
        # Close database connection
        if 'db_manager' in locals():
            db_manager.close_connection()


if __name__ == "__main__":
    success = assign_strategies_to_public_opinion_agent()
    if success:
        print("Public opinion strategies assignment completed successfully")
    else:
        print("Failed to assign public opinion strategies")
        sys.exit(1)

