#!/usr/bin/env python3
"""
Script to check the structure of strategies in the MongoDB database
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from data.mongodb_manager import MongoDBManager

def check_strategies_structure():
    """Check the structure of strategies in the database"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()

        # Get all strategies
        strategies = db_manager.get_strategies()

        print(f"Found {len(strategies)} strategies in the database")
        print("=" * 50)

        # Examine each strategy
        for i, strategy in enumerate(strategies):
            print(f"\nStrategy {i+1}:")
            print(f"  ID: {strategy.get('_id', 'N/A')}")
            print(f"  Name: {strategy.get('name', 'N/A')}")
            print(f"  Type: {strategy.get('type', 'N/A')}")

            # Check program field
            if 'program' in strategy:
                program = strategy['program']
                print(f"  Program field: {program} (type: {type(program)})")
                if isinstance(program, dict):
                    print(f"    File: {program.get('file', 'N/A')}")
                    print(f"    Class: {program.get('class', 'N/A')}")

            # Check file and class_name fields
            if 'file' in strategy:
                print(f"  File field: {strategy['file']}")
            if 'class_name' in strategy:
                print(f"  Class name field: {strategy['class_name']}")

            # Check parameters
            if 'parameters' in strategy:
                print(f"  Parameters: {strategy['parameters']}")

        # Close connection
        db_manager.close_connection()

    except Exception as e:
        print(f"Error checking strategies: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_strategies_structure()

