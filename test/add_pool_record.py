#!/usr/bin/env python3
"""
Script to add a record to the pool collection in MongoDB
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.mongodb_manager import MongoDBManager
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_record_to_pool():
    """Add a sample record to the pool collection"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()

        # Get the pool collection
        pool_collection = db_manager.db["pool"]

        # Check current count
        initial_count = pool_collection.count_documents({})
        logger.info(f"Initial documents in pool collection: {initial_count}")
        print(f"Initial documents in pool collection: {initial_count}")

        # Create a sample record to insert
        sample_record = {
            "date": datetime.now(),
            "stocks": ["000001", "000002", "000003"],  # Sample stock codes
            "count": 3,
            "created_at": datetime.now(),
        }

        # Insert the record
        result = pool_collection.insert_one(sample_record)
        logger.info(f"Successfully inserted record with ID: {result.inserted_id}")
        print(f"Successfully inserted record with ID: {result.inserted_id}")

        # Verify the insertion
        final_count = pool_collection.count_documents({})
        logger.info(f"Final documents in pool collection: {final_count}")
        print(f"Final documents in pool collection: {final_count}")

        # Show the inserted record
        inserted_record = pool_collection.find_one({"_id": result.inserted_id})
        if inserted_record:
            print(f"Inserted record: {inserted_record}")

        # Close connection
        db_manager.close_connection()
        logger.info("Database connection closed")
        print("Database connection closed")

        return True

    except Exception as e:
        logger.error(f"Error adding record to pool collection: {e}")
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    success = add_record_to_pool()
    if success:
        print("Record successfully added to pool collection")
    else:
        print("Failed to add record to pool collection")
