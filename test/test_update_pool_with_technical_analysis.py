#!/usr/bin/env python3
"""
Test script for updating pool with technical analysis results
"""

import sys
import os
from datetime import datetime

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.technical_selector import TechnicalStockSelector

def main():
    """Main function to test updating pool with technical analysis"""
    print("Testing update pool with technical analysis...")
    
    # Initialize components
    db_manager = MongoDBManager()
    data_fetcher = AkshareClient()
    
    # Initialize selector
    selector = TechnicalStockSelector(db_manager, data_fetcher)
    
    try:
        # Test updating pool with technical analysis
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"\nUpdating pool with technical analysis for date: {today}")
        
        success = selector.update_pool_with_technical_analysis(today, "移动平均线交叉策略")
        
        if success:
            print("Pool update with technical analysis completed successfully!")
            
            # Verify the update by checking the latest pool record
            latest_pool_record = db_manager.pool_collection.find_one(sort=[("selection_date", -1)])
            if latest_pool_record and "stocks" in latest_pool_record:
                stocks = latest_pool_record["stocks"]
                print(f"\nLatest pool record has {len(stocks)} stocks:")
                
                # Show first few stocks as examples
                for i, stock in enumerate(stocks[:3]):
                    print(f"  Stock {i+1}: {stock}")
                    
                # Count how many stocks have signal and position data
                stocks_with_signals = [s for s in stocks if "signal" in s and "position" in s]
                print(f"\nStocks with signal/position data: {len(stocks_with_signals)}/{len(stocks)}")
                
                if stocks_with_signals:
                    print("Sample signals:")
                    for i, stock in enumerate(stocks_with_signals[:3]):
                        print(f"  {stock['code']}: signal={stock['signal']}, position={stock['position']}")
            else:
                print("Could not retrieve latest pool record for verification")
        else:
            print("Pool update with technical analysis failed!")
            return 1
            
    except Exception as e:
        print(f"Error testing pool update: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Close database connection
        db_manager.close_connection()
    
    print("\nTest completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

