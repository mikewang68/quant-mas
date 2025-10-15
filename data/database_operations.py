"""
Database Operations Module
Separates database operations from the MongoDBManager class for better organization
"""

import pymongo
import pandas as pd
import logging
from typing import List, Optional, Dict, Any
from config.mongodb_config import MongoDBConfig
from bson import ObjectId
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseOperations:
    """Database operations separated from MongoDBManager for better organization"""

    def __init__(self, db_manager):
        """
        Initialize with reference to MongoDBManager

        Args:
            db_manager: MongoDBManager instance
        """
        self.db_manager = db_manager
        self.db = db_manager.db
        self.logger = logging.getLogger(__name__)
        # Initialize pool collection
        self.pool_collection = self.db["pool"]

    # Stock code operations
    def get_stock_codes(self) -> List[str]:
        """
        Get all stock codes from database

        Returns:
            List of stock codes
        """
        try:
            collection = self.db_manager.get_collection("stock_codes")
            codes = list(collection.find({}, {"_id": 0, "code": 1}))
            return [code["code"] for code in codes]
        except Exception as e:
            self.logger.error(f"Error getting stock codes: {e}")
            return []

    def save_stock_codes(self, codes: List[str]) -> bool:
        """
        Save stock codes to database

        Args:
            codes: List of stock codes

        Returns:
            True if successful, False otherwise
        """
        try:
            collection = self.db_manager.get_collection("stock_codes")
            # Clear existing codes
            collection.delete_many({})

            # Insert new codes
            if codes:
                documents = [{"code": code} for code in codes]
                collection.insert_many(documents)

            self.logger.info(f"Saved {len(codes)} stock codes to database")
            return True
        except Exception as e:
            self.logger.error(f"Error saving stock codes: {e}")
            return False

    # K-line data operations
    def get_k_data(
        self,
        code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: str = "daily",
    ) -> pd.DataFrame:
        """
        Get K-line data from database

        Args:
            code: Stock code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            frequency: Data frequency ('daily', 'weekly', etc.)

        Returns:
            DataFrame with K-line data
        """
        try:
            collection = self.db_manager.get_collection("k_data")

            # Build query with code
            query = {"代码": code}

            if start_date:
                query["日期"] = {"$gte": start_date}
            if end_date:
                if "日期" in query:
                    date_query = query["日期"]
                    if isinstance(date_query, dict):
                        date_query["$lte"] = end_date  # type: ignore
                    query["日期"] = date_query  # type: ignore
                else:
                    query["日期"] = {"$lte": end_date}

            # Query data
            cursor = collection.find(query, {"_id": 0})
            data = list(cursor)

            # Convert to DataFrame
            if data:
                df = pd.DataFrame(data)
                df["日期"] = pd.to_datetime(df["日期"])
                df = df.sort_values("日期").reset_index(drop=True)
                return df
            else:
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"Error getting K-line data for {code}: {e}")
            return pd.DataFrame()

    def save_k_data(
        self, code: str, k_data: pd.DataFrame, frequency: str = "daily"
    ) -> bool:
        """
        Save K-line data to database

        Args:
            code: Stock code
            k_data: DataFrame with K-line data
            frequency: Data frequency ('daily', 'weekly', etc.)

        Returns:
            True if successful, False otherwise
        """
        try:
            collection = self.db_manager.get_collection("k_data")

            if k_data.empty:
                self.logger.warning(f"No K-data to save for {code}")
                return True

            # Add code column
            k_data_with_code = k_data.copy()
            k_data_with_code["代码"] = code

            # Convert date to string for MongoDB storage
            if "date" in k_data_with_code.columns:
                k_data_with_code["日期"] = k_data_with_code["date"].dt.strftime(
                    "%Y-%m-%d"
                )

            # Convert DataFrame to list of dictionaries
            records = k_data_with_code.to_dict("records")

            # Delete existing data for this code and frequency
            delete_query = {"代码": code}
            collection.delete_many(delete_query)

            # Insert new data
            if records:
                collection.insert_many(records)

            self.logger.info(
                f"Saved {len(records)} {frequency} K-data records for {code}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error saving K-data for {code}: {e}")
            return False

    # Agent operations
    def get_agents(self) -> list:
        """
        Get all agents from agents collection

        Returns:
            List of agents
        """
        try:
            collection = self.db_manager.get_collection("agents")
            agents = list(
                collection.find(
                    {},
                    {
                        "_id": 1,
                        "name": 1,
                        "description": 1,
                        "status": 1,
                        "strategies": 1,
                        "program": 1,
                    },
                )
            )
            # Convert ObjectId to string for JSON serialization
            for agent in agents:
                agent["_id"] = str(agent["_id"])
            return agents
        except Exception as e:
            self.logger.error(f"Error getting agents: {e}")
            return []

    def get_agent(self, agent_id: str):
        """
        Get a specific agent by ID

        Args:
            agent_id: Agent ID

        Returns:
            Agent document or None
        """
        try:
            collection = self.db_manager.get_collection("agents")
            agent = collection.find_one({"_id": ObjectId(agent_id)})
            if agent:
                agent["_id"] = str(agent["_id"])
            return agent
        except Exception as e:
            self.logger.error(f"Error getting agent {agent_id}: {e}")
            return None

    def create_agent(self, agent_data: dict):
        """
        Create a new agent

        Args:
            agent_data: Agent data

        Returns:
            Inserted ID or None
        """
        try:
            collection = self.db_manager.get_collection("agents")
            result = collection.insert_one(agent_data)
            return str(result.inserted_id)
        except Exception as e:
            self.logger.error(f"Error creating agent: {e}")
            return None

    def update_agent(self, agent_id: str, agent_data: dict):
        """
        Update an existing agent

        Args:
            agent_id: Agent ID
            agent_data: Updated agent data

        Returns:
            True if successful, False otherwise
        """
        try:
            collection = self.db_manager.get_collection("agents")
            # Remove _id from update data if present
            if "_id" in agent_data:
                del agent_data["_id"]
            result = collection.update_one(
                {"_id": ObjectId(agent_id)}, {"$set": agent_data}
            )
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f"Error updating agent {agent_id}: {e}")
            return False

    def delete_agent(self, agent_id: str):
        """
        Delete an agent

        Args:
            agent_id: Agent ID

        Returns:
            True if successful, False otherwise
        """
        try:
            collection = self.db_manager.get_collection("agents")
            result = collection.delete_one({"_id": ObjectId(agent_id)})
            return result.deleted_count > 0
        except Exception as e:
            self.logger.error(f"Error deleting agent {agent_id}: {e}")
            return False

    # Strategy operations
    def get_strategies(self) -> list:
        """
        Get all strategies from strategies collection

        Returns:
            List of strategies
        """
        try:
            collection = self.db_manager.get_collection("strategies")
            strategies = list(
                collection.find(
                    {},
                    {"_id": 1, "name": 1, "type": 1, "description": 1, "parameters": 1},
                )
            )
            # Convert ObjectId to string for JSON serialization
            for strategy in strategies:
                strategy["_id"] = str(strategy["_id"])
            return strategies
        except Exception as e:
            self.logger.error(f"Error getting strategies: {e}")
            return []

    def get_strategy(self, strategy_id: str):
        """
        Get a specific strategy by ID

        Args:
            strategy_id: Strategy ID

        Returns:
            Strategy document or None
        """
        try:
            collection = self.db_manager.get_collection("strategies")
            strategy = collection.find_one({"_id": ObjectId(strategy_id)})
            if strategy:
                strategy["_id"] = str(strategy["_id"])
            return strategy
        except Exception as e:
            self.logger.error(f"Error getting strategy {strategy_id}: {e}")
            return None

    def create_strategy(self, strategy_data: dict):
        """
        Create a new strategy

        Args:
            strategy_data: Strategy data

        Returns:
            Inserted ID or None
        """
        try:
            collection = self.db_manager.get_collection("strategies")
            result = collection.insert_one(strategy_data)
            return str(result.inserted_id)
        except Exception as e:
            self.logger.error(f"Error creating strategy: {e}")
            return None

    def update_strategy(self, strategy_id: str, strategy_data: dict):
        """
        Update an existing strategy

        Args:
            strategy_id: Strategy ID
            strategy_data: Updated strategy data

        Returns:
            True if successful, False otherwise
        """
        try:
            collection = self.db_manager.get_collection("strategies")
            # Remove _id from update data if present
            if "_id" in strategy_data:
                del strategy_data["_id"]
            result = collection.update_one(
                {"_id": ObjectId(strategy_id)}, {"$set": strategy_data}
            )
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f"Error updating strategy {strategy_id}: {e}")
            return False

    def delete_strategy(self, strategy_id: str):
        """
        Delete a strategy

        Args:
            strategy_id: Strategy ID

        Returns:
            True if successful, False otherwise
        """
        try:
            collection = self.db_manager.get_collection("strategies")
            result = collection.delete_one({"_id": ObjectId(strategy_id)})
            return result.deleted_count > 0
        except Exception as e:
            self.logger.error(f"Error deleting strategy {strategy_id}: {e}")
            return False

    # Config operations
    def get_config(self, key: str):
        """
        Get a config value by key

        Args:
            key: Config key

        Returns:
            Config value or None
        """
        try:
            collection = self.db_manager.get_collection("config")
            config_doc = collection.find_one({"key": key})
            if config_doc:
                return config_doc.get("value")
            return None
        except Exception as e:
            self.logger.error(f"Error getting config {key}: {e}")
            return None

    def save_config(self, key: str, value: Any) -> Optional[bool | str]:
        """
        Save a config value by key

        Args:
            key: Config key
            value: Config value

        Returns:
            Modified count or inserted ID
        """
        try:
            collection = self.db_manager.get_collection("config")
            # Check if config already exists
            existing = collection.find_one({"key": key})
            if existing:
                result = collection.update_one({"key": key}, {"$set": {"value": value}})
                modified_count = (
                    result.modified_count if result.modified_count is not None else 0
                )
                return modified_count > 0
            else:
                result = collection.insert_one({"key": key, "value": value})
                return (
                    str(result.inserted_id) if result.inserted_id is not None else None
                )
        except Exception as e:
            self.logger.error(f"Error saving config {key}: {e}")
            return None

    # Pool operations
    def save_selected_stocks_to_pool(
        self,
        strategy_key: str,
        agent_name: str,
        strategy_id: str,
        strategy_name: str,
        stocks: List[Dict],
        date: str,
        last_data_date: Optional[str] = None,
        strategy_params: Optional[Dict] = None,
    ) -> bool:
        """
        Save selected stocks to pool collection by updating the latest record only
        Follows the rule: can only process the last record in the pool dataset

        Args:
            strategy_key: Unique key for this agent-strategy combination
            agent_name: Name of the agent
            strategy_id: Strategy ID
            strategy_name: Strategy name
            stocks: List of selected stocks with codes and selection reasons
            date: Selection date
            last_data_date: Last date of stock data used for selection
            strategy_params: Strategy parameters used for selection

        Returns:
            True if saved successfully, False otherwise
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        try:
            # Get pool collection
            collection = self.db["pool"]

            # Find the latest pool record
            latest_record = collection.find_one(sort=[("_id", -1)])

            if not latest_record:
                self.logger.error("No records found in pool collection - cannot update")
                return False

            # Prepare stocks data (already includes selection reasons)
            # Convert any numpy types to native Python types for MongoDB compatibility
            stocks_data = self._convert_numpy_types(stocks)

            # Get strategy configuration from database if not provided
            strategy_parameters = strategy_params or {}
            if not strategy_parameters:
                # Try to get strategy parameters from database
                strategy_doc = self.get_strategy(strategy_id)
                if strategy_doc and "parameters" in strategy_doc:
                    strategy_parameters = strategy_doc["parameters"]

            # Update the latest record with new strategy data
            update_data = {
                "strategy_key": strategy_key,
                "strategy_name": strategy_name,
                "stocks": stocks_data,
                "count": len(stocks),
                "updated_at": datetime.now(),
            }

            # Update the latest record
            result = collection.update_one(
                {"_id": latest_record["_id"]}, {"$set": update_data}
            )

            if result.modified_count > 0:
                self.logger.info(
                    f"Updated latest pool record with {len(stocks)} stocks from {strategy_name}"
                )
            else:
                self.logger.info("No changes made to the latest pool record")

            return True

        except Exception as e:
            self.logger.error(f"Error updating latest pool record: {e}")
            return False

    def get_latest_pool_record(self) -> Optional[Dict]:
        """
        Get the latest pool record

        Returns:
            Latest pool record or None if not found
        """
        try:
            # Get pool collection
            pool_collection = self.db["pool"]

            # Find the latest record sorted by selection_date
            latest_record = pool_collection.find_one(
                {},  # No filter, get any record
                sort=[("selection_date", -1)],  # Sort by selection_date descending
            )

            return latest_record

        except Exception as e:
            self.logger.error(f"Error retrieving latest pool record: {e}")
            return None

    def save_strategy_output_to_pool(
        self,
        strategy_key: str,
        agent_name: str,
        strategy_id: str,
        strategy_name: str,
        stocks: List[Dict],
        date: str,
        last_data_date: Optional[str] = None,
        strategy_params: Optional[Dict] = None,
        additional_metadata: Optional[Dict] = None,
    ) -> bool:
        """
        Save strategy output results to pool collection by updating the latest record's stocks field.
        This method updates existing stocks in the latest pool record rather than creating new records.

        Args:
            strategy_key: Unique key for this agent-strategy combination (used for logging)
            agent_name: Name of the agent that executed the strategy
            strategy_id: Strategy ID
            strategy_name: Strategy name
            stocks: List of selected stocks with codes and any additional information
            date: Selection date (YYYY-MM-DD)
            last_data_date: Last date of stock data used for selection (optional)
            strategy_params: Strategy parameters used for selection (optional)
            additional_metadata: Additional metadata to store with the record (optional)

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Get pool collection
            collection = self.db["pool"]

            # Find the latest pool record
            latest_pool_record = collection.find_one(sort=[("selection_date", -1)])

            if not latest_pool_record:
                self.logger.error("No records found in pool collection")
                return False

            # Get existing stocks from the latest record
            existing_stocks = latest_pool_record.get("stocks", [])

            # Create a mapping of existing stocks by code for easy lookup
            existing_stock_map = {stock.get("code"): stock for stock in existing_stocks}

            # Update or add technical analysis data to existing stocks
            updated_stocks = existing_stocks[:]  # Create a copy of existing stocks
            for new_stock in stocks:
                stock_code = new_stock.get("code")
                if stock_code in existing_stock_map:
                    # Update existing stock with new data
                    existing_index = next(
                        (
                            i
                            for i, s in enumerate(updated_stocks)
                            if s.get("code") == stock_code
                        ),
                        None,
                    )
                    if existing_index is not None:
                        # Get the existing stock data
                        existing_stock = updated_stocks[existing_index]

                        # Handle trend data merging to preserve data from multiple strategies
                        if "trend" in new_stock and "trend" in existing_stock:
                            # Merge trend data instead of replacing it
                            for strategy_name, strategy_data in new_stock[
                                "trend"
                            ].items():
                                existing_stock["trend"][strategy_name] = strategy_data

                        # Update other fields normally
                        existing_stock.update(new_stock)

                        # Remove trend field from new_stock to avoid overwriting the merged trend data
                        if "trend" in new_stock:
                            existing_stock.pop("trend", None)
                            existing_stock["trend"] = new_stock["trend"]
                else:
                    # Add new stock if it doesn't exist in the pool (optional based on requirements)
                    # For now, we'll skip stocks that don't already exist in the pool
                    pass

            # Prepare the update data
            update_data = {
                "stocks": self._convert_numpy_types(updated_stocks),
                "updated_at": datetime.now(),
            }

            # Add additional metadata if provided
            if additional_metadata:
                update_data.update(additional_metadata)

            # Update the latest pool record with modified stocks
            result = collection.update_one(
                {"_id": latest_pool_record["_id"]}, {"$set": update_data}
            )

            if result.modified_count > 0:
                self.logger.info(
                    f"Updated latest pool record with {len(stocks)} stocks from {strategy_name}"
                )
            else:
                self.logger.info("No changes made to the latest pool record")

            return True

        except Exception as e:
            self.logger.error(
                f"Error updating latest pool record with strategy output: {e}"
            )
            return False

    def _convert_numpy_types(self, obj):
        """
        Convert numpy data types to native Python types for MongoDB compatibility.

        Args:
            obj: Object to convert (dict, list, or value)

        Returns:
            Object with numpy types converted to native Python types
        """
        import numpy as np

        if isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, bool):
            return bool(obj)  # Convert Python bool to bool
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj

    def save_trend_output_to_pool(
        self,
        strategy_key: str,
        agent_name: str,
        strategy_id: str,
        strategy_name: str,
        stocks: List[Dict],
        date: str,
        last_data_date: str,
        strategy_params: Dict = None,
        additional_metadata: Dict = None,
    ) -> bool:
        """
        Save trend strategy output to pool collection, accumulating results from multiple strategies.

        This function is designed to handle trend data where each stock can be selected by multiple strategies,
        with each strategy's data stored under the 'trend' field with strategy name as key.

        Args:
            strategy_key: Strategy key for identification
            agent_name: Name of the agent executing the strategy
            strategy_id: Strategy ID from database
            strategy_name: Name of the strategy
            stocks: List of stock data with trend information
            date: Selection date
            last_data_date: Last data date used for analysis
            strategy_params: Strategy parameters (optional)
            additional_metadata: Additional metadata to store (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert any numpy types to native Python types
            stocks = [self._convert_numpy_types(stock) for stock in stocks]

            # Generate year-week ID from date
            from datetime import datetime as dt
            selection_date = dt.strptime(date, "%Y-%m-%d")
            year_week_id = f"{selection_date.year}-{selection_date.isocalendar()[1]}"

            # Check if record with this year-week ID already exists
            existing_record = self.pool_collection.find_one({"_id": year_week_id})

            if existing_record:
                # Update existing record
                existing_stocks = existing_record.get("stocks", [])

                # Create a map of existing stocks by code for quick lookup
                existing_stock_map = {
                    stock.get("code"): i
                    for i, stock in enumerate(existing_stocks)
                    if stock.get("code")
                }

                # Update or add trend data to existing stocks
                updated_stocks = existing_stocks[:]  # Create a copy of existing stocks
                for new_stock in stocks:
                    stock_code = new_stock.get("code")
                    if stock_code in existing_stock_map:
                        # Update existing stock with new trend data
                        existing_index = existing_stock_map[stock_code]
                        existing_stock = updated_stocks[existing_index]

                        # Handle trend data merging to preserve data from multiple strategies
                        if "trend" in new_stock:
                            if "trend" not in existing_stock:
                                existing_stock["trend"] = {}

                            # Merge trend data instead of replacing it
                            for strategy_name_key, strategy_data in new_stock[
                                "trend"
                            ].items():
                                existing_stock["trend"][strategy_name_key] = strategy_data
                    else:
                        # Add new stock if it doesn't exist in the pool
                        updated_stocks.append(new_stock)

                stocks_to_save = updated_stocks
            else:
                # Create new record with all stocks
                stocks_to_save = stocks

            # Prepare metadata
            metadata = {
                "strategy_key": strategy_key,
                "agent_name": agent_name,
                "strategy_id": strategy_id,
                "strategy_name": strategy_name,
                "date": date,
                "last_data_date": last_data_date,
                "strategy_params": strategy_params or {},
            }

            # Add additional metadata if provided
            if additional_metadata:
                metadata.update(additional_metadata)

            # Prepare strategy information
            strategy_info = {
                "strategy_key": [strategy_key],  # 策略key列表
                "strategy_name": [strategy_name],  # 策略名称列表
                "count": len(stocks),  # 当前策略选中的股票数
            }

            # Create or update the pool record
            update_data = {
                "$set": {
                    "stocks": stocks_to_save,
                    "updated_at": dt.now(),
                    "selection_date": date,
                },
                "$push": {"metadata": metadata},
            }

            # If this is a new record, add created_at
            if not existing_record:
                update_data["$set"]["created_at"] = dt.now()
                # For new record, set initial strategy info
                update_data["$set"]["strategy_key"] = [strategy_key]
                update_data["$set"]["strategy_name"] = [strategy_name]
                update_data["$set"]["count"] = len(stocks)
            else:
                # For existing record, update strategy info by adding to arrays and accumulating count
                update_data["$addToSet"] = {
                    "strategy_key": strategy_key,
                    "strategy_name": strategy_name,
                }
                update_data["$inc"] = {
                    "count": len(stocks)
                }

            result = self.pool_collection.update_one(
                {"_id": year_week_id},
                update_data,
                upsert=True  # Create new record if it doesn't exist
            )

            if result.upserted_id or result.modified_count > 0:
                action = "created" if result.upserted_id else "updated"
                self.logger.info(
                    f"Successfully {action} pool record {year_week_id} with trend data for {len(stocks)} stocks"
                )
                return True
            else:
                self.logger.warning("No changes made to pool record")
                return False

        except Exception as e:
            self.logger.error(f"Error saving trend output to pool: {e}")
            return False
