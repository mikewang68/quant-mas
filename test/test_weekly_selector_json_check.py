"""
Test script to check Weekly Selector JSON value handling for volume breakout strategy
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from agents.weekly_selector import WeeklyStockSelector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_weekly_selector_json_handling():
    """Test Weekly Selector JSON value handling for volume breakout strategy"""

    try:
        # Initialize components
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Get volume breakout strategy ID from database
        strategies = db_manager.get_strategies()
        volume_breakout_strategy = None

        for strategy in strategies:
            if "放量突破" in strategy.get("name", ""):
                volume_breakout_strategy = strategy
                break

        if not volume_breakout_strategy:
            logger.error("Volume breakout strategy not found in database")
            return False

        strategy_id = str(volume_breakout_strategy.get("_id"))
        logger.info(f"Found volume breakout strategy: {volume_breakout_strategy.get('name')} (ID: {strategy_id})")

        # Initialize Weekly Selector with specific strategy
        selector = WeeklyStockSelector(
            db_manager=db_manager,
            data_fetcher=data_fetcher,
            strategy_ids=[strategy_id]
        )

        logger.info(f"Weekly Selector initialized with {len(selector.strategies)} strategies")

        # Test with a small set of stocks
        test_stocks = ["000001", "000002", "600036"]  # 平安银行, 万科A, 招商银行

        # Get data for test stocks
        stock_data = selector.get_standard_data(test_stocks)
        logger.info(f"Retrieved data for {len(stock_data)} test stocks")

        # Test strategy execution for each stock
        for strategy_info in selector.strategies:
            strategy_name = strategy_info["name"]
            strategy_instance = strategy_info["instance"]

            logger.info(f"\nTesting strategy: {strategy_name}")

            for code, k_data in stock_data.items():
                if k_data.empty:
                    logger.warning(f"No data for stock {code}")
                    continue

                logger.info(f"\nProcessing stock {code}:")

                # Execute strategy directly
                result = selector._execute_strategy_for_instance(
                    code, k_data, strategy_instance, strategy_name
                )

                if result:
                    logger.info(f"  - Meets criteria: {result.get('meets_criteria', False)}")
                    logger.info(f"  - Score: {result.get('score', 0.0)}")

                    # Check JSON value
                    json_value = result.get('json_value', '')
                    logger.info(f"  - JSON value type: {type(json_value)}")
                    logger.info(f"  - JSON value length: {len(json_value) if json_value else 0}")

                    # Try to parse JSON
                    import json
                    try:
                        if json_value:
                            parsed_json = json.loads(json_value)
                            logger.info(f"  - JSON parsed successfully")
                            logger.info(f"  - JSON keys: {list(parsed_json.keys())}")
                            logger.info(f"  - Score in JSON: {parsed_json.get('score', 'N/A')}")
                            logger.info(f"  - Selection reason: {parsed_json.get('selection_reason', 'N/A')[:100]}...")
                    except Exception as e:
                        logger.error(f"  - Failed to parse JSON: {e}")
                        logger.info(f"  - Raw JSON value: {json_value[:200]}...")
                else:
                    logger.warning(f"  - No result returned")

        # Test full selection process
        logger.info("\n" + "="*50)
        logger.info("Testing full selection process...")

        strategy_results = selector.select_stocks()

        for strategy_name, result_tuple in strategy_results.items():
            logger.info(f"\nStrategy: {strategy_name}")

            if len(result_tuple) >= 3:
                selected_stocks = result_tuple[0]
                scores = result_tuple[1]
                json_values = result_tuple[2]

                logger.info(f"  - Selected stocks: {len(selected_stocks)}")
                logger.info(f"  - Scores dict type: {type(scores)}")
                logger.info(f"  - JSON values dict type: {type(json_values)}")

                # Check a few selected stocks
                for i, stock_code in enumerate(selected_stocks[:3]):  # Check first 3
                    score = scores.get(stock_code, 0.0)
                    json_value = json_values.get(stock_code, "")

                    logger.info(f"\n  Stock {stock_code}:")
                    logger.info(f"    - Score: {score}")
                    logger.info(f"    - JSON value length: {len(json_value) if json_value else 0}")

                    # Try to parse JSON
                    import json
                    try:
                        if json_value:
                            parsed_json = json.loads(json_value)
                            logger.info(f"    - JSON parsed successfully")
                            logger.info(f"    - Score in JSON: {parsed_json.get('score', 'N/A')}")
                            logger.info(f"    - Selection reason: {parsed_json.get('selection_reason', 'N/A')[:100]}...")
                    except Exception as e:
                        logger.error(f"    - Failed to parse JSON: {e}")
                        logger.info(f"    - Raw JSON value: {json_value[:200]}...")
            else:
                logger.error(f"  - Unexpected result tuple length: {len(result_tuple)}")

        logger.info("\n" + "="*50)
        logger.info("Test completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_weekly_selector_json_handling()
    if success:
        print("\n✅ Weekly Selector JSON handling test PASSED")
    else:
        print("\n❌ Weekly Selector JSON handling test FAILED")

