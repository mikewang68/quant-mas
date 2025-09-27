#!/usr/bin/env python3
"""
Script to check the enhanced public opinion analysis strategy in the MongoDB database
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

def check_enhanced_strategy():
    """Check the enhanced public opinion analysis strategy in the database"""
    try:
        # Load MongoDB configuration
        mongo_config = load_mongodb_config()

        # Connect to MongoDB
        client = MongoClient(mongo_config['host'], mongo_config['port'])
        db = client[mongo_config['database']]

        # Find the enhanced public opinion strategy
        strategy = db.strategies.find_one({"name": "增强型舆情分析策略"})

        if strategy:
            print("Enhanced Public Opinion Analysis Strategy found in database:")
            print(f"  ID: {strategy.get('_id')}")
            print(f"  Name: {strategy.get('name')}")
            print(f"  Type: {strategy.get('type')}")
            print(f"  Description: {strategy.get('description')}")

            # Check parameters
            parameters = strategy.get('parameters', {})
            print(f"  Parameters:")
            for key, value in parameters.items():
                print(f"    {key}: {value}")

            # Check program info
            program = strategy.get('program', {})
            print(f"  Program:")
            print(f"    File: {program.get('file')}")
            print(f"    Class: {program.get('class')}")

        else:
            print("Enhanced Public Opinion Analysis Strategy not found in database")

        # Close connection
        client.close()

    except Exception as e:
        print(f"Error checking enhanced strategy: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_enhanced_strategy()

