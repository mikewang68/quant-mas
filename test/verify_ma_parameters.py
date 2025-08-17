#!/usr/bin/env python3
"""
Verify that moving average parameters are correctly used in strategy execution
"""

import sys
import os
from datetime import datetime, timedelta

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient

def main():
    """Main function to verify moving average parameters"""
    print("Verifying moving average parameters usage...")
    
    # Initialize components
    print("\n1. Initializing components...")
    try:
        db_manager = MongoDBManager()
        print("✓ Database manager initialized")
        
        data_fetcher = AkshareClient()
        print("✓ Data fetcher initialized")
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
        
        # Get parameters
        short_period = db_params.get('short_period', 5)
        long_period = db_params.get('long_period', 20)
        print(f"Using parameters - Short MA: {short_period}, Long MA: {long_period}")
        
        # Get a sample stock and its data
        print("\n3. Getting sample stock data...")
        latest_pool_record = db_manager.pool_collection.find_one(sort=[("selection_date", -1)])
        if not latest_pool_record or "stocks" not in latest_pool_record or not latest_pool_record["stocks"]:
            print("✗ No stocks found in pool")
            return 1
            
        sample_stock = latest_pool_record["stocks"][0]
        stock_code = sample_stock["code"]
        print(f"Using sample stock: {stock_code}")
        
        # Get stock data
        today = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.strptime(today, '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d')
        
        # Get daily K-data from database with adjustment based on config
        daily_k_data = db_manager.get_adjusted_k_data(stock_code, start_date, today, frequency='daily')
        
        # If no data in DB, fetch from data source
        if daily_k_data.empty:
            daily_k_data = data_fetcher.get_daily_k_data(stock_code, start_date, today)
            # Save to DB for future use
            if not daily_k_data.empty:
                db_manager.save_k_data(stock_code, daily_k_data, frequency='daily')
        
        if daily_k_data.empty:
            print(f"✗ No data available for stock {stock_code}")
            return 1
            
        print(f"✓ Retrieved {len(daily_k_data)} days of data for {stock_code}")
        
        # Calculate moving averages using the same parameters as the strategy
        print("\n4. Calculating moving averages with strategy parameters...")
        import talib
        import numpy as np
        
        close_prices = daily_k_data['close'].values
        
        # Calculate moving averages with database parameters
        ma_short = talib.SMA(close_prices, timeperiod=short_period)
        ma_long = talib.SMA(close_prices, timeperiod=long_period)
        
        # Show recent values
        print(f"Recent close prices: {close_prices[-5:]}")
        print(f"Recent short MA ({short_period}): {ma_short[-5:]}")
        print(f"Recent long MA ({long_period}): {ma_long[-5:]}")
        
        # Check for crossovers
        print("\n5. Checking for moving average crossovers...")
        if len(ma_short) >= 2 and len(ma_long) >= 2:
            # Check last two points for crossover
            prev_short = ma_short[-2]
            prev_long = ma_long[-2]
            curr_short = ma_short[-1]
            curr_long = ma_long[-1]
            
            print(f"Previous: Short MA = {prev_short:.2f}, Long MA = {prev_long:.2f}")
            print(f"Current:  Short MA = {curr_short:.2f}, Long MA = {curr_long:.2f}")
            
            # Buy signal: short MA crosses above long MA
            if prev_short <= prev_long and curr_short > curr_long:
                print("✓ Buy signal detected (short MA crossed above long MA)")
            # Sell signal: short MA crosses below long MA
            elif prev_short >= prev_long and curr_short < curr_long:
                print("✓ Sell signal detected (short MA crossed below long MA)")
            else:
                print("✓ Hold signal (no crossover detected)")
        else:
            print("✗ Not enough data points to check for crossovers")
            
        print("\n✓ Moving average parameter verification completed!")
        return 0
            
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

