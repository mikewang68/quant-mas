#!/usr/bin/env python3
"""
Test script to check the agent and its associated strategies in detail
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def check_agent_details():
    """Check detailed information about the trend selection agent"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()

        print("=== Checking Trend Selection Agent Details ===")
        agents = db_manager.get_agents()

        trend_agent = None
        for agent in agents:
            agent_name = agent.get('name', '')
            if "趋势选股" in agent_name:
                trend_agent = agent
                break

        if not trend_agent:
            print("Trend selection agent not found!")
            return False

        print(f"Agent ID: {trend_agent.get('_id')}")
        print(f"Agent Name: {trend_agent.get('name')}")
        print(f"Agent Description: {trend_agent.get('description')}")
        print(f"Agent Program: {trend_agent.get('program')}")

        # Check associated strategies
        strategy_ids = trend_agent.get('strategies', [])
        print(f"Associated Strategy IDs: {strategy_ids}")

        if not strategy_ids:
            print("No strategies associated with this agent!")
            return False

        # Get detailed strategy information
        print("\n=== Associated Strategies Details ===")
        for strategy_id in strategy_ids:
            strategy = db_manager.get_strategy(strategy_id)
            if strategy:
                print(f"\nStrategy ID: {strategy.get('_id')}")
                print(f"Strategy Name: {strategy.get('name')}")
                print(f"Strategy Type: {strategy.get('type')}")
                print(f"Strategy Description: {strategy.get('description')}")

                # Check program field
                program = strategy.get('program', None)
                if program:
                    print(f"Program: {program}")
                    if isinstance(program, dict):
                        print(f"  File: {program.get('file', 'N/A')}")
                        print(f"  Class: {program.get('class', 'N/A')}")
                else:
                    print("No program field")

                # Check parameters
                parameters = strategy.get('parameters', {})
                print(f"Parameters: {parameters}")
            else:
                print(f"Strategy ID {strategy_id}: Not found!")

        return True

    except Exception as e:
        print(f"Error checking agent details: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            db_manager.close_connection()
        except:
            pass

if __name__ == "__main__":
    success = check_agent_details()
    if not success:
        sys.exit(1)

