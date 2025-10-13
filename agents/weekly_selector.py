"""
Weekly Stock Selector Agent
A clean framework that dynamically loads strategies from database with new architecture
"""

import sys
import os
# Add project root to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple, Union
from utils.akshare_client import AkshareClient
from data.mongodb_manager import MongoDBManager
from utils.strategy_result_formatter import StrategyResultFormatter
import logging
import importlib
import pandas as pd

# Add project root to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from interfaces.data_interface import DataProviderInterface, StandardDataFormat

# Configure logging
logger = logging.getLogger(__name__)


class WeeklyStockSelector(DataProviderInterface):
    """
    Weekly Stock Selector Agent - Clean framework with new architecture
    Dynamically loads strategies from database and executes them
    """

    def __init__(self, db_manager: MongoDBManager, data_fetcher: AkshareClient, strategy_ids: Optional[List[str]] = None):
        """
        Initialize the weekly stock selector framework

        Args:
            db_manager: MongoDBManager instance for database operations
            data_fetcher: AkshareClient instance for data fetching
            strategy_ids: Optional list of strategy IDs to load specific strategies, if None loads all strategies
        """
        self.db_manager = db_manager
        self.data_fetcher = data_fetcher
        self.strategy_ids = strategy_ids
        self.logger = logging.getLogger(__name__)

        # Strategy components - now supporting multiple strategies
        self.strategies = []  # List of strategy instances
        self.strategy_configs = []  # List of strategy configurations

        # Load strategies from database
        self._load_strategies_from_db()

        # Load and initialize the dynamic strategies
        self._load_dynamic_strategies()

    def get_standard_data(self, stock_codes: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Get standard format data for the given stock codes (365 days of daily data converted to weekly).

        Args:
            stock_codes: List of stock codes to get data for

        Returns:
            Dictionary mapping stock codes to standard format DataFrames (weekly data)
        """
        self.logger.info(f"Getting standard weekly data for {len(stock_codes)} stocks")

        # Prepare stock data for all stocks (1 year of daily data converted to weekly)
        stock_data = {}
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

        for i, code in enumerate(stock_codes):
            try:
                if i % 500 == 0:  # Log progress every 500 stocks
                    self.logger.info(f"Processing stock {i+1}/{len(stock_codes)}: {code}")

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
                    weekly_data = self._convert_daily_to_weekly(daily_k_data)

                    # Validate and store data for this stock
                    if not weekly_data.empty and StandardDataFormat.validate_data(weekly_data):
                        stock_data[code] = weekly_data
                    else:
                        self.logger.warning(f"Invalid or no weekly data available for {code}")

            except Exception as e:
                self.logger.warning(f"Error processing stock {code}: {e}")
                continue

        self.logger.info(f"Prepared standard weekly data for {len(stock_data)} stocks")
        return stock_data

    def get_data_for_stock(self, stock_code: str) -> pd.DataFrame:
        """
        Get standard format data for a single stock (weekly data).

        Args:
            stock_code: Stock code to get data for

        Returns:
            Standard format DataFrame with weekly stock data
        """
        stock_data = self.get_standard_data([stock_code])
        df = stock_data.get(stock_code, StandardDataFormat.create_empty_dataframe())
        return df if df is not None else StandardDataFormat.create_empty_dataframe()

    def _load_strategies_from_db(self):
        """
        Load strategy configurations from database
        """
        try:
            strategies = self.db_manager.get_strategies()
            if strategies and len(strategies) > 0:
                # Filter strategies if specific strategy_ids are provided
                if self.strategy_ids:
                    selected_strategies = []
                    for strategy in strategies:
                        if str(strategy.get('_id')) in self.strategy_ids:
                            selected_strategies.append(strategy)

                    if not selected_strategies:
                        self.logger.warning(f"No strategies found with IDs {self.strategy_ids}, using all strategies")
                        selected_strategies = strategies
                else:
                    # Use all strategies if no specific IDs provided
                    selected_strategies = strategies

                # Store strategy configurations
                self.strategy_configs = selected_strategies
                self.logger.info(f"Loaded {len(self.strategy_configs)} strategies from database")
            else:
                self.logger.warning("No strategies found in database")
        except Exception as e:
            self.logger.error(f"Error loading strategies from database: {e}")

    def _load_dynamic_strategies(self):
        """
        Dynamically load all strategies from files and instantiate strategy classes
        """
        try:
            if not self.strategy_configs:
                self.logger.warning("No strategy configurations found")
                return

            for strategy_config in self.strategy_configs:
                try:
                    strategy_params = strategy_config.get('parameters', {})
                    strategy_name = strategy_config.get('name', 'Unknown')

                    # Extract file and class from program field if it exists
                    strategy_file = None
                    strategy_class_name = None

                    if 'program' in strategy_config and isinstance(strategy_config['program'], dict):
                        strategy_file = strategy_config['program'].get('file', '')
                        strategy_class_name = strategy_config['program'].get('class', '')
                    else:
                        # Fallback to direct file and class_name fields
                        strategy_file = strategy_config.get('file', '')
                        strategy_class_name = strategy_config.get('class_name', '')

                    if not strategy_file or not strategy_class_name:
                        self.logger.warning(f"Strategy file or class not specified for {strategy_name}")
                        continue

                    # Dynamically import the strategy module
                    module_name = strategy_file

                    # Handle different formats of strategy file specification
                    if isinstance(strategy_file, dict):
                        # Handle the case where program is a dict with file and class fields
                        file_name = strategy_file.get('file', '')
                        if file_name:
                            if not file_name.endswith('.py'):
                                if '.' not in file_name and not file_name.startswith('strategies.'):
                                    module_name = f"strategies.{file_name}"
                            else:
                                module_name = file_name[:-3]
                                if '.' not in module_name and not module_name.startswith('strategies.'):
                                    module_name = f"strategies.{module_name}"
                        else:
                            self.logger.error(f"Invalid program field format for strategy {strategy_name}")
                            continue
                    elif isinstance(strategy_file, str):
                        # If it's just a filename without .py extension and without package prefix, add the strategies prefix
                        if not strategy_file.endswith('.py'):
                            if '.' not in strategy_file and not strategy_file.startswith('strategies.'):
                                module_name = f"strategies.{strategy_file}"
                        else:
                            # If it has .py extension, remove it for import
                            module_name = strategy_file[:-3]
                            # Add strategies prefix if needed
                            if '.' not in module_name and not module_name.startswith('strategies.'):
                                module_name = f"strategies.{module_name}"

                    strategy_module = importlib.import_module(module_name)

                    # Get the strategy class
                    strategy_class = getattr(strategy_module, strategy_class_name)

                    # Instantiate the strategy with parameters
                    strategy_instance = strategy_class(params=strategy_params)

                    # Store strategy instance with its configuration
                    self.strategies.append({
                        'instance': strategy_instance,
                        'name': strategy_name,
                        'config': strategy_config,
                        'params': strategy_params
                    })

                    self.logger.info(f"Successfully loaded dynamic strategy: {strategy_name}")
                except Exception as e:
                    self.logger.error(f"Error loading strategy {strategy_name}: {e}")
                    continue

            self.logger.info(f"Successfully loaded {len(self.strategies)} strategies")
        except Exception as e:
            self.logger.error(f"Error loading dynamic strategies: {e}")
            raise

    def select_stocks(self, date: Optional[str] = None) -> Union[Dict[str, Tuple[List[str], Optional[str], Dict[str, float], Dict[str, Dict]]], Tuple[List[str], Optional[str], Dict[str, bool], Dict[str, float], Dict[str, Dict], Dict]]:
        """
        Select stocks using all dynamically loaded strategies

        Args:
            date: Selection date (YYYY-MM-DD), defaults to today

        Returns:
            If multiple strategies: Dictionary mapping strategy names to tuples of (selected stock codes, last data date, scores, technical_analysis_data)
            If single strategy: Tuple of (selected_stocks, last_data_date, golden_cross_flags, selected_scores, technical_analysis_data, strategy_results)
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        self.logger.info(f"Selecting stocks for week of {date} using {len(self.strategies)} strategies")

        # Get all stock codes from database - only once
        all_codes = self.db_manager.get_stock_codes()
        if not all_codes:
            # If no codes in DB, fetch from data source
            all_codes = self.data_fetcher.get_stock_list()
            # Save to DB for future use
            self.db_manager.save_stock_codes(all_codes)

        # Get standard format data using the new interface - only once
        stock_data = self.get_standard_data(all_codes)
        self.logger.info(f"Retrieved data for {len(stock_data)} stocks")

        # Dictionary to store results for each strategy
        strategy_results = {}

        # Execute each strategy using the same stock data
        for strategy_info in self.strategies:
            strategy_name = strategy_info['name']
            strategy_instance = strategy_info['instance']

            self.logger.info(f"Executing strategy: {strategy_name}")

            # Filter stocks based on criteria for this strategy
            selected_stocks = []
            selected_scores = {}  # Store scores for each selected stock
            selection_reasons = {}  # Store selection reasons for each selected stock
            technical_analysis_data = {}  # Store technical analysis data for each selected stock
            golden_cross_flags = {}  # Store golden cross flags for each selected stock
            last_data_date = None

            # Process each stock's data for this strategy
            for code, k_data in stock_data.items():
                try:
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
                    if strategy_instance and not k_data.empty:
                        result = self._execute_strategy_for_instance(code, k_data, strategy_instance, strategy_name)
                        if result and isinstance(result, dict):
                            # Stock was selected, add to results
                            selected_stocks.append(code)
                            selected_scores[code] = result.get('score', 0.0)
                            # Store selection reason
                            selection_reasons[code] = result.get('selection_reason', "")
                            # Store technical analysis data
                            technical_analysis_data[code] = result.get('technical_analysis', {})
                            # Store golden cross flag (default to False if not present)
                            golden_cross_flags[code] = result.get('golden_cross', False)

                except Exception as e:
                    self.logger.warning(f"Error processing stock {code} for strategy {strategy_name}: {e}")
                    continue

            self.logger.info(f"Strategy {strategy_name} selected {len(selected_stocks)} stocks")
            if last_data_date:
                self.logger.info(f"Last data date used for selection: {last_data_date}")

            # Store results for this strategy
            strategy_results[strategy_name] = (selected_stocks, selection_reasons, selected_scores, technical_analysis_data)

        # Return format based on number of strategies
        if len(self.strategies) == 1:
            # Single strategy mode - return the 6-value tuple for backward compatibility
            strategy_name = self.strategies[0]['name']
            if strategy_name in strategy_results:
                selected_stocks, last_data_date, selected_scores, technical_analysis_data = strategy_results[strategy_name]
                # Create golden_cross_flags (default all to False for now)
                golden_cross_flags = {code: False for code in selected_stocks}
                return (
                    selected_stocks,
                    last_data_date,
                    golden_cross_flags,
                    selected_scores,
                    technical_analysis_data,
                    strategy_results
                )

        # Multiple strategies mode - return the dictionary format
        return strategy_results

    def _execute_strategy_for_instance(self, code: str, k_data, strategy_instance, strategy_name):
        """
        Execute strategy by calling the dynamic strategy instance

        Args:
            code: Stock code
            k_data: K-line data
            strategy_instance: The strategy instance to execute
            strategy_name: Name of the strategy

        Returns:
            Complete strategy result structure including all fields from strategy execution
        """
        try:
            if strategy_instance and k_data is not None and not k_data.empty:
                # Call the strategy's analyze method for individual stock selection
                meets_criteria, selection_reason, score, breakout_signal = strategy_instance.analyze(k_data)

                if meets_criteria:
                    # Get technical analysis data
                    technical_analysis = strategy_instance.get_technical_analysis_data(k_data)

                    # Calculate position size based on score
                    position_size = 0.0
                    if hasattr(strategy_instance, '_calculate_position_from_score'):
                        position_size = strategy_instance._calculate_position_from_score(score)

                    # Return the complete strategy result structure
                    return {
                        "code": code,
                        "score": score,
                        "selection_reason": selection_reason,
                        "technical_analysis": technical_analysis,
                        "breakout_signal": breakout_signal,
                        "position": position_size,
                    }

            return None
        except Exception as e:
            self.logger.warning(f"Error executing strategy {strategy_name} for stock {code}: {e}")
            return None

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

    def save_selected_stocks(self, strategy_results: Dict[str, Tuple[List[str], Optional[str], Dict[str, float], Dict[str, Dict]]],
                           date: Optional[str] = None) -> bool:
        """
        Save selected stocks from multiple strategies to database

        Args:
            strategy_results: Dictionary mapping strategy names to tuples of
                            (selected stock codes, last data date, scores, technical_analysis_data)
            date: Selection date

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Import here to avoid circular imports
            from data.database_operations import DatabaseOperations

            # Create database operations instance
            db_ops = DatabaseOperations(self.db_manager)

            # Ensure date is not None
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')

            # Process each strategy's results
            for strategy_name, (selected_stocks, last_data_date, scores, technical_analysis_data) in strategy_results.items():
                if not selected_stocks:
                    self.logger.info(f"No stocks selected by strategy {strategy_name}, skipping save")
                    continue

                # Convert stocks list to the expected format (list of dicts)
                stocks_data = []
                for stock_code in selected_stocks:
                    # Get score from scores dictionary
                    score = scores.get(stock_code, 0.0) if scores else 0.0

                    # Get technical analysis data from strategy results if available
                    value_text = ""
                    if technical_analysis_data and stock_code in technical_analysis_data:
                        # Use the new unified formatter
                        value_text = StrategyResultFormatter.format_value_field(
                            stock_code=stock_code,
                            technical_analysis_data=technical_analysis_data[stock_code],
                            strategy_name=strategy_name
                        )
                    elif scores and stock_code in scores:
                        # Extract technical data from score reason text
                        score_text = scores[stock_code]
                        # Use the new unified formatter with reason text
                        value_text = StrategyResultFormatter.format_value_field(
                            stock_code=stock_code,
                            technical_analysis_data=None,
                            strategy_name=strategy_name
                        )
                    else:
                        # Default fallback using the new formatter
                        value_text = StrategyResultFormatter.format_value_field(
                            stock_code=stock_code,
                            technical_analysis_data=None,
                            strategy_name=strategy_name
                        )

                    # Normalize score to 0-1 range and round to 2 decimal places
                    # Handle different score ranges:
                    # - Some strategies return scores in 0-1 range
                    # - Some strategies return scores in 0-100 range
                    if score is not None:
                        score_float = float(score)
                        # If score is greater than 1, assume it's in 0-100 range and normalize it
                        if score_float > 1.0:
                            normalized_score = max(0.0, min(1.0, score_float / 100.0))
                        else:
                            # Score is already in 0-1 range
                            normalized_score = max(0.0, min(1.0, score_float))
                    else:
                        normalized_score = 0.0

                    rounded_score = round(normalized_score, 2)

                    # Get the strategy result for this stock
                    strategy_result = None
                    # Try to get the original strategy execution result with selection_reason
                    if strategy_name in strategy_results:
                        selected_stocks, selection_reasons, selected_scores, technical_analysis_data = strategy_results[strategy_name]
                        if stock_code in selected_stocks:
                            # Use the existing technical analysis data and scores
                            # No need to re-execute strategy as we already have the results
                            strategy_result = {
                                'score': selected_scores.get(stock_code, 0.0),
                                'analysis': technical_analysis_data.get(stock_code, {}),
                                'selection_reason': selection_reasons.get(stock_code, "")  # Get selection_reason from selection_reasons dict
                            }

                            # Try to extract selection_reason from technical analysis data if not already set
                            if not strategy_result['selection_reason'] and stock_code in technical_analysis_data:
                                tech_data = technical_analysis_data[stock_code]
                                if 'selection_reason' in tech_data:
                                    strategy_result['selection_reason'] = tech_data['selection_reason']
                                elif 'reason' in tech_data:
                                    strategy_result['selection_reason'] = tech_data['reason']

                    # Create value data with required structure
                    value_content = {
                        "code": stock_code,
                        "score": rounded_score,
                        "selection_reason": "",  # Will be populated from strategy result
                        "technical_analysis": {},
                        "breakout_signal": False,
                        "position": 0.0,
                    }

                    # Populate from strategy result if available
                    if strategy_result:
                        if 'analysis' in strategy_result:
                            value_content['technical_analysis'] = strategy_result['analysis']
                        # Extract selection reason from strategy result
                        if 'selection_reason' in strategy_result:
                            value_content['selection_reason'] = strategy_result['selection_reason']
                        elif 'reason' in strategy_result:
                            value_content['selection_reason'] = strategy_result['reason']
                        # Also check in analysis if not found in strategy_result
                        elif 'selection_reason' in strategy_result.get('analysis', {}):
                            value_content['selection_reason'] = strategy_result['analysis']['selection_reason']
                        elif 'reason' in strategy_result.get('analysis', {}):
                            value_content['selection_reason'] = strategy_result['analysis']['reason']

                        # Set breakout signal and position based on score
                        value_content['breakout_signal'] = rounded_score > 0.5
                        value_content['position'] = round(min(rounded_score * 0.1, 0.1), 2)  # Max 10% position, rounded to 2 decimals

                    # Add signal field (based on breakout_signal)
                    value_content['signal'] = "买入" if value_content['breakout_signal'] else "观望"

                    # Convert to JSON string
                    import json
                    value_json = json.dumps(value_content, ensure_ascii=False)

                    stock_info = {
                        'code': stock_code,
                        'trend': {
                            strategy_name: {
                                'score': rounded_score,
                                'value': value_json
                            }
                        }
                    }
                    stocks_data.append(stock_info)

                # Get the actual strategy ID from database
                strategy_id = None
                strategies = self.db_manager.get_strategies()

                # Try to find the current strategy in the database
                for strategy in strategies:
                    if strategy.get('name') == strategy_name:
                        strategy_id = strategy.get('_id')
                        break

                # If we couldn't find the strategy, use a default
                if not strategy_id:
                    strategy_id = f"unknown_{strategy_name}"

                # Use strategy_id as the strategy key
                strategy_key = strategy_id

                # Get strategy parameters for this strategy
                strategy_params = {}
                for strategy_info in self.strategies:
                    if strategy_info['name'] == strategy_name:
                        strategy_params = strategy_info['params']
                        break

                # Save the selected stocks to pool
                save_result = db_ops.save_selected_stocks_to_pool(
                    strategy_key=strategy_key,
                    agent_name="WeeklySelector",
                    strategy_id=strategy_id,
                    strategy_name=strategy_name,
                    stocks=stocks_data,
                    date=date,
                    last_data_date=last_data_date,
                    strategy_params=strategy_params  # Pass actual strategy parameters
                )

                if save_result:
                    self.logger.info(f"Successfully saved {len(selected_stocks)} stocks for strategy {strategy_name}")
                else:
                    self.logger.error(f"Failed to save stocks for strategy {strategy_name}")

            return True
        except Exception as e:
            self.logger.error(f"Error saving selected stocks: {e}")
            return False

