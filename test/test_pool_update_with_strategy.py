#!/usr/bin/env python3
"""
Test script for updating pool with technical analysis strategy results
"""

import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.technical_selector import TechnicalStockSelector

def main():
    """Main function to test pool update with technical analysis"""
    print("Testing Pool Update with Technical Analysis Strategy Results...")
    
    # Initialize components
    db_manager = MongoDBManager()
    data_fetcher = AkshareClient()
    
    # Initialize selector
    selector = TechnicalStockSelector(db_manager, data_fetcher)
    
    try:
        # Test updating pool with technical analysis
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"\nUpdating pool with technical analysis for date: {today}")
        
        success = selector.update_pool_with_technical_analysis(today)
        
        if success:
            print("Pool update with technical analysis completed successfully!")
            
            # Verify the update by checking the latest pool record
            latest_pool_record = db_manager.pool_collection.find_one(sort=[("selection_date", -1)])
            if latest_pool_record and 'stocks' in latest_pool_record:
                stocks = latest_pool_record['stocks']
                print(f"\nLatest pool record contains {len(stocks)} stocks:")
                
                # Show first few stocks as examples
                for i, stock in enumerate(stocks[:5]):
                    print(f"  {i+1}. Code: {stock.get('code', 'N/A')}")
                    print(f"     Golden Cross: {stock.get('golden_cross', 'N/A')}")
                    print(f"     Signal: {stock.get('signal', 'N/A')}")
                    print(f"     Position: {stock.get('position', 'N/A')}")
                    if 'selection_reason' in stock:
                        print(f"     Reason: {stock['selection_reason']}")
                    print()
                    
                # Count stocks with different signals
                buy_signals = sum(1 for stock in stocks if stock.get('signal') == 'BUY')
                sell_signals = sum(1 for stock in stocks if stock.get('signal') == 'SELL')
                hold_signals = sum(1 for stock in stocks if stock.get('signal') == 'HOLD')
                
                print(f"Signal Summary:")
                print(f"  BUY signals: {buy_signals}")
                print(f"  SELL signals: {sell_signals}")
                print(f"  HOLD signals: {hold_signals}")
            else:
                print("Could not retrieve latest pool record for verification")
        else:
            print("Pool update with technical analysis failed!")
            return 1
            
    except Exception as e:
        print(f"Error testing pool update: {e}")
        return 1
    finally:
        # Close database connection
        db_manager.close_connection()
    
    print("\nTest completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

