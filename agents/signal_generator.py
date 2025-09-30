"""
Signal Generator Agent
Generates trading signals by executing strategies and writing results to database.
"""

import sys
import os
# Add project root to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import pandas as pd
import importlib

from agents.base_agent import BaseAgent
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient
from interfaces.data_interface import DataProviderInterface, StandardDataFormat

# Configure logging
logger = logging.getLogger(__name__)


class SignalGenerator(BaseAgent, DataProviderInterface):
    """
    Signal Generator Agent - Executes strategies to generate trading signals
    and writes results to database
    """

    def __init__(
        self,
        db_manager: MongoDBManager,
        data_fetcher: AkshareClient,
        name: str = "SignalGenerator",
        strategy_id: Optional[str] = None,
    ):
        """
        Initialize the signal generator agent

        Args:
            db_manager: MongoDBManager instance for database operations
            data_fetcher: AkshareClient instance for data fetching
            name: Name of the agent
            strategy_id: Optional strategy ID to load specific strategy instead of first one
        """
        super().__init__(name)
        self.db_manager = db_manager
        self.data_fetcher = data_fetcher
        self.strategy_id = strategy_id
        self.logger = logging.getLogger(__name__)

        # Strategy components
        self.strategy_names = []
        self.strategy_files = []
        self.strategy_class_names = []
        self.strategy_params_list = []
        self.strategy_instances = []

        # Load strategies from database
        self._load_strategies_from_db()

        # Load and initialize the dynamic strategies
        self._load_dynamic_strategies()

    def _load_strategies_from_db(self):
        """
        Load all strategy configurations from database
        """
        try:
            # Get the signal generation agent from database
            agent = self.db_manager.agents_collection.find_one(
                {"name": "信号生成Agent"}
            )
            if not agent:
                self.log_error("Signal generation agent not found in database")
                return

            # Get strategy IDs assigned to this agent
            strategy_ids = agent.get("strategies", [])
            if not strategy_ids:
                self.log_warning("No strategies assigned to signal generation agent")
                return

            # Load all strategies
            from bson import ObjectId
            for strategy_id in strategy_ids:
                selected_strategy = self.db_manager.strategies_collection.find_one(
                    {"_id": ObjectId(strategy_id)}
                )

                if not selected_strategy:
                    self.log_warning(f"Strategy {strategy_id} not found in database")
                    continue

                # Extract strategy information
                self.strategy_params_list.append(selected_strategy.get("parameters", {}))
                self.strategy_names.append(selected_strategy.get("name", "Unknown"))

                # Extract file and class from program field if it exists
                if "program" in selected_strategy and isinstance(
                    selected_strategy["program"], dict
                ):
                    self.strategy_files.append(selected_strategy["program"].get("file", ""))
                    self.strategy_class_names.append(selected_strategy["program"].get(
                        "class", ""
                    ))
                    self.log_info("Loaded strategy file and class from program field")
                else:
                    # Fallback to direct file and class_name fields
                    self.strategy_files.append(selected_strategy.get("file", ""))
                    self.strategy_class_names.append(selected_strategy.get("class_name", ""))

                self.log_info("Loaded strategy from database: %s" % selected_strategy.get("name", "Unknown"))

        except Exception as e:
            self.log_error(f"Error loading strategies from database: {e}")

    def _load_dynamic_strategies(self):
        """
        Dynamically load all strategies from files and instantiate the strategy classes
        """
        try:
            # Clear existing instances
            self.strategy_instances = []

            # Load each strategy
            for i in range(len(self.strategy_files)):
                strategy_file = self.strategy_files[i]
                strategy_class_name = self.strategy_class_names[i]
                strategy_name = self.strategy_names[i]
                strategy_params = self.strategy_params_list[i] if i < len(self.strategy_params_list) else {}

                if not strategy_file or not strategy_class_name:
                    self.log_warning(f"Strategy file or class not specified for strategy {i}")
                    continue

                # Dynamically import the strategy module
                # Handle both direct file names and package.module format
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
                            if "." not in module_name and not module_name.startswith(
                                "strategies."
                            ):
                                module_name = f"strategies.{module_name}"
                    else:
                        self.log_error("Invalid program field format")
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
                strategy_class = getattr(
                    strategy_module, strategy_class_name
                )

                # Instantiate the strategy with parameters
                strategy_instance = strategy_class(
                    name=strategy_name, params=strategy_params
                )

                # Add to instances list
                self.strategy_instances.append(strategy_instance)

                self.log_info(
                    "Successfully loaded dynamic strategy: %s" % strategy_name
                )
        except Exception as e:
            self.log_error(f"Error loading dynamic strategies: {e}")
            raise

    def get_standard_data(self, stock_codes: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Get standard format data for the given stock codes.
        For signal generation, we don't need K-line data, so return empty DataFrames.

        Args:
            stock_codes: List of stock codes to get data for

        Returns:
            Dictionary mapping stock codes to standard format DataFrames (empty for signal generation)
        """
        self.log_info(f"Signal generation - no K-line data needed for {len(stock_codes)} stocks")

        # For signal generation, we don't need K-line data
        # Return empty DataFrames for compatibility with the interface
        stock_data = {}
        for code in stock_codes:
            stock_data[code] = StandardDataFormat.create_empty_dataframe()

        self.log_info(f"Returned empty data for {len(stock_data)} stocks (signal generation)")
        return stock_data

    def get_data_for_stock(self, stock_code: str) -> pd.DataFrame:
        """
        Get standard format data for a single stock.

        Args:
            stock_code: Stock code to get data for

        Returns:
            Standard format DataFrame with stock data
        """
        stock_data = self.get_standard_data([stock_code])
        return stock_data.get(stock_code, StandardDataFormat.create_empty_dataframe())

    def generate_signals(self) -> bool:
        """
        Generate trading signals by executing assigned strategies and save results to database

        Returns:
            True if successful, False otherwise
        """
        self.log_info(
            "Generating signals using dynamic strategy loading"
        )

        try:
            # Get stock codes from the latest record in pool collection
            pool_collection = self.db_manager.db["pool"]
            latest_pool_record = pool_collection.find_one(sort=[("_id", -1)])

            if not latest_pool_record:
                self.log_error("No records found in pool collection")
                return False

            # Extract stock codes from the latest pool record
            pool_stocks = latest_pool_record.get("stocks", [])
            stock_codes = [
                stock.get("code") for stock in pool_stocks if stock.get("code")
            ]

            if not stock_codes:
                self.log_error("No stock codes found in latest pool record")
                return False

            self.log_info(
                f"Analyzing {len(stock_codes)} stocks from latest pool record"
            )

            # Get standard format data using the new interface
            stock_data = self.get_standard_data(stock_codes)

            if not stock_data:
                self.log_error("No stock data available for analysis")
                return False

            # Execute all dynamically loaded strategies
            all_selected_stocks = []
            for i, strategy_instance in enumerate(self.strategy_instances):
                try:
                    strategy_name = self.strategy_names[i] if i < len(self.strategy_names) else f"Strategy_{i}"
                    # Execute the strategy
                    self.log_info(f"Executing strategy: {strategy_name}")
                    selected_stocks = strategy_instance.execute(
                        stock_data, "信号生成Agent", self.db_manager
                    )

                    # Add strategy identifier to each selected stock
                    for stock in selected_stocks:
                        # Only pass necessary fields to update_latest_pool_record
                        signal_stock = {
                            'code': stock.get('code'),
                            'selection_reason': stock.get('selection_reason', stock.get('value', '')),
                            'score': stock.get('score', 0),  # Include the actual score from strategy
                            'strategy_name': strategy_name,
                            'signals': stock.get('signals', {})  # Include the actual signals data from strategy
                        }
                        all_selected_stocks.append(signal_stock)

                    self.log_info(
                        f"Strategy {strategy_name} generated signals for {len(selected_stocks)} stocks"
                    )

                except Exception as e:
                    strategy_name = self.strategy_names[i] if i < len(self.strategy_names) else f"Strategy_{i}"
                    self.log_error(f"Error executing strategy {strategy_name}: {e}")

            self.log_info(
                f"Signal generation completed. Total selected stocks: {len(all_selected_stocks)}"
            )

            # Update the latest pool record with signal generation results
            success = self.update_latest_pool_record(all_selected_stocks)
            return success

        except Exception as e:
            self.log_error(f"Error generating signals: {e}")
            return False

    def update_latest_pool_record(self, signal_stocks: List[Dict]) -> bool:
        """
        Update the latest pool record with signal generation results

        Args:
            signal_stocks: List of stocks with signal generation data

        Returns:
            True if updated successfully, False otherwise
        """
        try:
            # Get pool collection
            collection = self.db_manager.db["pool"]

            # Find the latest pool record
            # Using _id field for sorting
            latest_pool_record = collection.find_one(sort=[("_id", -1)])

            if not latest_pool_record:
                self.log_error("No records found in pool collection")
                return False

            # Get existing stocks from the latest record
            existing_stocks = latest_pool_record.get("stocks", [])

            # Create a mapping of existing stocks by code for easy lookup
            existing_stock_map = {stock.get("code"): stock for stock in existing_stocks}

            # Update signal data for existing stocks only
            for signal_stock in signal_stocks:
                code = signal_stock.get('code')
                strategy_name = signal_stock.get('strategy_name', 'unknown_strategy')

                if code in existing_stock_map:
                    # Normalize score to 0-1 range and round to 2 decimal places
                    # Handle different score ranges:
                    # - Some strategies return scores in 0-1 range
                    # - Some strategies return scores in 0-100 range
                    score = signal_stock.get('score', 0.0)
                    try:
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
                    except (ValueError, TypeError):
                        # If score conversion fails, default to 0.0
                        self.log_warning(f"Invalid score value for stock {code}: {score}")
                        normalized_score = 0.0

                    rounded_score = round(normalized_score, 2)

                    # Get strategy name and validate it
                    strategy_name = signal_stock.get('strategy_name', 'unknown_strategy')
                    if not strategy_name or not isinstance(strategy_name, str):
                        strategy_name = 'unknown_strategy'

                    # Update the signals field for the existing stock
                    if 'signals' not in existing_stock_map[code]:
                        existing_stock_map[code]['signals'] = {}

                    # Get the signal data from the strategy result
                    signal_data = signal_stock.get('signals', {})
                    # Use the actual strategy name from database configuration instead of agent class name
                    strategy_name = signal_stock.get('strategy_name', 'unknown_strategy')
                    if not strategy_name or not isinstance(strategy_name, str):
                        strategy_name = 'unknown_strategy'

                    existing_stock_map[code]['signals'][strategy_name] = signal_data

            # Prepare cleaned stocks for database update
            # Only preserve essential fields: code, trend, tech, fund, pub, and signals
            cleaned_stocks = []
            for stock in existing_stocks:
                # Create a clean stock with only essential fields
                clean_stock = {
                    'code': stock.get('code'),
                    'trend': stock.get('trend', {})  # Preserve trend field if it exists
                }

                # Update the tech field if it exists in the updated stock
                updated_stock = existing_stock_map.get(stock.get('code'))
                if updated_stock:
                    if 'tech' in updated_stock:
                        clean_stock['tech'] = updated_stock['tech']
                    if 'fund' in updated_stock:
                        clean_stock['fund'] = updated_stock['fund']
                    if 'pub' in updated_stock:
                        clean_stock['pub'] = updated_stock['pub']
                    if 'signals' in updated_stock:
                        clean_stock['signals'] = updated_stock['signals']

                # Convert numpy types to native Python types for MongoDB compatibility
                from data.database_operations import DatabaseOperations
                db_ops = DatabaseOperations(self.db_manager)
                clean_stock = db_ops._convert_numpy_types(clean_stock)

                cleaned_stocks.append(clean_stock)

            # Update the latest pool record with modified stocks and only signals_at timestamp
            result = collection.update_one(
                {"_id": latest_pool_record["_id"]},
                {
                    "$set": {
                        "stocks": cleaned_stocks,
                        "signals_at": datetime.now(),
                    },
                    "$unset": {
                        "selected_stocks_count": "",
                        "strategy_execution_time": "",
                        "strategy_version": "",
                        "total_stocks_analyzed": ""
                    }
                },
            )

            if result.modified_count > 0:
                self.log_info(
                    f"Updated latest pool record with {len(signal_stocks)} signal generation stocks"
                )
            else:
                self.log_info("No changes made to the latest pool record")

            return True

        except Exception as e:
            self.log_error(
                f"Error updating latest pool record with signal generation: {e}"
            )
            return False

    def run(self) -> bool:
        """
        Main execution method for the signal generator agent.
        This method is required by the BaseAgent abstract class.

        Returns:
            True if successful, False otherwise
        """
        return self.generate_signals()


# Example usage
if __name__ == "__main__":
    # This is just a placeholder to make the file importable
    pass

