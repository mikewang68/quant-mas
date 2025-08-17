#!/usr/bin/env python3
"""
Check what strategies would be associated by update_technical_agent.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_strategies_for_technical_agent():
    """Check what strategies would be associated by update_technical_agent.py"""
    try:
        # Initialize MongoDB manager
        db_manager = MongoDBManager()
        
        # Get all strategies
        strategies = db_manager.get_strategies()
        
        print(f"Found {len(strategies)} total strategies:")
        for strategy in strategies:
            print(f"  - {strategy.get('name', 'Unknown')} ({strategy.get('_id')}, Type: {strategy.get('type', 'Unknown')})")
        
        # Filter for technical strategies (like update_technical_agent.py would do)
        technical_strategies = [s for s in strategies if s.get("type") in ["technical", "rsi", "macd", "bollinger"]]
        print(f"\nFound {len(technical_strategies)} technical strategies (would be associated by update_technical_agent.py):")
        for strategy in technical_strategies:
            print(f"  - {strategy.get('name', 'Unknown')} ({strategy.get('_id')}, Type: {strategy.get('type', 'Unknown')})")
        
        strategy_ids = [str(strategy.get('_id')) for strategy in technical_strategies]
        print(f"\nStrategy IDs that would be associated: {strategy_ids}")
        print(f"Total count: {len(strategy_ids)}")
        
        # Close connection
        db_manager.close_connection()
        logger.info("Database connection closed")
        
    except Exception as e:
        logger.error(f"Error checking strategies: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_strategies_for_technical_agent()

