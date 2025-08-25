"""
MACD Strategy
A strategy that generates buy/sell signals based on MACD (Moving Average Convergence Divergence).
"""

import pandas as pd
import numpy as np
import talib
from typing import Dict, Optional, List
from strategies.base_strategy import BaseStrategy

class MACDStrategy(BaseStrategy):
    """
    MACD Strategy
    Generates buy signals when MACD line crosses above signal line,
    and sell signals when MACD line crosses below signal line.
    """
    
    def __init__(self, name: str = "MACD", params: Optional[Dict] = None):
        """
        Initialize the MACD strategy.
        
        Args:
            name: Strategy name
            params: Strategy parameters
                - fast_period: Fast EMA period (default: 12)
                - slow_period: Slow EMA period (default: 26)
                - signal_period: Signal line period (default: 9)
                - max_position_ratio: Maximum position ratio (default: 0.1)
        """
        super().__init__(name, params)
        
        # Strategy parameters
        self.fast_period = self.params.get('fast_period', 12)
        self.slow_period = self.params.get('slow_period', 26)
        self.signal_period = self.params.get('signal_period', 9)
        self.max_position_ratio = self.params.get('max_position_ratio', 0.1)

        self.logger.info(f"Initialized {self.name} strategy with params: "
                        f"fast_period={self.fast_period}, slow_period={self.slow_period}, "
                        f"signal_period={self.signal_period}")

    def execute(self, stock_data: Dict[str, pd.DataFrame], agent_name: str, db_manager) -> List[Dict]:
        """
        Execute the strategy on provided stock data and automatically save results

        Args:
            stock_data: Dictionary mapping stock codes to their data DataFrames
            agent_name: Name of the agent executing this strategy
            db_manager: Database manager instance

        Returns:
            List of selected stocks with analysis results
        """
        self.log_info(f"Executing {self.name} strategy on {len(stock_data)} stocks")

        selected_stocks = []

        # Process each stock
        for code, data in stock_data.items():
            try:
                # Generate signals for this stock
                signals = self.generate_signals(data)

                # Check if we have any buy signals
                buy_signals = signals[signals['signal'] == 'BUY']

                if not buy_signals.empty:
                    # Get the latest signal
                    latest_signal = buy_signals.iloc[-1]

                    # Calculate score based on signal strength
                    # For MACD, we can use the MACD histogram as a measure of signal strength
                    macd_hist = latest_signal['macd_hist']
                    score = min(1.0, max(0.0, abs(macd_hist) * 10))  # Normalize score to 0-1 range

                    # Calculate position size
                    position = self.calculate_position_size(
                        latest_signal['signal'],
                        100000,  # Default portfolio value - in practice this would be dynamic
                        latest_signal['close']
                    )

                    # Create technical analysis data
                    technical_analysis = {
                        'price': float(latest_signal['close']),
                        'macd': {
                            'macd_line': float(latest_signal['macd']),
                            'signal_line': float(latest_signal['macd_signal']),
                            'histogram': float(latest_signal['macd_hist'])
                        },
                        'score': score,
                        'position': position
                    }

                    # Add to selected stocks
                    selected_stocks.append({
                        'code': code,
                        'selection_reason': f"MACD buy signal with strength {macd_hist:.4f}",
                        'score': score,
                        'position': position,
                        'technical_analysis': technical_analysis,
                        'signals': {
                            'signal': latest_signal['signal'],
                            'close_price': float(latest_signal['close'])
                        }
                    })

            except Exception as e:
                self.log_warning(f"Error processing stock {code}: {e}")
                continue

        self.log_info(f"Selected {len(selected_stocks)} stocks")

        # Automatically save results to pool collection
        if selected_stocks:
            from datetime import datetime

            current_date = datetime.now().strftime("%Y-%m-%d")

            # Use the new common formatting methods
            formatted_output = self.format_strategy_output(
                stocks=selected_stocks,
                agent_name=agent_name,
                date=current_date,
                strategy_params=self.params,
                additional_metadata={
                    "strategy_version": "1.0",
                    "total_stocks_analyzed": len(stock_data),
                }
            )

            save_success = self.save_to_pool(
                db_manager=db_manager,
                agent_name=agent_name,
                stocks=selected_stocks,
                date=current_date,
                strategy_params=self.params,
                additional_metadata={
                    "strategy_version": "1.0",
                    "total_stocks_analyzed": len(stock_data),
                },
            )

            if save_success:
                self.log_info("Strategy results saved to pool successfully")
            else:
                self.log_error("Failed to save strategy results to pool")

        return selected_stocks
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate MACD signals.
        
        Args:
            data: DataFrame with columns ['date', 'open', 'high', 'low', 'close', 'volume']
            
        Returns:
            DataFrame with signals
        """
        if not self.validate_data(data):
            return pd.DataFrame()
        
        # Calculate MACD
        close_prices = data['close'].values
        macd, macd_signal, macd_hist = talib.MACD(
            close_prices,
            fastperiod=self.fast_period,
            slowperiod=self.slow_period,
            signalperiod=self.signal_period
        )
        
        # Initialize signals
        signals = pd.DataFrame(index=data.index)
        signals['date'] = data['date']
        signals['close'] = data['close']
        signals['macd'] = macd
        signals['macd_signal'] = macd_signal
        signals['macd_hist'] = macd_hist
        signals['signal'] = 'HOLD'
        signals['position'] = 0.0
        
        # Generate signals
        for i in range(1, len(signals)):
            # Buy signal: MACD line crosses above signal line
            if (macd[i-1] <= macd_signal[i-1] and 
                macd[i] > macd_signal[i]):
                signals.loc[i, 'signal'] = 'BUY'
                signals.loc[i, 'position'] = 1.0
            
            # Sell signal: MACD line crosses below signal line
            elif (macd[i-1] >= macd_signal[i-1] and 
                  macd[i] < macd_signal[i]):
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
    strategy = MACDStrategy()
    
    # Generate signals
    signals = strategy.generate_signals(sample_data)
    print(f"Generated {len(signals[signals['signal'] != 'HOLD'])} trading signals")
    print(signals.tail(10))

