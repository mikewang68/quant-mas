"""
Public Opinion Stock Selector Agent
Selects stocks based on public opinion analysis strategies with new architecture.
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


class PublicOpinionStockSelector(BaseAgent, DataProviderInterface):
    """
    Public Opinion Stock Selector Agent - Clean framework with new architecture
    Dynamically loads strategies from database and executes them
    """

    def __init__(
        self,
        db_manager: MongoDBManager,
        data_fetcher: AkshareClient,
        name: str = "PublicOpinionStockSelector",
        strategy_id: Optional[str] = None,
    ):
        """
        Initialize the public opinion stock selector framework

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
            # Get the public opinion analysis agent from database
            agent = self.db_manager.agents_collection.find_one(
                {"name": "舆情分析Agent"}
            )
            if not agent:
                self.log_error("Public opinion analysis agent not found in database")
                return

            # Get strategy IDs assigned to this agent
            strategy_ids = agent.get("strategies", [])
            if not strategy_ids:
                self.log_warning("No strategies assigned to 舆情分析 agent")
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
                    self.log_info(f"Loaded strategy file and class from program field: {selected_strategy['program'].get('file', '')}.{selected_strategy['program'].get('class', '')}")
                else:
                    # Fallback to direct file and class_name fields
                    self.strategy_files.append(selected_strategy.get("file", ""))
                    self.strategy_class_names.append(selected_strategy.get("class_name", ""))

                self.log_info(f"Loaded strategy from database: {selected_strategy.get('name', 'Unknown')} (ID: {strategy_id})")

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

                self.log_info(f"Attempting to import module: {module_name}")
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

    def _load_dynamic_strategy(self):
        """
        Dynamically load strategy from file and instantiate the strategy class
        (Deprecated - kept for backward compatibility)
        """
        try:
            if not self.strategy_files or not self.strategy_class_names:
                self.log_warning("Strategy files or classes not specified")
                return

            # Load first strategy for backward compatibility
            strategy_file = self.strategy_files[0] if self.strategy_files else None
            strategy_class_name = self.strategy_class_names[0] if self.strategy_class_names else None
            strategy_name = self.strategy_names[0] if self.strategy_names else "Unknown"
            strategy_params = self.strategy_params_list[0] if self.strategy_params_list else {}

            if not strategy_file or not strategy_class_name:
                self.log_warning("Strategy file or class not specified")
                return

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
                    return
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

            self.strategy_module = importlib.import_module(module_name)

            # Get the strategy class
            self.strategy_class = getattr(
                self.strategy_module, strategy_class_name
            )

            # Instantiate the strategy with parameters
            self.strategy_instance = self.strategy_class(
                name=strategy_name, params=strategy_params
            )

            self.log_info(
                "Successfully loaded dynamic strategy: %s" % strategy_name
            )
        except Exception as e:
            self.log_error(f"Error loading dynamic strategy: {e}")
            raise

    def get_standard_data(self, stock_codes: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Get standard format data for the given stock codes.
        For public opinion analysis, we don't need K-line data, so return empty DataFrames.

        Args:
            stock_codes: List of stock codes to get data for

        Returns:
            Dictionary mapping stock codes to standard format DataFrames (empty for public opinion analysis)
        """
        self.log_info(f"Public opinion analysis - no K-line data needed for {len(stock_codes)} stocks")

        # For public opinion analysis, we don't need K-line data
        # Return empty DataFrames for compatibility with the interface
        stock_data = {}
        for code in stock_codes:
            stock_data[code] = StandardDataFormat.create_empty_dataframe()

        self.log_info(f"Returned empty data for {len(stock_data)} stocks (public opinion analysis)")
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

    def update_pool_with_public_opinion_analysis(self) -> bool:
        """
        Update pool with public opinion analysis results by executing assigned strategies

        Returns:
            True if successful, False otherwise
        """
        self.log_info(
            "Updating pool with public opinion analysis using dynamic strategy loading"
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
                    self.log_info(f"Strategy instance type: {type(strategy_instance)}")
                    self.log_info(f"Strategy parameters: {strategy_instance.params}")
                    selected_stocks = strategy_instance.execute(
                        stock_data, "舆情分析Agent", self.db_manager
                    )

                    # Add strategy identifier to each selected stock
                    for stock in selected_stocks:
                        stock['strategy_name'] = strategy_name
                        all_selected_stocks.append(stock)

                    self.log_info(
                        f"Strategy {strategy_name} selected {len(selected_stocks)} stocks"
                    )

                except Exception as e:
                    strategy_name = self.strategy_names[i] if i < len(self.strategy_names) else f"Strategy_{i}"
                    self.log_error(f"Error executing strategy {strategy_name}: {e}")

            self.log_info(
                f"Public opinion analysis completed. Total selected stocks: {len(all_selected_stocks)}"
            )

            # Update the latest pool record with public opinion analysis results
            success = self.update_latest_pool_record(all_selected_stocks)
            return success

        except Exception as e:
            self.log_error(f"Error updating pool with public opinion analysis: {e}")
            return False

    def update_latest_pool_record(self, public_opinion_stocks: List[Dict]) -> bool:
        """
        Update the latest pool record with public opinion analysis results

        Args:
            public_opinion_stocks: List of stocks with public opinion analysis data

        Returns:
            True if updated successfully, False otherwise
        """
        try:
            # Get pool collection
            collection = self.db_manager.db["pool"]

            # Find the latest pool record
            latest_pool_record = collection.find_one(sort=[("_id", -1)])

            if not latest_pool_record:
                self.log_error("No records found in pool collection")
                return False

            # Get existing stocks from the latest record
            existing_stocks = latest_pool_record.get("stocks", [])

            # Create a mapping of existing stocks by code for easy lookup
            existing_stock_map = {stock.get("code"): stock for stock in existing_stocks}

            # Update public opinion analysis data for existing stocks only
            for pub_stock in public_opinion_stocks:
                code = pub_stock.get('code')
                strategy_name = pub_stock.get('strategy_name', 'unknown_strategy')

                if code in existing_stock_map:
                    # Normalize score to 0-1 range and round to 2 decimal places
                    # Handle different score ranges:
                    # - Some strategies return scores in 0-1 range
                    # - Some strategies return scores in 0-100 range
                    score = pub_stock.get('score', 0.0)
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

                    # Update the pub field for the existing stock
                    if 'pub' not in existing_stock_map[code]:
                        existing_stock_map[code]['pub'] = {}
                    existing_stock_map[code]['pub'][strategy_name] = {
                        'score': rounded_score,
                        'value': pub_stock.get('value', ''),
                    }

            # Prepare cleaned stocks for database update
            # Preserve all existing fields and only update the pub field
            cleaned_stocks = []
            for stock in existing_stocks:
                # Copy all existing fields to preserve data integrity
                clean_stock = stock.copy()

                # Convert numpy types to native Python types for MongoDB compatibility
                from data.database_operations import DatabaseOperations
                db_ops = DatabaseOperations(self.db_manager)
                clean_stock = db_ops._convert_numpy_types(clean_stock)

                # Ensure score is properly formatted
                if 'score' in clean_stock:
                    clean_stock['score'] = round(float(clean_stock['score']), 2)

                cleaned_stocks.append(clean_stock)

            # Update the latest pool record with modified stocks and only pub_at timestamp
            result = collection.update_one(
                {"_id": latest_pool_record["_id"]},
                {
                    "$set": {
                        "stocks": cleaned_stocks,
                        "pub_at": datetime.now(),
                    },
                    "$unset": {
                        "selected_stocks_count": "",
                        "strategy_execution_time": ""
                    }
                },
            )

            if result.modified_count > 0:
                self.log_info(
                    f"Updated latest pool record with {len(public_opinion_stocks)} public opinion analysis stocks"
                )
            else:
                self.log_info("No changes made to the latest pool record")

            return True

        except Exception as e:
            self.log_error(
                f"Error updating latest pool record with public opinion analysis: {e}"
            )
            return False

    def run(self) -> bool:
        """
        Main execution method for the public opinion stock selector agent.
        This method is required by the BaseAgent abstract class.

        Returns:
            True if successful, False otherwise
        """
        return self.update_pool_with_public_opinion_analysis()


# Example usage
if __name__ == "__main__":
    # This is just a placeholder to make the file importable
    pass

