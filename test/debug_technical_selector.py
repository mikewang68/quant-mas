#!/usr/bin/env python3
"""
Debug technical selector to see exactly which strategies it runs
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.technical_selector import TechnicalStockSelector
import logging

# Configure logging to show debug info
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def debug_technical_selector():
    """Debug technical selector to see exactly which strategies it runs"""
    print("Debugging Technical Stock Selector...")

    # Initialize components
    db_manager = MongoDBManager()
    data_fetcher = AkshareClient()

    # Initialize selector
    selector = TechnicalStockSelector(db_manager, data_fetcher)

    # Get the technical analysis agent
    agent = db_manager.get_agent("68993413e3032fe19a7b41ae")
    if not agent:
        print("Error: Technical Analysis Agent not found")
        return 1

    print(f"Agent ID: {agent.get('_id')}")
    print(f"Agent Name: {agent.get('name')}")

    strategy_ids = agent.get("strategies", [])
    print(f"Found {len(strategy_ids)} strategies configured for agent:")
    for i, strategy_id in enumerate(strategy_ids):
        strategy = db_manager.get_strategy(strategy_id)
        if strategy:
            print(
                f"  {i + 1}. {strategy.get('name', strategy_id)} ({strategy_id}) - Type: {strategy.get('type')}"
            )
        else:
            print(f"  {i + 1}. {strategy_id} (Strategy not found in database)")

    # Run selector with debug info
    try:
        # Use today's date for selection
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"\nRunning strategies for date: {today}")

        # Run with the actual agent ID
        results = selector.run("68993413e3032fe19a7b41ae", today)

        print("\nExecution Results:")
        print(f"Agent ID: {results.get('agent_id')}")
        print(f"Agent Name: {results.get('agent_name')}")
        print(f"Strategies executed: {results.get('strategies_executed', 0)}")
        print(f"Last data date: {results.get('last_data_date', 'N/A')}")

        # Print individual strategy results
        strategy_results = results.get("results", {})
        print(f"\nDetailed strategy results ({len(strategy_results)} strategies):")
        for strategy_id, result in strategy_results.items():
            strategy = db_manager.get_strategy(strategy_id)
            strategy_name = (
                strategy.get("name", strategy_id) if strategy else strategy_id
            )

            if result.get("success", False):
                print(f"  {strategy_name}:")
                print(f"    Success: True")
                print(f"    Stocks selected: {result.get('count', 0)}")
                print(f"    Details: {result.get('details', {})}")
            else:
                print(f"  {strategy_name}:")
                print(f"    Success: False")
                print(f"    Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"Error running technical selector: {e}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        # Close database connection
        db_manager.close_connection()

    print("\nDebug completed!")
    return 0


if __name__ == "__main__":
    sys.exit(debug_technical_selector())
