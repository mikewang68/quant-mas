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
    
    # Stock code operations
    def get_stock_codes(self) -> List[str]:
        """
        Get all stock codes from database
        
        Returns:
            List of stock codes
        """
        try:
            collection = self.db_manager.get_collection('stock_codes')
            codes = list(collection.find({}, {'_id': 0, 'code': 1}))
            return [code['code'] for code in codes]
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
            collection = self.db_manager.get_collection('stock_codes')
            # Clear existing codes
            collection.delete_many({})
            
            # Insert new codes
            if codes:
                documents = [{'code': code} for code in codes]
                collection.insert_many(documents)
            
            self.logger.info(f"Saved {len(codes)} stock codes to database")
            return True
        except Exception as e:
            self.logger.error(f"Error saving stock codes: {e}")
            return False
    
    # K-line data operations
    def get_k_data(self, code: str, start_date: Optional[str] = None,
                   end_date: Optional[str] = None, frequency: str = 'daily') -> pd.DataFrame:
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
            collection = self.db_manager.get_collection('k_data')
            
            # Build query with code
            query = {'代码': code}

            if start_date:
                query['日期'] = {'$gte': start_date}
            if end_date:
                if '日期' in query:
                    date_query = query['日期']
                    if isinstance(date_query, dict):
                        date_query['$lte'] = end_date  # type: ignore
                    query['日期'] = date_query  # type: ignore
                else:
                    query['日期'] = {'$lte': end_date}

            # Query data
            cursor = collection.find(query, {'_id': 0})
            data = list(cursor)

            # Convert to DataFrame
            if data:
                df = pd.DataFrame(data)
                df['日期'] = pd.to_datetime(df['日期'])
                df = df.sort_values('日期').reset_index(drop=True)
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error getting K-line data for {code}: {e}")
            return pd.DataFrame()
    
    def save_k_data(self, code: str, k_data: pd.DataFrame, frequency: str = 'daily') -> bool:
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
            collection = self.db_manager.get_collection('k_data')
            
            if k_data.empty:
                self.logger.warning(f"No K-data to save for {code}")
                return True
            
            # Add code column
            k_data_with_code = k_data.copy()
            k_data_with_code['代码'] = code
            
            # Convert date to string for MongoDB storage
            if 'date' in k_data_with_code.columns:
                k_data_with_code['日期'] = k_data_with_code['date'].dt.strftime('%Y-%m-%d')
            
            # Convert DataFrame to list of dictionaries
            records = k_data_with_code.to_dict('records')
            
            # Delete existing data for this code and frequency
            delete_query = {'代码': code}
            collection.delete_many(delete_query)
            
            # Insert new data
            if records:
                collection.insert_many(records)
            
            self.logger.info(f"Saved {len(records)} {frequency} K-data records for {code}")
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
            collection = self.db_manager.get_collection('agents')
            agents = list(collection.find({}, {'_id': 1, 'name': 1, 'description': 1, 'status': 1, 'strategies': 1, 'program': 1}))
            # Convert ObjectId to string for JSON serialization
            for agent in agents:
                agent['_id'] = str(agent['_id'])
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
            collection = self.db_manager.get_collection('agents')
            agent = collection.find_one({'_id': ObjectId(agent_id)})
            if agent:
                agent['_id'] = str(agent['_id'])
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
            collection = self.db_manager.get_collection('agents')
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
            collection = self.db_manager.get_collection('agents')
            # Remove _id from update data if present
            if '_id' in agent_data:
                del agent_data['_id']
            result = collection.update_one(
                {'_id': ObjectId(agent_id)},
                {'$set': agent_data}
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
            collection = self.db_manager.get_collection('agents')
            result = collection.delete_one({'_id': ObjectId(agent_id)})
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
            collection = self.db_manager.get_collection('strategies')
            strategies = list(collection.find({}, {'_id': 1, 'name': 1, 'type': 1, 'description': 1, 'parameters': 1}))
            # Convert ObjectId to string for JSON serialization
            for strategy in strategies:
                strategy['_id'] = str(strategy['_id'])
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
            collection = self.db_manager.get_collection('strategies')
            strategy = collection.find_one({'_id': ObjectId(strategy_id)})
            if strategy:
                strategy['_id'] = str(strategy['_id'])
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
            collection = self.db_manager.get_collection('strategies')
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
            collection = self.db_manager.get_collection('strategies')
            # Remove _id from update data if present
            if '_id' in strategy_data:
                del strategy_data['_id']
            result = collection.update_one(
                {'_id': ObjectId(strategy_id)},
                {'$set': strategy_data}
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
            collection = self.db_manager.get_collection('strategies')
            result = collection.delete_one({'_id': ObjectId(strategy_id)})
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
            collection = self.db_manager.get_collection('config')
            config_doc = collection.find_one({'key': key})
            if config_doc:
                return config_doc.get('value')
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
            collection = self.db_manager.get_collection('config')
            # Check if config already exists
            existing = collection.find_one({'key': key})
            if existing:
                result = collection.update_one(
                    {'key': key},
                    {'$set': {'value': value}}
                )
                modified_count = result.modified_count if result.modified_count is not None else 0
                return modified_count > 0
            else:
                result = collection.insert_one({'key': key, 'value': value})
                return str(result.inserted_id) if result.inserted_id is not None else None
        except Exception as e:
            self.logger.error(f"Error saving config {key}: {e}")
            return None

    # Pool operations
    def save_selected_stocks_to_pool(self, strategy_key: str, agent_name: str, strategy_id: str,
                                   strategy_name: str, stocks: List[Dict], date: str,
                                   last_data_date: Optional[str] = None,
                                   strategy_params: Optional[Dict] = None) -> bool:
        """
        Save selected stocks to pool collection with proper identification

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
            date = datetime.now().strftime('%Y-%m-%d')

        # Use last_data_date to determine year-week key, fallback to selection date
        if last_data_date:
            reference_date = datetime.strptime(last_data_date, '%Y-%m-%d')
        else:
            reference_date = datetime.strptime(date, '%Y-%m-%d')

        try:
            # Create a collection for pool
            collection = self.db['pool']

            # Calculate ISO year and week number based on reference date
            iso_year, iso_week, _ = reference_date.isocalendar()
            year_week_key = f"{iso_year}-{iso_week:02d}"

            # Prepare stocks data (already includes selection reasons)
            # Convert any numpy types to native Python types for MongoDB compatibility
            stocks_data = self._convert_numpy_types(stocks)

            # Get strategy configuration from database if not provided
            strategy_parameters = strategy_params or {}
            if not strategy_parameters:
                # Try to get strategy parameters from database
                strategy_doc = self.get_strategy(strategy_id)
                if strategy_doc and 'parameters' in strategy_doc:
                    strategy_parameters = strategy_doc['parameters']

            # Save selection record with upsert
            record = {
                '_id': year_week_key,  # Use year-week as primary key
                'strategy_key': strategy_key,
                'strategy_name': strategy_name,
                'strategy_parameters': strategy_parameters,
                'stocks': stocks_data,
                'count': len(stocks),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }

            # Use upsert to insert or update the record
            result = collection.replace_one(
                {'_id': year_week_key},  # Filter by _id
                record,  # Document to insert/update
                upsert=True  # Create if doesn't exist
            )

            if result.upserted_id:
                self.logger.info(f"Inserted new strategy selection record {year_week_key} with {len(stocks)} stocks")
            else:
                self.logger.info(f"Updated existing strategy selection record {year_week_key} with {len(stocks)} stocks")

            return True

        except Exception as e:
            self.logger.error(f"Error saving strategy selection to pool: {e}")
            return False

    def get_latest_pool_record(self) -> Optional[Dict]:
        """
        Get the latest pool record
        
        Returns:
            Latest pool record or None if not found
        """
        try:
            # Get pool collection
            pool_collection = self.db['pool']
            
            # Find the latest record sorted by selection_date
            latest_record = pool_collection.find_one(
                {},  # No filter, get any record
                sort=[('selection_date', -1)]  # Sort by selection_date descending
            )
            
            return latest_record
            
        except Exception as e:
            self.logger.error(f"Error retrieving latest pool record: {e}")
            return None

    def save_strategy_output_to_pool(self, strategy_key: str, agent_name: str, strategy_id: str,
                                   strategy_name: str, stocks: List[Dict], date: str,
                                   last_data_date: Optional[str] = None,
                                   strategy_params: Optional[Dict] = None,
                                   additional_metadata: Optional[Dict] = None) -> bool:
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
            collection = self.db['pool']

            # Find the latest pool record
            latest_pool_record = collection.find_one(sort=[('selection_date', -1)])

            if not latest_pool_record:
                self.logger.error("No records found in pool collection")
                return False

            # Get existing stocks from the latest record
            existing_stocks = latest_pool_record.get('stocks', [])

            # Create a mapping of existing stocks by code for easy lookup
            existing_stock_map = {stock.get('code'): stock for stock in existing_stocks}

            # Update or add technical analysis data to existing stocks
            updated_stocks = existing_stocks[:]  # Create a copy of existing stocks
            for new_stock in stocks:
                stock_code = new_stock.get('code')
                if stock_code in existing_stock_map:
                    # Update existing stock with new data
                    existing_index = next((i for i, s in enumerate(updated_stocks) if s.get('code') == stock_code), None)
                    if existing_index is not None:
                        updated_stocks[existing_index].update(new_stock)
                else:
                    # Add new stock if it doesn't exist in the pool (optional based on requirements)
                    # For now, we'll skip stocks that don't already exist in the pool
                    pass

            # Prepare the update data
            update_data = {
                'stocks': self._convert_numpy_types(updated_stocks),
                'updated_at': datetime.now()
            }

            # Add additional metadata if provided
            if additional_metadata:
                update_data.update(additional_metadata)

            # Update the latest pool record with modified stocks
            result = collection.update_one(
                {'_id': latest_pool_record['_id']},
                {'$set': update_data}
            )

            if result.modified_count > 0:
                self.logger.info(f"Updated latest pool record with {len(stocks)} stocks from {strategy_name}")
            else:
                self.logger.info("No changes made to the latest pool record")

            return True

        except Exception as e:
            self.logger.error(f"Error updating latest pool record with strategy output: {e}")
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
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj

