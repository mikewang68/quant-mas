#!/usr/bin/env python3
"""
Test script to verify enhanced logging in public opinion analysis strategy
"""

import sys
import os
import logging

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from strategies.enhanced_public_opinion_analysis_strategy import EnhancedPublicOpinionAnalysisStrategy
import pandas as pd

# Configure logging to see detailed output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main function to test enhanced logging in public opinion analysis strategy"""
    try:
        # Initialize strategy
        logger.info("Initializing enhanced public opinion analysis strategy...")
        strategy = EnhancedPublicOpinionAnalysisStrategy()

        # Create mock stock data
        mock_stock_data = {
            "000001": pd.DataFrame({
                "date": ["2023-01-01", "2023-01-02"],
                "open": [10.0, 10.5],
                "high": [11.0, 11.5],
                "low": [9.5, 10.0],
                "close": [10.5, 11.0],
                "volume": [1000, 1200]
            }),
            "000002": pd.DataFrame({
                "date": ["2023-01-01", "2023-01-02"],
                "open": [20.0, 20.5],
                "high": [21.0, 21.5],
                "low": [19.5, 20.0],
                "close": [20.5, 21.0],
                "volume": [2000, 2200]
            })
        }

        # Test the analyze method with mock data
        logger.info("Testing analyze method with mock stock data...")

        # Test analyze method for one stock
        meets_criteria, reason, score = strategy.analyze(
            mock_stock_data["000001"], "000001", "平安银行"
        )

        logger.info(f"Analysis result for 000001: meets_criteria={meets_criteria}, reason={reason}, score={score}")

        # Test analyze method for another stock
        meets_criteria, reason, score = strategy.analyze(
            mock_stock_data["000002"], "000002", "万科A"
        )

        logger.info(f"Analysis result for 000002: meets_criteria={meets_criteria}, reason={reason}, score={score}")

        logger.info("Enhanced logging test completed!")

    except Exception as e:
        logger.error(f"Error testing enhanced logging: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()

