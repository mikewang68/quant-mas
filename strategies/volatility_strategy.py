"""
Volatility Strategy
A strategy that generates buy/sell signals based on volatility indicators.
"""

import pandas as pd
import numpy as np
import talib
from typing import Dict, Optional
from strategies.base_strategy import BaseStrategy

class VolatilityStrategy(BaseStrategy):
    """
    Volatility Strategy
    Generates buy signals when volatility is low (expecting breakout),
    and sell signals when volatility is high (expecting reversal).
    """
    
    def __init__(self, name: str = "Volatility", params: Optional[Dict] = None):
        """
        Initialize the Volatility strategy.
        
        Args:
            name: Strategy name
            params: Strategy parameters
                - period: Volatility calculation period (default: 14)
                - low_percentile: Low volatility percentile threshold (default: 20)
                - high_percentile: High volatility percentile threshold (default: 80)
                - max_position_ratio: Maximum position ratio (default: 0.1)
        """
        super().__init__(name, params)
        
        # Strategy parameters
        self.period = self.params.get('period', 14)
        self.low_percentile = self.params.get('low_percentile', 20)
        self.high_percentile = self.params.get('high_percentile', 80)
        self.max_position_ratio = self.params.get('max_position_ratio', 0.1)
        
        self.logger.info(f"Initialized {self.name} strategy with params: "
                        f"period={self.period}, low_percentile={self.low_percentile}, "
                        f"high_percentile={self.high_percentile}")
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate volatility signals.
        
        Args:
            data: DataFrame with columns ['date', 'open', 'high', 'low', 'close', 'volume']
            
        Returns:
            DataFrame with signals
        """
        if not self.validate_data(data):
            return pd.DataFrame()
        
        # Calculate volatility (ATR - Average True Range)
        high_prices = data['high'].values
        low_prices = data['low'].values
        close_prices = data['close'].values
        
        atr = talib.ATR(high_prices, low_prices, close_prices, timeperiod=self.period)
        
        # Calculate percentile thresholds
        low_threshold = np.percentile(atr[~np.isnan(atr)], self.low_percentile)
        high_threshold = np.percentile(atr[~np.isnan(atr)], self.high_percentile)
        
        # Initialize signals
        signals = pd.DataFrame(index=data.index)
        signals['date'] = data['date']
        signals['close'] = data['close']
        signals['atr'] = atr
        signals['signal'] = 'HOLD'
        signals['position'] = 0.0
        
        # Generate signals
        for i in range(1, len(signals)):
            # Buy signal: ATR crosses below low threshold (low volatility)
            if (atr[i-1] >= low_threshold and 
                atr[i] < low_threshold and 
                not np.isnan(atr[i])):
                signals.loc[i, 'signal'] = 'BUY'
                signals.loc[i, 'position'] = 1.0
            
            # Sell signal: ATR crosses above high threshold (high volatility)
            elif (atr[i-1] <= high_threshold and 
                  atr[i] > high_threshold and 
                  not np.isnan(atr[i])):
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
    strategy = VolatilityStrategy()
    
    # Generate signals
    signals = strategy.generate_signals(sample_data)
    print(f"Generated {len(signals[signals['signal'] != 'HOLD'])} trading signals")
    print(signals.tail(10))

