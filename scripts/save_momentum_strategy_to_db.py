#!/usr/bin/env python3
"""
Script to save momentum strategy information to the database
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data.mongodb_manager import MongoDBManager

def save_momentum_strategy():
    """Save momentum strategy information to the database"""

    # Initialize MongoDB manager
    db_manager = MongoDBManager()

    # Prepare strategy information
    strategy_info = {
        "name": "动量策略",
        "type": "technical",
        "description": "基于动量指标选择股票的策略，当动量值超过阈值时产生买入信号，当动量值低于阈值时产生卖出信号。",
        "parameters": {
            "period": 14,
            "threshold": 0,
            "lookback_period": 20
        },
        "file": "strategies/momentum_strategy.py",
        "class_name": "MomentumStrategy",
        "program": "momentum_strategy"
    }

    try:
        # Check if strategy already exists
        existing_strategy = db_manager.get_strategy_by_name("动量策略")

        if existing_strategy:
            print(f"Strategy '动量策略' already exists with ID: {existing_strategy['_id']}")
            print("Updating strategy information...")

            # Update existing strategy
            strategy_id = existing_strategy['_id']
            update_result = db_manager.update_strategy(strategy_id, strategy_info)

            if update_result:
                print("Strategy updated successfully")
            else:
                print("Failed to update strategy")
        else:
            print("Creating new strategy...")

            # Create new strategy
            strategy_id = db_manager.create_strategy(strategy_info)

            if strategy_id:
                print(f"Strategy created successfully with ID: {strategy_id}")
            else:
                print("Failed to create strategy")

    except Exception as e:
        print(f"Error saving strategy to database: {e}")
    finally:
        # Close database connection
        db_manager.close_connection()

if __name__ == "__main__":
    save_momentum_strategy()

