#!/usr/bin/env python3
"""
Save VWAP Turnover Strategy to MongoDB database
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data.mongodb_manager import MongoDBManager

def save_vwap_turnover_strategy():
    """Save VWAP Turnover Strategy to database"""

    # Initialize database manager
    db_manager = MongoDBManager()

    try:
        # Define strategy parameters
        strategy_data = {
            "name": "均线价格加速换手率过滤策略",
            "type": "technical",
            "description": "利用短期成交量加权平均价格(VWAP)的价格加速特性，结合换手率过滤来识别具有上涨动力且流动性适中的股票。当短期VWAP高于中期VWAP且短期VWAP呈上升趋势时，如果换手率在合理范围内(5-25%)，则产生买入信号。",
            "parameters": {
                "short_period": 5,
                "mid_period": 13,
                "min_turnover": 5.0,
                "max_turnover": 25.0
            },
            "program": {
                "file": "vmap_turnover_strategy.py",
                "class": "VMAPTurnoverStrategy"
            }
        }

        # Check if strategy already exists
        existing_strategy = db_manager.strategies_collection.find_one({
            "name": strategy_data["name"]
        })

        if existing_strategy:
            print(f"Strategy '{strategy_data['name']}' already exists with ID: {existing_strategy['_id']}")
            # Update the existing strategy
            result = db_manager.strategies_collection.update_one(
                {"_id": existing_strategy["_id"]},
                {"$set": strategy_data}
            )
            if result.modified_count > 0:
                print("Strategy updated successfully")
            else:
                print("No changes made to existing strategy")
        else:
            # Insert new strategy
            result = db_manager.strategies_collection.insert_one(strategy_data)
            print(f"Strategy saved successfully with ID: {result.inserted_id}")

    except Exception as e:
        print(f"Error saving strategy: {e}")
        return False
    finally:
        # Close database connection
        db_manager.close_connection()

    return True

if __name__ == "__main__":
    success = save_vwap_turnover_strategy()
    if success:
        print("VWAP Turnover Strategy saved to database successfully")
        sys.exit(0)
    else:
        print("Failed to save VWAP Turnover Strategy to database")
        sys.exit(1)

