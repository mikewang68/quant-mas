#!/usr/bin/env python3
"""
Script to check the specific technical analysis agent and all its strategies
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_technical_analysis_agent():
    """Check the technical analysis agent and all its strategies"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()
        
        # Find the technical analysis agent
        agents = db_manager.get_agents()
        technical_agent = None
        
        print("Searching for technical analysis agent...")
        for agent in agents:
            agent_name = agent.get('name', '')
            if "技术分析" in agent_name:
                technical_agent = agent
                print(f"Found technical analysis agent: {agent_name}")
                break
        
        if not technical_agent:
            print("Technical analysis agent not found!")
            return False
            
        print(f"\n=== Technical Analysis Agent ===")
        print(f"Agent Name: {technical_agent.get('name')}")
        print(f"Agent ID: {technical_agent.get('_id')}")
        print(f"Description: {technical_agent.get('description', 'N/A')}")
        print(f"Status: {technical_agent.get('status', 'N/A')}")
        
        strategy_ids = technical_agent.get('strategies', [])
        print(f"\nConfigured strategies ({len(strategy_ids)}):")
        
        all_strategy_details = []
        for strategy_id in strategy_ids:
            strategy = db_manager.get_strategy(strategy_id)
            if strategy:
                strategy_name = strategy.get('name', strategy_id)
                strategy_type = strategy.get('type', 'N/A')
                strategy_description = strategy.get('description', 'N/A')
                strategy_params = strategy.get('parameters', {})
                
                print(f"  - Strategy: {strategy_name}")
                print(f"    ID: {strategy_id}")
                print(f"    Type: {strategy_type}")
                print(f"    Description: {strategy_description}")
                print(f"    Parameters: {strategy_params}")
                
                all_strategy_details.append({
                    'name': strategy_name,
                    'id': strategy_id,
                    'type': strategy_type,
                    'description': strategy_description,
                    'parameters': strategy_params
                })
            else:
                print(f"  - Strategy ID {strategy_id}: NOT FOUND")
        
        # Close connection
        db_manager.close_connection()
        logger.info("Database connection closed")
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking technical analysis agent: {e}")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = check_technical_analysis_agent()
    if success:
        print("\n✓ Technical analysis agent check completed successfully")
    else:
        print("\n✗ Technical analysis agent check failed")

