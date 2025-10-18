"""
Weekly Stock Selector Agent
A clean framework that dynamically loads strategies from database with new architecture
"""

import sys
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# Add project root to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from data.mongodb_manager import MongoDBManager
import logging
import importlib
import pandas as pd

# Add project root to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from interfaces.data_interface import DataProviderInterface, StandardDataFormat

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class StrategyStockResult:
    """Data class representing detailed results for a single stock from a strategy"""

    code: str
    score: float
    selection_reason: str
    technical_analysis: Dict
    breakout_signal: bool
    position: float
    json_value: str
    meets_criteria: bool


StrategyResultsType = Dict[str, Tuple[List[str], Dict[str, float], Dict[str, str]]]


class WeeklyStockSelector(BaseAgent, DataProviderInterface):
    """
    Weekly Stock Selector Agent - Clean framework with new architecture
    Dynamically loads strategies from database and executes them
    """

    def __init__(
        self,
        db_manager: MongoDBManager,
        strategy_ids: Optional[List[str]] = None,
    ):
        """
        Initialize the weekly stock selector framework

        Args:
            db_manager: MongoDBManager instance for database operations
            strategy_ids: Optional list of strategy IDs to load specific strategies, if None loads all strategies
        """
        super().__init__("WeeklyStockSelector")
        self.db_manager = db_manager
        self.strategy_ids = strategy_ids

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
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        for i, code in enumerate(stock_codes):
            try:
                if i % 500 == 0:  # Log progress every 500 stocks
                    self.logger.info(
                        f"Processing stock {i + 1}/{len(stock_codes)}: {code}"
                    )

                # Get adjusted daily K-line data
                daily_k_data = self.db_manager.get_adjusted_k_data(
                    code, start_date, end_date, frequency="daily"
                )

                # Convert to weekly data
                if not daily_k_data.empty:
                    weekly_data = self._convert_daily_to_weekly(daily_k_data)

                    # Validate and store data for this stock
                    if not weekly_data.empty and StandardDataFormat.validate_data(
                        weekly_data
                    ):
                        stock_data[code] = weekly_data
                    else:
                        self.logger.warning(
                            f"Invalid or no weekly data available for {code}"
                        )

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
        Load strategy configurations from database for the weekly selector agent
        """
        try:
            # Get the weekly selector agent from database
            agent = self.db_manager.agents_collection.find_one(
                {"name": "趋势选股Agent"}
            )
            if not agent:
                self.log_error("Weekly selector agent not found in database")
                return

            # Get strategy IDs assigned to this agent
            strategy_ids = agent.get("strategies", [])
            if not strategy_ids:
                self.log_warning("No strategies assigned to weekly selector agent")
                return

            # Load only the strategies assigned to this agent
            from bson import ObjectId

            selected_strategies = []
            for strategy_id in strategy_ids:
                strategy = self.db_manager.strategies_collection.find_one(
                    {"_id": ObjectId(strategy_id)}
                )
                if strategy:
                    selected_strategies.append(strategy)

            # Store strategy configurations
            self.strategy_configs = selected_strategies
            self.log_info(
                f"Loaded {len(self.strategy_configs)} strategies for weekly selector agent"
            )

        except Exception as e:
            self.log_error(f"Error loading strategies from database: {e}")

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
                    strategy_params = strategy_config.get("parameters", {})
                    strategy_name = strategy_config.get("name", "Unknown")

                    # Extract file and class from program field if it exists
                    strategy_file = None
                    strategy_class_name = None

                    if "program" in strategy_config and isinstance(
                        strategy_config["program"], dict
                    ):
                        strategy_file = strategy_config["program"].get("file", "")
                        strategy_class_name = strategy_config["program"].get(
                            "class", ""
                        )
                    else:
                        # Fallback to direct file and class_name fields
                        strategy_file = strategy_config.get("file", "")
                        strategy_class_name = strategy_config.get("class_name", "")

                    if not strategy_file or not strategy_class_name:
                        self.logger.warning(
                            f"Strategy file or class not specified for {strategy_name}"
                        )
                        continue

                    # Dynamically import the strategy module
                    module_name = strategy_file

                    # Handle different formats of strategy file specification
                    if isinstance(strategy_file, dict):
                        # Handle the case where program is a dict with file and class fields
                        file_name = strategy_file.get("file", "")
                        if file_name:
                            if not file_name.endswith(".py"):
                                if "." not in file_name and not file_name.startswith(
                                    "strategies."
                                ):
                                    module_name = f"strategies.{file_name}"
                            else:
                                module_name = file_name[:-3]
                                if (
                                    "." not in module_name
                                    and not module_name.startswith("strategies.")
                                ):
                                    module_name = f"strategies.{module_name}"
                        else:
                            self.logger.error(
                                f"Invalid program field format for strategy {strategy_name}"
                            )
                            continue
                    elif isinstance(strategy_file, str):
                        # If it's just a filename without .py extension and without package prefix, add the strategies prefix
                        if not strategy_file.endswith(".py"):
                            if (
                                "." not in strategy_file
                                and not strategy_file.startswith("strategies.")
                            ):
                                module_name = f"strategies.{strategy_file}"
                        else:
                            # If it has .py extension, remove it for import
                            module_name = strategy_file[:-3]
                            # Add strategies prefix if needed
                            if "." not in module_name and not module_name.startswith(
                                "strategies."
                            ):
                                module_name = f"strategies.{module_name}"

                    strategy_module = importlib.import_module(module_name)

                    # Get the strategy class
                    strategy_class = getattr(strategy_module, strategy_class_name)

                    # Instantiate the strategy with parameters
                    strategy_instance = strategy_class(params=strategy_params)

                    # Store strategy instance with its configuration
                    self.strategies.append(
                        {
                            "instance": strategy_instance,
                            "name": strategy_name,
                            "config": strategy_config,
                            "params": strategy_params,
                        }
                    )

                    self.logger.info(
                        f"Successfully loaded dynamic strategy: {strategy_name}"
                    )
                except Exception as e:
                    self.logger.error(f"Error loading strategy {strategy_name}: {e}")
                    continue

            self.logger.info(f"Successfully loaded {len(self.strategies)} strategies")
        except Exception as e:
            self.logger.error(f"Error loading dynamic strategies: {e}")
            raise

    def select_stocks(
        self, date: Optional[str] = None
    ) -> Dict[str, Tuple[List[str], Dict[str, float], Dict[str, str]]]:
        """
        Select stocks using all dynamically loaded strategies

        Args:
            date: Selection date (YYYY-MM-DD), defaults to today

        Returns:
                Dictionary mapping strategy names to tuples of (selected stock codes, scores, json_values)
                where:
                - selected stock codes: List of stock codes that meet the strategy criteria
                - scores: Dictionary mapping stock codes to their strategy scores
                - json_values: Dictionary mapping stock codes to JSON strings containing detailed analysis data
                  Each JSON string contains fields: code, score, selection_reason, technical_analysis,
                  breakout_signal, position, and meets_criteria
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        self.logger.info(
            f"Selecting stocks for week of {date} using {len(self.strategies)} strategies"
        )

        # Get all stock codes from database - only once
        all_codes = self.db_manager.get_stock_codes()

        # Get standard format data using the new interface - only once
        stock_data = self.get_standard_data(all_codes)
        self.logger.info(f"Retrieved data for {len(stock_data)} stocks")

        # Dictionary to store results for each strategy
        strategy_results = {}

        # Execute each strategy using the same stock data
        for strategy_info in self.strategies:
            strategy_name = strategy_info["name"]
            strategy_instance = strategy_info["instance"]

            self.logger.info(f"Executing strategy: {strategy_name}")

            # Filter stocks based on criteria for this strategy
            selected_stocks = []
            selected_scores = {}  # Store scores for each selected stock
            json_values = {}  # Store JSON values for each selected stock
            last_data_date = None

            # Process each stock's data for this strategy
            for code, k_data in stock_data.items():
                try:
                    # Update last_data_date
                    if not k_data.empty and "date" in k_data.columns:
                        stock_last_date = k_data["date"].iloc[-1]
                        if hasattr(stock_last_date, "strftime"):
                            stock_last_date = stock_last_date.strftime("%Y-%m-%d")
                        else:
                            stock_last_date = str(stock_last_date)

                        # Update last_data_date to the latest date among all selected stocks
                        if stock_last_date and (
                            not last_data_date or stock_last_date > last_data_date
                        ):
                            last_data_date = stock_last_date

                    # Execute strategy
                    if strategy_instance and not k_data.empty:
                        result = self._execute_strategy_for_instance(
                            code, k_data, strategy_instance, strategy_name
                        )
                        if result and isinstance(result, dict):
                            # Check if stock meets criteria
                            if result.get("meets_criteria", False):
                                # Stock was selected, add to results
                                selected_stocks.append(code)
                                selected_scores[code] = result.get("score", 0.0)
                                # Store the actual JSON value for database writing
                                json_values[code] = result.get("json_value", "")

                except Exception as e:
                    self.logger.warning(
                        f"Error processing stock {code} for strategy {strategy_name}: {e}"
                    )
                    continue

            self.logger.info(
                f"Strategy {strategy_name} selected {len(selected_stocks)} stocks"
            )
            if last_data_date:
                self.logger.info(f"Last data date used for selection: {last_data_date}")

            # Store results for this strategy
            # Sort stocks by score and take top 10
            sorted_stocks = sorted(
                selected_stocks,
                key=lambda code: selected_scores.get(code, 0.0),
                reverse=True,
            )
            top_10_stocks = sorted_stocks[:10]

            # Create filtered dictionaries for top 10 stocks
            top_10_scores = {
                code: selected_scores[code]
                for code in top_10_stocks
                if code in selected_scores
            }
            top_10_json_values = {
                code: json_values[code] for code in top_10_stocks if code in json_values
            }

            strategy_results[strategy_name] = (
                top_10_stocks,
                top_10_scores,  # 这是字典，包含每个股票的分数
                top_10_json_values,  # 这是字典，包含每个股票的JSON值
            )

        # Multiple strategies mode - return the dictionary format
        # self.logger.info(strategy_results)
        return strategy_results

    def _execute_strategy_for_instance(
        self, code: str, k_data, strategy_instance, strategy_name
    ):
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
                # Call the strategy's analyze method
                # For volume_breakout_strategy, format is: (meets_criteria, score, value)
                meets_criteria, score, value = strategy_instance.analyze(
                    k_data, code=code
                )

                # Return the complete strategy result structure
                return {
                    "code": code,
                    "score": score,
                    "json_value": value,  # Store the JSON string value
                    "meets_criteria": meets_criteria,  # Store whether criteria were met
                }

            return None
        except Exception as e:
            self.logger.warning(
                f"Error executing strategy {strategy_name} for stock {code}: {e}"
            )
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
            daily_data = daily_data.set_index("date")

            # Resample to weekly data
            weekly_data = daily_data.resample("W-FRI").agg(
                {
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum",
                    "amount": "sum",
                }
            )

            # Remove any rows with NaN values
            weekly_data = weekly_data.dropna()

            # Reset index to make date a column again
            weekly_data = weekly_data.reset_index()

            return weekly_data

        except Exception as e:
            self.logger.error(f"Error converting daily to weekly data: {e}")
            return pd.DataFrame()

    def save_selected_stocks(
        self,
        strategy_results: Dict[str, Tuple[List[str], Dict[str, float], Dict[str, str]]],
        date: Optional[str] = None,
    ) -> bool:
        """
        Save selected stocks to pool collection for multiple strategies

        Args:
            strategy_results: Dictionary mapping strategy names to tuples of
                            (selected_stocks, scores, json_values)
            date: Selection date, defaults to current date

        Returns:
            True if successful, False otherwise
        """
        try:
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")

            # Collect all data from all strategies first
            all_stocks_data = []  # List to collect all stock data from all strategies
            all_strategy_ids = []  # List to collect all strategy IDs
            all_strategy_names = []  # List to collect all strategy names

            # Dictionary to track stocks by code to avoid duplicates
            stocks_by_code = {}

            # Process each strategy's results and collect data
            for strategy_name, strategy_result in strategy_results.items():
                # Extract strategy results using standard format
                # Standard format: (selected_stocks, scores, json_values)
                selected_stocks = strategy_result[0]
                scores = strategy_result[1]  # 分数字典
                json_values = strategy_result[2]  # JSON值字典

                # Find the strategy configuration to get strategy_id
                strategy_config = None
                for config in self.strategy_configs:
                    if config.get("name") == strategy_name:
                        strategy_config = config
                        break

                if not strategy_config:
                    self.logger.warning(
                        f"Strategy configuration not found for {strategy_name}"
                    )
                    continue

                # Get strategy_id and strategy_key
                strategy_id = str(strategy_config.get("_id", ""))
                strategy_key = strategy_config.get("name", strategy_name)

                # Add strategy ID and name to collections
                if strategy_id and strategy_id not in all_strategy_ids:
                    all_strategy_ids.append(strategy_id)
                if strategy_name and strategy_name not in all_strategy_names:
                    all_strategy_names.append(strategy_name)

                # Process stocks for this strategy
                for stock_code in selected_stocks:
                    # Get score from scores dictionary - use the original score directly
                    score = 0.0
                    if scores and isinstance(scores, dict):
                        score = scores.get(stock_code, 0.0)
                    else:
                        self.logger.warning(
                            f"scores is not a dictionary for stock {stock_code}, using default score 0.0"
                        )

                    # Get selection value from strategy results if available - use the JSON value directly
                    value_text = ""
                    if (
                        json_values
                        and isinstance(json_values, dict)
                        and stock_code in json_values
                    ):
                        # Use the JSON value directly
                        value_text = json_values[stock_code]
                    else:
                        # Fallback to simple text
                        value_text = f"Selected by {strategy_name}"

                    # Create stock data with trend information
                    stock_data = {
                        "code": stock_code,
                        "trend": {
                            strategy_key: {
                                "score": score,
                                "value": value_text,
                            }
                        },
                    }

                    # Check if we already have this stock
                    if stock_code in stocks_by_code:
                        # Merge trend information for existing stock
                        existing_stock = stocks_by_code[stock_code]
                        existing_stock["trend"][strategy_key] = {
                            "score": score,
                            "value": value_text,
                        }
                    else:
                        # Add new stock
                        stocks_by_code[stock_code] = stock_data

            # Convert stocks_by_code dictionary to list
            all_stocks_data = list(stocks_by_code.values())

            # Get pool collection
            collection = self.db_manager.db["pool"]

            # Find the latest pool record
            latest_record = collection.find_one(sort=[("_id", -1)])

            if not latest_record:
                self.log_error("No pool record found")
                return False

            # Determine if we should update existing record or create new one based on year-week
            # Get year-week from latest record's _id (assuming _id is in year-week format like "2025-41")
            latest_record_year_week = latest_record["_id"]

            # Validate that the _id is in the expected year-week format
            if not (
                isinstance(latest_record_year_week, str)
                and "-" in latest_record_year_week
                and len(latest_record_year_week) == 7
            ):
                # If _id is not in expected format, use current week
                latest_record_year_week = f"{datetime.now().isocalendar()[0]}-{datetime.now().isocalendar()[1]:02d}"

            current_year_week = f"{datetime.now().isocalendar()[0]}-{datetime.now().isocalendar()[1]:02d}"

            is_same_week = latest_record_year_week == current_year_week

            if is_same_week:
                # UPDATE existing record - same week
                # Completely replace all data instead of merging
                update_data = {
                    "$set": {
                        "stocks": all_stocks_data,
                        "updated_at": datetime.now(),
                        "count": len(all_stocks_data),
                        "strategy_key": all_strategy_ids,
                        "strategy_name": all_strategy_names,
                    }
                }

                # Update the pool record
                result = collection.update_one(
                    {"_id": latest_record["_id"]}, update_data
                )
            else:
                # CREATE new record - different week
                # Prepare new record data with correct _id (year-week format)
                current_year_week = f"{datetime.now().isocalendar()[0]}-{datetime.now().isocalendar()[1]:02d}"
                new_record = {
                    "_id": current_year_week,
                    "stocks": all_stocks_data,
                    "strategy_key": all_strategy_ids,  # Use all strategy IDs
                    "strategy_name": all_strategy_names,  # Use all strategy names
                    "count": len(all_stocks_data),
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                }

                # Insert new pool record
                result = collection.insert_one(new_record)

            if (
                hasattr(result, "modified_count") and result.modified_count > 0
            ) or result.inserted_id:
                self.log_info(
                    f"Successfully {'updated' if is_same_week else 'created'} pool with {len(all_stocks_data)} stocks from {len(all_strategy_names)} strategies"
                )
                success = True
            else:
                self.log_warning("No changes made to pool record")
                success = False

            if success:
                self.logger.info(
                    f"Successfully saved {len(all_stocks_data)} stocks from {len(all_strategy_names)} strategies"
                )
            else:
                self.logger.error(f"Failed to save stocks from strategies")

            return success
        except Exception as e:
            self.logger.error(f"Error saving selected stocks: {e}")
            return False

    def run(self) -> bool:
        """
        Main execution method for the weekly stock selector agent.
        This method is required by the BaseAgent abstract class.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Execute weekly selection
            strategy_results = self.select_stocks()

            # Calculate total number of selected stocks across all strategies
            total_stocks = 0
            for strategy_name, strategy_result in strategy_results.items():
                selected_stocks = strategy_result[
                    0
                ]  # First element is list of selected stocks
                total_stocks += len(selected_stocks)

            # Save selection to pool
            success = self.save_selected_stocks(
                strategy_results, date=datetime.now().strftime("%Y-%m-%d")
            )

            # Return success status
            return success
        except Exception as e:
            self.logger.error(f"Error running weekly selector agent: {e}")
            return False
