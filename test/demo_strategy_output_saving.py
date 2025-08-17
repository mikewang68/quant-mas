#!/usr/bin/env python3
"""
Demo script showing how strategies can automatically save their output results to the pool collection
"""

import sys
import os
import logging
from datetime import datetime
from typing import List, Dict

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from data.database_operations import DatabaseOperations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demo_strategy_execution() -> List[Dict]:
    """
    Simulate a strategy execution that selects stocks based on some criteria
    In a real implementation, this would contain actual strategy logic
    """
    logger.info("Executing demo strategy...")
    
    # Simulated stock selection results
    selected_stocks = [
        {
            'code': '000001',
            'selection_reason': 'RSI in range 30-70 and positive MACD',
            'score': 0.85,
            'technical_analysis': {
                'rsi': 55.2,
                'macd': {'line': 0.12, 'signal': 0.08, 'histogram': 0.04},
                'moving_averages': {'sma_5': 15.2, 'sma_20': 14.8}
            }
        },
        {
            'code': '000002',
            'selection_reason': 'Bullish crossover detected',
            'score': 0.78,
            'technical_analysis': {
                'rsi': 62.1,
                'macd': {'line': 0.08, 'signal': 0.05, 'histogram': 0.03},
                'moving_averages': {'sma_5': 22.5, 'sma_20': 21.9}
            }
        },
        {
            'code': '000003',
            'selection_reason': 'Price above upper Bollinger Band',
            'score': 0.92,
            'technical_analysis': {
                'rsi': 68.5,
                'macd': {'line': 0.15, 'signal': 0.11, 'histogram': 0.04},
                'bollinger_bands': {'upper': 35.8, 'middle': 32.1, 'lower': 28.4}
            }
        }
    ]
    
    logger.info(f"Strategy selected {len(selected_stocks)} stocks")
    return selected_stocks

def save_strategy_results_to_pool(db_ops: DatabaseOperations, stocks: List[Dict], 
                                 strategy_name: str = "DemoStrategy") -> bool:
    """
    Save strategy results to pool collection using the new utility method
    
    Args:
        db_ops: DatabaseOperations instance
        stocks: List of selected stocks with analysis data
        strategy_name: Name of the strategy
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        # Get current date for selection
        selection_date = datetime.now().strftime('%Y-%m-%d')
        
        # Create a unique strategy key (in real implementation, this might include agent info)
        strategy_key = f"{strategy_name}_{datetime.now().strftime('%Y-%W')}"
        
        # Strategy parameters (if any)
        strategy_params = {
            'rsi_min': 30,
            'rsi_max': 70,
            'ma_short': 5,
            'ma_long': 20
        }
        
        # Additional metadata
        metadata = {
            'strategy_version': '1.0',
            'execution_time': datetime.now()
        }
        
        # Save results to pool using the new utility method
        success = db_ops.save_strategy_output_to_pool(
            strategy_key=strategy_key,
            agent_name="DemoAgent",
            strategy_id="demo_strategy_001",
            strategy_name=strategy_name,
            stocks=stocks,
            date=selection_date,
            strategy_params=strategy_params,
            additional_metadata=metadata
        )
        
        if success:
            logger.info(f"Successfully saved strategy results to pool with key: {strategy_key}")
        else:
            logger.error("Failed to save strategy results to pool")
            
        return success
        
    except Exception as e:
        logger.error(f"Error saving strategy results: {e}")
        return False

def main():
    """Main function to demonstrate strategy output saving"""
    print("Demonstrating automatic strategy output saving to pool collection...")
    
    # Initialize database manager and operations
    db_manager = MongoDBManager()
    db_ops = DatabaseOperations(db_manager)
    
    try:
        # 1. Execute strategy (simulated)
        selected_stocks = demo_strategy_execution()
        
        # 2. Save results to pool collection
        print("\nSaving strategy results to pool collection...")
        success = save_strategy_results_to_pool(db_ops, selected_stocks)
        
        if success:
            print("✓ Strategy results successfully saved to pool collection")
        else:
            print("✗ Failed to save strategy results to pool collection")
            return 1
            
        # 3. Verify the saved data
        print("\nVerifying saved data...")
        pool_collection = db_manager.db['pool']
        latest_record = pool_collection.find_one(
            {},  # No filter
            sort=[('created_at', -1)]  # Sort by creation time descending
        )
        
        if latest_record:
            print(f"✓ Found latest pool record with {latest_record.get('count', 0)} stocks")
            print(f"  Strategy: {latest_record.get('strategy_name', 'Unknown')}")
            print(f"  Agent: {latest_record.get('agent_name', 'Unknown')}")
            print(f"  Date: {latest_record.get('selection_date', 'Unknown')}")
        else:
            print("✗ No pool record found")
            
    except Exception as e:
        logger.error(f"Error in demo: {e}")
        return 1
    finally:
        # Close database connection
        db_manager.close_connection()
    
    print("\nDemo completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())

