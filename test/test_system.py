#!/usr/bin/env python3
"""
Test script for the multi-agent stock trading system.
This script tests the core components of the system.
"""

import sys
import os
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_data_fetcher():
    """Test the data fetcher component"""
    logger.info("Testing AkshareClient...")
    
    try:
        from utils.akshare_client import AkshareClient
        fetcher = AkshareClient()
        
        # Test getting stock list
        logger.info("Getting stock list...")
        codes = fetcher.get_stock_list()
        logger.info(f"Found {len(codes)} stocks")
        
        if codes:
            # Test with first stock
            test_code = codes[0]
            logger.info(f"Testing with stock {test_code}")
            
            # Test getting stock info
            info = fetcher.get_stock_info(test_code)
            if info:
                logger.info(f"Stock info retrieved: {len(info)} fields")
            
            # Test getting daily data
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            daily_data = fetcher.get_daily_k_data(test_code, start_date, end_date)
            logger.info(f"Daily data shape: {daily_data.shape}")
            
            # Test getting weekly data
            weekly_data = fetcher.get_weekly_k_data(test_code, start_date, end_date)
            logger.info(f"Weekly data shape: {weekly_data.shape}")
        
        logger.info("AkshareClient tests completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error in AkshareClient test: {e}")
        return False

def test_mongodb_manager():
    """Test the MongoDB manager component"""
    logger.info("Testing MongoDBManager...")
    
    try:
        from data.mongodb_manager import MongoDBManager
        db_manager = MongoDBManager()
        
        # Test getting stock codes
        codes = db_manager.get_all_stock_codes()
        logger.info(f"Retrieved {len(codes)} stock codes from database")
        
        # Test getting latest update date
        latest_date = db_manager.get_latest_update_date()
        logger.info(f"Latest update date: {latest_date}")
        
        logger.info("MongoDBManager tests completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error in MongoDBManager test: {e}")
        return False

def test_strategies():
    """Test the strategy components"""
    logger.info("Testing Strategies...")
    
    try:
        from strategies.ma_crossover_strategy import MACrossoverStrategy
        
        # Create sample data
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        sample_data = pd.DataFrame({
            'date': dates,
            'open': np.random.uniform(100, 110, 100),
            'high': np.random.uniform(110, 120, 100),
            'low': np.random.uniform(90, 100, 100),
            'close': np.random.uniform(100, 110, 100),
            'volume': np.random.uniform(1000000, 2000000, 100)
        })
        
        # Test MA Crossover Strategy
        strategy = MACrossoverStrategy()
        signals = strategy.generate_signals(sample_data)
        logger.info(f"Generated {len(signals[signals['signal'] != 'HOLD'])} trading signals")
        
        logger.info("Strategy tests completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error in Strategy test: {e}")
        return False

def test_backtester():
    """Test the backtesting component"""
    logger.info("Testing Backtester...")
    
    try:
        from backtesting.backtester import Backtester
        
        # Create sample data
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        sample_data = pd.DataFrame({
            'date': dates,
            'open': np.random.uniform(100, 110, 100),
            'high': np.random.uniform(110, 120, 100),
            'low': np.random.uniform(90, 100, 100),
            'close': np.random.uniform(100, 110, 100),
            'volume': np.random.uniform(1000000, 2000000, 100)
        })
        
        # Initialize backtester
        backtester = Backtester(initial_capital=100000, commission=0.001)
        backtester.add_data(sample_data, "TEST")
        
        logger.info("Backtester tests completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error in Backtester test: {e}")
        return False

def main():
    """Main test function"""
    logger.info("Starting multi-agent stock trading system tests...")
    
    # Test components
    tests = [
        ("AkshareClient", test_data_fetcher),
        ("MongoDBManager", test_mongodb_manager),
        ("Strategies", test_strategies),
        ("Backtester", test_backtester)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    logger.info("\n" + "="*50)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("="*50)
    
    all_passed = True
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test_name:20} : {status}")
        if not result:
            all_passed = False
    
    logger.info("="*50)
    if all_passed:
        logger.info("ALL TESTS PASSED!")
    else:
        logger.info("SOME TESTS FAILED!")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

