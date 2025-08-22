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

from agents.base_agent import BaseAgent
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient

# Configure logging
logger = logging.getLogger(__name__)


class TechnicalStockSelector(BaseAgent):
    """
    Technical Stock Selector Agent
    Selects stocks based on technical analysis strategies
    """

    def __init__(self, db_manager: MongoDBManager, data_fetcher: AkshareClient,
                 name: str = "TechnicalStockSelector"):
        """
        Initialize the technical stock selector

        Args:
            db_manager: MongoDBManager instance
            data_fetcher: DataFetcher instance
            name: Name of the agent
        """
        super().__init__(name)
        self.db_manager = db_manager
        self.data_fetcher = data_fetcher

    def update_pool_with_technical_analysis(self) -> bool:
        """
        Update pool with technical analysis results by executing assigned strategies

        Returns:
            True if successful, False otherwise
        """
        self.log_info("Updating pool with technical analysis")

        try:
            # Get the technical analysis agent from database
            agent = self.db_manager.agents_collection.find_one({"name": "技术分析Agent"})
            if not agent:
                self.log_error("Technical analysis agent not found in database")
                return False

            # Get strategy IDs assigned to this agent
            strategy_ids = agent.get("strategies", [])
            if not strategy_ids:
                self.log_warning("No strategies assigned to technical分析 agent")
                return True  # No strategies to execute, but not an error

            self.log_info(f"Found {len(strategy_ids)} strategies to execute")

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

            for code in stock_codes:
                try:
                    # First check if buf_data collection exists
                    collection_names = self.db_manager.db.list_collection_names()
                    if 'buf_data' in collection_names:
                        buf_data_collection = self.db_manager.db['buf_data']
                        buf_record = buf_data_collection.find_one({
                            'code': code,
                            'date': {'$gte': start_date, '$lte': end_date}
                        })
                        if buf_record and 'data' in buf_record:
                            # Use cached data from buf_data
                            k_data = pd.DataFrame(buf_record['data'])
                            if not k_data.empty and 'date' in k_data.columns:
                                k_data['date'] = pd.to_datetime(k_data['date'])
                                k_data = k_data.sort_values('date').reset_index(drop=True)
                        else:
                            # Get daily K-data from database with adjustment based on config
                            k_data = self.db_manager.get_adjusted_k_data(code, start_date, end_date, frequency='daily')

                            # If no data in DB, fetch from data source with rate limiting
                            if k_data.empty:
                                # Add rate limiting delay
                                import time
                                time.sleep(0.1)  # 100ms delay between requests

                                k_data = self.data_fetcher.get_daily_k_data(code, start_date, end_date)
                                # Save to DB for future use
                                if not k_data.empty:
                                    self.db_manager.save_k_data(code, k_data, frequency='daily')

                                    # Also save to buf_data for caching
                                    buf_data_collection.insert_one({
                                        'code': code,
                                        'date': end_date,
                                        'data': k_data.to_dict('records')
                                    })
                    else:
                        # If no buf_data collection, use standard approach
                        k_data = self.db_manager.get_adjusted_k_data(code, start_date, end_date, frequency='daily')

                        # If no data in DB, fetch from data source with rate limiting
                        if k_data.empty:
                            # Add rate limiting delay
                            import time
                            time.sleep(0.1)  # 100ms delay between requests

                            k_data = self.data_fetcher.get_daily_k_data(code, start_date, end_date)
                            # Save to DB for future use
                            if not k_data.empty:
                                self.db_manager.save_k_data(code, k_data, frequency='daily')

                    if not k_data.empty:
                        stock_data[code] = k_data
                    else:
                        self.log_warning(f"No data available for stock {code}")

                except Exception as e:
                    self.log_warning(f"Error fetching data for stock {code}: {e}")
                    continue

            if not stock_data:
                self.log_error("No stock data available for analysis")
                return False

            self.log_info(f"Prepared data for {len(stock_data)} stocks")

            # Execute each strategy on the stock data
            all_selected_stocks = []
            for strategy_id in strategy_ids:
                try:
                    # Get strategy from database
                    from bson import ObjectId
                    strategy_doc = self.db_manager.strategies_collection.find_one({"_id": ObjectId(strategy_id)})
                    if not strategy_doc:
                        self.log_warning(f"Strategy {strategy_id} not found in database")
                        continue

                    # Import and instantiate the strategy
                    strategy_program = strategy_doc.get("program", "")
                    strategy_name = strategy_doc.get("name", "")
                    strategy_params = strategy_doc.get("parameters", {})

                    if not strategy_program:
                        self.log_warning(f"No program specified for strategy {strategy_name}")
                        continue

                    # Dynamically import the strategy module
                    # Remove .py extension if present
                    module_name = strategy_program.replace(".py", "")
                    strategy_module = __import__(f"strategies.{module_name}", fromlist=[strategy_name])

                    # Get the strategy class (assuming it's named after the module)
                    strategy_class_name = "".join(word.capitalize() for word in module_name.split("_"))
                    if hasattr(strategy_module, strategy_class_name):
                        strategy_class = getattr(strategy_module, strategy_class_name)
                    else:
                        # Fallback: try to find any class that inherits from BaseStrategy
                        strategy_class = None
                        for attr_name in dir(strategy_module):
                            attr = getattr(strategy_module, attr_name)
                            if isinstance(attr, type) and hasattr(attr, '__bases__') and 'BaseStrategy' in [base.__name__ for base in attr.__bases__]:
                                strategy_class = attr
                                break

                        if not strategy_class:
                            self.log_warning(f"Could not find strategy class in {module_name}")
                            continue

                    # Instantiate the strategy
                    strategy = strategy_class(name=strategy_name, params=strategy_params)

                    # Execute the strategy
                    self.log_info(f"Executing strategy: {strategy_name}")
                    selected_stocks = strategy.execute(stock_data, "技术分析Agent", self.db_manager)

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
                    self.log_info(f"Strategy {strategy_name} selected {len(selected_stocks)} stocks")

                except Exception as e:
                    self.log_error(f"Error executing strategy {strategy_id}: {e}")
                    continue

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

