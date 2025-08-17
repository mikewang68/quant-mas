#!/usr/bin/env python3
"""
Script to check the specific configuration of trend selector and technical selector agents
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_specific_agents():
    """Check the specific configuration of trend and technical selector agents"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()
        
        # Get all agents
        agents = db_manager.get_agents()
        
        print("=== 趋势选股Agent ===")
        trend_agents = [agent for agent in agents if '趋势选股' in agent.get('name', '')]
        for agent in trend_agents:
            print(f"Agent Name: {agent.get('name')}")
            print(f"Agent ID: {agent.get('_id')}")
            print(f"Description: {agent.get('description', 'N/A')}")
            
            strategy_ids = agent.get('strategies', [])
            print(f"Configured strategies ({len(strategy_ids)}): {strategy_ids}")
            
            for strategy_id in strategy_ids:
                strategy = db_manager.get_strategy(strategy_id)
                if strategy:
                    print(f"  - Strategy: {strategy.get('name', strategy_id)}")
                    print(f"    ID: {strategy_id}")
                    print(f"    Type: {strategy.get('type', 'N/A')}")
                    print(f"    Description: {strategy.get('description', 'N/A')}")
                    if 'parameters' in strategy:
                        print(f"    Parameters: {strategy['parameters']}")
        
        print("\n=== 技术选股Agent ===")
        tech_agents = [agent for agent in agents if '技术选股' in agent.get('name', '')]
        for agent in tech_agents:
            print(f"Agent Name: {agent.get('name')}")
            print(f"Agent ID: {agent.get('_id')}")
            print(f"Description: {agent.get('description', 'N/A')}")
            
            strategy_ids = agent.get('strategies', [])
            print(f"Configured strategies ({len(strategy_ids)}): {strategy_ids}")
            
            for strategy_id in strategy_ids:
                strategy = db_manager.get_strategy(strategy_id)
                if strategy:
                    print(f"  - Strategy: {strategy.get('name', strategy_id)}")
                    print(f"    ID: {strategy_id}")
                    print(f"    Type: {strategy.get('type', 'N/A')}")
                    print(f"    Description: {strategy.get('description', 'N/A')}")
                    if 'parameters' in strategy:
                        print(f"    Parameters: {strategy['parameters']}")
        
        # Close connection
        db_manager.close_connection()
        logger.info("Database connection closed")
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking specific agents: {e}")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = check_specific_agents()
    if success:
        print("\n✓ Specific agent check completed successfully")
    else:
        print("\n✗ Specific agent check failed")

