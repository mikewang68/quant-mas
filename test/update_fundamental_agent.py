#!/usr/bin/env python3
"""
Update the 基本面分析Agent in the database to add the program field and description
"""

import sys
import os
from bson import ObjectId

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.mongodb_manager import MongoDBManager


def update_fundamental_agent():
    """Update the fundamental analysis agent with program field and description"""
    try:
        # Initialize MongoDB manager
        mongo_manager = MongoDBManager()

        # Find the 基本面分析Agent by name
        agent = mongo_manager.agents_collection.find_one({"name": "基本面分析Agent"})

        if not agent:
            print("Error: 基本面分析Agent not found in database")
            return False

        agent_id = agent["_id"]
        print(f"Found 基本面分析Agent with ID: {agent_id}")

        # Update the agent with program field and description
        result = mongo_manager.agents_collection.update_one(
            {"_id": ObjectId(agent_id)},
            {
                "$set": {
                    "program": "fundamental_selector.py",
                    "description": "从股票池中选取股票，运用基本面指标进行筛选"
                }
            }
        )

        if result.modified_count > 0:
            print("Successfully updated 基本面分析Agent with program field and description")
            print(f"Modified {result.modified_count} document(s)")

            # Verify the update
            updated_agent = mongo_manager.agents_collection.find_one({"_id": ObjectId(agent_id)})
            print(f"\nUpdated agent details:")
            print(f"  Name: {updated_agent.get('name', 'N/A')}")
            print(f"  Program: {updated_agent.get('program', 'N/A')}")
            print(f"  Description: {updated_agent.get('description', 'N/A')}")
            print(f"  Status: {updated_agent.get('status', 'N/A')}")
            print(f"  Strategies: {updated_agent.get('strategies', 'N/A')}")

            return True
        else:
            print("No changes were made to the agent")
            return False

    except Exception as e:
        print(f"Error updating agent: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = update_fundamental_agent()
    if success:
        print("\nAgent update completed successfully")
    else:
        print("\nAgent update failed")

