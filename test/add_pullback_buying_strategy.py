#!/usr/bin/env python3
"""
Script to add the Pullback Buying Strategy to the strategies collection in MongoDB
"""

import sys
import os
import logging

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data.mongodb_manager import MongoDBManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_pullback_buying_strategy():
    """Add the Pullback Buying Strategy to the strategies collection"""
    db_manager = None
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()

        # Define the new strategy
        strategy_data = {
            "name": "回踩低吸型策略",
            "type": "technical",
            "description": "在长期趋势向上的背景下，寻找价格有效回踩重要支撑位的机会进行低吸买入。通过趋势、超卖和支撑三重确认，在相对低位布局。",
            "parameters": {
                "ma_period": 13,
                "kdj_n": 9,
                "rsi_period": 14,
                "oversold_threshold": 30,
                "support_band_pct": 0.03
            },
            "program": {
                "file": "pullback_buying_strategy",
                "class": "PullbackBuyingStrategy"
            }
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
    add_pullback_buying_strategy()

