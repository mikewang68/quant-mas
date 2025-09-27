#!/usr/bin/env python3
"""
Script to create the Public Opinion Analysis Agent in MongoDB
"""

import sys
import os

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager


def create_public_opinion_agent():
    """
    Create the 舆情分析Agent in the database if it doesn't already exist
    """
    db_manager = None
    try:
        # Initialize database manager
        db_manager = MongoDBManager()

        # Check if the agent already exists
        existing_agent = db_manager.agents_collection.find_one(
            {"name": "舆情分析Agent"}
        )

        if existing_agent:
            print("舆情分析Agent already exists in database:")
            print(f"  ID: {existing_agent.get('_id')}")
            print(f"  Name: {existing_agent.get('name')}")
            print(f"  Description: {existing_agent.get('description', 'No description')}")
            print(f"  Strategies: {existing_agent.get('strategies', [])}")
            print(f"  Enabled: {existing_agent.get('enabled', True)}")

            # Update the description to match the pattern of other agents
            current_description = existing_agent.get('description', '')
            if not current_description or 'Public opinion analysis agent' in current_description:
                result = db_manager.agents_collection.update_one(
                    {"_id": existing_agent["_id"]},
                    {"$set": {"description": "从股票池中选取股票，运用舆情分析指标进行筛选"}}
                )
                if result.modified_count > 0:
                    print("  Updated description for 舆情分析Agent")

            # Add program field if it doesn't exist
            if 'program' not in existing_agent:
                result = db_manager.agents_collection.update_one(
                    {"_id": existing_agent["_id"]},
                    {"$set": {"program": "public_opinion_selector.py"}}
                )
                if result.modified_count > 0:
                    print("  Added program field for 舆情分析Agent")
            return True

        # Define the agent document
        agent_document = {
            "name": "舆情分析Agent",
            "description": "从股票池中选取股票，运用舆情分析指标进行筛选",
            "strategies": [],  # Will be populated when strategies are added
            "program": "public_opinion_selector.py",
            "enabled": True
        }

        # Insert the agent
        result = db_manager.agents_collection.insert_one(agent_document)

        if result.inserted_id:
            print(f"Successfully created 舆情分析Agent with ID: {result.inserted_id}")
            return True
        else:
            print("Failed to create 舆情分析Agent")
            return False

    except Exception as e:
        print(f"Error creating 舆情分析Agent: {e}")
        return False
    finally:
        # Close database connection
        if db_manager:
            db_manager.close_connection()


def list_agents():
    """
    List all agents in the database
    """
    db_manager = None
    try:
        # Initialize database manager
        db_manager = MongoDBManager()

        # Get all agents
        agents = list(db_manager.agents_collection.find({}))

        print("Current agents in database:")
        for agent in agents:
            print(f"  - {agent.get('name', 'Unknown')}: {agent.get('description', 'No description')}")

        return True

    except Exception as e:
        print(f"Error listing agents: {e}")
        return False
    finally:
        # Close database connection
        if db_manager:
            db_manager.close_connection()


def main():
    """
    Main function to create the public opinion agent
    """
    print("Creating 舆情分析Agent...")
    success = create_public_opinion_agent()

    if success:
        print("\nListing all agents:")
        list_agents()
        print("\nPublic opinion agent creation completed successfully")
    else:
        print("\nFailed to create public opinion agent")
        sys.exit(1)


if __name__ == "__main__":
    main()

