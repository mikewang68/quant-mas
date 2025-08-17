#!/usr/bin/env python3
"""
Test script for data adjustment feature
"""

import sys
import os
import logging

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data.mongodb_manager import MongoDBManager

def test_data_adjustment():
    """Test the data adjustment feature"""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize MongoDB manager
    db_manager = MongoDBManager()
    
    # Test getting adjustment setting
    adjust_setting = db_manager.get_adjustment_setting()
    print(f"Current adjustment setting: {adjust_setting}")
    
    # Test getting stock data with adjustment
    # Using a sample stock code (you may need to change this to a valid code in your database)
    test_code = "000001"  # Ping An Bank
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    
    try:
        # Test getting data with current adjustment setting
        k_data = db_manager.get_k_data(test_code, start_date, end_date)
        print(f"Retrieved {len(k_data)} records for {test_code}")
        if not k_data.empty:
            print("First few records:")
            print(k_data.head())
    except Exception as e:
        print(f"Error getting data: {e}")
    
    # Close database connection
    db_manager.client.close()

if __name__ == "__main__":
    test_data_adjustment()

