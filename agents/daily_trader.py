"""
Daily Trader Agent
Makes daily trading decisions based on technical indicators and market conditions
"""

import pandas as pd
import numpy as np
import talib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient

# Configure logging
logger = logging.getLogger(__name__)

class DailyTrader:
    """
    Daily Trader Agent
    Makes daily trading decisions based on technical indicators and market conditions
    """
    
    def __init__(self, db_manager: MongoDBManager, data_fetcher: AkshareClient):
        """
        Initialize the daily trader
        
        Args:
            db_manager: MongoDBManager instance
            data_fetcher: DataFetcher instance
        """
        self.db_manager = db_manager
        self.data_fetcher = data_fetcher
        self.logger = logging.getLogger(__name__)
        
        # Trading parameters
        self.max_position = 0.1  # Maximum 10% of portfolio in one stock
        self.stop_loss = 0.05    # 5% stop loss
        self.take_profit = 0.1   # 10% take profit
        self.max_stocks = 10     # Maximum number of stocks to hold
    
    def make_trading_decisions(self, selected_stocks: List[str], 
                             portfolio_value: float,
                             current_positions: Dict[str, float],
                             date: Optional[str] = None) -> List[Dict]:
        """
        Make daily trading decisions
        
        Args:
            selected_stocks: List of stocks selected for trading
            portfolio_value: Current portfolio value
            current_positions: Current stock positions {code: value}
            date: Trading date (YYYY-MM-DD), defaults to today
            
        Returns:
            List of trading decisions [{'action': 'BUY/SELL/HOLD', 'code': 'stock_code', 'amount': value}]
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        self.logger.info(f"Making trading decisions for {date}")
        
        decisions = []
        
        # Process each selected stock
        for code in selected_stocks:
            try:
                decision = self._analyze_stock(code, date, portfolio_value, current_positions)
                if decision:
                    decisions.append(decision)
            except Exception as e:
                self.logger.warning(f"Error analyzing stock {code}: {e}")
                continue
        
        # Sort decisions by priority (buy decisions first)
        decisions.sort(key=lambda x: 0 if x['action'] == 'BUY' else 1)
        
        self.logger.info(f"Generated {len(decisions)} trading decisions")
        return decisions
    
    def _analyze_stock(self, code: str, date: str, portfolio_value: float,
                      current_positions: Dict[str, float]) -> Optional[Dict]:
        """
        Analyze a single stock and make trading decision
        
        Args:
            code: Stock code
            date: Trading date
            portfolio_value: Current portfolio value
            current_positions: Current stock positions
            
        Returns:
            Trading decision dictionary or None
        """
        # Get daily K-data for the past 3 months
        end_date = date
        start_date = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=90)).strftime('%Y-%m-%d')
        
        k_data = self.db_manager.get_k_data(code, start_date, end_date, frequency='daily')
        
        # If no data in DB, fetch from data source
        if k_data.empty:
            k_data = self.data_fetcher.get_daily_k_data(code, start_date, end_date)
            # Save to DB for future use
            if not k_data.empty:
                self.db_manager.save_k_data(code, k_data, frequency='daily')
        
        if k_data.empty or len(k_data) < 20:  # Need at least 20 days of data
            return None
        
        # Calculate technical indicators
        try:
            # Moving averages
            ma5 = talib.SMA(k_data['close'].values, timeperiod=5)
            ma20 = talib.SMA(k_data['close'].values, timeperiod=20)
            
            # MACD
            macd, macd_signal, macd_hist = talib.MACD(k_data['close'].values)
            
            # RSI
            rsi = talib.RSI(k_data['close'].values, timeperiod=14)
            
            # Bollinger Bands
            upper, middle, lower = talib.BBANDS(k_data['close'].values)
            
            # Current values
            current_price = k_data['close'].iloc[-1]
            ma5_last = ma5[-1]
            ma20_last = ma20[-1]
            macd_last = macd[-1]
            macd_signal_last = macd_signal[-1]
            macd_hist_last = macd_hist[-1]
            rsi_last = rsi[-1]
            upper_last = upper[-1]
            lower_last = lower[-1]
            
            # Check current position
            current_position_value = current_positions.get(code, 0)
            current_position_ratio = current_position_value / portfolio_value if portfolio_value > 0 else 0
            
            # Make trading decision
            if current_position_value > 0:
                # Already holding this stock, check exit conditions
                entry_price = self._get_entry_price(code)  # This would need to be implemented
                if entry_price > 0:
                    # Check stop loss
                    if current_price / entry_price - 1 < -self.stop_loss:
                        return {
                            'action': 'SELL',
                            'code': code,
                            'amount': current_position_value,
                            'reason': 'Stop loss triggered'
                        }
                    
                    # Check take profit
                    if current_price / entry_price - 1 > self.take_profit:
                        return {
                            'action': 'SELL',
                            'code': code,
                            'amount': current_position_value,
                            'reason': 'Take profit triggered'
                        }
                
                # Check technical exit signals
                if self._should_exit(ma5_last, ma20_last, macd_last, macd_signal_last, rsi_last):
                    return {
                        'action': 'SELL',
                        'code': code,
                        'amount': current_position_value,
                        'reason': 'Technical exit signal'
                    }
                
                # Hold position
                return {
                    'action': 'HOLD',
                    'code': code,
                    'amount': current_position_value,
                    'reason': 'No exit signal'
                }
            else:
                # Not holding this stock, check entry conditions
                if current_position_ratio < self.max_position:
                    if self._should_enter(ma5_last, ma20_last, macd_last, macd_signal_last, 
                                        macd_hist_last, rsi_last, current_price, upper_last, lower_last):
                        # Calculate position size
                        target_position_ratio = min(self.max_position, 0.02)  # Max 2% per stock
                        target_position_value = portfolio_value * target_position_ratio
                        
                        return {
                            'action': 'BUY',
                            'code': code,
                            'amount': target_position_value,
                            'reason': 'Technical entry signal'
                        }
        
        except Exception as e:
            self.logger.warning(f"Error analyzing indicators for {code}: {e}")
        
        # Default to hold if no clear signal
        return {
            'action': 'HOLD',
            'code': code,
            'amount': current_positions.get(code, 0),
            'reason': 'No clear signal'
        }
    
    def _should_enter(self, ma5: float, ma20: float, macd: float, macd_signal: float,
                     macd_hist: float, rsi: float, price: float, upper: float, lower: float) -> bool:
        """
        Check if conditions are met for entering a position
        
        Returns:
            True if should enter, False otherwise
        """
        # Golden cross (5-day MA crosses above 20-day MA)
        if ma5 > ma20:
            # MACD bullish crossover
            if macd > macd_signal and macd_hist > 0:
                # RSI not overbought
                if rsi < 70:
                    # Price above lower Bollinger Band
                    if price > lower:
                        return True
        return False
    
    def _should_exit(self, ma5: float, ma20: float, macd: float, macd_signal: float, rsi: float) -> bool:
        """
        Check if conditions are met for exiting a position
        
        Returns:
            True if should exit, False otherwise
        """
        # Death cross (5-day MA crosses below 20-day MA)
        if ma5 < ma20:
            # MACD bearish crossover
            if macd < macd_signal:
                # RSI oversold or overbought
                if rsi > 70 or rsi < 30:
                    return True
        return False
    
    def _get_entry_price(self, code: str) -> float:
        """
        Get entry price for a stock (this would need to be implemented based on your system)
        
        Returns:
            Entry price or 0 if not available
        """
        # This is a placeholder implementation
        # In a real system, you would store entry prices in the database
        try:
            # Try to get from positions database
            positions_collection = self.db_manager.db['positions']
            position = positions_collection.find_one({'code': code, 'status': 'OPEN'})
            if position and 'entry_price' in position:
                return position['entry_price']
        except Exception as e:
            self.logger.warning(f"Error getting entry price for {code}: {e}")
        
        return 0.0

# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize components
    db_manager = MongoDBManager()
    data_fetcher = AkshareClient()
    
    # Initialize trader
    trader = DailyTrader(db_manager, data_fetcher)
    
    # Example trading decisions
    selected_stocks = ['000001', '000002', '600000']
    portfolio_value = 1000000
    current_positions = {'000001': 100000, '000002': 50000}
    
    decisions = trader.make_trading_decisions(selected_stocks, portfolio_value, current_positions)
    print(f"Trading decisions: {decisions}")
    
    # Close database connection
    db_manager.close_connection()

