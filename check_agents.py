#!/usr/bin/env python3
"""
Check existing agents in the database to see if program field is properly saved
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.mongodb_manager import MongoDBManager


def check_agents():
    """Check agents in database"""
    try:
        # Initialize MongoDB manager
        mongo_manager = MongoDBManager()

        # Get all agents
        agents = mongo_manager.get_agents()
        print("Existing agents in database:")
        print(f"Total agents: {len(agents)}")

        for i, agent in enumerate(agents):
            print(f"\nAgent {i + 1}:")
            print(f"  ID: {agent.get('_id', 'N/A')}")
            print(f"  Name: {agent.get('name', 'N/A')}")
            print(f"  Description: {agent.get('description', 'N/A')}")
            print(f"  Status: {agent.get('status', 'N/A')}")
            print(f"  Program: {agent.get('program', 'N/A')}")
            print(f"  Strategies: {agent.get('strategies', 'N/A')}")

        # Get specific agent by ID to check full details
        if agents:
            first_agent_id = agents[0]["_id"]
            full_agent = mongo_manager.get_agent(first_agent_id)
            print(f"\nFull details of first agent (ID: {first_agent_id}):")
            for key, value in full_agent.items():
                print(f"  {key}: {value}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    check_agents()
