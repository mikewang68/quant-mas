#!/usr/bin/env python3
"""
Script to update the enhanced public opinion analysis strategy with simple LLM configuration
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set Python path to include project root
sys.path.append(str(project_root))

from pymongo import MongoClient
import yaml

def load_mongodb_config():
    """Load MongoDB configuration from config file"""
    config_path = project_root / "config" / "database.yaml"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config.get('mongodb', {})
    else:
        # Default configuration
        return {
            'host': 'localhost',
            'port': 27017,
            'database': 'stock'
        }

def update_enhanced_strategy_simple_llm():
    """Update the enhanced strategy with simple LLM configuration"""
    try:
        # Load MongoDB configuration
        mongo_config = load_mongodb_config()

        # Connect to MongoDB
        client = MongoClient(mongo_config['host'], mongo_config['port'])
        db = client[mongo_config['database']]

        # Update the strategy with simple LLM configuration
        result = db.strategies.update_one(
            {"name": "增强型舆情分析策略"},
            {
                "$set": {
                    "parameters.llm_name": "gemini-2.0-flash"
                },
                "$unset": {
                    "parameters.llm_config": ""
                }
            }
        )

        if result.modified_count > 0:
            print("Successfully updated enhanced strategy with simple LLM configuration")
            print("Removed complex llm_config and added simple llm_name parameter")
        else:
            print("No changes made to the strategy")

        # Verify the update
        strategy = db.strategies.find_one({"name": "增强型舆情分析策略"})
        if strategy:
            parameters = strategy.get('parameters', {})
            print("\nUpdated parameters:")
            for key, value in parameters.items():
                print(f"  {key}: {value}")

        # Close connection
        client.close()

    except Exception as e:
        print(f"Error updating enhanced strategy: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_enhanced_strategy_simple_llm()

