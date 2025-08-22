#!/usr/bin/env python3
"""
Check existing strategies in the database to see if they have program fields.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.mongodb_manager import MongoDBManager

def check_strategies():
    """Check strategies in database"""
    try:
        # Initialize MongoDB manager
        mongo_manager = MongoDBManager()
        
        # Get all strategies
        strategies = mongo_manager.get_strategies()
        print("Existing strategies in database:")
        print(f"Total strategies: {len(strategies)}")
        
        for i, strategy in enumerate(strategies):
            print(f"\nStrategy {i+1}:")
            print(f"  ID: {strategy.get('_id', 'N/A')}")
            print(f"  Name: {strategy.get('name', 'N/A')}")
            print(f"  Type: {strategy.get('type', 'N/A')}")
            print(f"  Description: {strategy.get('description', 'N/A')}")
            print(f"  Program: {strategy.get('program', 'N/A')}")
            print(f"  Parameters: {strategy.get('parameters', 'N/A')}")
        
        # Get specific strategy by ID to check full details
        if strategies:
            first_strategy_id = strategies[0]['_id']
            full_strategy = mongo_manager.get_strategy(first_strategy_id)
            print(f"\nFull details of first strategy (ID: {first_strategy_id}):")
            for key, value in full_strategy.items():
                print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_strategies()

