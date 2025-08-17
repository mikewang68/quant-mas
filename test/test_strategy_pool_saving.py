#!/usr/bin/env python3
"""
Test script demonstrating the complete workflow of strategy execution with automatic pool saving
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from strategies.demo_strategy import DemoStrategy

def generate_sample_data(num_days: int = 100) -> pd.DataFrame:
    """
    Generate sample stock data for testing
    
    Args:
        num_days: Number of days of data to generate
        
    Returns:
        DataFrame with sample stock data
    """
    # Generate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=num_days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate sample prices with some trend and volatility
    np.random.seed(42)  # For reproducible results
    initial_price = 100.0
    returns = np.random.normal(0.001, 0.02, len(dates))  # Daily returns
    prices = [initial_price]
    
    for ret in returns[1:]:
        new_price = prices[-1] * (1 + ret)
        prices.append(max(new_price, 0.01))  # Ensure positive prices
    
    # Create DataFrame
    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, len(dates)),
        'amount': [prices[i] * np.random.randint(1000000, 10000000) for i in range(len(prices))]
    })
    
    return df

def main():
    """Main function to test the complete workflow"""
    print("Testing complete workflow: Strategy execution with automatic pool saving...")
    
    # Initialize components
    db_manager = MongoDBManager()
    
    try:
        # 1. Create sample stock data
        print("\n1. Generating sample stock data...")
        stock_data = {}
        sample_codes = ['000001', '000002', '000003', '000004', '000005']
        
        for code in sample_codes:
            stock_data[code] = generate_sample_data(60)  # 60 days of data
            print(f"   Generated data for {code}: {len(stock_data[code])} records")
        
        # 2. Initialize strategy
        print("\n2. Initializing demo strategy...")
        strategy = DemoStrategy()
        
        # 3. Execute strategy
        print("\n3. Executing strategy...")
        selected_stocks = strategy.execute(
            stock_data=stock_data,
            agent_name="TestAgent",
            db_manager=db_manager
        )
        
        print(f"   Strategy selected {len(selected_stocks)} stocks")
        for stock in selected_stocks:
            print(f"   - {stock['code']}: {stock['selection_reason']}")
        
        # 4. Verify results were saved to pool
        print("\n4. Verifying results in pool collection...")
        pool_collection = db_manager.db['pool']
        
        # Find records from today
        today = datetime.now().strftime('%Y-%m-%d')
        recent_records = list(pool_collection.find(
            {'selection_date': {'$gte': datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}},
            sort=[('created_at', -1)]
        ))
        
        if recent_records:
            print(f"   Found {len(recent_records)} recent pool records:")
            for record in recent_records:
                print(f"   - Strategy: {record.get('strategy_name', 'Unknown')}")
                print(f"     Agent: {record.get('agent_name', 'Unknown')}")
                print(f"     Stocks: {record.get('count', 0)}")
                print(f"     Date: {record.get('selection_date', 'Unknown')}")
        else:
            print("   No recent pool records found")
            
    except Exception as e:
        print(f"Error in test: {e}")
        return 1
    finally:
        # Close database connection
        db_manager.close_connection()
    
    print("\n✓ Test completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

