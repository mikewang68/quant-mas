#!/usr/bin/env python3
"""
Script to check pool collection for both technical and weekly selector results
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

def check_all_pool_results():
    """Check all results in pool collection to see what strategies have run"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()
        
        # Get the pool collection
        pool_collection = db_manager.db['pool']
        
        # Get all records sorted by timestamp
        all_records = list(pool_collection.find(
            {}, 
            sort=[("created_at", -1)],
            limit=20
        ))
        
        print(f"Found {len(all_records)} records in pool collection:")
        print("=" * 80)
        
        for i, record in enumerate(all_records):
            print(f"\n--- Record {i+1} ---")
            
            # Basic record info
            record_id = record.get('_id', 'N/A')
            strategy_name = record.get('strategy_name', 'Unknown/Weekly')
            agent_name = record.get('agent_name', 'Unknown')
            count = record.get('count', 0)
            created_at = record.get('created_at', 'N/A')
            
            print(f"ID: {record_id}")
            print(f"Strategy: {strategy_name}")
            print(f"Agent: {agent_name}")
            print(f"Stocks count: {count}")
            
            # Timestamp info
            selection_date = record.get('selection_date', 'N/A')
            selection_timestamp = record.get('selection_timestamp')
            
            if selection_timestamp:
                if hasattr(selection_timestamp, 'strftime'):
                    timestamp_str = selection_timestamp.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    timestamp_str = str(selection_timestamp)
                print(f"Timestamp: {timestamp_str}")
            else:
                print(f"Selection date: {selection_date}")
            
            # Check if this is a weekly selector record (has year/week fields)
            if 'year' in record and 'week' in record:
                print(f"Type: Weekly Selector (Year: {record['year']}, Week: {record['week']})")
            
            # Show some stock details if available
            stocks = record.get('stocks', [])
            if stocks:
                print(f"Sample stocks ({min(3, len(stocks))} of {len(stocks)}):")
                for j, stock in enumerate(stocks[:3]):
                    if isinstance(stock, dict):
                        code = stock.get('code', 'N/A')
                        if 'golden_cross' in stock:
                            print(f"  - {code} (golden_cross: {stock['golden_cross']})")
                        else:
                            reason = stock.get('selection_reason', 'N/A')
                            print(f"  - {code}: {reason[:50]}...")
                    else:
                        print(f"  - {stock}")
        
        # Close connection
        db_manager.close_connection()
        logger.info("Database connection closed")
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking pool results: {e}")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = check_all_pool_results()
    if success:
        print("\n✓ Pool results check completed successfully")
    else:
        print("\n✗ Pool results check failed")

