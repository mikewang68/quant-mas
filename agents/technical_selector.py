"""
Technical Stock Selector Agent
Selects stocks based on technical analysis strategies
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

# Configure logging
logger = logging.getLogger(__name__)


class TechnicalStockSelector(BaseAgent):
    """
    Technical Stock Selector Agent - Clean framework
    Dynamically loads strategies from database and executes them
    """

    def __init__(self, db_manager: MongoDBManager, data_fetcher: AkshareClient,
                 name: str = "TechnicalStockSelector", strategy_id: Optional[str] = None):
        """
        Initialize the technical stock selector framework

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
            # Get the technical analysis agent from database
            agent = self.db_manager.agents_collection.find_one({"name": "技术分析Agent"})
            if not agent:
                self.log_error("Technical analysis agent not found in database")
                return

            # Get strategy IDs assigned to this agent
            strategy_ids = agent.get("strategies", [])
            if not strategy_ids:
                self.log_warning("No strategies assigned to technical分析 agent")
                return

            # Use the specified strategy if strategy_id is provided, otherwise use the first strategy
            if self.strategy_id:
                selected_strategy = None
                for strategy_id in strategy_ids:
                    from bson import ObjectId
                    strategy = self.db_manager.strategies_collection.find_one({"_id": ObjectId(strategy_id)})
                    if strategy and str(strategy.get('_id')) == self.strategy_id:
                        selected_strategy = strategy
                        break

                if not selected_strategy:
                    self.log_warning(f"Strategy with ID {self.strategy_id} not found, using first strategy")
                    from bson import ObjectId
                    selected_strategy = self.db_manager.strategies_collection.find_one({"_id": ObjectId(strategy_ids[0])})
            else:
                # Use the first strategy for now (original behavior)
                from bson import ObjectId
                selected_strategy = self.db_manager.strategies_collection.find_one({"_id": ObjectId(strategy_ids[0])})

            if selected_strategy:
                self.strategy_params = selected_strategy.get('parameters', {})
                self.strategy_name = selected_strategy.get('name', 'Unknown')

                # Extract file and class from program field if it exists
                if 'program' in selected_strategy and isinstance(selected_strategy['program'], dict):
                    self.strategy_file = selected_strategy['program'].get('file', '')
                    self.strategy_class_name = selected_strategy['program'].get('class', '')
                    self.log_info("Loaded strategy file and class from program field")
                else:
                    # Fallback to direct file and class_name fields
                    self.strategy_file = selected_strategy.get('file', '')
                    self.strategy_class_name = selected_strategy.get('class_name', '')

                self.log_info("Loaded strategy from database: %s" % self.strategy_name)
            else:
                self.log_warning("No strategies found in database")

        except Exception as e:
            self.log_error(f"Error loading strategy from database: {e}")

    def _load_dynamic_strategy(self):
        """
        Dynamically load strategy from file and instantiate the strategy class
        """
        try:
            if not self.strategy_file or not self.strategy_class_name:
                self.log_warning("Strategy file or class not specified")
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
                    self.log_error("Invalid program field format")
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
            self.strategy_instance = self.strategy_class(name=self.strategy_name, params=self.strategy_params)

            self.log_info("Successfully loaded dynamic strategy: %s" % self.strategy_name)
        except Exception as e:
            self.log_error(f"Error loading dynamic strategy: {e}")
            raise

    def update_pool_with_technical_analysis(self) -> bool:
        """
        Update pool with technical analysis results by executing assigned strategies

        Returns:
            True if successful, False otherwise
        """
        self.log_info("Updating pool with technical analysis using dynamic strategy loading")

        try:
            # Get stock codes from the latest record in pool collection
            pool_collection = self.db_manager.db['pool']
            latest_pool_record = pool_collection.find_one(sort=[('selection_date', -1)])

            if not latest_pool_record:
                self.log_error("No records found in pool collection")
                return False

            # Extract stock codes from the latest pool record
            pool_stocks = latest_pool_record.get('stocks', [])
            stock_codes = [stock.get('code') for stock in pool_stocks if stock.get('code')]

            if not stock_codes:
                self.log_error("No stock codes found in latest pool record")
                return False

            self.log_info(f"Analyzing {len(stock_codes)} stocks from latest pool record")

            # Prepare stock data for all stocks (90 days of data)
            stock_data = {}
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')


            # Get buf_data collection
            buf_data_collection = self.db_manager.db['buf_data']

            for code in stock_codes:
                try:
                    # Check if we have data in buf_data for this stock within the last 90 days
                    buf_record = buf_data_collection.find_one({
                        'code': code,
                        'date': {'$gte': start_date, '$lte': end_date}
                    })

                    # Try to get data from buf_data first
                    k_data = pd.DataFrame()
                    if buf_record:
                        # Use cached data from buf_data
                        if 'data' in buf_record:
                            k_data = pd.DataFrame(buf_record['data'])
                        else:
                            # Try to get individual records from buf_data
                            buf_records = list(buf_data_collection.find({
                                'code': code,
                                'date': {'$gte': start_date, '$lte': end_date}
                            }))
                            if buf_records:
                                # Convert list of records to DataFrame
                                k_data = pd.DataFrame(buf_records)
                                # Remove MongoDB _id field
                                if '_id' in k_data.columns:
                                    k_data = k_data.drop('_id', axis=1)

                    if not k_data.empty:
                        if 'date' in k_data.columns:
                            k_data['date'] = pd.to_datetime(k_data['date'])
                            k_data = k_data.sort_values('date').reset_index(drop=True)
                        self.log_info(f"Using cached data for {code} from buf_data")
                    else:
                        # If no data in buf_data, fetch from data source with rate limiting
                        # Add rate limiting delay (1 second as requested)
                        import time
                        time.sleep(1.0)  # 1 second delay between requests

                        k_data = self.data_fetcher.get_daily_k_data(code, start_date, end_date)

                        # Save each day's data to buf_data with _id as date:code
                        if not k_data.empty:
                            self.log_info(f"Saving {len(k_data)} records to buf_data for {code}")
                            records_to_insert = []
                            for _, row in k_data.iterrows():
                                # Handle date conversion properly
                                if hasattr(row['date'], 'strftime'):
                                    record_date = row['date'].strftime('%Y-%m-%d')
                                else:
                                    record_date = str(row['date'])

                                record_id = f"{record_date}:{code}"

                                # Check if record already exists
                                existing_record = buf_data_collection.find_one({'_id': record_id})
                                if not existing_record:
                                    record = {
                                        '_id': record_id,
                                        'code': code,
                                        'date': record_date,
                                        'open': float(row['open']),
                                        'high': float(row['high']),
                                        'low': float(row['low']),
                                        'close': float(row['close']),
                                        'volume': float(row['volume']) if 'volume' in row else 0
                                    }
                                    records_to_insert.append(record)

                            # Bulk insert new records
                            if records_to_insert:
                                try:
                                    buf_data_collection.insert_many(records_to_insert)
                                    self.log_info(f"Inserted {len(records_to_insert)} new records to buf_data for {code}")
                                except Exception as insert_error:
                                    self.log_error(f"Error inserting records to buf_data for {code}: {insert_error}")
                        else:
                            self.log_warning(f"No data available for {code}")

                    # Store data for this stock
                    if not k_data.empty:
                        stock_data[code] = k_data
                    else:
                        self.log_warning(f"No data available for {code}")

                except Exception as e:
                    self.log_error(f"Error processing data for {code}: {e}")
                    continue

            if not stock_data:
                self.log_error("No stock data available for analysis")
                return False

            self.log_info(f"Prepared data for {len(stock_data)} stocks")

            # Execute the dynamically loaded strategy
            all_selected_stocks = []
            if self.strategy_instance:
                try:
                    # Execute the strategy
                    self.log_info(f"Executing strategy: {self.strategy_name}")
                    selected_stocks = self.strategy_instance.execute(stock_data, "技术分析Agent", self.db_manager)

                    # Calculate positions for selected stocks using position_calculator
                    from utils.position_calculator import calculate_position_from_score
                    for stock in selected_stocks:
                        if 'score' in stock:
                            try:
                                stock['position'] = calculate_position_from_score(stock['score'])
                            except Exception as pos_error:
                                self.log_warning(f"Error calculating position for stock {stock.get('code', 'unknown')}: {pos_error}")
                                stock['position'] = 0.0

                    all_selected_stocks.extend(selected_stocks)
                    self.log_info(f"Strategy {self.strategy_name} selected {len(selected_stocks)} stocks")

                except Exception as e:
                    self.log_error(f"Error executing strategy: {e}")

            self.log_info(f"Technical analysis completed. Total selected stocks: {len(all_selected_stocks)}")

            # Update the latest pool record with technical analysis results
            success = self.update_latest_pool_record(all_selected_stocks)
            return success

        except Exception as e:
            self.log_error(f"Error updating pool with technical analysis: {e}")
            return False

    def update_latest_pool_record(self, technical_stocks: List[Dict]) -> bool:
        """
        Update the latest pool record with technical analysis results

        Args:
            technical_stocks: List of stocks with technical analysis data

        Returns:
            True if updated successfully, False otherwise
        """
        try:
            # Get pool collection
            collection = self.db_manager.db['pool']

            # Find the latest pool record
            latest_pool_record = collection.find_one(sort=[('selection_date', -1)])

            if not latest_pool_record:
                self.log_error("No records found in pool collection")
                return False

            # Get existing stocks from the latest record
            existing_stocks = latest_pool_record.get('stocks', [])

            # Create a mapping of existing stocks by code for easy lookup
            existing_stock_map = {stock.get('code'): stock for stock in existing_stocks}

            # Update technical analysis data for existing stocks only
            for tech_stock in technical_stocks:
                stock_code = tech_stock.get('code')
                if stock_code in existing_stock_map:
                    # Update existing stock with technical analysis data
                    existing_stock_map[stock_code].update({
                        'technical_analysis': tech_stock.get('technical_analysis', {}),
                        'score': tech_stock.get('score', 0.0),
                        'position': tech_stock.get('position', 0.0),
                        'strategy_name': tech_stock.get('strategy_name', ''),
                        'selection_reason': tech_stock.get('selection_reason', ''),
                    })
                # Skip stocks that don't exist in the pool (don't add them)

            # Convert numpy types to native Python types before saving to MongoDB
            from data.database_operations import DatabaseOperations
            db_ops = DatabaseOperations(self.db_manager)
            existing_stocks = db_ops._convert_numpy_types(existing_stocks)

            # Update the latest pool record with modified stocks and technical analysis completion time
            result = collection.update_one(
                {'_id': latest_pool_record['_id']},
                {
                    '$set': {
                        'stocks': existing_stocks,
                        'technical_analysis_completed_at': datetime.now(),
                        'updated_at': datetime.now()
                    }
                }
            )

            if result.modified_count > 0:
                self.log_info(f"Updated latest pool record with {len(technical_stocks)} technical analysis stocks")
            else:
                self.log_info("No changes made to the latest pool record")

            return True

        except Exception as e:
            self.log_error(f"Error updating latest pool record with technical analysis: {e}")
            return False

    def run(self) -> bool:
        """
        Main execution method for the technical stock selector agent.
        This method is required by the BaseAgent abstract class.

        Returns:
            True if successful, False otherwise
        """
        return self.update_pool_with_technical_analysis()


# Example usage
if __name__ == "__main__":
    # This is just a placeholder to make the file importable
    pass

