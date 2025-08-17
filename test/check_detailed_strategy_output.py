#!/usr/bin/env python3
"""
Check the detailed output of the moving average crossover strategy
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def check_detailed_strategy_output():
    """Check the detailed output of the moving average crossover strategy"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()
        pool_collection = db_manager.db['pool']
        
        # Get the MA crossover strategy record
        ma_record = pool_collection.find_one({'strategy_name': '移动平均线交叉策略'})
        
        if not ma_record:
            print("MA Crossover Strategy record not found")
            return
            
        print("=== Moving Average Crossover Strategy Output ===")
        print(f"Record ID: {ma_record.get('_id')}")
        print(f"Agent: {ma_record.get('agent_name')}")
        print(f"Strategy: {ma_record.get('strategy_name')}")
        print(f"Execution date: {ma_record.get('selection_date')}")
        print(f"Stocks selected: {ma_record.get('count')}")
        print(f"Strategy parameters: {ma_record.get('strategy_parameters')}")
        
        # Show all stocks with their selection reasons
        stocks = ma_record.get('stocks', [])
        print(f"\nAll selected stocks ({len(stocks)}):")
        for i, stock in enumerate(stocks):
            print(f"  {i+1:2d}. {stock.get('code')}: {stock.get('selection_reason')}")
            
        # Check if there are technical analysis records
        tech_record = pool_collection.find_one({
            'stocks': {
                '$elemMatch': {
                    'technical_analysis': {'$exists': True}
                }
            }
        })
        
        if tech_record:
            print("\n=== Technical Analysis Records ===")
            print(f"Record ID: {tech_record.get('_id')}")
            tech_stocks = tech_record.get('stocks', [])
            if tech_stocks and 'technical_analysis' in tech_stocks[0]:
                ta = tech_stocks[0]['technical_analysis']
                print(f"Technical indicators present: {list(ta.keys())}")
                print(f"Number of indicators: {len(ta.keys())}")
        
        # Close connection
        db_manager.close_connection()
        print("\n✓ Detailed strategy output check completed")
        
    except Exception as e:
        print(f"Error checking detailed strategy output: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    check_detailed_strategy_output()

