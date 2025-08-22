#!/usr/bin/env python3
"""
Test to check if a specific strategy can be found in the database
"""

import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from bson import ObjectId

def check_strategy_exists(strategy_id):
    """Check if a strategy exists in the database"""
    print(f"Checking if strategy {strategy_id} exists in database...")

    try:
        # Initialize database manager
        db_manager = MongoDBManager()
        print("✓ Database connection established")

        # Try to get the strategy directly
        strategy = db_manager.strategies_collection.find_one({"_id": ObjectId(strategy_id)})

        if strategy:
            print(f"✓ Strategy found:")
            print(f"  Name: {strategy.get('name', 'N/A')}")
            print(f"  Type: {strategy.get('type', 'N/A')}")
            print(f"  Description: {strategy.get('description', 'N/A')}")
            print(f"  Program: {strategy.get('program', 'N/A')}")
            if 'parameters' in strategy:
                print(f"  Parameters: {strategy['parameters']}")
        else:
            print(f"✗ Strategy with ID {strategy_id} not found")

            # List all strategies to see what's available
            print("\nListing all strategies in database:")
            all_strategies = list(db_manager.strategies_collection.find())
            print(f"Found {len(all_strategies)} strategies:")
            for i, strat in enumerate(all_strategies):
                print(f"  {i+1}. ID: {strat.get('_id')}, Name: {strat.get('name', 'N/A')}")

        db_manager.close_connection()
        print("\n✓ Database connection closed")
        return strategy is not None

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    strategy_id = "689ff023b05905912308aa05"
    success = check_strategy_exists(strategy_id)
    sys.exit(0 if success else 1)

