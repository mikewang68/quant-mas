#!/usr/bin/env python3
"""
Check technical selector execution results
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def check_technical_selector_results():
    """Check technical selector execution results"""
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
            
            # Check if this is the MA crossover strategy record
            if '移动平均线交叉策略' in str(record.get('strategy_name', '')) or '689e6bfdd227f4d150c07a70' in str(record.get('_id', '')):
                print(">>> THIS IS THE MA CROSSOVER STRATEGY RECORD <<<")
                print(f"Strategy parameters: {record.get('strategy_parameters', {})}")
                
                # Show sample stocks
                stocks = record.get('stocks', [])
                if stocks:
                    print(f"Sample stocks ({min(3, len(stocks))} of {len(stocks)}):")
                    for j, stock in enumerate(stocks[:3]):
                        print(f"  {j+1}. Code: {stock.get('code')}")
                        print(f"      Reason: {stock.get('selection_reason', 'N/A')}")
                        if 'technical_analysis' in stock:
                            print(f"      Technical analysis keys: {list(stock['technical_analysis'].keys())}")
                else:
                    print("No stocks found in this record")
            
        # Close connection
        db_manager.close_connection()
        print("\n✓ Pool records check completed")
        
    except Exception as e:
        print(f"Error checking pool records: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    check_technical_selector_results()

