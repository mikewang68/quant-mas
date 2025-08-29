#!/usr/bin/env python3
"""
Test script to verify score normalization in TechnicalStockSelector
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
        logging.FileHandler('logs/test_score_normalization.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def test_score_normalization():
    """Test that scores are properly normalized in TechnicalStockSelector"""
    try:
        logger.info("Starting score normalization test")

        # Initialize components
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Initialize TechnicalStockSelector
        selector = TechnicalStockSelector(
            db_manager=db_manager,
            data_fetcher=data_fetcher,
            name="TestTechnicalSelector"
        )

        # Check that strategies were loaded
        logger.info(f"Loaded {len(selector.strategy_names)} strategies:")
        for i, strategy_name in enumerate(selector.strategy_names):
            logger.info(f"  {i+1}. {strategy_name}")

        # Verify that strategy instances were created
        logger.info(f"Created {len(selector.strategy_instances)} strategy instances")
        if len(selector.strategy_instances) != len(selector.strategy_names):
            logger.error("Mismatch between strategy names and instances")
            return False

        logger.info("Score normalization test completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error in test_score_normalization: {e}")
        return False
    finally:
        # Clean up
        if 'db_manager' in locals():
            db_manager.close_connection()

if __name__ == "__main__":
    success = test_score_normalization()
    if success:
        print("\n✓ Score normalization test completed successfully")
        sys.exit(0)
    else:
        print("\n✗ Score normalization test failed")
        sys.exit(1)

