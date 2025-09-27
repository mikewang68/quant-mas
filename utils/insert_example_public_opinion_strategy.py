#!/usr/bin/env python3
"""
Script to insert an example public opinion analysis strategy into MongoDB
This demonstrates how to add strategies to the public opinion selector agent
"""

import sys
import os
import json

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from bson import ObjectId


def insert_example_public_opinion_strategy():
    """
    Insert an example public opinion analysis strategy into the database
    """
    try:
        # Initialize database manager
        db_manager = MongoDBManager()

        # Define the example strategy
        example_strategy = {
            "name": "示例舆情分析策略",
            "description": "示例舆情分析策略，分析市场情绪和新闻 sentiment",
            "file": "example_public_opinion_strategy",
            "class_name": "ExamplePublicOpinionStrategy",
            "category": "public_opinion",
            "parameters": {
                "sentiment_threshold": 0.7,
                "volume_multiplier": 1.5
            },
            "program": {
                "file": "example_public_opinion_strategy",
                "class": "ExamplePublicOpinionStrategy"
            },
            "enabled": True,
            "created_at": "2025-08-30",
            "updated_at": "2025-08-30"
        }

        # Check if strategy already exists
        existing_strategy = db_manager.strategies_collection.find_one(
            {"name": example_strategy["name"]}
        )

        if existing_strategy:
            print(f"Strategy '{example_strategy['name']}' already exists in database")
            return False

        # Insert the strategy
        result = db_manager.strategies_collection.insert_one(example_strategy)

        if result.inserted_id:
            print(f"Successfully inserted example public opinion strategy with ID: {result.inserted_id}")

            # Now assign this strategy to the 舆情分析Agent
            assign_strategy_to_agent(db_manager, result.inserted_id)
            return True
        else:
            print("Failed to insert example public opinion strategy")
            return False

    except Exception as e:
        print(f"Error inserting example public opinion strategy: {e}")
        return False
    finally:
        # Close database connection
        if 'db_manager' in locals():
            db_manager.close_connection()


def assign_strategy_to_agent(db_manager, strategy_id):
    """
    Assign the example strategy to the 舆情分析Agent

    Args:
        db_manager: MongoDBManager instance
        strategy_id: ID of the strategy to assign
    """
    try:
        # Get the 舆情分析Agent
        public_opinion_agent = db_manager.agents_collection.find_one(
            {"name": "舆情分析Agent"}
        )

        if not public_opinion_agent:
            print("舆情分析Agent not found in database")
            # Create the agent if it doesn't exist
            agent_doc = {
                "name": "舆情分析Agent",
                "description": "Public opinion analysis agent for analyzing market sentiment and news",
                "strategies": [str(strategy_id)],
                "enabled": True
            }
            result = db_manager.agents_collection.insert_one(agent_doc)
            if result.inserted_id:
                print(f"Created 舆情分析Agent and assigned strategy {strategy_id}")
            return

        # Add the strategy to the agent's strategies list if not already present
        current_strategies = public_opinion_agent.get("strategies", [])

        # Convert strategy_id to string for comparison
        strategy_id_str = str(strategy_id)

        if strategy_id_str not in current_strategies:
            current_strategies.append(strategy_id_str)
            result = db_manager.agents_collection.update_one(
                {"_id": public_opinion_agent["_id"]},
                {"$set": {"strategies": current_strategies}}
            )

            if result.modified_count > 0:
                print(f"Successfully assigned strategy {strategy_id} to 舆情分析Agent")
            else:
                print("No changes made to 舆情分析Agent")
        else:
            print(f"Strategy {strategy_id} is already assigned to 舆情分析Agent")

    except Exception as e:
        print(f"Error assigning strategy to agent: {e}")


if __name__ == "__main__":
    success = insert_example_public_opinion_strategy()
    if success:
        print("Example public opinion strategy insertion completed successfully")
    else:
        print("Failed to insert example public opinion strategy")
        sys.exit(1)

