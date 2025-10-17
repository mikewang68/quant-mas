"""
Debug script to check why value field is empty in database for volume breakout strategy
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.weekly_selector import WeeklyStockSelector
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from strategies.volume_breakout_strategy import VolumeBreakoutStrategy
import pandas as pd
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_volume_breakout_strategy_directly():
    """Test volume breakout strategy directly to see its output"""
    logger.info("Testing Volume Breakout Strategy directly...")

    # Create strategy instance
    strategy = VolumeBreakoutStrategy()

    # Create sample data
    dates = pd.date_range("2023-01-01", periods=50, freq="D")
    sample_data = pd.DataFrame({
        "date": dates,
        "open": [100 + i for i in range(50)],
        "high": [110 + i for i in range(50)],
        "low": [90 + i for i in range(50)],
        "close": [105 + i for i in range(50)],
        "volume": [1000000 + i * 10000 for i in range(50)],
    })

    # Test analyze method
    meets_criteria, score, value = strategy.analyze(sample_data, code="000001")

    logger.info(f"Direct strategy test results:")
    logger.info(f"  meets_criteria: {meets_criteria}")
    logger.info(f"  score: {score}")
    logger.info(f"  value: {value}")

    # Parse the JSON value
    try:
        value_dict = json.loads(value)
        logger.info(f"  Parsed value dict: {json.dumps(value_dict, indent=2, ensure_ascii=False)}")
    except Exception as e:
        logger.error(f"  Failed to parse value as JSON: {e}")

def test_weekly_selector_with_volume_breakout():
    """Test weekly selector with volume breakout strategy"""
    logger.info("Testing Weekly Selector with Volume Breakout Strategy...")

    # Initialize components
    db_manager = MongoDBManager()
    data_fetcher = AkshareClient()

    # Get volume breakout strategy ID from database
    strategies = db_manager.get_strategies()
    volume_breakout_strategy_id = None
    for strategy in strategies:
        if "放量突破" in strategy.get("name", ""):
            volume_breakout_strategy_id = str(strategy.get("_id"))
            logger.info(f"Found Volume Breakout Strategy: {strategy.get('name')} with ID: {volume_breakout_strategy_id}")
            break

    if not volume_breakout_strategy_id:
        logger.error("Volume Breakout Strategy not found in database")
        return

    # Create weekly selector with only volume breakout strategy
    selector = WeeklyStockSelector(
        db_manager=db_manager,
        data_fetcher=data_fetcher,
        strategy_ids=[volume_breakout_strategy_id]
    )

    logger.info(f"Weekly Selector initialized with {len(selector.strategies)} strategies")

    # Test with a small set of stocks
    test_stocks = ["000001", "000002", "000858"]  # Ping An, Vanke, Wuliangye

    # Get data for test stocks
    stock_data = selector.get_standard_data(test_stocks)
    logger.info(f"Got data for {len(stock_data)} test stocks")

    # Test strategy execution for each stock
    for code, data in stock_data.items():
        if not data.empty:
            logger.info(f"\nTesting stock {code}:")

            # Execute strategy directly
            strategy_info = selector.strategies[0]  # First strategy (volume breakout)
            strategy_instance = strategy_info["instance"]
            strategy_name = strategy_info["name"]

            result = selector._execute_strategy_for_instance(
                code, data, strategy_instance, strategy_name
            )

            if result:
                logger.info(f"  Strategy result for {code}:")
                logger.info(f"    meets_criteria: {result.get('meets_criteria')}")
                logger.info(f"    score: {result.get('score')}")
                logger.info(f"    json_value: {result.get('json_value')}")

                # Parse JSON value
                try:
                    value_dict = json.loads(result.get('json_value', '{}'))
                    logger.info(f"    Parsed value: {json.dumps(value_dict, indent=2, ensure_ascii=False)}")
                except Exception as e:
                    logger.error(f"    Failed to parse JSON value: {e}")
            else:
                logger.warning(f"  No result for stock {code}")

def test_full_selection_process():
    """Test the full selection process"""
    logger.info("\nTesting full selection process...")

    # Initialize components
    db_manager = MongoDBManager()
    data_fetcher = AkshareClient()

    # Get volume breakout strategy ID
    strategies = db_manager.get_strategies()
    volume_breakout_strategy_id = None
    for strategy in strategies:
        if "放量突破" in strategy.get("name", ""):
            volume_breakout_strategy_id = str(strategy.get("_id"))
            break

    if not volume_breakout_strategy_id:
        logger.error("Volume Breakout Strategy not found")
        return

    # Create selector with only volume breakout
    selector = WeeklyStockSelector(
        db_manager=db_manager,
        data_fetcher=data_fetcher,
        strategy_ids=[volume_breakout_strategy_id]
    )

    # Run selection
    strategy_results = selector.select_stocks()

    logger.info(f"Selection completed with {len(strategy_results)} strategies")

    # Check the results
    for strategy_name, result in strategy_results.items():
        selected_stocks = result[0]
        scores = result[1]
        json_values = result[2]

        logger.info(f"\nStrategy: {strategy_name}")
        logger.info(f"  Selected stocks: {len(selected_stocks)}")

        # Check JSON values for first few stocks
        for i, code in enumerate(selected_stocks[:3]):
            score = scores.get(code, 0.0)
            json_value = json_values.get(code, "")

            logger.info(f"  Stock {code}:")
            logger.info(f"    Score: {score}")
            logger.info(f"    JSON value length: {len(json_value)}")
            logger.info(f"    JSON value preview: {json_value[:100]}...")

            # Try to parse JSON
            try:
                if json_value:
                    value_dict = json.loads(json_value)
                    logger.info(f"    Parsed successfully, keys: {list(value_dict.keys())}")
                else:
                    logger.warning(f"    Empty JSON value!")
            except Exception as e:
                logger.error(f"    Failed to parse JSON: {e}")

    # Save to database
    logger.info("\nSaving to database...")
    save_result = selector.save_selected_stocks(strategy_results)
    logger.info(f"Save result: {save_result}")

    # Check database after save
    if save_result:
        pool_data = db_manager.get_pool_data()
        latest_record = None
        for record in pool_data:
            if record.get("strategy_key") == volume_breakout_strategy_id:
                latest_record = record
                break

        if latest_record:
            logger.info(f"\nLatest pool record:")
            logger.info(f"  Strategy key: {latest_record.get('strategy_key')}")
            logger.info(f"  Date: {latest_record.get('date')}")

            stocks = latest_record.get("stocks", [])
            logger.info(f"  Number of stocks: {len(stocks)}")

            # Check first few stocks
            for i, stock in enumerate(stocks[:3]):
                code = stock.get("code")
                trend_data = stock.get("trend", {})
                strategy_data = trend_data.get(strategy_name, {})

                logger.info(f"  Stock {code}:")
                logger.info(f"    Score: {strategy_data.get('score')}")
                logger.info(f"    Value length: {len(strategy_data.get('value', ''))}")
                logger.info(f"    Value preview: {strategy_data.get('value', '')[:100]}...")

if __name__ == "__main__":
    logger.info("Starting Volume Breakout Value Debug...")

    # Test 1: Direct strategy test
    test_volume_breakout_strategy_directly()

    # Test 2: Weekly selector integration test
    test_weekly_selector_with_volume_breakout()

    # Test 3: Full selection process
    test_full_selection_process()

    logger.info("Debug completed")

