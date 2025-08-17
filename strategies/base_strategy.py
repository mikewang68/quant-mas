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

# Example usage
if __name__ == "__main__":
    # This is an abstract class, so we can't instantiate it directly
    pass

