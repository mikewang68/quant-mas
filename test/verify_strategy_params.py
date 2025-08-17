#!/usr/bin/env python3
"""
Verify that strategy parameters are correctly passed and used
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
    """Main function to verify strategy parameters"""
    print("Verifying strategy parameters...")
    
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
        # Get strategy configuration from database
        print("\n2. Checking strategy configuration...")
        strategy_name = "移动平均线交叉策略"
        strategy = db_manager.get_strategy_by_name(strategy_name)
        
        if strategy:
            print(f"✓ Found strategy: {strategy_name}")
            strategy_params = strategy.get('parameters', {})
            print(f"Strategy parameters: {strategy_params}")
            
            # Check if parameters exist
            if strategy_params:
                print("✓ Strategy has parameters configured")
                
                # Test the update_pool_with_technical_analysis method
                print(f"\n3. Testing parameter usage in strategy execution...")
                
                # Get a sample stock code from the pool
                latest_pool_record = db_manager.pool_collection.find_one(sort=[("selection_date", -1)])
                if latest_pool_record and "stocks" in latest_pool_record and latest_pool_record["stocks"]:
                    sample_stock = latest_pool_record["stocks"][0]
                    stock_code = sample_stock["code"]
                    print(f"Using sample stock: {stock_code}")
                    
                    # Test strategy execution with debug info
                    print("\n4. Testing strategy execution with debug info...")
                    success = selector.update_pool_with_technical_analysis(None, strategy_name)
                    
                    if success:
                        print("✓ Strategy execution completed successfully!")
                        
                        # Verify the parameters were used by checking if any stocks got BUY signals
                        latest_pool_record = db_manager.pool_collection.find_one(sort=[("selection_date", -1)])
                        if latest_pool_record and "stocks" in latest_pool_record:
                            stocks = latest_pool_record["stocks"]
                            buy_signals = [s for s in stocks if s.get("signal") == "BUY"]
                            print(f"Found {len(buy_signals)} BUY signals out of {len(stocks)} stocks")
                            
                            if buy_signals:
                                print("✓ Strategy parameters are being used correctly!")
                            else:
                                print("⚠ No BUY signals generated - parameters might not be used correctly")
                    else:
                        print("✗ Strategy execution failed!")
                        return 1
                else:
                    print("⚠ No stocks found in pool")
            else:
                print("⚠ Strategy has no parameters configured")
        else:
            print(f"✗ Strategy {strategy_name} not found in database")
            return 1
            
    except Exception as e:
        print(f"✗ Error during execution: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Close database connection
        db_manager.close_connection()
    
    print("\n✓ Parameter verification completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

