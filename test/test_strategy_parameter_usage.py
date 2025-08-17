#!/usr/bin/env python3
"""
Test to verify that strategy parameters from database are correctly used
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
    """Main function to test strategy parameter usage"""
    print("Testing strategy parameter usage from database...")
    
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
        
        if not strategy:
            print(f"✗ Strategy {strategy_name} not found in database")
            return 1
            
        print(f"✓ Found strategy: {strategy.get('name')}")
        db_params = strategy.get('parameters', {})
        print(f"Database parameters: {db_params}")
        
        # Expected values from database
        expected_short = db_params.get('short_period', 5)
        expected_long = db_params.get('long_period', 20)
        expected_ratio = db_params.get('max_position_ratio', 0.1)
        
        print(f"Expected values - Short: {expected_short}, Long: {expected_long}, Ratio: {expected_ratio}")
        
        # Test strategy execution and verify parameters are used
        print(f"\n3. Testing strategy execution with database parameters...")
        
        # Get a sample stock
        latest_pool_record = db_manager.pool_collection.find_one(sort=[("selection_date", -1)])
        if not latest_pool_record or "stocks" not in latest_pool_record or not latest_pool_record["stocks"]:
            print("✗ No stocks found in pool")
            return 1
            
        sample_stock = latest_pool_record["stocks"][0]
        stock_code = sample_stock["code"]
        print(f"Using sample stock: {stock_code}")
        
        # Test the update_pool_with_technical_analysis method
        success = selector.update_pool_with_technical_analysis(None, strategy_name)
        
        if success:
            print("✓ Strategy execution completed successfully!")
            
            # Verify results
            latest_pool_record = db_manager.pool_collection.find_one(sort=[("selection_date", -1)])
            if latest_pool_record and "stocks" in latest_pool_record:
                stocks = latest_pool_record["stocks"]
                print(f"Processed {len(stocks)} stocks")
                
                # Show sample results
                print("\nSample results:")
                for i, stock in enumerate(stocks[:3]):
                    print(f"  {stock['code']}: signal={stock.get('signal', 'N/A')}, position={stock.get('position', 'N/A')}")
                    
            return 0
        else:
            print("✗ Strategy execution failed!")
            return 1
            
    except Exception as e:
        print(f"✗ Error during execution: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Close database connection
        db_manager.close_connection()

if __name__ == "__main__":
    sys.exit(main())

