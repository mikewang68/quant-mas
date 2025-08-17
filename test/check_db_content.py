#!/usr/bin/env python3
"""
Script to check the database contents for agents and strategies
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pymongo import MongoClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_database():
    """Check database contents"""
    try:
        # MongoDB connection details
        host = "192.168.1.2"
        port = 27017
        database_name = "stock"
        username = "stock"
        password = "681123"
        auth_database = "admin"

        # Create connection URI
        uri = f"mongodb://{username}:{password}@{host}:{port}/{database_name}?authSource={auth_database}"

        # Connect to MongoDB
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)

        # Test connection
        client.admin.command("ping")
        logger.info("Successfully connected to MongoDB")

        # Get database
        db = client[database_name]

        # Check agents collection
        agents_collection = db["agents"]
        agents = list(
            agents_collection.find(
                {},
                {"_id": 1, "name": 1, "description": 1, "status": 1, "strategies": 1},
            )
        )

        print("=== Agents in database ===")
        for agent in agents:
            print(f"  - ID: {agent.get('_id')}")
            print(f"    Name: {agent.get('name')}")
            print(f"    Description: {agent.get('description')}")
            print(f"    Status: {agent.get('status')}")
            print(f"    Strategies: {agent.get('strategies', [])}")
            print()

        # Check strategies collection
        strategies_collection = db["strategies"]
        strategies = list(
            strategies_collection.find(
                {}, {"_id": 1, "name": 1, "type": 1, "description": 1, "parameters": 1}
            )
        )

        print("=== Strategies in database ===")
        for strategy in strategies:
            print(f"  - ID: {strategy.get('_id')}")
            print(f"    Name: {strategy.get('name')}")
            print(f"    Type: {strategy.get('type')}")
            print(f"    Description: {strategy.get('description')}")
            print(f"    Parameters: {strategy.get('parameters', {})}")
            print()

        # Check pool collection
        pool_collection = db["pool"]
        pool_count = pool_collection.count_documents({})
        print(f"=== Pool collection ===")
        print(f"Number of documents in pool: {pool_count}")

        # Close connection
        client.close()
        logger.info("Database check completed")

    except Exception as e:
        logger.error(f"Error checking database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    check_database()
