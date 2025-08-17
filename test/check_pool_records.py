#!/usr/bin/env python3
"""
Script to check the enhanced pool records in MongoDB
"""

import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def main():
    """Main function to check pool records"""
    print("Checking enhanced pool records...")
    
    # Initialize database manager
    db_manager = MongoDBManager()
    
    try:
        # Get the most recent technical selector record
        record = db_manager.db['pool'].find_one(
            {"agent_name": "TechnicalStockSelector"},
            sort=[("created_at", -1)]
        )
        
        if not record:
            print("No technical selector records found!")
            return 1
            
        print(f"Latest record created at: {record.get('created_at', 'N/A')}")
        print(f"Strategy ID: {record.get('strategy_id', 'N/A')}")
        print(f"Strategy name: {record.get('strategy_name', 'N/A')}")
        print(f"Stocks selected: {record.get('count', 0)}")
        
        # Check if enhanced fields are present
        print("\nEnhanced fields check:")
        print(f"Strategy parameters stored: {'strategy_parameters' in record}")
        print(f"Selection date stored: {'selection_date' in record}")
        print(f"Reference date stored: {'reference_date' in record}")
        
        # Check first few stocks for selection reasons
        stocks = record.get('stocks', [])
        if stocks:
            print(f"\nFirst 3 stock selections with reasons:")
            for i, stock in enumerate(stocks[:3]):
                print(f"  {i+1}. Code: {stock.get('code', 'N/A')}")
                print(f"     Reason: {stock.get('selection_reason', 'N/A')}")
        
        print("\nRecord check completed successfully!")
        return 0
        
    except Exception as e:
        print(f"Error checking pool records: {e}")
        return 1
    finally:
        # Close database connection
        db_manager.close_connection()

if __name__ == "__main__":
    sys.exit(main())

