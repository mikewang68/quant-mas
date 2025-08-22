#!/usr/bin/env python3
"""
Check the structure of strategy documents in the database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def check_strategy_structure():
    """Check the structure of strategy documents"""
    try:
        # Initialize MongoDB manager
        manager = MongoDBManager()

        # Get all strategies
        strategies = manager.get_strategies()
        print(f"Found {len(strategies)} strategies")

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

            # Check for file and class_name fields
            if 'file' in strategy:
                print(f"File: {strategy['file']}")
            if 'class_name' in strategy:
                print(f"Class name: {strategy['class_name']}")

            print(f"Parameters: {strategy.get('parameters', 'N/A')}")

        # Get specific strategy by name
        target_strategy = manager.get_strategy_by_name("三均线多头排列策略（基本型）")
        if target_strategy:
            print(f"\n--- Target Strategy: 三均线多头排列策略（基本型） ---")
            print(f"Full document: {target_strategy}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            manager.close_connection()
        except:
            pass

if __name__ == "__main__":
    check_strategy_structure()

