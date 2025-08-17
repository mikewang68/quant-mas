"""
Momentum Strategy
A strategy that generates buy/sell signals based on momentum indicators.
"""

import pandas as pd
import numpy as np
import talib
from typing import Dict, Optional
from strategies.base_strategy import BaseStrategy

class MomentumStrategy(BaseStrategy):
    """
    Momentum Strategy
    Generates buy signals when momentum turns positive,
    and sell signals when momentum turns negative.
    """
    
    def __init__(self, name: str = "Momentum", params: Optional[Dict] = None):
        """
        Initialize the Momentum strategy.
        
        Args:
            name: Strategy name
            params: Strategy parameters
                - period: Momentum calculation period (default: 14)
                - threshold: Momentum threshold (default: 0)
                - max_position_ratio: Maximum position ratio (default: 0.1)
        """
        super().__init__(name, params)
        
        # Strategy parameters
        self.period = self.params.get('period', 14)
        self.threshold = self.params.get('threshold', 0)
        self.max_position_ratio = self.params.get('max_position_ratio', 0.1)
        
        self.logger.info(f"Initialized {self.name} strategy with params: "
                        f"period={self.period}, threshold={self.threshold}")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate momentum signals.
        
        Args:
            data: DataFrame with columns ['date', 'open', 'high', 'low', 'close', 'volume']
            
        Returns:
            DataFrame with signals
        """
        if not self.validate_data(data):
            return pd.DataFrame()
        
        # Calculate momentum
        close_prices = data['close'].values
        momentum = talib.MOM(close_prices, timeperiod=self.period)
        
        # Initialize signals
        signals = pd.DataFrame(index=data.index)
        signals['date'] = data['date']
        signals['close'] = data['close']
        signals['momentum'] = momentum
        signals['signal'] = 'HOLD'
        signals['position'] = 0.0
        
        # Generate signals
        for i in range(1, len(signals)):
            # Buy signal: Momentum crosses above threshold
            if (momentum[i-1] <= self.threshold and 
                momentum[i] > self.threshold):
                signals.loc[i, 'signal'] = 'BUY'
                signals.loc[i, 'position'] = 1.0
            
            # Sell signal: Momentum crosses below threshold
            elif (momentum[i-1] >= self.threshold and 
                  momentum[i] < self.threshold):
                signals.loc[i, 'signal'] = 'SELL'
                signals.loc[i, 'position'] = -1.0
            
            # Hold signal: maintain previous position
            else:
                signals.loc[i, 'signal'] = 'HOLD'
                signals.loc[i, 'position'] = signals.loc[i-1, 'position']
        
        return signals
    
    def calculate_position_size(self, signal: str, portfolio_value: float, 
                              price: float) -> float:
        """
        Calculate position size based on signal.
        
        Args:
            signal: Trading signal ('BUY', 'SELL', 'HOLD')
            portfolio_value: Current portfolio value
            price: Current asset price
            
        Returns:
            Position size (number of shares)
        """
        if signal == 'BUY':
            # Calculate maximum position value
            max_position_value = portfolio_value * self.max_position_ratio
            
            # Calculate number of shares
            shares = max_position_value / price
            
            # Round to nearest 100 shares (common in Chinese market)
            shares = round(shares / 100) * 100
            
            return float(shares)
        
        elif signal == 'SELL':
            # For sell signals, return negative position size
            # In practice, this would depend on current holdings
            return -100.0  # Placeholder
        
        else:
            return 0.0

# Example usage
if __name__ == "__main__":
    import logging
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create sample data
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    sample_data = pd.DataFrame({
        'date': dates,
        'open': np.random.uniform(100, 110, 100),
        'high': np.random.uniform(110, 120, 100),
        'low': np.random.uniform(90, 100, 100),
        'close': np.random.uniform(100, 110, 100),
        'volume': np.random.uniform(1000000, 2000000, 100)
    })
    
    # Initialize strategy
    strategy = MomentumStrategy()
    
    # Generate signals
    signals = strategy.generate_signals(sample_data)
    print(f"Generated {len(signals[signals['signal'] != 'HOLD'])} trading signals")
    print(signals.tail(10))

