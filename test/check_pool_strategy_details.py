#!/usr/bin/env python3
"""
Check detailed strategy information in pool records
"""

import sys
import os
import logging

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from data.mongodb_manager import MongoDBManager

def check_pool_strategy_details():
    """Check detailed strategy information in pool records"""
    print("Checking detailed strategy information in pool records...")
    
    try:
        # Initialize database manager
        db_manager = MongoDBManager()
        pool_collection = db_manager.db['pool']
        
        # Get all records sorted by selection date
        records = list(pool_collection.find().sort('selection_date', -1))
        
        print(f"Found {len(records)} total records in pool:")
        
        for i, record in enumerate(records):
            print(f"\n--- Record {i+1} ---")
            print(f"ID: {record.get('_id', 'N/A')}")
            print(f"Agent: {record.get('agent_name', 'N/A')} ({record.get('agent_id', 'N/A')})")
            print(f"Strategy: {record.get('strategy_name', 'N/A')} ({record.get('strategy_id', 'N/A')})")
            print(f"Type: {record.get('type', 'individual')}")
            print(f"Selection Date: {record.get('selection_date', 'N/A')}")
            print(f"Selection Timestamp: {record.get('selection_timestamp', 'N/A')}")
            print(f"Stocks Count: {record.get('count', 0)}")
            
            # Check for strategy details
            if 'strategy_details' in record:
                print(f"Strategy Details: {record['strategy_details']}")
                print(f"Number of strategies in details: {len(record['strategy_details'])}")
            
            # Check for strategy IDs
            if 'strategy_ids' in record:
                print(f"Strategy IDs: {record['strategy_ids']}")
                print(f"Number of strategy IDs: {len(record['strategy_ids'])}")
            
            # Check stock structure
            if 'stocks' in record and record['stocks']:
                first_stock = record['stocks'][0]
                print(f"Sample stock structure: {list(first_stock.keys()) if first_stock else 'None'}")
                
                # Check if stocks have strategy information
                if 'strategies' in first_stock:
                    print(f"First stock strategies: {first_stock['strategies']}")
                
                if 'selection_reasons' in first_stock:
                    print(f"First stock selection reasons: {first_stock['selection_reasons']}")
        
        # Close database connection
        db_manager.close_connection()
        print("\n✓ Detailed pool strategy check completed successfully")
        
    except Exception as e:
        print(f"Error checking pool strategy details: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = check_pool_strategy_details()
    if not success:
        sys.exit(1)

