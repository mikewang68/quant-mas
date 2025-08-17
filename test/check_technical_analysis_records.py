#!/usr/bin/env python3
"""
Check for records with technical analysis indicators
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

def check_technical_analysis_records():
    """Check for records with technical analysis indicators"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()
        pool_collection = db_manager.db['pool']
        
        # Find records with technical analysis data
        tech_records = list(pool_collection.find({
            'stocks': {
                '$elemMatch': {
                    'technical_analysis': {'$exists': True}
                }
            }
        }))
        
        print(f"Found {len(tech_records)} records with technical analysis data:")
        
        for i, record in enumerate(tech_records):
            print(f"\n--- Technical Analysis Record {i+1} ---")
            print(f"ID: {record.get('_id')}")
            print(f"Agent: {record.get('agent_name', 'N/A')}")
            print(f"Strategy: {record.get('strategy_name', 'N/A')}")
            print(f"Type: {record.get('type', 'individual')}")
            print(f"Stocks count: {record.get('count', 0)}")
            
            # Show technical analysis details from first stock
            stocks = record.get('stocks', [])
            if stocks and 'technical_analysis' in stocks[0]:
                ta = stocks[0]['technical_analysis']
                print(f"Technical indicators: {list(ta.keys())}")
                
                # Show sample values
                if 'rsi' in ta:
                    print(f"RSI: {ta['rsi']}")
                if 'macd' in ta:
                    print(f"MACD: {ta['macd']}")
                if 'bollinger_bands' in ta:
                    print(f"Bollinger Bands: {ta['bollinger_bands']}")
                if 'moving_averages' in ta:
                    print(f"Moving Averages: {ta['moving_averages']}")
        
        # Close connection
        db_manager.close_connection()
        print("\n✓ Technical analysis records check completed")
        
    except Exception as e:
        print(f"Error checking technical analysis records: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    check_technical_analysis_records()

