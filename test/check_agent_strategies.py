#!/usr/bin/env python3
"""
Script to check what strategies are configured for the technical selector agent
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_agent_strategies():
    """Check what strategies are configured for the technical selector agent"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()
        
        # Get all agents
        agents = db_manager.get_agents()
        print(f"Found {len(agents)} agents:")
        
        for agent in agents:
            print(f"\n--- Agent: {agent.get('name', 'Unknown')} (ID: {agent.get('_id')}) ---")
            print(f"Description: {agent.get('description', 'N/A')}")
            print(f"Status: {agent.get('status', 'N/A')}")
            
            # Get strategies for this agent
            strategy_ids = agent.get('strategies', [])
            print(f"Configured strategies ({len(strategy_ids)}): {strategy_ids}")
            
            # Get details of each strategy
            for strategy_id in strategy_ids:
                strategy = db_manager.get_strategy(strategy_id)
                if strategy:
                    print(f"  - Strategy: {strategy.get('name', strategy_id)} (ID: {strategy_id})")
                    print(f"    Type: {strategy.get('type', 'N/A')}")
                    print(f"    Description: {strategy.get('description', 'N/A')}")
                    if 'parameters' in strategy:
                        print(f"    Parameters: {strategy['parameters']}")
                else:
                    print(f"  - Strategy ID {strategy_id}: Not found in database")
        
        # Also check all available strategies
        print(f"\n--- All Available Strategies ---")
        all_strategies = db_manager.get_strategies()
        print(f"Total strategies in database: {len(all_strategies)}")
        
        for strategy in all_strategies:
            print(f"  - {strategy.get('name', 'Unknown')} (ID: {strategy.get('_id')}, Type: {strategy.get('type', 'N/A')})")
        
        # Close connection
        db_manager.close_connection()
        logger.info("Database connection closed")
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking agent strategies: {e}")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = check_agent_strategies()
    if success:
        print("\n✓ Agent strategy check completed successfully")
    else:
        print("\n✗ Agent strategy check failed")

