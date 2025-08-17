"""
Mean Reversion Strategy
A strategy that generates buy/sell signals based on mean reversion principles.
"""

import pandas as pd
import numpy as np
import talib
from typing import Dict, Optional
from strategies.base_strategy import BaseStrategy

class MeanReversionStrategy(BaseStrategy):
    """
    Mean Reversion Strategy
    Generates buy signals when price deviates significantly below moving average,
    and sell signals when price deviates significantly above moving average.
    """
    
    def __init__(self, name: str = "Mean_Reversion", params: Optional[Dict] = None):
        """
        Initialize the Mean Reversion strategy.
        
        Args:
            name: Strategy name
            params: Strategy parameters
                - period: Moving average period (default: 20)
                - std_dev_multiplier: Standard deviation multiplier (default: 2)
                - max_position_ratio: Maximum position ratio (default: 0.1)
        """
        super().__init__(name, params)
        
        # Strategy parameters
        self.period = self.params.get('period', 20)
        self.std_dev_multiplier = self.params.get('std_dev_multiplier', 2)
        self.max_position_ratio = self.params.get('max_position_ratio', 0.1)
        
        self.logger.info(f"Initialized {self.name} strategy with params: "
                        f"period={self.period}, std_dev_multiplier={self.std_dev_multiplier}")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate mean reversion signals.
        
        Args:
            data: DataFrame with columns ['date', 'open', 'high', 'low', 'close', 'volume']
            
        Returns:
            DataFrame with signals
        """
        if not self.validate_data(data):
            return pd.DataFrame()
        
        # Calculate indicators
        close_prices = data['close'].values
        ma = talib.SMA(close_prices, timeperiod=self.period)
        std_dev = talib.STDDEV(close_prices, timeperiod=self.period)
        
        upper_band = ma + (std_dev * self.std_dev_multiplier)
        lower_band = ma - (std_dev * self.std_dev_multiplier)
        
        # Initialize signals
        signals = pd.DataFrame(index=data.index)
        signals['date'] = data['date']
        signals['close'] = data['close']
        signals['ma'] = ma
        signals['upper_band'] = upper_band
        signals['lower_band'] = lower_band
        signals['signal'] = 'HOLD'
        signals['position'] = 0.0
        
        # Generate signals
        for i in range(1, len(signals)):
            # Buy signal: Price crosses below lower band (oversold)
            if (close_prices[i-1] >= lower_band[i-1] and 
                close_prices[i] < lower_band[i]):
                signals.loc[i, 'signal'] = 'BUY'
                signals.loc[i, 'position'] = 1.0
            
            # Sell signal: Price crosses above upper band (overbought)
            elif (close_prices[i-1] <= upper_band[i-1] and 
                  close_prices[i] > upper_band[i]):
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
    strategy = MeanReversionStrategy()
    
    # Generate signals
    signals = strategy.generate_signals(sample_data)
    print(f"Generated {len(signals[signals['signal'] != 'HOLD'])} trading signals")
    print(signals.tail(10))

