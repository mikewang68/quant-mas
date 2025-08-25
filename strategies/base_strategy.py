"""
Base strategy class for the quant trading system.
All strategies should inherit from this class.
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

# Configure logger
logger = logging.getLogger(__name__)

class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    """
    
    def __init__(self, name: str, params: Optional[Dict] = None):
        """
        Initialize the base strategy.
        
        Args:
            name: Name of the strategy
            params: Strategy parameters
        """
        self.name = name
        self.params = params or {}
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on input data.
        
        Args:
            data: Input data DataFrame with required columns
            
        Returns:
            DataFrame with signals
        """
        pass
    
    @abstractmethod
    def calculate_position_size(self, signal: str, portfolio_value: float, 
                              price: float) -> float:
        """
        Calculate position size based on signal and portfolio value.
        
        Args:
            signal: Trading signal ('BUY', 'SELL', 'HOLD')
            portfolio_value: Current portfolio value
            price: Current asset price
            
        Returns:
            Position size (number of shares/contracts)
        """
        pass
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate input data format.
        
        Args:
            data: Input data DataFrame
            
        Returns:
            True if data is valid, False otherwise
        """
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in data.columns:
                self.logger.error(f"Missing required column: {col}")
                return False
        return True
    
    def log_info(self, message: str):
        """Log info message with strategy name"""
        self.logger.info(f"[{self.name}] {message}")
    
    def log_warning(self, message: str):
        """Log warning message with strategy name"""
        self.logger.warning(f"[{self.name}] {message}")
    
    def log_error(self, message: str):
        """Log error message with strategy name"""
        self.logger.error(f"[{self.name}] {message}")

    def save_to_pool(self, db_manager, agent_name: str, stocks: List[Dict], 
                     date: str, strategy_params: Optional[Dict] = None,
                     additional_metadata: Optional[Dict] = None) -> bool:
        """
        Save strategy results to pool collection.
        
        Args:
            db_manager: Database manager instance with database_operations
            agent_name: Name of the agent executing this strategy
            stocks: List of selected stocks with analysis data
            date: Selection date (YYYY-MM-DD)
            strategy_params: Strategy parameters used (optional)
            additional_metadata: Additional metadata (optional)
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Import here to avoid circular imports
            from data.database_operations import DatabaseOperations
            
            # Create database operations instance
            db_ops = DatabaseOperations(db_manager)
            
            # Create a unique strategy key
            from datetime import datetime
            strategy_key = f"{agent_name}_{self.name}_{datetime.now().strftime('%Y-%W')}"
            
            # Save results to pool using the utility method
            success = db_ops.save_strategy_output_to_pool(
                strategy_key=strategy_key,
                agent_name=agent_name,
                strategy_id=self.name.lower().replace(' ', '_'),
                strategy_name=self.name,
                stocks=stocks,
                date=date,
                strategy_params=strategy_params or self.params,
                additional_metadata=additional_metadata
            )
            
            if success:
                self.log_info(f"Successfully saved strategy results to pool with key: {strategy_key}")
            else:
                self.log_error("Failed to save strategy results to pool")
                
            return success
            
        except Exception as e:
            self.log_error(f"Error saving strategy results to pool: {e}")
            return False

    def format_stock_data_for_pool(self, stock_data: Dict) -> Dict:
        """
        Format stock data for consistent storage in pool collection.

        This method ensures all strategies structure their output data in a
        consistent format for the pool collection.

        Args:
            stock_data: Dictionary containing stock analysis data

        Returns:
            Formatted stock data dictionary
        """
        formatted_data = {
            'code': stock_data.get('code', ''),
            'selection_reason': stock_data.get('selection_reason', ''),
            'score': float(stock_data.get('score', 0.0)),
            'position': float(stock_data.get('position', 0.0)),
            'strategy_name': self.name,
            'strategy_key': f"{self.name}_{self.__class__.__name__}".lower().replace(' ', '_'),
            'technical_analysis': stock_data.get('technical_analysis', {}),
            'signals': stock_data.get('signals', {}),
            'metadata': stock_data.get('metadata', {})
        }

        # Add any additional fields that might be present
        for key, value in stock_data.items():
            if key not in formatted_data:
                formatted_data[key] = value

        return formatted_data

    def format_strategy_output(self, stocks: List[Dict], agent_name: str,
                             date: str, strategy_params: Optional[Dict] = None,
                             additional_metadata: Optional[Dict] = None) -> Dict:
        """
        Format strategy output for consistent database storage.

        Args:
            stocks: List of selected stocks with analysis data
            agent_name: Name of the agent executing this strategy
            date: Selection date (YYYY-MM-DD)
            strategy_params: Strategy parameters used
            additional_metadata: Additional metadata

        Returns:
            Formatted strategy output dictionary
        """
        from datetime import datetime

        # Format all stock data
        formatted_stocks = [self.format_stock_data_for_pool(stock) for stock in stocks]

        # Create strategy key
        strategy_key = f"{agent_name}_{self.name}_{datetime.now().strftime('%Y-%W')}"

        # Prepare output structure
        output = {
            'strategy_key': strategy_key,
            'agent_name': agent_name,
            'strategy_id': self.name.lower().replace(' ', '_'),
            'strategy_name': self.name,
            'stocks': formatted_stocks,
            'date': date,
            'count': len(formatted_stocks),
            'strategy_params': strategy_params or self.params,
            'metadata': {
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'total_stocks_analyzed': len(stocks)
            }
        }

        # Add additional metadata if provided
        if additional_metadata:
            output['metadata'].update(additional_metadata)

        return output

# Example usage
if __name__ == "__main__":
    # This is an abstract class, so we can't instantiate it directly
    pass

