#!/usr/bin/env python3
"""
Directly check pool collection to see what technical indicators are present
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
import json

def check_pool_technical_indicators():
    """Directly check what technical indicators are present in pool records"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()
        pool_collection = db_manager.db['pool']
        
        # Get all records
        records = list(pool_collection.find().sort('selection_date', -1))
        
        print(f"Found {len(records)} records in pool collection:")
        
        for i, record in enumerate(records):
            print(f"\n--- Record {i+1} ---")
            print(f"ID: {record.get('_id')}")
            print(f"Agent: {record.get('agent_name', 'N/A')}")
            print(f"Strategy: {record.get('strategy_name', 'N/A')}")
            print(f"Type: {record.get('type', 'individual')}")
            print(f"Stocks count: {record.get('count', 0)}")
            
            # Check stocks for technical indicators
            if 'stocks' in record and record['stocks']:
                stocks = record['stocks']
                print(f"Sample stock technical analysis structure:")
                if 'technical_analysis' in stocks[0]:
                    ta = stocks[0]['technical_analysis']
                    print(f"  Keys in technical_analysis: {list(ta.keys())}")
                    
                    # Check what indicators are present
                    indicators = []
                    if 'rsi' in ta and ta['rsi'] is not None:
                        indicators.append('rsi')
                    if 'macd' in ta and ta['macd'] is not None:
                        indicators.append('macd')
                    if 'bollinger_bands' in ta and ta['bollinger_bands'] is not None:
                        indicators.append('bollinger_bands')
                    if 'moving_averages' in ta and ta['moving_averages'] is not None:
                        indicators.append('moving_averages')
                    if 'stochastic' in ta and ta['stochastic'] is not None:
                        indicators.append('stochastic')
                    if 'williams_r' in ta and ta['williams_r'] is not None:
                        indicators.append('williams_r')
                    if 'cci' in ta and ta['cci'] is not None:
                        indicators.append('cci')
                    
                    print(f"  Indicators present: {indicators}")
                    print(f"  Number of indicators: {len(indicators)}")
                else:
                    print("  No technical_analysis field found")
                
                # Show first stock details
                first_stock = stocks[0]
                if 'technical_analysis' in first_stock:
                    print(f"  Sample technical analysis data:")
                    ta = first_stock['technical_analysis']
                    if 'rsi' in ta:
                        print(f"    RSI: {ta['rsi']}")
                    if 'macd' in ta:
                        print(f"    MACD: {ta['macd']}")
                    if 'bollinger_bands' in ta:
                        print(f"    Bollinger Bands: {ta['bollinger_bands']}")
        
        # Close connection
        db_manager.close_connection()
        print("\n✓ Pool technical indicators check completed")
        
    except Exception as e:
        print(f"Error checking pool technical indicators: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    check_pool_technical_indicators()

