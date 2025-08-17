#!/usr/bin/env python3
"""
Check the actual output of the moving average crossover strategy in the pool
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def check_strategy_output():
    """Check the actual output of strategies in the pool"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()
        pool_collection = db_manager.db['pool']
        
        # Get all records sorted by selection date
        records = list(pool_collection.find().sort('selection_date', -1))
        
        print(f"Found {len(records)} records in pool collection:")
        
        for i, record in enumerate(records):
            print(f"\n--- Record {i+1} ---")
            print(f"ID: {record.get('_id')}")
            print(f"Agent: {record.get('agent_name', 'N/A')}")
            print(f"Strategy: {record.get('strategy_name', 'N/A')}")
            print(f"Type: {record.get('type', 'individual')}")
            print(f"Stocks count: {record.get('count', 0)}")
            
            # Check if this is the moving average crossover strategy record
            if record.get('strategy_name') == '移动平均线交叉策略':
                print("  >>> This is the MA Crossover Strategy record <<<")
                
                # Show sample stocks and their selection reasons
                stocks = record.get('stocks', [])
                if stocks:
                    print(f"  Sample stocks ({min(3, len(stocks))} of {len(stocks)}):")
                    for j, stock in enumerate(stocks[:3]):
                        print(f"    {j+1}. {stock.get('code', 'N/A')}: {stock.get('selection_reason', 'N/A')}")
                else:
                    print("  No stocks found in this record")
            
            # Check for technical analysis data
            stocks = record.get('stocks', [])
            if stocks and 'technical_analysis' in stocks[0]:
                print("  Contains technical_analysis data:")
                ta = stocks[0]['technical_analysis']
                print(f"    Keys: {list(ta.keys())}")
        
        # Close connection
        db_manager.close_connection()
        print("\n✓ Pool records check completed")
        
    except Exception as e:
        print(f"Error checking pool records: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    check_strategy_output()

