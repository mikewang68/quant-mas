#!/usr/bin/env python3
"""
Script to check what strategies are actually present in the pool collection
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_pool_strategies():
    """Check what strategies are actually present in the pool collection"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()
        
        # Get the pool collection
        pool_collection = db_manager.db['pool']
        
        # Get all unique strategy names from pool
        strategy_names = pool_collection.distinct('strategy_name')
        print(f"Found {len(strategy_names)} unique strategies in pool:")
        for name in strategy_names:
            print(f"  - {name}")
        
        # Get count of records by strategy
        print("\nRecord count by strategy:")
        pipeline = [
            {"$group": {"_id": "$strategy_name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        strategy_counts = list(pool_collection.aggregate(pipeline))
        for item in strategy_counts:
            print(f"  - {item['_id']}: {item['count']} records")
        
        # Get recent records to see what's been running
        print("\nMost recent 10 records in pool:")
        recent_records = list(pool_collection.find(
            {}, 
            {"strategy_name": 1, "agent_name": 1, "selection_date": 1, "selection_timestamp": 1, "count": 1},
            sort=[("selection_timestamp", -1)],
            limit=10
        ))
        
        for record in recent_records:
            timestamp = record.get('selection_timestamp', 'N/A')
            if hasattr(timestamp, 'strftime'):
                timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            else:
                timestamp_str = str(timestamp)
                
            print(f"  - {record.get('strategy_name', 'Unknown')} by {record.get('agent_name', 'Unknown')} "
                  f"({record.get('count', 0)} stocks) at {timestamp_str}")
        
        # Close connection
        db_manager.close_connection()
        logger.info("Database connection closed")
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking pool strategies: {e}")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = check_pool_strategies()
    if success:
        print("\n✓ Pool strategy check completed successfully")
    else:
        print("\n✗ Pool strategy check failed")

