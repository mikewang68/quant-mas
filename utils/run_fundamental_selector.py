#!/usr/bin/env python3
"""
Run the fundamental stock selector to analyze stocks and save results to pool collection
"""

import sys
import os
import logging

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.fundamental_selector import FundamentalStockSelector
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main function to run the fundamental stock selector"""
    try:
        # Initialize components
        logger.info("Initializing components...")
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Initialize selector
        logger.info("Initializing fundamental stock selector...")
        selector = FundamentalStockSelector(db_manager, data_fetcher)

        # Analyze stocks
        logger.info("Analyzing stocks with fundamental strategies...")
        success = selector.run()

        if success:
            logger.info("Successfully updated pool with fundamental analysis")
        else:
            logger.error("Failed to update pool with fundamental analysis")

        # Close database connection
        db_manager.close_connection()
        logger.info("Fundamental stock analysis completed")

    except Exception as e:
        logger.error(f"Error running fundamental stock selector: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

