#!/usr/bin/env python3
"""
Script to check if there are any stocks with golden_cross = True in the pool collection
"""

import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.mongodb_manager import MongoDBManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_golden_cross_in_pool():
    """Check if there are stocks with golden_cross = True in pool collection"""
    db_manager = None
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()
        
        # Query pool collection for records
        logger.info("Querying pool collection...")
        pool_records = list(db_manager.pool_collection.find())
        
        logger.info(f"Found {len(pool_records)} pool records")
        
        # Check each record for stocks with golden_cross = True
        golden_cross_found = False
        total_stocks_with_golden_cross = 0
        records_with_golden_cross = 0
        
        for record in pool_records:
            stocks = record.get('stocks', [])
            if stocks:
                # Count stocks with golden_cross = True
                golden_cross_stocks = [stock for stock in stocks if stock.get('golden_cross', False)]
                if golden_cross_stocks:
                    golden_cross_found = True
                    records_with_golden_cross += 1
                    total_stocks_with_golden_cross += len(golden_cross_stocks)
                    record_id = record.get('_id', 'N/A')
                    selection_date = record.get('selection_date', 'N/A')
                    logger.info(f"Record {record_id} (date: {selection_date}) has {len(golden_cross_stocks)} stocks with golden_cross = True")
                    
                    # Show details of first few stocks with golden_cross = True
                    for stock in golden_cross_stocks[:3]:  # Show first 3
                        code = stock.get('code', 'N/A')
                        logger.info(f"  - Stock {code}: golden_cross = {stock.get('golden_cross', False)}")
                    if len(golden_cross_stocks) > 3:
                        logger.info(f"  ... and {len(golden_cross_stocks) - 3} more")
        
        # Summary
        logger.info("=== Summary ===")
        if golden_cross_found:
            logger.info(f"✓ Found stocks with golden_cross = True in pool records")
            logger.info(f"✓ Total records with golden_cross = True: {records_with_golden_cross}")
            logger.info(f"✓ Total stocks with golden_cross = True: {total_stocks_with_golden_cross}")
        else:
            logger.info("✗ No stocks with golden_cross = True found in any pool records")
            
        return golden_cross_found
        
    except Exception as e:
        logger.error(f"Error querying pool collection: {e}")
        return False
    finally:
        # Close connection
        if db_manager:
            db_manager.close_connection()

if __name__ == "__main__":
    check_golden_cross_in_pool()

