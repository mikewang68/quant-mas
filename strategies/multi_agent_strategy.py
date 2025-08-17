"""
Multi-agent quant trading system implementation.
This strategy uses weekly stock selection and daily trading decisions.
"""

import backtrader as bt
import pandas as pd
import numpy as np
import talib
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logger
logger = logging.getLogger(__name__)

class MultiAgentStrategy(bt.Strategy):
    """
    Multi-agent quant trading strategy.
    Uses weekly stock selection and daily trading decisions.
    """
    
    params = (
        ('max_position', 0.1),  # Maximum 10% of portfolio in one stock
        ('stop_loss', 0.05),    # 5% stop loss
        ('take_profit', 0.1),   # 10% take profit
        ('commission', 0.001),  # Commission rate
    )
    
    def __init__(self):
        """
        Initialize the strategy.
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize variables
        self.orders = {}  # Track orders for each data
        self.buy_prices = {}  # Track buy prices
        self.position_sizes = {}  # Track position sizes
        
        # Performance tracking
        self.start_value = self.broker.getvalue()
        self.end_value = self.start_value
        
        # Initialize indicators for each data
        self.indicators = {}
        for data in self.datas:
            symbol = data._name
            self.indicators[symbol] = {
                'sma5': bt.indicators.SimpleMovingAverage(data.close, period=5),
                'sma20': bt.indicators.SimpleMovingAverage(data.close, period=20),
                'rsi': bt.indicators.RSI(data.close, period=14),
                'macd': bt.indicators.MACD(data.close),
                'bollinger': bt.indicators.BollingerBands(data.close, period=20)
            }
    
    def next(self):
        """
        Main strategy logic executed on each bar.
        """
        # Process each data (stock)
        for data in self.datas:
            symbol = data._name
            self._process_stock(symbol, data)
    
    def _process_stock(self, symbol: str, data):
        """
        Process a single stock.
        
        Args:
            symbol: Stock symbol
            data: Stock data
        """
        # Get current position
        position = self.getposition(data)
        position_size = position.size
        
        # Get indicators
        sma5 = self.indicators[symbol]['sma5'][0]
        sma20 = self.indicators[symbol]['sma20'][0]
        rsi = self.indicators[symbol]['rsi'][0]
        macd = self.indicators[symbol]['macd'].macd[0]
        macd_signal = self.indicators[symbol]['macd'].signal[0]
        bollinger_upper = self.indicators[symbol]['bollinger'].top[0]
        bollinger_lower = self.indicators[symbol]['bollinger'].bot[0]
        
        current_price = data.close[0]
        
        # Check if we have an open position
        if position_size > 0:
            # Check exit conditions
            exit_signal = self._check_exit_conditions(
                current_price, symbol, sma5, sma20, macd, macd_signal, rsi
            )
            
            if exit_signal:
                # Close position
                self.close(data)
                self.logger.info(f"Closed position for {symbol} at {current_price:.2f}")
        else:
            # Check entry conditions
            entry_signal = self._check_entry_conditions(
                current_price, sma5, sma20, macd, macd_signal, rsi, 
                bollinger_upper, bollinger_lower
            )
            
            if entry_signal:
                # Calculate position size
                portfolio_value = self.broker.getvalue()
                target_position_value = portfolio_value * self.p.max_position
                size = target_position_value / current_price
                
                # Round to nearest 100 shares
                size = int(size / 100) * 100
                
                if size > 0:
                    # Open position
                    self.buy(data, size=size)
                    self.buy_prices[symbol] = current_price
                    self.position_sizes[symbol] = size
                    self.logger.info(f"Opened position for {symbol} at {current_price:.2f}, size: {size}")
    
    def _check_entry_conditions(self, price: float, sma5: float, sma20: float, 
                               macd: float, macd_signal: float, rsi: float,
                               bollinger_upper: float, bollinger_lower: float) -> bool:
        """
        Check if entry conditions are met.
        
        Returns:
            True if should enter, False otherwise
        """
        # Golden cross (5-day MA crosses above 20-day MA)
        if sma5 > sma20:
            # MACD bullish crossover
            if macd > macd_signal:
                # RSI not overbought
                if rsi < 70:
                    # Price above lower Bollinger Band
                    if price > bollinger_lower:
                        return True
        return False
    
    def _check_exit_conditions(self, price: float, symbol: str, sma5: float, sma20: float,
                              macd: float, macd_signal: float, rsi: float) -> bool:
        """
        Check if exit conditions are met.
        
        Returns:
            True if should exit, False otherwise
        """
        # Check stop loss
        if symbol in self.buy_prices:
            entry_price = self.buy_prices[symbol]
            if price / entry_price - 1 < -self.p.stop_loss:
                return True
        
        # Check take profit
        if symbol in self.buy_prices:
            entry_price = self.buy_prices[symbol]
            if price / entry_price - 1 > self.p.take_profit:
                return True
        
        # Death cross (5-day MA crosses below 20-day MA)
        if sma5 < sma20:
            # MACD bearish crossover
            if macd < macd_signal:
                # RSI oversold or overbought
                if rsi > 70 or rsi < 30:
                    return True
        
        return False
    
    def notify_order(self, order):
        """
        Notify when an order is submitted, accepted, or completed.
        """
        if order.status in [order.Submitted, order.Accepted]:
            # Order submitted/accepted - nothing to do
            return
        
        # Order completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.logger.info(f"BUY EXECUTED: {order.data._name}, Price: {order.executed.price:.2f}, Size: {order.executed.size}")
            else:
                self.logger.info(f"SELL EXECUTED: {order.data._name}, Price: {order.executed.price:.2f}, Size: {order.executed.size}")
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.logger.warning(f"Order {order.Status[order.status]} for {order.data._name}")
    
    def notify_trade(self, trade):
        """
        Notify when a trade is opened or closed.
        """
        if not trade.isclosed:
            return
        
        self.logger.info(f"OPERATION PROFIT: Gross {trade.pnl:.2f}, Net {trade.pnlcomm:.2f}")
    
    def stop(self):
        """
        Called when the strategy finishes.
        """
        self.end_value = self.broker.getvalue()
        profit = self.end_value - self.start_value
        profit_pct = (profit / self.start_value) * 100 if self.start_value > 0 else 0
        
        self.logger.info(f"Final Portfolio Value: {self.end_value:.2f}")
        self.logger.info(f"Profit: {profit:.2f} ({profit_pct:.2f}%)")

# Example usage
if __name__ == "__main__":
    # This strategy is designed to be used with backtrader
    pass

