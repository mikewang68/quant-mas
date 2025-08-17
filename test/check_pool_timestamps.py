#!/usr/bin/env python3
"""
Script to check if pool records include timestamps
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

def check_pool_timestamps():
    """Check if pool records include timestamps"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()
        
        # Get the pool collection
        pool_collection = db_manager.db['pool']
        
        # Find recent records
        recent_records = list(pool_collection.find(
            {},  # No filter
            sort=[('created_at', -1)],  # Sort by creation time descending
            limit=5
        ))
        
        print(f"Found {len(recent_records)} recent pool records:")
        
        for i, record in enumerate(recent_records):
            print(f"\n--- Record {i+1} ---")
            print(f"ID: {record.get('_id', 'N/A')}")
            print(f"Strategy: {record.get('strategy_name', 'N/A')}")
            print(f"Agent: {record.get('agent_name', 'N/A')}")
            print(f"Stocks count: {record.get('count', 0)}")
            
            # Check for timestamp fields
            selection_date = record.get('selection_date')
            selection_timestamp = record.get('selection_timestamp')
            created_at = record.get('created_at')
            updated_at = record.get('updated_at')
            
            print(f"Selection date: {selection_date}")
            print(f"Selection timestamp: {selection_timestamp}")
            print(f"Created at: {created_at}")
            print(f"Updated at: {updated_at}")
            
            # Check if timestamps include time information
            if selection_timestamp:
                if isinstance(selection_timestamp, datetime):
                    has_time = selection_timestamp.hour > 0 or selection_timestamp.minute > 0 or selection_timestamp.second > 0
                    print(f"Selection timestamp includes time: {has_time}")
                else:
                    print(f"Selection timestamp type: {type(selection_timestamp)}")
        
        # Close connection
        db_manager.close_connection()
        logger.info("Database connection closed")
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking pool timestamps: {e}")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = check_pool_timestamps()
    if success:
        print("\n✓ Timestamp check completed successfully")
    else:
        print("\n✗ Timestamp check failed")

