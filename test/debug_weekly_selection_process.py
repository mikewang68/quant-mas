"""
Debug script to understand why weekly selector is not selecting any stocks
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

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from strategies.three_ma_bullish_arrangement_strategy import ThreeMABullishArrangementStrategy

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_selection_process.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def debug_strategy_parameters():
    """Debug what strategy parameters are loaded from database"""
    logger.info("=== DEBUGGING STRATEGY PARAMETERS ===")

    try:
        # Initialize database manager
        db_manager = MongoDBManager()
        logger.info("Connected to database")

        # Load strategies from database
        strategies = db_manager.get_strategies()
        logger.info(f"Found {len(strategies)} strategies in database")

        if strategies:
            first_strategy = strategies[0]
            logger.info(f"Strategy name: {first_strategy.get('name', 'Unknown')}")
            logger.info(f"Strategy parameters: {first_strategy.get('parameters', {})}")

            # Try to instantiate the strategy
            strategy_params = first_strategy.get('parameters', {})
            strategy = ThreeMABullishArrangementStrategy(params=strategy_params)
            logger.info(f"Strategy instantiated successfully with params: {strategy.params}")

        else:
            logger.warning("No strategies found in database")

        db_manager.close_connection()

    except Exception as e:
        logger.error(f"Error in debug_strategy_parameters: {e}", exc_info=True)

def debug_data_flow():
    """Debug the data flow in weekly selector"""
    logger.info("=== DEBUGGING DATA FLOW ===")

    try:
        # Initialize components
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()
        logger.info("Initialized database manager and data fetcher")

        # Load strategy from database
        strategies = db_manager.get_strategies()
        if not strategies:
            logger.error("No strategies found in database")
            return

        first_strategy = strategies[0]
        strategy_params = first_strategy.get('parameters', {})
        strategy_name = first_strategy.get('name', 'Unknown')
        logger.info(f"Loaded strategy: {strategy_name} with params: {strategy_params}")

        # Instantiate strategy
        strategy = ThreeMABullishArrangementStrategy(params=strategy_params)
        logger.info("Strategy instantiated successfully")

        # Get stock codes
        all_codes = db_manager.get_stock_codes()
        logger.info(f"Total stock codes: {len(all_codes)}")

        if not all_codes:
            logger.error("No stock codes found")
            return

        # Test with a small sample first
        sample_codes = all_codes[:5]  # Just test with first 5 stocks
        logger.info(f"Testing with sample codes: {sample_codes}")

        # Calculate date range (1 year of data)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d')
        logger.info(f"Date range: {start_date} to {end_date}")

        selected_stocks = []
        processed_count = 0

        for code in sample_codes:
            try:
                logger.info(f"Processing stock: {code}")
                processed_count += 1

                # Get adjusted daily K-line data
                daily_k_data = db_manager.get_adjusted_k_data(code, start_date, end_date, frequency='daily')
                logger.info(f"Daily data shape for {code}: {daily_k_data.shape}")

                if daily_k_data.empty:
                    logger.warning(f"No daily data for {code}")
                    continue

                # Check if we have enough data
                required_data = max(strategy.params.get('short', 5), strategy.params.get('mid', 13), strategy.params.get('long', 34))
                if len(daily_k_data) < required_data:
                    logger.warning(f"Insufficient data for {code}: {len(daily_k_data)} < {required_data}")
                    continue

                # Convert to weekly data
                weekly_k_data = convert_daily_to_weekly(daily_k_data)
                logger.info(f"Weekly data shape for {code}: {weekly_k_data.shape}")

                if weekly_k_data.empty:
                    logger.warning(f"No weekly data for {code}")
                    continue

                # Check weekly data
                required_weekly = max(strategy.params.get('short', 5), strategy.params.get('mid', 13), strategy.params.get('long', 34))
                if len(weekly_k_data) < required_weekly:
                    logger.warning(f"Insufficient weekly data for {code}: {len(weekly_k_data)} < {required_weekly}")
                    continue

                # Execute strategy
                meets_criteria, reason, score, golden_cross = strategy.analyze(weekly_k_data)
                logger.info(f"Strategy result for {code}: meets_criteria={meets_criteria}, reason={reason}, score={score}")

                if meets_criteria:
                    selected_stocks.append(code)
                    logger.info(f"Stock {code} SELECTED")
                else:
                    logger.info(f"Stock {code} NOT selected: {reason}")

            except Exception as e:
                logger.error(f"Error processing stock {code}: {e}", exc_info=True)
                continue

            # Limit processing for debugging
            if processed_count >= 5:
                break

        logger.info(f"Selected stocks: {selected_stocks}")
        logger.info(f"Total selected: {len(selected_stocks)}")

        db_manager.close_connection()

    except Exception as e:
        logger.error(f"Error in debug_data_flow: {e}", exc_info=True)

def convert_daily_to_weekly(daily_data):
    """
    Convert daily K-line data to weekly K-line data

    Args:
        daily_data: DataFrame with daily K-line data

    Returns:
        DataFrame with weekly K-line data
    """
    if daily_data.empty:
        return daily_data

    try:
        # Set date as index for resampling
        daily_data = daily_data.set_index('date')

        # Resample to weekly data
        weekly_data = daily_data.resample('W-FRI').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'amount': 'sum'
        })

        # Remove any rows with NaN values
        weekly_data = weekly_data.dropna()

        # Reset index to make date a column again
        weekly_data = weekly_data.reset_index()

        return weekly_data

    except Exception as e:
        logger.error(f"Error converting daily to weekly data: {e}")
        return pd.DataFrame()

def debug_strategy_logic():
    """Debug the strategy logic with sample data"""
    logger.info("=== DEBUGGING STRATEGY LOGIC ===")

    try:
        # Create sample data that should meet criteria
        dates = pd.date_range(start='2023-01-01', periods=50, freq='W-FRI')
        close_prices = np.linspace(10, 20, 50)  # Rising prices

        # Add some realistic volatility
        np.random.seed(42)
        noise = np.random.normal(0, 0.5, 50)
        close_prices = close_prices + noise
        close_prices = np.abs(close_prices)  # Ensure positive prices

        sample_data = pd.DataFrame({
            'date': dates,
            'open': close_prices * 0.98,
            'high': close_prices * 1.02,
            'low': close_prices * 0.95,
            'close': close_prices,
            'volume': np.random.randint(1000000, 5000000, 50),
            'amount': close_prices * np.random.randint(1000000, 5000000, 50)
        })

        logger.info(f"Sample data shape: {sample_data.shape}")
        logger.info(f"Sample data head:\n{sample_data.head()}")

        # Test strategy with ideal data
        strategy_params = {'short': 5, 'mid': 13, 'long': 34}
        strategy = ThreeMABullishArrangementStrategy(params=strategy_params)

        meets_criteria, reason, score, golden_cross = strategy.analyze(sample_data)
        logger.info(f"Ideal data test - meets_criteria: {meets_criteria}, reason: {reason}, score: {score}")

        # Test with database parameters format
        db_params = {'ma_short': 5, 'ma_mid': 13, 'ma_long': 34}
        strategy_db = ThreeMABullishArrangementStrategy(params=db_params)
        logger.info(f"Strategy with DB params instantiated, params: {strategy_db.params}")

        meets_criteria_db, reason_db, score_db, golden_cross_db = strategy_db.analyze(sample_data)
        logger.info(f"DB params test - meets_criteria: {meets_criteria_db}, reason: {reason_db}, score: {score_db}")

    except Exception as e:
        logger.error(f"Error in debug_strategy_logic: {e}", exc_info=True)

if __name__ == "__main__":
    logger.info("Starting debug process for weekly selection")

    # Debug strategy parameters
    debug_strategy_parameters()

    # Debug data flow
    debug_data_flow()

    # Debug strategy logic
    debug_strategy_logic()

    logger.info("Debug process completed")

