"""
Backtesting engine for the quant trading system.
Uses backtrader to perform strategy backtesting.
"""

import backtrader as bt
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import matplotlib.pyplot as plt

# Configure logger
logger = logging.getLogger(__name__)

class Backtester:
    """
    Backtesting engine using backtrader.
    """
    
    def __init__(self, initial_capital: float = 1000000.0, commission: float = 0.001):
        """
        Initialize the backtester.
        
        Args:
            initial_capital: Initial capital for backtesting
            commission: Commission rate per trade
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.logger = logging.getLogger(__name__)
        
        # Initialize cerebro engine
        self.cerebro = bt.Cerebro()
        self.cerebro.broker.setcash(initial_capital)
        self.cerebro.broker.setcommission(commission=commission)
        
        self.logger.info(f"Backtester initialized with initial_capital={initial_capital}, commission={commission}")
    
    def add_data(self, data: pd.DataFrame, symbol: str = "STOCK"):
        """
        Add data to the backtesting engine.
        
        Args:
            data: DataFrame with OHLCV data
            symbol: Symbol name for the data
        """
        try:
            # Convert pandas DataFrame to backtrader data feed
            bt_data = bt.feeds.PandasData(
                dataname=data,
                name=symbol,
                datetime='date',
                open='open',
                high='high',
                low='low',
                close='close',
                volume='volume',
                openinterest=-1
            )
            
            self.cerebro.adddata(bt_data)
            self.logger.info(f"Added data for {symbol} with {len(data)} records")
            
        except Exception as e:
            self.logger.error(f"Error adding data for {symbol}: {e}")
            raise
    
    def add_strategy(self, strategy_class, **kwargs):
        """
        Add strategy to the backtesting engine.
        
        Args:
            strategy_class: Strategy class to add
            **kwargs: Strategy parameters
        """
        try:
            self.cerebro.addstrategy(strategy_class, **kwargs)
            self.logger.info(f"Added strategy {strategy_class.__name__}")
            
        except Exception as e:
            self.logger.error(f"Error adding strategy {strategy_class.__name__}: {e}")
            raise
    
    def run(self) -> List[Any]:
        """
        Run the backtest.
        
        Returns:
            List of strategy instances
        """
        self.logger.info("Starting backtest...")
        
        # Print starting portfolio value
        start_value = self.cerebro.broker.getvalue()
        self.logger.info(f"Starting Portfolio Value: {start_value:.2f}")
        
        # Run the backtest
        results = self.cerebro.run()
        
        # Print final portfolio value
        end_value = self.cerebro.broker.getvalue()
        profit = end_value - start_value
        profit_pct = (profit / start_value) * 100 if start_value > 0 else 0
        
        self.logger.info(f"Final Portfolio Value: {end_value:.2f}")
        self.logger.info(f"Profit: {profit:.2f} ({profit_pct:.2f}%)")
        
        return results
    
    def plot(self, filename: Optional[str] = None):
        """
        Plot the backtest results.
        
        Args:
            filename: Output filename for the plot (optional)
        """
        try:
            if filename:
                # Save plot to file
                self.cerebro.plot(savefig=True, figfilename=filename)
                self.logger.info(f"Plot saved to {filename}")
            else:
                # Display plot
                self.cerebro.plot()
                
        except Exception as e:
            self.logger.error(f"Error plotting results: {e}")
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """
        Calculate performance metrics.
        
        Returns:
            Dictionary of performance metrics
        """
        try:
            # Get analyzer results (if analyzers were added)
            analyzers = {}
            
            # Add common analyzers
            self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
            self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
            self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
            self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
            
            # Run backtest with analyzers
            results = self.cerebro.run()
            
            if results:
                strategy = results[0]
                
                # Extract metrics
                analyzers['returns'] = strategy.analyzers.returns.get_analysis()
                analyzers['sharpe'] = strategy.analyzers.sharpe.get_analysis()
                analyzers['drawdown'] = strategy.analyzers.drawdown.get_analysis()
                analyzers['trades'] = strategy.analyzers.trades.get_analysis()
                
                # Calculate additional metrics
                metrics = {
                    'total_return': analyzers['returns'].get('rtot', 0),
                    'annual_return': analyzers['returns'].get('ravg', 0) * 252,  # Assuming 252 trading days
                    'sharpe_ratio': analyzers['sharpe'].get('sharperatio', 0),
                    'max_drawdown': analyzers['drawdown'].get('max.drawdown', 0),
                    'max_drawdown_pct': analyzers['drawdown'].get('max.drawdown.pct', 0),
                }
                
                # Add trade statistics
                if 'total' in analyzers['trades']:
                    total_trades = analyzers['trades']['total']['total']
                    won_trades = analyzers['trades']['won']['total'] if 'won' in analyzers['trades'] else 0
                    win_rate = won_trades / total_trades if total_trades > 0 else 0
                    
                    metrics['total_trades'] = total_trades
                    metrics['win_rate'] = win_rate
                    
                    if 'won' in analyzers['trades'] and 'pnl' in analyzers['trades']['won']:
                        avg_win = analyzers['trades']['won']['pnl']['average']
                        metrics['avg_win'] = avg_win
                        
                    if 'lost' in analyzers['trades'] and 'pnl' in analyzers['trades']['lost']:
                        avg_loss = analyzers['trades']['lost']['pnl']['average']
                        metrics['avg_loss'] = avg_loss
                        
                    if metrics.get('avg_win') and metrics.get('avg_loss'):
                        profit_factor = abs(metrics['avg_win'] / metrics['avg_loss'])
                        metrics['profit_factor'] = profit_factor
                
                return metrics
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error calculating performance metrics: {e}")
            return {}

# Example usage
if __name__ == "__main__":
    import logging
    import yfinance as yf
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create sample data (using yfinance for demonstration)
    try:
        # Download sample data
        data = yf.download("AAPL", start="2020-01-01", end="2023-01-01")
        data.reset_index(inplace=True)
        data.rename(columns={'Date': 'date'}, inplace=True)
        
        # Initialize backtester
        backtester = Backtester(initial_capital=100000, commission=0.001)
        
        # Add data
        backtester.add_data(data, "AAPL")
        
        # Add a simple strategy (using backtrader's built-in strategy)
        class SimpleMAStrategy(bt.Strategy):
            params = (('maperiod', 15),)
            
            def __init__(self):
                self.sma = bt.indicators.SimpleMovingAverage(
                    self.datas[0], period=self.params.maperiod)
            
            def next(self):
                if not self.position:
                    if self.datas[0].close[0] > self.sma[0]:
                        self.buy()
                else:
                    if self.datas[0].close[0] < self.sma[0]:
                        self.sell()
        
        backtester.add_strategy(SimpleMAStrategy)
        
        # Run backtest
        results = backtester.run()
        
        # Get performance metrics
        metrics = backtester.get_performance_metrics()
        print("Performance Metrics:")
        for key, value in metrics.items():
            print(f"{key}: {value}")
            
    except Exception as e:
        print(f"Error in example: {e}")

