#!/usr/bin/env python3
"""
Test script to check agents and strategies in the database
to determine which program and strategy are used by the trend selection agent.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def check_agents_and_strategies():
    """Check agents and strategies in the database"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()

        print("=== Checking Agents ===")
        agents = db_manager.get_agents()
        print(f"Found {len(agents)} agents:")

        trend_selection_agents = []
        for agent in agents:
            agent_name = agent.get('name', 'Unknown')
            print(f"\nAgent ID: {agent.get('_id')}")
            print(f"Agent Name: {agent_name}")
            print(f"Agent Description: {agent.get('description', 'N/A')}")
            print(f"Agent Status: {agent.get('status', 'N/A')}")

            # Check if this is a trend selection agent
            if "趋势" in agent_name or "trend" in agent_name.lower():
                trend_selection_agents.append(agent)
                print("*** This is a trend selection agent ***")

            # Check strategies associated with this agent
            strategies = agent.get('strategies', [])
            if strategies:
                print(f"Associated Strategies: {strategies}")
            else:
                print("No associated strategies")

            # Check program field
            program = agent.get('program', None)
            if program:
                print(f"Program: {program}")
            else:
                print("No program field")

        print("\n=== Checking Strategies ===")
        strategies = db_manager.get_strategies()
        print(f"Found {len(strategies)} strategies:")

        for strategy in strategies:
            strategy_name = strategy.get('name', 'Unknown')
            print(f"\nStrategy ID: {strategy.get('_id')}")
            print(f"Strategy Name: {strategy_name}")
            print(f"Strategy Type: {strategy.get('type', 'N/A')}")
            print(f"Strategy Description: {strategy.get('description', 'N/A')}")

            # Check program field
            program = strategy.get('program', None)
            if program:
                print(f"Program: {program}")
                if isinstance(program, dict):
                    print(f"  File: {program.get('file', 'N/A')}")
                    print(f"  Class: {program.get('class', 'N/A')}")
            else:
                print("No program field")

            # Check file and class_name fields (fallback)
            file_field = strategy.get('file', 'N/A')
            class_name_field = strategy.get('class_name', 'N/A')
            if file_field != 'N/A' or class_name_field != 'N/A':
                print(f"File: {file_field}")
                print(f"Class Name: {class_name_field}")

            # Check parameters
            parameters = strategy.get('parameters', {})
            if parameters:
                print(f"Parameters: {parameters}")
            else:
                print("No parameters")

        # Focus on trend selection agents
        print("\n=== Trend Selection Agents Details ===")
        if trend_selection_agents:
            for agent in trend_selection_agents:
                print(f"\nAgent: {agent.get('name')} (ID: {agent.get('_id')})")

                # Get associated strategies
                strategy_ids = agent.get('strategies', [])
                if strategy_ids:
                    print(f"Associated Strategy IDs: {strategy_ids}")
                    for strategy_id in strategy_ids:
                        strategy = db_manager.get_strategy(strategy_id)
                        if strategy:
                            print(f"  Strategy ID {strategy_id}:")
                            print(f"    Name: {strategy.get('name', 'Unknown')}")

                            # Check program field
                            program = strategy.get('program', None)
                            if program:
                                print(f"    Program: {program}")
                                if isinstance(program, dict):
                                    print(f"      File: {program.get('file', 'N/A')}")
                                    print(f"      Class: {program.get('class', 'N/A')}")
                            else:
                                print("    No program field")

                            # Check file and class_name fields (fallback)
                            file_field = strategy.get('file', 'N/A')
                            class_name_field = strategy.get('class_name', 'N/A')
                            if file_field != 'N/A' or class_name_field != 'N/A':
                                print(f"    File: {file_field}")
                                print(f"    Class Name: {class_name_field}")

                            # Check parameters
                            parameters = strategy.get('parameters', {})
                            if parameters:
                                print(f"    Parameters: {parameters}")
                            else:
                                print("    No parameters")
                        else:
                            print(f"  Strategy ID {strategy_id}: Not found")
                else:
                    print("No associated strategies")
        else:
            print("No trend selection agents found")

        return True

    except Exception as e:
        print(f"Error checking agents and strategies: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            db_manager.close_connection()
        except:
            pass

if __name__ == "__main__":
    success = check_agents_and_strategies()
    if not success:
        sys.exit(1)

