"""
Demo Strategy Implementation
Example showing how to use the new save_to_pool functionality
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategies.base_strategy import BaseStrategy

class DemoStrategy(BaseStrategy):
    """
    Demo strategy that demonstrates how to automatically save results to pool collection
    """
    
    def __init__(self, name: str = "Demo Strategy", params: Optional[Dict] = None):
        """
        Initialize the demo strategy
        
        Args:
            name: Strategy name
            params: Strategy parameters
        """
        super().__init__(name, params or {
            'rsi_period': 14,
            'rsi_min': 30,
            'rsi_max': 70,
            'short': 5,
            'long': 20
        })
    
    def analyze(self, data: pd.DataFrame) -> Tuple[bool, str, Optional[float]]:
        """
        Analyze stock data and determine if it meets selection criteria
        
        Args:
            data: DataFrame with stock data including OHLCV columns
            
        Returns:
            Tuple of (meets_criteria, selection_reason, score)
        """
        if data.empty or len(data) < self.params['ma_long']:
            return False, "Insufficient data", None
        
        try:
            # Get latest prices
            close_prices = data['close'].values
            current_price = close_prices[-1]
            
            # Calculate simple moving averages
            ma_short = np.mean(close_prices[-self.params['ma_short']:])
            ma_long = np.mean(close_prices[-self.params['ma_long']:])
            
            # Simple technical analysis - price above both moving averages
            meets_criteria = current_price > ma_short > ma_long
            
            if meets_criteria:
                reason = f"Selected - Price: {current_price:.2f}, MA{self.params['ma_short']}: {ma_short:.2f}, MA{self.params['ma_long']}: {ma_long:.2f}"
                # Simple score based on how much price is above moving averages
                score = min(1.0, (current_price / ma_long - 1) * 10)
            else:
                reason = f"Not selected - Price: {current_price:.2f}, MA{self.params['ma_short']}: {ma_short:.2f}, MA{self.params['ma_long']}: {ma_long:.2f}"
                score = None
                
            return meets_criteria, reason, score
            
        except Exception as e:
            self.log_error(f"Error in analysis: {e}")
            return False, f"Error in analysis: {e}", None
    
    def execute(self, stock_data: Dict[str, pd.DataFrame], 
                agent_name: str, db_manager) -> List[Dict]:
        """
        Execute the strategy on provided stock data and automatically save results
        
        Args:
            stock_data: Dictionary mapping stock codes to their data DataFrames
            agent_name: Name of the agent executing this strategy
            db_manager: Database manager instance
            
        Returns:
            List of selected stocks with analysis results
        """
        self.log_info(f"Executing {self.name} on {len(stock_data)} stocks")
        
        selected_stocks = []
        
        # Analyze each stock
        for code, data in stock_data.items():
            try:
                meets_criteria, reason, score = self.analyze(data)
                
                if meets_criteria:
                    # Add technical analysis data
                    technical_analysis = {}
                    if not data.empty:
                        close_prices = data['close'].values
                        if len(close_prices) >= 20:  # Need at least 20 data points for basic analysis
                            technical_analysis = {
                                'price': float(close_prices[-1]),
                                'moving_averages': {
                                    'sma_5': float(np.mean(close_prices[-5:])),
                                    'sma_20': float(np.mean(close_prices[-20:]))
                                }
                            }
                    
                    selected_stocks.append({
                        'code': code,
                        'selection_reason': reason,
                        'score': score,
                        'technical_analysis': technical_analysis
                    })
                    
            except Exception as e:
                self.log_warning(f"Error processing stock {code}: {e}")
                continue
        
        self.log_info(f"Selected {len(selected_stocks)} stocks")
        
        # Automatically save results to pool collection
        if selected_stocks:
            from datetime import datetime
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            save_success = self.save_to_pool(
                db_manager=db_manager,
                agent_name=agent_name,
                stocks=selected_stocks,
                date=current_date,
                strategy_params=self.params,
                additional_metadata={
                    'strategy_version': '1.0',
                    'total_stocks_analyzed': len(stock_data)
                }
            )
            
            if save_success:
                self.log_info("Strategy results automatically saved to pool collection")
            else:
                self.log_error("Failed to save strategy results to pool collection")
        
        return selected_stocks

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on input data.
        
        Args:
            data: Input data DataFrame with required columns
            
        Returns:
            DataFrame with signals
        """
        # For demo purposes, we'll just return a simple signal
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 'HOLD'
        signals['position'] = 0.0
        return signals
    
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
        if signal == 'BUY':
            # For demo, allocate 10% of portfolio value
            return (portfolio_value * 0.1) / price
        elif signal == 'SELL':
            return -100.0  # Sell 100 shares
        else:
            return 0.0  # Hold position

# Example usage
if __name__ == "__main__":
    # This is just an example - in practice, this would be called by an agent
    pass

