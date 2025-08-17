#!/usr/bin/env python3
"""
Script to check the specific technical selector agent and its strategies
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_technical_selector_agent():
    """Check specifically for the technical selector agent and its strategies"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()
        
        # Get all agents
        agents = db_manager.get_agents()
        
        print("ALL AGENTS IN SYSTEM:")
        print("=" * 60)
        
        for agent in agents:
            agent_name = agent.get('name', 'Unknown')
            agent_id = agent.get('_id', 'Unknown')
            agent_description = agent.get('description', 'N/A')
            strategy_ids = agent.get('strategies', [])
            
            print(f"\nAgent Name: {agent_name}")
            print(f"Agent ID: {agent_id}")
            print(f"Description: {agent_description}")
            print(f"Strategies Count: {len(strategy_ids)}")
            print(f"Strategy IDs: {strategy_ids}")
            
            # Get details of each strategy
            for strategy_id in strategy_ids:
                strategy = db_manager.get_strategy(strategy_id)
                if strategy:
                    print(f"  - Strategy: {strategy.get('name', strategy_id)}")
                    print(f"    ID: {strategy_id}")
                    print(f"    Type: {strategy.get('type', 'N/A')}")
                    print(f"    Description: {strategy.get('description', 'N/A')}")
                    if 'parameters' in strategy:
                        print(f"    Parameters: {strategy['parameters']}")
                else:
                    print(f"  - Strategy ID {strategy_id}: NOT FOUND")
            
            # Highlight if this is the technical selector agent
            if "技术" in agent_name or "technical" in agent_name.lower():
                print(f"  *** THIS IS A TECHNICAL AGENT ***")
        
        # Close connection
        db_manager.close_connection()
        logger.info("Database connection closed")
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking technical selector agent: {e}")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = check_technical_selector_agent()
    if success:
        print("\n✓ Technical selector agent check completed successfully")
    else:
        print("\n✗ Technical selector agent check failed")

