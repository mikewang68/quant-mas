#!/usr/bin/env python3
"""
Test script to verify that TechnicalStockSelector can run multiple strategies
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.technical_selector import TechnicalStockSelector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/test_technical_selector.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def test_multi_strategy_execution():
    """Test that TechnicalStockSelector can execute multiple strategies"""
    try:
        logger.info("Starting TechnicalStockSelector multi-strategy test")

        # Initialize components
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Initialize TechnicalStockSelector
        selector = TechnicalStockSelector(
            db_manager=db_manager,
            data_fetcher=data_fetcher,
            name="TestTechnicalSelector"
        )

        # Check that multiple strategies were loaded
        logger.info(f"Loaded {len(selector.strategy_names)} strategies:")
        for i, strategy_name in enumerate(selector.strategy_names):
            logger.info(f"  {i+1}. {strategy_name}")
            logger.info(f"     File: {selector.strategy_files[i]}")
            logger.info(f"     Class: {selector.strategy_class_names[i]}")
            logger.info(f"     Params: {selector.strategy_params_list[i]}")

        # Verify that multiple strategy instances were created
        logger.info(f"Created {len(selector.strategy_instances)} strategy instances")
        if len(selector.strategy_instances) != len(selector.strategy_names):
            logger.error("Mismatch between strategy names and instances")
            return False

        # Run the technical analysis
        logger.info("Running technical analysis with all strategies...")
        success = selector.update_pool_with_technical_analysis()

        if success:
            logger.info("Technical analysis completed successfully")
            logger.info(f"Strategy names: {selector.strategy_names}")
            logger.info(f"Number of strategies: {len(selector.strategy_names)}")
            return True
        else:
            logger.error("Technical analysis failed")
            return False

    except Exception as e:
        logger.error(f"Error in test_multi_strategy_execution: {e}")
        return False
    finally:
        # Clean up
        if 'db_manager' in locals():
            db_manager.close_connection()

if __name__ == "__main__":
    success = test_multi_strategy_execution()
    if success:
        print("\n✓ TechnicalStockSelector multi-strategy test completed successfully")
        sys.exit(0)
    else:
        print("\n✗ TechnicalStockSelector multi-strategy test failed")
        sys.exit(1)

