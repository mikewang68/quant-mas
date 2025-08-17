#!/usr/bin/env python3
"""
Detailed pool records checker
"""
import sys
import os
import logging

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from data.mongodb_manager import MongoDBManager
except ImportError as e:
    logger.error(f"Import error: {e}")
    sys.exit(1)

def check_pool_detailed():
    """Check detailed pool records"""
    print("Checking detailed pool records...")
    
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
            if 'stocks' in record and record['stocks']:
                first_stock = record['stocks'][0]
                print(f"Sample stock structure: {list(first_stock.keys()) if first_stock else 'None'}")
                if len(record['stocks']) > 3:
                    print(f"First 3 stocks: {record['stocks'][:3]}")
                else:
                    print(f"All stocks: {record['stocks']}")
        
        # Close database connection
        db_manager.close_connection()
        print("\n✓ Detailed pool check completed successfully")
        
    except Exception as e:
        print(f"Error checking pool records: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = check_pool_detailed()
    if not success:
        sys.exit(1)

