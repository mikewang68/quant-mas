#!/usr/bin/env python3
"""
Script to insert the public opinion analysis strategy into MongoDB
This strategy uses FireCrawl web search and LLM evaluation for sentiment analysis
"""

import sys
import os
import json

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from bson import ObjectId


def insert_public_opinion_analysis_strategy():
    """
    Insert the public opinion analysis strategy into the database
    """
    try:
        # Initialize database manager
        db_manager = MongoDBManager()

        # Define the public opinion analysis strategy
        public_opinion_strategy = {
            "name": "舆情分析策略",
            "description": "基于FireCrawl网络搜索和LLM情感分析的舆情分析策略",
            "file": "public_opinion_analysis_strategy",
            "class_name": "PublicOpinionAnalysisStrategy",
            "category": "public_opinion",
            "parameters": {
                "sentiment_threshold": 0.6,
                "news_count_threshold": 3,
                "search_depth": 5,
                "firecrawl_config": {
                    "api_url": "http://192.168.1.2:8080/v1",
                    "timeout": 30
                },
                "llm_config": {
                    "api_url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-pro:generateContent",
                    "api_key_env_var": "GEMINI_API_KEY",
                    "model": "gemini-2.0-pro",
                    "timeout": 60
                }
            },
            "program": {
                "file": "public_opinion_analysis_strategy",
                "class": "PublicOpinionAnalysisStrategy"
            },
            "enabled": True,
            "created_at": "2025-08-30",
            "updated_at": "2025-08-30"
        }

        # Check if strategy already exists
        existing_strategy = db_manager.strategies_collection.find_one(
            {"name": public_opinion_strategy["name"]}
        )

        if existing_strategy:
            print(f"Strategy '{public_opinion_strategy['name']}' already exists in database")
            # Update the existing strategy
            result = db_manager.strategies_collection.update_one(
                {"_id": existing_strategy["_id"]},
                {"$set": public_opinion_strategy}
            )
            if result.modified_count > 0:
                print(f"Successfully updated public opinion strategy")
                strategy_id = existing_strategy["_id"]
            else:
                print("No changes made to existing strategy")
                strategy_id = existing_strategy["_id"]
        else:
            # Insert the strategy
            result = db_manager.strategies_collection.insert_one(public_opinion_strategy)

            if result.inserted_id:
                print(f"Successfully inserted public opinion strategy with ID: {result.inserted_id}")
                strategy_id = result.inserted_id
            else:
                print("Failed to insert public opinion strategy")
                return False

        # Now assign this strategy to the 舆情分析Agent
        assign_strategy_to_agent(db_manager, strategy_id)
        return True

    except Exception as e:
        print(f"Error inserting public opinion strategy: {e}")
        return False
    finally:
        # Close database connection
        if 'db_manager' in locals():
            db_manager.close_connection()


def assign_strategy_to_agent(db_manager, strategy_id):
    """
    Assign the strategy to the 舆情分析Agent

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
            return False

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

        return True

    except Exception as e:
        print(f"Error assigning strategy to agent: {e}")
        return False


if __name__ == "__main__":
    success = insert_public_opinion_analysis_strategy()
    if success:
        print("Public opinion strategy insertion completed successfully")
    else:
        print("Failed to insert public opinion strategy")
        sys.exit(1)

