#!/usr/bin/env python3
"""
Script to insert fundamental strategies into MongoDB database.
"""

import sys
import os
import json
import logging

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_strategy_config(config_file):
    """Load strategy configuration from JSON file."""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                  'strategies', 'config', config_file)
        with open(config_path, 'r', encoding='utf-8') as f:
            strategy_config = json.load(f)
        logger.info(f"Loaded strategy configuration from {config_file}")
        return strategy_config
    except Exception as e:
        logger.error(f"Error loading strategy configuration from {config_file}: {e}")
        return None

def insert_strategy_to_mongodb(strategy_config):
    """Insert strategy information into MongoDB."""
    try:
        # Initialize MongoDB manager
        mongodb_manager = MongoDBManager()

        # Check if strategy already exists by name
        existing_strategy = mongodb_manager.get_strategy_by_name(strategy_config['name'])
        if existing_strategy:
            logger.info(f"Strategy '{strategy_config['name']}' already exists in database with ID: {existing_strategy['_id']}")
            logger.info("Updating existing strategy...")
            # Update existing strategy
            strategy_id = existing_strategy['_id']
            # Remove _id from config for update
            strategy_config.pop('_id', None)
            result = mongodb_manager.update_strategy(strategy_id, strategy_config)
            if result:
                logger.info(f"Updated existing strategy: {strategy_config['name']}")
            else:
                logger.error(f"Failed to update strategy: {strategy_config['name']}")
        else:
            # Insert new strategy
            result = mongodb_manager.create_strategy(strategy_config)
            if result:
                logger.info(f"Inserted new strategy: {strategy_config['name']} with ID: {result}")
            else:
                logger.error(f"Failed to insert strategy: {strategy_config['name']}")

        # Close MongoDB connection
        mongodb_manager.close_connection()
        return True

    except Exception as e:
        logger.error(f"Error inserting strategy to MongoDB: {e}")
        return False

def main():
    """Main function to load and insert strategy information."""
    logger.info("Starting fundamental strategies insertion process")

    try:
        # Load fundamental strategy configuration
        fundamental_config = load_strategy_config('fundamental_strategy_config.json')
        if not fundamental_config:
            logger.error("Failed to load fundamental strategy configuration")
            return False

        # Load LLM fundamental strategy configuration
        llm_fundamental_config = load_strategy_config('llm_fundamental_strategy_config.json')
        if not llm_fundamental_config:
            logger.error("Failed to load LLM fundamental strategy configuration")
            return False

        # Insert strategies into MongoDB
        success1 = insert_strategy_to_mongodb(fundamental_config)
        success2 = insert_strategy_to_mongodb(llm_fundamental_config)

        if success1 and success2:
            logger.info("Successfully processed fundamental strategies in MongoDB")
            print("Successfully processed fundamental strategies in MongoDB")
            return True
        else:
            logger.error("Failed to process one or more fundamental strategies in MongoDB")
            print("Failed to process one or more fundamental strategies in MongoDB")
            return False

    except Exception as e:
        logger.error(f"Error in main process: {e}")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    main()

