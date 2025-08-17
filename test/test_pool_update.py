#!/usr/bin/env python3
"""
Test script for updating pool with technical analysis
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
    print("Testing Pool Update with Technical Analysis...")
    
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

