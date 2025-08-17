#!/usr/bin/env python3
"""
Script to add test stocks to the pool collection
"""

import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def main():
    """Main function to add test stocks to pool"""
    print("Adding test stocks to pool collection...")
    
    # Initialize database manager
    db_manager = MongoDBManager()
    
    try:
        # Get some stock codes from the database
        all_codes = db_manager.get_all_stock_codes()
        print(f"Found {len(all_codes)} stock codes in database")
        
        # Take first 50 codes for testing
        test_codes = all_codes[:50]
        print(f"Adding {len(test_codes)} stocks to pool collection")
        
        # Clear existing pool collection
        db_manager.pool_collection.delete_many({})
        print("Cleared existing pool collection")
        
        # Add test stocks to pool
        pool_documents = [{'code': code} for code in test_codes]
        if pool_documents:
            result = db_manager.pool_collection.insert_many(pool_documents)
            print(f"Added {len(result.inserted_ids)} stocks to pool collection")
        else:
            print("No stocks to add")
            
        # Verify the addition
        pool_codes = db_manager.get_stock_codes_from_pool()
        print(f"Pool collection now contains {len(pool_codes)} stocks")
        print("First 10 pool codes:", pool_codes[:10])
        
    except Exception as e:
        print(f"Error adding stocks to pool: {e}")
        return 1
    finally:
        # Close database connection
        db_manager.close_connection()
    
    print("Test stocks added successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

