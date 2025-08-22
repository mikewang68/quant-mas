"""
Weekly Stock Selector Agent
A clean framework that dynamically loads strategies from database
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
from utils.akshare_client import AkshareClient
from data.mongodb_manager import MongoDBManager
import logging
import importlib
import sys
import os
import pandas as pd

# Add the project root to the path for importing strategies
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logger = logging.getLogger(__name__)


class WeeklyStockSelector:
    """
    Weekly Stock Selector Agent - Clean framework
    Dynamically loads strategies from database and executes them
    """

    def __init__(self, db_manager: MongoDBManager, data_fetcher: AkshareClient):
        """
        Initialize the weekly stock selector framework

        Args:
            db_manager: MongoDBManager instance for database operations
            data_fetcher: AkshareClient instance for data fetching
        """
        self.db_manager = db_manager
        self.data_fetcher = data_fetcher
        self.logger = logging.getLogger(__name__)

        # Strategy components
        self.strategy_name = None
        self.strategy_file = None
        self.strategy_class_name = None
        self.strategy_params = {}
        self.strategy_instance = None

        # Load strategy from database
        self._load_strategy_from_db()

        # Load and initialize the dynamic strategy
        self._load_dynamic_strategy()

    def _load_strategy_from_db(self):
        """
        Load strategy configuration from database
        """
        try:
            strategies = self.db_manager.get_strategies()
            if strategies and len(strategies) > 0:
                # Use the first strategy for now
                first_strategy = strategies[0]
                self.strategy_params = first_strategy.get('parameters', {})
                self.strategy_name = first_strategy.get('name', 'Unknown')

                # Extract file and class from program field if it exists
                if 'program' in first_strategy and isinstance(first_strategy['program'], dict):
                    self.strategy_file = first_strategy['program'].get('file', '')
                    self.strategy_class_name = first_strategy['program'].get('class', '')
                    self.logger.info("Loaded strategy file and class from program field")
                else:
                    # Fallback to direct file and class_name fields
                    self.strategy_file = first_strategy.get('file', '')
                    self.strategy_class_name = first_strategy.get('class_name', '')

                    self.logger.info("Loaded strategy from database: %s" % self.strategy_name)
            else:
                self.logger.warning("No strategies found in database")
        except Exception as e:
            self.logger.error(f"Error loading strategy from database: {e}")

    def _load_dynamic_strategy(self):
        """
        Dynamically load strategy from file and instantiate the strategy class
        """
        try:
            if not self.strategy_file or not self.strategy_class_name:
                self.logger.warning("Strategy file or class not specified")
                return

            # Dynamically import the strategy module
            # Handle both direct file names and package.module format
            module_name = self.strategy_file

            # Handle different formats of strategy file specification
            if isinstance(self.strategy_file, dict):
                # Handle the case where program is a dict with file and class fields
                file_name = self.strategy_file.get('file', '')
                if file_name:
                    if not file_name.endswith('.py'):
                        if '.' not in file_name and not file_name.startswith('strategies.'):
                            module_name = f"strategies.{file_name}"
                    else:
                        module_name = file_name[:-3]
                        if '.' not in module_name and not module_name.startswith('strategies.'):
                            module_name = f"strategies.{module_name}"
                else:
                    self.logger.error("Invalid program field format")
                    return
            elif isinstance(self.strategy_file, str):
                # If it's just a filename without .py extension and without package prefix, add the strategies prefix
                if not self.strategy_file.endswith('.py'):
                    if '.' not in self.strategy_file and not self.strategy_file.startswith('strategies.'):
                        module_name = f"strategies.{self.strategy_file}"
                else:
                    # If it has .py extension, remove it for import
                    module_name = self.strategy_file[:-3]
                    # Add strategies prefix if needed
                    if '.' not in module_name and not module_name.startswith('strategies.'):
                        module_name = f"strategies.{module_name}"

            self.strategy_module = importlib.import_module(module_name)

            # Get the strategy class
            self.strategy_class = getattr(self.strategy_module, self.strategy_class_name)

            # Instantiate the strategy with parameters
            self.strategy_instance = self.strategy_class(params=self.strategy_params)

            self.logger.info("Successfully loaded dynamic strategy: %s" % self.strategy_name)
        except Exception as e:
            self.logger.error(f"Error loading dynamic strategy: {e}")
            raise

    def select_stocks(self, date: Optional[str] = None) -> Tuple[List[str], Optional[str], Dict[str, bool], Dict[str, float], Dict[str, Dict]]:
        """
        Select stocks using the dynamically loaded strategy

        Args:
            date: Selection date (YYYY-MM-DD), defaults to today

        Returns:
            Tuple of (selected stock codes, last data date, golden cross flags, scores)
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

            self.logger.info("Selecting stocks for week of %s using strategy: %s", date, self.strategy_name)

        # Get all stock codes from database
        all_codes = self.db_manager.get_stock_codes()
        if not all_codes:
            # If no codes in DB, fetch from data source
            all_codes = self.data_fetcher.get_stock_list()
            # Save to DB for future use
            self.db_manager.save_stock_codes(all_codes)

        # Filter stocks based on criteria
        selected_stocks = []
        selected_scores = {}  # Store scores for each selected stock
        golden_cross_flags = {}
        technical_analysis_data = {}  # Store technical analysis data for each selected stock
        last_data_date = None

        # Calculate date range (1 year of data)
        end_date = date
        start_date = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d')

        for i, code in enumerate(all_codes):
            try:
                if i % 500 == 0:  # Log progress every 500 stocks
                    self.logger.info(f"Processing stock {i+1}/{len(all_codes)}: {code}")

                # Get adjusted daily K-line data
                daily_k_data = self.db_manager.get_adjusted_k_data(code, start_date, end_date, frequency='daily')

                # If no data in DB, fetch from data source
                if daily_k_data.empty:
                    daily_k_data = self.data_fetcher.get_daily_k_data(code, start_date, end_date)
                    # Save to DB for future use
                    if not daily_k_data.empty:
                        self.db_manager.save_k_data(code, daily_k_data, frequency='daily')

                # Convert to weekly data
                if not daily_k_data.empty:
                    k_data = self._convert_daily_to_weekly(daily_k_data)

                    # Update last_data_date
                    if not k_data.empty and 'date' in k_data.columns:
                        stock_last_date = k_data['date'].iloc[-1]
                        if hasattr(stock_last_date, 'strftime'):
                            stock_last_date = stock_last_date.strftime('%Y-%m-%d')
                        else:
                            stock_last_date = str(stock_last_date)

                        # Update last_data_date to the latest date among all selected stocks
                        if stock_last_date and (not last_data_date or stock_last_date > last_data_date):
                            last_data_date = stock_last_date

                    # Execute strategy
                    if self.strategy_instance and not k_data.empty:
                        result = self._execute_strategy(code, k_data)
                        if result and len(result) >= 4:
                            meets_criteria, score, golden_cross, technical_analysis = result
                            if meets_criteria:
                                selected_stocks.append(code)
                                selected_scores[code] = score if score is not None else 1.0
                                # Check for golden cross from strategy result
                                golden_cross_flags[code] = golden_cross
                                # Store technical analysis data
                                technical_analysis_data[code] = technical_analysis
                        elif result and len(result) >= 3:
                            meets_criteria = result[0]
                            score = result[1]
                            golden_cross = result[2]
                            technical_analysis = {}
                            if meets_criteria:
                                selected_stocks.append(code)
                                selected_scores[code] = score if score is not None else 1.0
                                # Check for golden cross from strategy result
                                golden_cross_flags[code] = golden_cross
                                # Store empty technical analysis data
                                technical_analysis_data[code] = technical_analysis

            except Exception as e:
                self.logger.warning(f"Error processing stock {code}: {e}")
                continue

        self.logger.info(f"Selected {len(selected_stocks)} stocks for weekly trading")
        if last_data_date:
            self.logger.info(f"Last data date used for selection: {last_data_date}")
        return selected_stocks, last_data_date, golden_cross_flags, selected_scores, technical_analysis_data

    def _execute_strategy(self, code: str, k_data):
        """
        Execute strategy by calling the dynamic strategy instance

        Args:
            code: Stock code
            k_data: K-line data

        Returns:
            Tuple of (meets_criteria, score, golden_cross, technical_analysis_data) where meets_criteria is True if stock meets strategy criteria, False otherwise,
            score is the strategy score (or None if not applicable), golden_cross is the golden cross flag,
            and technical_analysis_data contains moving average values
        """
        try:
            if self.strategy_instance and k_data is not None and not k_data.empty:
                # Call the strategy's analyze method for stock selection
                result = self.strategy_instance.analyze(k_data)

                # Log the result for debugging
                # self.logger.info(f"Strategy {self.strategy_name} returned: {result}")

                # Extract technical analysis data
                technical_analysis_data = {}
                if hasattr(self.strategy_instance, 'params'):
                    params = self.strategy_instance.params
                    short_period = params.get('short', 5)
                    mid_period = params.get('mid', 13)
                    long_period = params.get('long', 34)

                    # Calculate moving averages for technical analysis
                    if len(k_data) >= max(short_period, mid_period, long_period):
                        import numpy as np
                        close_prices = np.array(k_data['close'].values, dtype=np.float64)

                        # Calculate moving averages
                        if len(close_prices) >= short_period:
                            ma_short = np.mean(close_prices[-short_period:])
                            technical_analysis_data['ma_short'] = float(ma_short)

                        if len(close_prices) >= mid_period:
                            ma_mid = np.mean(close_prices[-mid_period:])
                            technical_analysis_data['ma_mid'] = float(ma_mid)

                        if len(close_prices) >= long_period:
                            ma_long = np.mean(close_prices[-long_period:])
                            technical_analysis_data['ma_long'] = float(ma_long)

                        # Add current price
                        if len(close_prices) > 0:
                            technical_analysis_data['price'] = float(close_prices[-1])

                # The strategy returns (meets_criteria, reason, score, golden_cross)
                # We need to unpack correctly and return (meets_criteria, score, golden_cross, technical_analysis_data)
                if isinstance(result, tuple):
                    meets_criteria = result[0] if len(result) > 0 else False
                    reason = result[1] if len(result) > 1 else ""
                    score = result[2] if len(result) > 2 else None
                    golden_cross = result[3] if len(result) > 3 else False
                    return meets_criteria, score, golden_cross, technical_analysis_data

            return False, None, False, {}
        except Exception as e:
            self.logger.warning(f"Error executing strategy for stock {code}: {e}")
            return False, None, False, {}

    def _convert_daily_to_weekly(self, daily_data):
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
            self.logger.error(f"Error converting daily to weekly data: {e}")
            return pd.DataFrame()

    def save_selected_stocks(self, stocks: List[str], golden_cross_flags: Optional[Dict[str, bool]] = None,
                           date: Optional[str] = None, last_data_date: Optional[str] = None,
                           scores: Optional[Dict[str, float]] = None,
                           technical_analysis_data: Optional[Dict[str, Dict]] = None) -> bool:
        """
        Save selected stocks to database

        Args:
            stocks: List of selected stock codes
            golden_cross_flags: Dictionary mapping stock codes to golden cross flags
            date: Selection date
            last_data_date: Last date of stock data used for selection
            technical_analysis_data: Technical analysis data for each stock

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Import here to avoid circular imports
            from data.database_operations import DatabaseOperations

            # Create database operations instance
            db_ops = DatabaseOperations(self.db_manager)

            # Convert stocks list to the expected format (list of dicts)
            stocks_data = []
            for stock_code in stocks:
                # Get score from scores dictionary
                score = scores.get(stock_code, 0.0) if scores else 0.0
                golden_cross = golden_cross_flags.get(stock_code, False) if golden_cross_flags else False

                # Get technical analysis data from strategy results if available
                value_text = ""
                if technical_analysis_data and stock_code in technical_analysis_data:
                    tech_data = technical_analysis_data[stock_code]
                    close_price = tech_data.get('price', 'N/A')
                    ma_short = tech_data.get('ma_short', 'N/A')
                    ma_mid = tech_data.get('ma_mid', 'N/A')
                    ma_long = tech_data.get('ma_long', 'N/A')

                    # Format the value text with actual values
                    if all(isinstance(val, (int, float)) for val in [close_price, ma_short, ma_mid, ma_long]):
                        value_text = f"收盘价={close_price:.2f}, MA5={ma_short:.2f}, MA13={ma_mid:.2f}, MA34={ma_long:.2f}"
                    else:
                        # Handle case where some values might be 'N/A'
                        close_str = f"{close_price:.2f}" if isinstance(close_price, (int, float)) else str(close_price)
                        ma5_str = f"{ma_short:.2f}" if isinstance(ma_short, (int, float)) else str(ma_short)
                        ma13_str = f"{ma_mid:.2f}" if isinstance(ma_mid, (int, float)) else str(ma_mid)
                        ma34_str = f"{ma_long:.2f}" if isinstance(ma_long, (int, float)) else str(ma_long)
                        value_text = f"收盘价={close_str}, MA5={ma5_str}, MA13={ma13_str}, MA34={ma34_str}"
                elif scores and stock_code in scores:
                    # Extract technical data from score reason text
                    score_text = scores[stock_code]
                    # Convert to string if it's not already
                    if not isinstance(score_text, str):
                        score_text = str(score_text)
                    # Remove the "满足多头排列: " prefix if present
                    if score_text.startswith("满足多头排列: "):
                        value_text = score_text.replace("满足多头排列: ", "")
                    else:
                        value_text = score_text
                else:
                    value_text = "收盘价=N/A, MA5=N/A, MA13=N/A, MA34=N/A"

                stock_info = {
                    'code': stock_code,
                    'score': score,
                    'golden_cross': bool(golden_cross),  # Convert numpy bool to Python bool
                    'value': value_text
                }
                stocks_data.append(stock_info)

            # Ensure date is not None
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')

            # Get the actual strategy ID from database
            strategy_id = None
            strategies = self.db_manager.get_strategies()
            for strategy in strategies:
                if strategy.get('name') == "三均线多头排列策略（基本型）":
                    strategy_id = strategy.get('_id')
                    break

            # If we couldn't find the strategy, use a default
            if not strategy_id:
                strategy_id = "three_ma_bullish_arrangement"

            return db_ops.save_selected_stocks_to_pool(
                strategy_key="weekly_selector_three_ma",
                agent_name="WeeklySelector",
                strategy_id=strategy_id,
                strategy_name="三均线多头排列策略",
                stocks=stocks_data,
                date=date,
                last_data_date=last_data_date,
                strategy_params=None  # Let the database operations fetch parameters from DB
            )
        except Exception as e:
            self.logger.error(f"Error saving selected stocks: {e}")
            return False

