#!/usr/bin/env python3
"""
Check the actual structure of strategy documents in the database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def check_strategy_documents():
    """Check the actual structure of strategy documents in the database"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()

        # Get all strategies
        strategies = db_manager.get_strategies()
        print(f"Found {len(strategies)} strategies in database")

        # Print structure of each strategy
        for i, strategy in enumerate(strategies):
            print(f"\n--- Strategy {i+1} ---")
            print(f"ID: {strategy.get('_id', 'N/A')}")
            print(f"Name: {strategy.get('name', 'N/A')}")
            print(f"Type: {strategy.get('type', 'N/A')}")
            print(f"Description: {strategy.get('description', 'N/A')}")

            # Check for program field
            if 'program' in strategy:
                print(f"Program: {strategy['program']}")
                if isinstance(strategy['program'], dict):
                    print(f"  Program is dict with keys: {list(strategy['program'].keys())}")
                    for key, value in strategy['program'].items():
                        print(f"    {key}: {value}")
                elif isinstance(strategy['program'], str):
                    print(f"  Program is string: {strategy['program']}")
            else:
                print("No program field")

            # Check for file and class_name fields
            if 'file' in strategy:
                print(f"File: {strategy['file']}")
            if 'class_name' in strategy:
                print(f"Class name: {strategy['class_name']}")

            print(f"Parameters: {strategy.get('parameters', 'N/A')}")

        # Get specific strategy by name
        target_strategy = db_manager.get_strategy_by_name("三均线多头排列策略（基本型）")
        if target_strategy:
            print(f"\n--- Target Strategy: 三均线多头排列策略（基本型） ---")
            print(f"Full document: {target_strategy}")

            # Check program field specifically
            if 'program' in target_strategy:
                print(f"Program field: {target_strategy['program']}")
                if isinstance(target_strategy['program'], dict):
                    print(f"  Program keys: {list(target_strategy['program'].keys())}")
                    for key, value in target_strategy['program'].items():
                        print(f"    {key}: {value}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            db_manager.close_connection()
        except:
            pass

if __name__ == "__main__":
    check_strategy_documents()

