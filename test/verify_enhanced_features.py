#!/usr/bin/env python3
"""
Script to verify all enhanced features of the technical analysis system
"""

import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def main():
    """Main function to verify enhanced features"""
    print("Verifying enhanced technical analysis features...")
    
    # Initialize database manager
    db_manager = MongoDBManager()
    
    try:
        # Get multiple recent technical selector records
        records = list(db_manager.db['pool'].find(
            {"agent_name": "TechnicalStockSelector"}
        ).sort("created_at", -1).limit(3))
        
        print(f"\nFound {len(records)} recent technical analysis records:")
        
        for i, record in enumerate(records):
            print(f"\n--- Record {i+1}: {record.get('_id')} ---")
            print(f"Agent Name: {record.get('agent_name')}")
            print(f"Strategy Name: {record.get('strategy_name')}")
            print(f"Strategy ID: {record.get('strategy_id')}")
            print(f"Selection Date: {record.get('selection_date')}")
            print(f"Stocks Count: {record.get('count')}")
            
            # Check enhanced fields
            print("Enhanced fields:")
            print(f"  Strategy parameters stored: {'strategy_parameters' in record}")
            print(f"  Selection date stored: {'selection_date' in record}")
            print(f"  Reference date stored: {'reference_date' in record}")
            
            # Show strategy parameters if available
            params = record.get('strategy_parameters', {})
            if params:
                print("  Strategy Parameters:")
                for key, value in params.items():
                    print(f"    {key}: {value}")
            else:
                print("  Strategy Parameters: None")
            
            # Show first few stocks with selection reasons
            stocks = record.get('stocks', [])
            print(f"  Sample Stocks ({min(3, len(stocks))} of {len(stocks)}):")
            for j, stock in enumerate(stocks[:3]):
                code = stock.get('code', 'N/A')
                reason = stock.get('selection_reason', 'N/A')
                print(f"    {j+1}. {code}: {reason}")
        
        print("\nEnhanced features verification completed successfully!")
        return 0
        
    except Exception as e:
        print(f"Error verifying enhanced features: {e}")
        return 1
    finally:
        # Close database connection
        db_manager.close_connection()

if __name__ == "__main__":
    sys.exit(main())

