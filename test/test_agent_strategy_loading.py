#!/usr/bin/env python3
"""
Test script to verify that the fundamental selector agent loads strategies from the database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.fundamental_selector import FundamentalSelector

def test_agent_strategy_loading():
    """Test that the fundamental selector agent loads strategies from database."""
    print("Testing fundamental selector agent strategy loading from database...")

    try:
        # Create fundamental selector agent
        agent = FundamentalSelector()

        # Check if strategies were loaded
        if not hasattr(agent, 'strategy_params_list') or not agent.strategy_params_list:
            print("ERROR: No strategies loaded by fundamental selector agent")
            return False

        print(f"Number of strategies loaded: {len(agent.strategy_params_list)}")
        print(f"Strategy names: {getattr(agent, 'strategy_names', 'N/A')}")

        # Check strategy parameters
        for i, params in enumerate(agent.strategy_params_list):
            print(f"\nStrategy {i+1} parameters: {params}")

            # Verify that parameters are dictionaries (from database)
            if not isinstance(params, dict):
                print(f"ERROR: Strategy {i+1} parameters are not a dictionary")
                return False

        print("\n✓ Fundamental selector agent correctly loads strategies from database")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_agent_strategy_loading()
    if success:
        print("\n🎉 Test passed: Fundamental selector agent loads strategies from database")
    else:
        print("\n❌ Test failed: Fundamental selector agent does not load strategies from database")
        sys.exit(1)

