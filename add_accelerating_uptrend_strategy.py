#!/usr/bin/env python3
"""
Script to add the Accelerating Uptrend Strategy to the strategies collection in MongoDB
"""

import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.mongodb_manager import MongoDBManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_accelerating_uptrend_strategy():
    """Add the Accelerating Uptrend Strategy to the strategies collection"""
    db_manager = None
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()
        
        # Define the new strategy
        strategy_data = {
            "name": "加速上涨策略",
            "type": "technical",
            "description": "通过计算股价上涨角度并检测角度加速来识别具有强劲上涨动力的股票。当股价上涨角度超过阈值且在加速时产生买入信号。",
            "parameters": {
                "angle_threshold": 30,
                "lookback_period": 20,
                "volume_ratio_threshold": 1.2,
                "acceleration_window": 2
            },
            "program": "accelerating_uptrend_strategy.py"
        }
        
        # Check if strategy already exists
        existing_strategy = db_manager.strategies_collection.find_one({"name": strategy_data["name"]})
        
        if existing_strategy:
            logger.info(f"Strategy '{strategy_data['name']}' already exists. Updating...")
            # Update existing strategy
            result = db_manager.strategies_collection.update_one(
                {"name": strategy_data["name"]},
                {"$set": strategy_data}
            )
            if result.modified_count > 0:
                logger.info(f"Successfully updated strategy '{strategy_data['name']}'")
            else:
                logger.info(f"No changes made to strategy '{strategy_data['name']}'")
        else:
            # Insert new strategy
            result = db_manager.strategies_collection.insert_one(strategy_data)
            logger.info(f"Successfully inserted strategy '{strategy_data['name']}' with ID: {result.inserted_id}")
        
        # Verify the strategy was added/updated
        updated_strategy = db_manager.strategies_collection.find_one({"name": strategy_data["name"]})
        if updated_strategy:
            logger.info("Strategy details:")
            logger.info(f"  Name: {updated_strategy['name']}")
            logger.info(f"  Type: {updated_strategy['type']}")
            logger.info(f"  Description: {updated_strategy['description']}")
            logger.info(f"  Program: {updated_strategy['program']}")
            logger.info("  Parameters:")
            for param, value in updated_strategy['parameters'].items():
                logger.info(f"    {param}: {value}")
        else:
            logger.error("Failed to verify strategy insertion/update")
            
        return True
        
    except Exception as e:
        logger.error(f"Error adding strategy to database: {e}")
        return False
    finally:
        # Close connection
        if db_manager:
            db_manager.close_connection()

if __name__ == "__main__":
    add_accelerating_uptrend_strategy()

