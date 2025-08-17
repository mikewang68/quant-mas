#!/usr/bin/env python3
"""
Debug script to test technical analysis execution step by step
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
    """Main function to debug technical analysis execution"""
    print("Debugging technical analysis execution...")
    
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
        # Check if there are stocks in the pool
        print("\n2. Checking pool stocks...")
        pool_stocks = list(db_manager.pool_collection.find())
        if pool_stocks:
            latest_record = max(pool_stocks, key=lambda x: x.get('selection_date', datetime.min))
            stock_count = len(latest_record.get('stocks', []))
            print(f"✓ Found pool record with {stock_count} stocks")
        else:
            print("⚠ No pool records found")
        
        # Check available strategies
        print("\n3. Checking available strategies...")
        strategies = list(db_manager.db['strategies'].find())
        print(f"Found {len(strategies)} strategies:")
        for strategy in strategies:
            name = strategy.get('name', 'Unknown')
            strategy_type = strategy.get('type', 'Unknown')
            print(f"  - {name} ({strategy_type})")
        
        # Try to find the technical strategy
        technical_strategy = None
        for strategy in strategies:
            if '技术' in strategy.get('name', '') and '选股' in strategy.get('name', ''):
                technical_strategy = strategy
                break
        
        if not technical_strategy:
            # Try to find any technical strategy
            for strategy in strategies:
                if strategy.get('type') == 'technical':
                    technical_strategy = strategy
                    break
        
        if technical_strategy:
            strategy_name = technical_strategy.get('name')
            print(f"\n4. Found technical strategy: {strategy_name}")
            
            # Test the update_pool_with_technical_analysis method
            print(f"\n5. Testing update_pool_with_technical_analysis with strategy: {strategy_name}")
            today = datetime.now().strftime('%Y-%m-%d')
            print(f"Using date: {today}")
            
            success = selector.update_pool_with_technical_analysis(today, strategy_name)
            
            if success:
                print("✓ Technical analysis completed successfully!")
                
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
                print("✗ Technical analysis failed!")
                return 1
        else:
            print("✗ No technical strategy found")
            return 1
            
    except Exception as e:
        print(f"✗ Error during execution: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Close database connection
        db_manager.close_connection()
    
    print("\nDebug completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

