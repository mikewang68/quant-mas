"""
MongoDB Manager Module
Provides a comprehensive interface for MongoDB database operations including
data fetching, storage, and management for the quant trading system.
"""

import pymongo
import pandas as pd
import logging
from typing import List, Optional, Dict, Any
from config.mongodb_config import MongoDBConfig
from bson import ObjectId
import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import program manager utility
try:
    from utils.program_manager import create_strategy_program_file
except ImportError:
    # If import fails, define a dummy function
    def create_strategy_program_file(strategy_name: str, strategy_type: str = "technical") -> Optional[str]:
        """Dummy function when import fails"""
        return None

# Configure logging
logger = logging.getLogger(__name__)


class MongoDBManager:
    """MongoDB manager for database operations in the quant trading system"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        # Logger
        self.logger = logging.getLogger(__name__)
        
        # Load database configuration
        self.config_loader = MongoDBConfig()
        self.mongodb_config = self.config_loader.get_mongodb_config()
        self.collections_config = self.config_loader.get_collections_config()
        
        # Connection parameters
        self.host = self.mongodb_config['host']
        self.port = self.mongodb_config['port']
        self.database_name = self.config_loader.get_database_name()
        self.username = self.mongodb_config.get('username')
        self.password = self.mongodb_config.get('password')
        self.auth_database = self.mongodb_config.get('auth_database', 'admin')
        
        # Connect to MongoDB
        self.client = self._connect()
        self.db = self.client[self.database_name]
        
        # Initialize collections
        self._initialize_collections()
        
        # Field mappings for different data types
        self.field_mappings = {
            'stock_basic': {
                'code': 'code',
                'name': 'name',
                'industry': 'industry',
                'market': 'market'
            },
            'k_data': {
                'date': 'date',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume',
                'amount': 'amount'
            }
        }
    
    def _connect(self) -> pymongo.MongoClient:
        """
        Establish connection to MongoDB
        
        Returns:
            MongoClient instance
        """
        try:
            if self.username and self.password:
                # With authentication
                uri = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.database_name}?authSource={self.auth_database}"
            else:
                # Without authentication
                uri = f"mongodb://{self.host}:{self.port}/"
            
            client = pymongo.MongoClient(uri)
            # Test connection
            client.admin.command('ping')
            self.logger.info("Successfully connected to MongoDB")
            return client
        except Exception as e:
            self.logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _initialize_collections(self):
        """Initialize collection references"""
        try:
            self.stock_codes_collection = self.db[self.config_loader.get_collection_name('stock_codes')]
            self.k_data_collection = self.db[self.config_loader.get_collection_name('k_data')]
            self.agents_collection = self.db[self.config_loader.get_collection_name('agents')]
            self.strategies_collection = self.db[self.config_loader.get_collection_name('strategies')]
            self.config_collection = self.db[self.config_loader.get_collection_name('config')]
            self.update_dates_collection = self.db[self.config_loader.get_collection_name('update_dates')]
            self.accounts_collection = self.db['accounts']  # Default name
            self.pool_collection = self.db[self.config_loader.get_collection_name('pool')]  # Pool collection
        except Exception as e:
            self.logger.error(f"Error initializing collections: {e}")
            raise
    
    def get_collection(self, collection_key: str):
        """
        Get a collection by key from config
        
        Args:
            collection_key: Key for the collection in the config
            
        Returns:
            MongoDB collection instance
        """
        collection_name = self.config_loader.get_collection_name(collection_key)
        return self.db[collection_name]
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.logger.info("MongoDB connection closed")
    
    # Data adjustment settings
    def get_adjustment_setting(self) -> str:
        """
        Get the data adjustment setting from config collection.
        
        Returns:
            Adjustment type ('qfq', 'hfq', or '' for no adjustment)
        """
        try:
            config_record = self.config_collection.find_one()
            
            if config_record and 'data_adjustment' in config_record:
                adjust_setting = config_record['data_adjustment']
                # Validate the setting
                if adjust_setting in ['qfq', 'hfq', '']:
                    return adjust_setting
                else:
                    self.logger.warning(f"Invalid adjustment setting '{adjust_setting}', using default 'qfq'")
                    return 'qfq'
            else:
                # Default to pre-adjusted if not set
                self.logger.info("No adjustment setting found, using default 'qfq'")
                return 'qfq'
                
        except Exception as e:
            self.logger.error(f"Error getting adjustment setting: {e}")
            # Default to pre-adjusted if there's an error
            return 'qfq'
    
    def _get_column_mapping(self, adjust_type: str) -> Dict[str, str]:
        """
        Get column mapping based on adjustment type.
        
        Args:
            adjust_type: Adjustment type ('qfq', 'hfq', or 'none')
            
        Returns:
            Dictionary mapping database columns to standard column names
        """
        # Define column mappings based on adjustment type
        column_mapping: Dict[str, str] = {}
        if adjust_type == 'qfq':  # Pre-adjusted (forward adjust)
            column_mapping = {
                '日期': 'date',
                '开盘q': 'open',
                '最高q': 'high',
                '最低q': 'low',
                '收盘q': 'close',
                '成交量q': 'volume',
                '成交额q': 'amount'
            }
        elif adjust_type == 'hfq':  # Post-adjusted (backward adjust)
            column_mapping = {
                '日期': 'date',
                '开盘h': 'open',
                '最高h': 'high',
                '最低h': 'low',
                '收盘h': 'close',
                '成交量h': 'volume',
                '成交额h': 'amount'
            }
        else:  # No adjustment
            column_mapping = {
                '日期': 'date',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盘': 'close',
                '成交量': 'volume',
                '成交额': 'amount'
            }
        return column_mapping
    
    def _apply_column_mapping(self, df: pd.DataFrame, adjust_type: str) -> pd.DataFrame:
        """
        Apply column mapping to DataFrame based on adjustment type.
        
        Args:
            df: DataFrame with raw data from database
            adjust_type: Adjustment type ('qfq', 'hfq', or 'none')
            
        Returns:
            DataFrame with properly mapped columns
        """
        # Get column mapping
        column_mapping = self._get_column_mapping(adjust_type)
        
        # Select and rename columns
        available_columns = [col for col in column_mapping.keys() if col in df.columns]
        df_selected = df[available_columns].copy()
        
        # Convert column_mapping to a format suitable for pandas rename
        rename_dict: Dict[str, str] = {k: v for k, v in column_mapping.items() if k in df_selected.columns}
        if rename_dict:
            df_selected = df_selected.rename(columns=rename_dict)
        
        return df_selected
    
    def get_adjusted_k_data(self, code: str, start_date: Optional[str] = None,
                           end_date: Optional[str] = None, frequency: str = 'daily') -> pd.DataFrame:
        """
        Get K-line data with adjustment based on config settings.
        
        This is a common function that fetches K-line data with the appropriate
        adjustment (qfq, hfq, or none) based on the configuration in the database.
        
        Args:
            code: Stock code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            frequency: Data frequency ('daily', 'weekly', etc.)
            
        Returns:
            DataFrame with adjusted K-line data
        """
        try:
            # Get adjustment setting from config
            adjust_type = self.get_adjustment_setting()
            
            # Handle the case where adjust_type is an empty string (no adjustment)
            if adjust_type == '':
                adjust_type = 'none'

            # Build query with code
            query = {'代码': code}

            if start_date:
                query['日期'] = {'$gte': start_date}
            if end_date:
                if '日期' in query:
                    date_query = query['日期']
                    if isinstance(date_query, dict):
                        date_query['$lte'] = end_date
                    query['日期'] = date_query
                else:
                    query['日期'] = {'$lte': end_date}

            # Query data
            cursor = self.k_data_collection.find(query, {'_id': 0})
            data = list(cursor)

            # Convert to DataFrame
            if data:
                df = pd.DataFrame(data)
                df['日期'] = pd.to_datetime(df['日期'])
                df = df.sort_values('日期').reset_index(drop=True)

                # Apply column mapping
                df_selected = self._apply_column_mapping(df, adjust_type)

                # Ensure required columns exist
                required_columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'amount']
                for col in required_columns:
                    if col not in df_selected.columns:
                        self.logger.warning(f"Missing required column '{col}' in data for {code}")
                        return pd.DataFrame()

                self.logger.info(f"Retrieved adjusted K-data for {code} with {adjust_type} adjustment")
                return df_selected
            else:
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error getting adjusted K-line data for {code}: {e}")
            return pd.DataFrame()
    
    # Stock code management
    def get_stock_codes(self) -> List[str]:
        """
        Get all stock codes from database (alias for get_all_stock_codes)
        
        Returns:
            List of stock codes
        """
        return self.get_all_stock_codes()
    
    def get_stock_codes_from_pool(self) -> List[str]:
        """
        Get stock codes from pool collection
        
        Returns:
            List of stock codes from pool
        """
        try:
            # Get all documents from pool collection
            pool_docs = list(self.pool_collection.find({}, {'_id': 0, 'code': 1}))
            return [doc['code'] for doc in pool_docs if 'code' in doc]
        except Exception as e:
            self.logger.error(f"Error getting stock codes from pool: {e}")
            return []
    
    def get_all_stock_codes(self) -> List[str]:
        """
        Get all stock codes from database
        
        Returns:
            List of stock codes
        """
        try:
            codes = list(self.stock_codes_collection.find({}, {'_id': 0, 'code': 1}))
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
            # Clear existing codes
            self.stock_codes_collection.delete_many({})
            
            # Insert new codes
            if codes:
                documents = [{'code': code} for code in codes]
                self.stock_codes_collection.insert_many(documents)
            
            self.logger.info(f"Saved {len(codes)} stock codes to database")
            return True
        except Exception as e:
            self.logger.error(f"Error saving stock codes: {e}")
            return False
    
    # K-line data management
    def get_k_data(self, code: str, start_date: Optional[str] = None,
                   end_date: Optional[str] = None, frequency: str = 'daily') -> pd.DataFrame:
        """
        Get K-line data from database with adjustment type from config

        Args:
            code: Stock code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            frequency: Data frequency ('daily', 'weekly', etc.)
            
        Returns:
            DataFrame with K-line data
        """
        try:
            # For daily data, use the standard method
            if frequency == 'daily':
                # Get adjustment setting from config
                adjust_type = self.get_adjustment_setting()
                
                # Validate adjust_type parameter
                valid_adjust_types = ['none', 'qfq', 'hfq']
                if adjust_type not in valid_adjust_types:
                    self.logger.warning(f"Invalid adjust_type: {adjust_type}, using 'none' instead")
                    adjust_type = 'none'

                # Build query with code
                query = {'代码': code}

                if start_date:
                    query['日期'] = {'$gte': start_date}
                if end_date:
                    if '日期' in query:
                        date_query = query['日期']
                        if isinstance(date_query, dict):
                            date_query['$lte'] = end_date
                    else:
                        query['日期'] = {'$lte': end_date}

                # Query data
                cursor = self.k_data_collection.find(query, {'_id': 0})
                data = list(cursor)

                # Convert to DataFrame
                if data:
                    df = pd.DataFrame(data)
                    df['日期'] = pd.to_datetime(df['日期'])
                    df = df.sort_values('日期').reset_index(drop=True)

                    # Define column mappings based on adjustment type
                    column_mapping: Dict[str, str] = {}
                    if adjust_type == 'qfq':  # Pre-adjusted (forward adjust)
                        column_mapping = {
                            '日期': 'date',
                            '开盘q': 'open',
                            '最高q': 'high',
                            '最低q': 'low',
                            '收盘q': 'close',
                            '成交量q': 'volume',
                            '成交额q': 'amount'
                        }
                    elif adjust_type == 'hfq':  # Post-adjusted (backward adjust)
                        column_mapping = {
                            '日期': 'date',
                            '开盘h': 'open',
                            '最高h': 'high',
                            '最低h': 'low',
                            '收盘h': 'close',
                            '成交量h': 'volume',
                            '成交额h': 'amount'
                        }
                    else:  # No adjustment
                        column_mapping = {
                            '日期': 'date',
                            '开盘': 'open',
                            '最高': 'high',
                            '最低': 'low',
                            '收盘': 'close',
                            '成交量': 'volume',
                            '成交额': 'amount'
                        }

                    # Select and rename columns
                    available_columns = [col for col in column_mapping.keys() if col in df.columns]
                    df_selected = df[available_columns].copy()
                    df_selected = df_selected.rename(columns=column_mapping)  # type: ignore

                    # Ensure required columns exist
                    required_columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'amount']
                    for col in required_columns:
                        if col not in df_selected.columns:
                            self.logger.warning(f"Missing required column '{col}' in data for {code}")
                            return pd.DataFrame()

                    self.logger.info(f"Retrieved K-data for {code} with {adjust_type} adjustment")
                    return df_selected
                else:
                    return pd.DataFrame()
            else:
                # For other frequencies, we might need different handling
                # For now, we'll use the same approach but this could be extended
                query = {'代码': code}
                
                if start_date:
                    query['日期'] = {'$gte': start_date}
                if end_date:
                    if '日期' in query:
                        date_query = query['日期']
                        if isinstance(date_query, dict):
                            date_query['$lte'] = end_date
                        query['日期'] = date_query
                    else:
                        query['日期'] = {'$lte': end_date}
                
                # Add frequency to query if we have a way to distinguish it in the database
                # This would depend on how the data is stored
                
                cursor = self.k_data_collection.find(query, {'_id': 0})
                data = list(cursor)
                
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
            # If we need to distinguish by frequency, we would add that to the query
            self.k_data_collection.delete_many(delete_query)
            
            # Insert new data
            if records:
                self.k_data_collection.insert_many(records)
            
            self.logger.info(f"Saved {len(records)} {frequency} K-data records for {code}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving K-data for {code}: {e}")
            return False
    
    # Agent management methods
    def get_agents(self) -> list:
        """
        Get all agents from agents collection
        
        Returns:
            List of agents
        """
        try:
            agents = list(self.agents_collection.find({}, {'_id': 1, 'name': 1, 'description': 1, 'status': 1, 'strategies': 1, 'program': 1}))
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
            agent = self.agents_collection.find_one({'_id': ObjectId(agent_id)})
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
            result = self.agents_collection.insert_one(agent_data)
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
            # Remove _id from update data if present
            if '_id' in agent_data:
                del agent_data['_id']
            result = self.agents_collection.update_one(
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
            result = self.agents_collection.delete_one({'_id': ObjectId(agent_id)})
            return result.deleted_count > 0
        except Exception as e:
            self.logger.error(f"Error deleting agent {agent_id}: {e}")
            return False

    # Strategy management methods
    def get_strategies(self) -> list:
        """
        Get all strategies from strategies collection

        Returns:
            List of strategies
        """
        try:
            strategies = list(self.strategies_collection.find({}, {'_id': 1, 'name': 1, 'type': 1, 'description': 1, 'parameters': 1, 'program': 1, 'file': 1, 'class_name': 1}))
            # Convert ObjectId to string for JSON serialization and handle field mapping
            for strategy in strategies:
                strategy['_id'] = str(strategy['_id'])
                # Handle backward compatibility: convert program field to file/class_name if needed
                if 'program' in strategy and isinstance(strategy['program'], dict):
                    if 'file' in strategy['program']:
                        strategy['file'] = strategy['program']['file']
                    if 'class' in strategy['program']:
                        strategy['class_name'] = strategy['program']['class']
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
            strategy = self.strategies_collection.find_one({'_id': ObjectId(strategy_id)})
            if strategy:
                strategy['_id'] = str(strategy['_id'])
                # Handle backward compatibility: convert program field to file/class_name if needed
                if 'program' in strategy and isinstance(strategy['program'], dict):
                    if 'file' in strategy['program']:
                        strategy['file'] = strategy['program']['file']
                    if 'class' in strategy['program']:
                        strategy['class_name'] = strategy['program']['class']
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
            # Check if strategy has a program field and create the program file if needed
            if 'program' in strategy_data and strategy_data['program']:
                program_name = strategy_data['program']
                strategy_name = strategy_data.get('name', '')
                strategy_type = strategy_data.get('type', 'technical')
                
                # Create the program file
                try:
                    program_path = create_strategy_program_file(strategy_name, strategy_type)
                    if program_path:
                        self.logger.info(f"Created program file: {program_path}")
                    else:
                        self.logger.warning(f"Failed to create program file for strategy: {strategy_name}")
                except Exception as program_error:
                    self.logger.error(f"Error creating program file for strategy '{strategy_name}': {program_error}")
                    # Continue with strategy creation even if program creation fails
            
            result = self.strategies_collection.insert_one(strategy_data)
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
            # Check if strategy has a program field and create the program file if needed
            if 'program' in strategy_data and strategy_data['program']:
                program_name = strategy_data['program']
                strategy_name = strategy_data.get('name', '')
                strategy_type = strategy_data.get('type', 'technical')
                
                # Create the program file
                program_path = create_strategy_program_file(strategy_name, strategy_type)
                if program_path:
                    self.logger.info(f"Created program file: {program_path}")
                else:
                    self.logger.warning(f"Failed to create program file for strategy: {strategy_name}")
            
            # Remove _id from update data if present
            if '_id' in strategy_data:
                del strategy_data['_id']
            result = self.strategies_collection.update_one(
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
            result = self.strategies_collection.delete_one({'_id': ObjectId(strategy_id)})
            return result.deleted_count > 0
        except Exception as e:
            self.logger.error(f"Error deleting strategy {strategy_id}: {e}")
            return False

    def get_strategy_by_name(self, strategy_name: str):
        """
        Get a specific strategy by name
        
        Args:
            strategy_name: Strategy name
            
        Returns:
            Strategy document or None
        """
        try:
            strategy = self.strategies_collection.find_one({'name': strategy_name})
            if strategy:
                strategy['_id'] = str(strategy['_id'])
            return strategy
        except Exception as e:
            self.logger.error(f"Error getting strategy {strategy_name}: {e}")
            return None

    # Config management methods
    def get_config(self, key: str):
        """
        Get a config value by key
        
        Args:
            key: Config key
            
        Returns:
            Config value or None
        """
        try:
            config_doc = self.config_collection.find_one({'key': key})
            if config_doc:
                return config_doc.get('value')
            return None
        except Exception as e:
            self.logger.error(f"Error getting config {key}: {e}")
            return None

    def save_config(self, key: str, value):
        """
        Save a config value by key
        
        Args:
            key: Config key
            value: Config value
            
        Returns:
            Modified count or inserted ID
        """
        try:
            # Check if config already exists
            existing = self.config_collection.find_one({'key': key})
            if existing:
                result = self.config_collection.update_one(
                    {'key': key},
                    {'$set': {'value': value}}
                )
                return result.modified_count > 0
            else:
                result = self.config_collection.insert_one({'key': key, 'value': value})
                return str(result.inserted_id)
        except Exception as e:
            self.logger.error(f"Error saving config {key}: {e}")
            return None

    def get_latest_update_date(self) -> Optional[str]:
        """
        Get the latest update date
        
        Returns:
            Latest update date string or None
        """
        try:
            record = self.update_dates_collection.find_one(sort=[('date', -1)])
            if record:
                return record['date'].strftime('%Y-%m-%d')
            return None
        except Exception as e:
            self.logger.error(f"Error getting latest update date: {e}")
            return None


# Global instance for easy access
mongodb_manager = MongoDBManager()

if __name__ == "__main__":
    # Example usage
    manager = MongoDBManager()
    
    # Get all stock codes
    codes = manager.get_all_stock_codes()
    print(f"Found {len(codes)} stock codes")
    
    # Get agents
    agents = manager.get_agents()
    print(f"Found {len(agents)} agents")
    
    # Close connection
    manager.close_connection()

