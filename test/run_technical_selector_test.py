#!/usr/bin/env python3
"""
Test script for running TechnicalStockSelector with a specific strategy
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
    """Main function to run technical selector test"""
    print("Starting Technical Stock Selector Test...")
    
    # Initialize components
    db_manager = MongoDBManager()
    data_fetcher = AkshareClient()
    
    # Initialize selector
    selector = TechnicalStockSelector(db_manager, data_fetcher)
    
    # Get the moving average crossover strategy
    strategy_name = "移动平均线交叉策略"  # Use the actual strategy name from database
    strategy = db_manager.get_strategy_by_name(strategy_name)
    if not strategy:
        print("Error: Moving Average Crossover Strategy not found")
        return 1
    
    print(f"Found strategy: {strategy.get('name', 'Unknown')} ({strategy.get('_id', 'No ID')})")
    print(f"Strategy program: {strategy.get('program', 'No program')}")
    
    # Run selector with the strategy
    try:
        # Use today's date for selection
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"\nRunning strategy for date: {today}")
        
        selected_stocks, last_data_date, strategy_details = selector.run(today, strategy_name)
        
        print("\nExecution Results:")
        print(f"Stocks selected: {len(selected_stocks)}")
        print(f"Last data date: {last_data_date}")
        print(f"Strategy details: {strategy_details}")
        
        # Print selected stocks with their signals and positions
        if selected_stocks:
            print(f"\nSelected stocks:")
            for stock in selected_stocks[:10]:  # Show first 10 stocks
                print(f"  - {stock['code']}: {stock['selection_reason']}")
                print(f"    Signal: {stock['signal']}, Position: {stock['position']}")
            if len(selected_stocks) > 10:
                print(f"  ... and {len(selected_stocks) - 10} more stocks")
                
    except Exception as e:
        print(f"Error running technical selector: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Close database connection
        db_manager.close_connection()
    
    print("\nTest completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

