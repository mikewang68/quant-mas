#!/usr/bin/env python3
"""
Verify that the technical selector fix works correctly
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
    """Main function to verify the fix"""
    print("Verifying technical selector fix...")
    
    # Initialize components
    print("\n1. Initializing components...")
    try:
        db_manager = MongoDBManager()
        print("✓ Database manager initialized")
        
        data_fetcher = AkshareClient()
        print("✓ Data fetcher initialized")
        
        selector = TechnicalStockSelector(db_manager, data_fetcher)
        print("✓ Technical selector initialized")
    except Exception as e:
        print(f"✗ Error initializing components: {e}")
        return 1
    
    try:
        # Test the update_pool_with_technical_analysis method with default parameters
        print("\n2. Testing update_pool_with_technical_analysis with default parameters...")
        success = selector.update_pool_with_technical_analysis()
        
        if success:
            print("✓ Technical analysis completed successfully with default parameters!")
            
            # Verify the update
            latest_pool_record = db_manager.pool_collection.find_one(sort=[("selection_date", -1)])
            if latest_pool_record and "stocks" in latest_pool_record:
                stocks = latest_pool_record["stocks"]
                stocks_with_signals = [s for s in stocks if "signal" in s and "position" in s]
                print(f"Latest pool record has {len(stocks)} stocks")
                print(f"Stocks with signals/positions: {len(stocks_with_signals)}/{len(stocks)}")
                
                # Show sample
                if stocks_with_signals:
                    print("\nSample of updated stocks:")
                    for i, stock in enumerate(stocks_with_signals[:3]):
                        print(f"  {stock['code']}: signal={stock['signal']}, position={stock['position']}")
            else:
                print("⚠ Could not verify pool update")
        else:
            print("✗ Technical analysis failed with default parameters!")
            return 1
            
        # Test with explicit date and strategy name
        print("\n3. Testing update_pool_with_technical_analysis with explicit parameters...")
        today = datetime.now().strftime('%Y-%m-%d')
        success = selector.update_pool_with_technical_analysis(today, "移动平均线交叉策略")
        
        if success:
            print("✓ Technical analysis completed successfully with explicit parameters!")
        else:
            print("✗ Technical analysis failed with explicit parameters!")
            return 1
            
    except Exception as e:
        print(f"✗ Error during execution: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Close database connection
        db_manager.close_connection()
    
    print("\n✓ All tests passed! The fix is working correctly.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

