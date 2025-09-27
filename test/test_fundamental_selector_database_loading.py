#!/usr/bin/env python3
"""
Test script to verify that the fundamental selector agent loads strategies from the database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.fundamental_selector import FundamentalSelector
from data.mongodb_manager import MongoDBManager

def test_fundamental_selector_strategy_loading():
    """Test that the fundamental selector loads strategies from the database."""
    print("Testing fundamental selector strategy loading from database...")

    # Initialize MongoDB manager
    mongodb_manager = MongoDBManager()

    try:
        # Get the fundamental analysis agent from database
        agent = mongodb_manager.agents_collection.find_one(
            {"name": "基本面分析Agent"}
        )

        if not agent:
            print("ERROR: Fundamental analysis agent not found in database")
            return False

        print(f"Agent name: {agent.get('name')}")
        strategy_ids = agent.get("strategies", [])
        print(f"Strategy IDs assigned to agent: {strategy_ids}")

        # Get strategy details from database
        from bson import ObjectId
        strategies = []
        for strategy_id in strategy_ids:
            strategy = mongodb_manager.strategies_collection.find_one(
                {"_id": ObjectId(strategy_id)}
            )
            if strategy:
                strategies.append(strategy)
                print(f"Strategy loaded: {strategy.get('name')} with parameters: {strategy.get('parameters', {})}")

        # Test fundamental selector loading
        print("\nTesting FundamentalSelector agent...")
        selector = FundamentalSelector()

        # Check if strategies were loaded
        if hasattr(selector, 'strategy_names') and hasattr(selector, 'strategy_params_list'):
            print(f"Loaded strategy names: {getattr(selector, 'strategy_names', [])}")
            print(f"Loaded strategy parameters: {getattr(selector, 'strategy_params_list', [])}")

            # Verify that parameters match database values
            if len(strategies) == len(selector.strategy_params_list):
                print("✓ Number of strategies matches database")
                match = True
                for i, (db_strategy, loaded_params) in enumerate(zip(strategies, selector.strategy_params_list)):
                    db_params = db_strategy.get('parameters', {})
                    if db_params != loaded_params:
                        print(f"✗ Strategy {i} parameters don't match: DB={db_params}, Loaded={loaded_params}")
                        match = False
                if match:
                    print("✓ All strategy parameters match database values")
                    return True
            else:
                print(f"✗ Number of strategies doesn't match: DB={len(strategies)}, Loaded={len(selector.strategy_params_list)}")
                return False
        else:
            print("✗ FundamentalSelector doesn't have strategy loading attributes")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        # Close MongoDB connection
        mongodb_manager.close_connection()

if __name__ == "__main__":
    success = test_fundamental_selector_strategy_loading()
    if success:
        print("\n🎉 Test passed: Fundamental selector correctly loads strategies from database")
    else:
        print("\n❌ Test failed: Fundamental selector is not correctly loading strategies from database")
        sys.exit(1)

