"""
Weekly Stock Selector Agent
Selects stocks for weekly trading based on technical indicators and fundamental analysis
"""

import talib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from utils.akshare_client import AkshareClient
from data.mongodb_manager import MongoDBManager
import logging

# Configure logging
logger = logging.getLogger(__name__)

class WeeklyStockSelector:
    """
    Weekly Stock Selector Agent
    Selects stocks for weekly trading based on technical indicators and fundamental analysis
    """
    
    def __init__(self, db_manager: MongoDBManager, data_fetcher: AkshareClient, strategy_params: Optional[Dict] = None):
        """
        Initialize the weekly stock selector
        
        Args:
            db_manager: MongoDBManager instance
            data_fetcher: DataFetcher instance
            strategy_params: Strategy parameters (optional)
        """
        self.db_manager = db_manager
        self.data_fetcher = data_fetcher  # This should be AkshareClient now
        self.strategy_params = strategy_params or {}
        self.logger = logging.getLogger(__name__)
        
        # Strategy parameters for moving averages
        self.ma_short = int(self.strategy_params.get('short', 5))
        self.ma_mid = int(self.strategy_params.get('mid', 13))
        self.ma_long = int(self.strategy_params.get('long', 34))
        
        # Monthly golden cross parameters (for weekly data)
        self.monthly_golden_cross_short = int(self.strategy_params.get('monthly_golden_cross_short', 5))
        self.monthly_golden_cross_long = int(self.strategy_params.get('monthly_golden_cross_long', 20))
        
        # RSI parameters
        self.rsi_period = int(self.strategy_params.get('rsi_period', 14))
        self.rsi_min = int(self.strategy_params.get('rsi_min', 30))
        self.rsi_max = int(self.strategy_params.get('rsi_max', 70))
        
        # Volume parameters
        self.volume_period = int(self.strategy_params.get('volume_period', 20))
        self.min_volume = int(self.strategy_params.get('min_volume', 1000000))
    
    def select_stocks(self, date: Optional[str] = None) -> tuple[List[str], Optional[str], Dict[str, bool]]:
        """
        Select stocks for weekly trading
        
        Args:
            date: Selection date (YYYY-MM-DD), defaults to today
            
        Returns:
            Tuple of (selected stock codes, last data date, golden cross flags)
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        self.logger.info(f"Selecting stocks for week of {date}")
        
        # Get all stock codes
        all_codes = self.db_manager.get_stock_codes()
        if not all_codes:
            # If no codes in DB, fetch from data source
            all_codes = self.data_fetcher.get_stock_list()
            # Save to DB for future use
            self.db_manager.save_stock_codes(all_codes)
        
        # Filter stocks based on criteria
        selected_stocks = []
        golden_cross_flags = {}  # Dictionary to store golden cross flag for each stock
        last_data_date = None
        
        for code in all_codes:
            try:
                # Check if stock meets selection criteria and get last data date
                meets_criteria, stock_last_date = self._meets_selection_criteria_with_date(code, date)
                if meets_criteria:
                    selected_stocks.append(code)
                    # Store golden cross flag for this stock
                    # Get weekly data for golden cross detection
                    end_date = date
                    start_date = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d')
                    
                    # Get daily K-data from database with adjustment based on config
                    daily_k_data = self.db_manager.get_adjusted_k_data(code, start_date, end_date, frequency='daily')
                    
                    # Convert daily to weekly data
                    if not daily_k_data.empty:
                        k_data = self._convert_daily_to_weekly(daily_k_data)
                        # Detect golden cross for this stock
                        golden_cross_flags[code] = self._detect_golden_cross_with_params(k_data)
                    else:
                        golden_cross_flags[code] = False
                    
                    # Update last_data_date to the latest date among all selected stocks
                    if stock_last_date and (not last_data_date or stock_last_date > last_data_date):
                        last_data_date = stock_last_date
                        
            except Exception as e:
                self.logger.warning(f"Error processing stock {code}: {e}")
                continue
        
        self.logger.info(f"Selected {len(selected_stocks)} stocks for weekly trading")
        if last_data_date:
            self.logger.info(f"Last data date used for selection: {last_data_date}")
        return selected_stocks, last_data_date, golden_cross_flags
    
    def _meets_selection_criteria_with_date(self, code: str, date: str) -> tuple[bool, Optional[str]]:
        """
        Check if a stock meets selection criteria and return last data date.
        
        Args:
            code: Stock code
            date: Selection date
            
        Returns:
            Tuple of (meets criteria, last data date)
        """
        # Get daily K-data for the past year
        end_date = date
        start_date = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d')
        
        # Get daily K-data from database with adjustment based on config
        daily_k_data = self.db_manager.get_adjusted_k_data(code, start_date, end_date, frequency='daily')
        
        # If no data in DB, fetch from data source
        if daily_k_data.empty:
            daily_k_data = self.data_fetcher.get_daily_k_data(code, start_date, end_date)
            # Save to DB for future use
            if not daily_k_data.empty:
                self.db_manager.save_k_data(code, daily_k_data, frequency='daily')
        
        # Get last data date
        last_data_date = None
        if not daily_k_data.empty and 'date' in daily_k_data.columns:
            max_date = daily_k_data['date'].max()
            # Convert pandas Timestamp to string if needed
            if hasattr(max_date, 'strftime'):
                last_data_date = max_date.strftime('%Y-%m-%d')
            else:
                last_data_date = str(max_date)
        
        # Convert daily to weekly data
        if not daily_k_data.empty:
            k_data = self._convert_daily_to_weekly(daily_k_data)
        else:
            k_data = pd.DataFrame()
        
        # Need enough data for all calculations
        required_data = max(self.ma_short, self.ma_mid, self.ma_long, self.monthly_golden_cross_short, self.monthly_golden_cross_long)
        if k_data.empty or len(k_data) < required_data:
            return False, last_data_date
        
        # Calculate technical indicators
        try:
            # Convert pandas Series to numpy array for TA-Lib
            close_prices = np.array(k_data['close'].values, dtype=np.float64)
            
            # Moving averages using strategy parameters
            ma_short = talib.SMA(close_prices, timeperiod=self.ma_short)
            ma_mid = talib.SMA(close_prices, timeperiod=self.ma_mid)
            ma_long = talib.SMA(close_prices, timeperiod=self.ma_long)
            
            # Current price relative to moving averages
            current_price = close_prices[-1]
            ma_short_last = ma_short[-1] if len(ma_short) > 0 and not np.isnan(ma_short[-1]) else None
            ma_mid_last = ma_mid[-1] if len(ma_mid) > 0 and not np.isnan(ma_mid[-1]) else None
            ma_long_last = ma_long[-1] if len(ma_long) > 0 and not np.isnan(ma_long[-1]) else None
            
            # Check if all moving averages are valid (not None)
            if ma_short_last is None or ma_mid_last is None or ma_long_last is None:
                self.logger.debug(f"Stock {code} has invalid moving averages")
                return False, last_data_date
            
            # Check if price is above moving averages in specific order (uptrend)
            # Current price > MA5 > MA13 > MA34
            price_condition = (current_price > ma_short_last) and \
                             (ma_short_last > ma_mid_last) and \
                             (ma_mid_last > ma_long_last)
            if not price_condition:
                self.logger.debug(f"Stock {code} failed price condition: close={current_price}, ma_short={ma_short_last}, ma_mid={ma_mid_last}, ma_long={ma_long_last}")
                return False, last_data_date
            
            # Check for golden cross pattern using strategy parameters
            golden_cross_condition = self._detect_golden_cross_with_params(k_data)
            if not golden_cross_condition:
                self.logger.debug(f"Stock {code} failed golden cross condition")
                return False, last_data_date
            
            return True, last_data_date
            
        except Exception as e:
            self.logger.warning(f"Error calculating indicators for {code}: {e}")
            return False, last_data_date
    
    def _meets_selection_criteria(self, code: str, date: str) -> bool:
        """
        Check if a stock meets selection criteria using strategy parameters.
        
        Args:
            code: Stock code
            date: Selection date
            
        Returns:
            True if stock meets criteria, False otherwise
        """
        # Get daily K-data for the past year
        end_date = date
        start_date = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d')
        
        # Get daily K-data from database with adjustment based on config
        daily_k_data = self.db_manager.get_adjusted_k_data(code, start_date, end_date, frequency='daily')
        
        # If no data in DB, fetch from data source
        if daily_k_data.empty:
            daily_k_data = self.data_fetcher.get_daily_k_data(code, start_date, end_date)
            # Save to DB for future use
            if not daily_k_data.empty:
                self.db_manager.save_k_data(code, daily_k_data, frequency='daily')
        
        # Convert daily to weekly data
        if not daily_k_data.empty:
            k_data = self._convert_daily_to_weekly(daily_k_data)
        else:
            k_data = pd.DataFrame()
        
        # Need enough data for all calculations
        required_data = max(self.ma_short, self.ma_mid, self.ma_long, self.monthly_golden_cross_short, self.monthly_golden_cross_long)
        if k_data.empty or len(k_data) < required_data:
            return False
        
        # Calculate technical indicators
        try:
            # Convert pandas Series to numpy array for TA-Lib
            close_prices = np.array(k_data['close'].values, dtype=np.float64)
            
            # Moving averages using strategy parameters
            ma_short = talib.SMA(close_prices, timeperiod=self.ma_short)
            ma_mid = talib.SMA(close_prices, timeperiod=self.ma_mid)
            ma_long = talib.SMA(close_prices, timeperiod=self.ma_long)
            
            # Current price relative to moving averages
            current_price = close_prices[-1]
            ma_short_last = ma_short[-1] if len(ma_short) > 0 and not np.isnan(ma_short[-1]) else 0
            ma_mid_last = ma_mid[-1] if len(ma_mid) > 0 and not np.isnan(ma_mid[-1]) else 0
            ma_long_last = ma_long[-1] if len(ma_long) > 0 and not np.isnan(ma_long[-1]) else 0
            
            # Check if price is above moving averages in specific order (uptrend)
            # Current price > MA5 > MA13 > MA34
            price_condition = (current_price > ma_short_last) and \
                             (ma_short_last > ma_mid_last) and \
                             (ma_mid_last > ma_long_last)
            if not price_condition:
                return False
            
            # Check for golden cross pattern using strategy parameters
            if not self._detect_golden_cross_with_params(k_data):
                return False
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Error calculating indicators for {code}: {e}")
            return False
    
    def _convert_daily_to_weekly(self, daily_data: pd.DataFrame) -> pd.DataFrame:
        """
        Convert daily K-line data to weekly K-line data
        
        Args:
            daily_data: DataFrame with daily K-line data
            
        Returns:
            DataFrame with weekly K-line data
        """
        if daily_data.empty:
            return daily_data
            
        try:
            # Set date as index for resampling
            daily_data = daily_data.set_index('date')
            
            # Resample to weekly data
            weekly_data = daily_data.resample('W-FRI').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum',
                'amount': 'sum'
            })
            
            # Remove any rows with NaN values
            weekly_data = weekly_data.dropna()
            
            # Reset index to make date a column again
            weekly_data = weekly_data.reset_index()
            
            return weekly_data
            
        except Exception as e:
            self.logger.error(f"Error converting daily to weekly data: {e}")
            return pd.DataFrame()
    
    def _detect_golden_cross(self, k_data: pd.DataFrame) -> bool:
        """
        Detect golden cross pattern (MA5 crosses above MA20)
        
        Args:
            k_data: DataFrame with K-line data
            
        Returns:
            True if golden cross detected, False otherwise
        """
        if k_data.empty or len(k_data) < 20:
            return False
            
        try:
            # Convert pandas Series to numpy array for TA-Lib
            close_prices = np.asarray(k_data['close'].values, dtype=np.float64)
            
            # Calculate moving averages
            ma5 = talib.SMA(close_prices, timeperiod=5)
            ma20 = talib.SMA(close_prices, timeperiod=20)
            
            # Check if we have enough data points
            if len(ma5) < 2 or len(ma20) < 2:
                return False
                
            # Check for golden cross (MA5 crosses above MA20)
            # Current: MA5 > MA20
            # Previous: MA5 <= MA20
            current_ma5_above_ma20 = ma5[-1] > ma20[-1] if not np.isnan(ma5[-1]) and not np.isnan(ma20[-1]) else False
            previous_ma5_below_ma20 = ma5[-2] <= ma20[-2] if not np.isnan(ma5[-2]) and not np.isnan(ma20[-2]) else False
            
            return current_ma5_above_ma20 and previous_ma5_below_ma20
            
        except Exception as e:
            self.logger.warning(f"Error detecting golden cross: {e}")
            return False
    
    def _detect_golden_cross_with_params(self, k_data: pd.DataFrame) -> bool:
        """
        Detect golden cross pattern using strategy parameters (short and mid MA)
        
        Args:
            k_data: DataFrame with K-line data
            
        Returns:
            True if golden cross detected, False otherwise
        """
        if k_data.empty or len(k_data) < max(self.ma_short, self.ma_mid):
            return False
            
        try:
            # Convert pandas Series to numpy array for TA-Lib
            close_prices = np.asarray(k_data['close'].values, dtype=np.float64)
            
            # Calculate moving averages using strategy parameters (short and mid for golden cross)
            ma_short = talib.SMA(close_prices, timeperiod=self.ma_short)
            ma_mid = talib.SMA(close_prices, timeperiod=self.ma_mid)
            
            # Check if we have enough data points
            if len(ma_short) < 2 or len(ma_mid) < 2:
                return False
                
            # Check for golden cross (short MA crosses above mid MA)
            # Current: short MA > mid MA
            # Previous: short MA <= mid MA
            current_short_above_mid = ma_short[-1] > ma_mid[-1] if not np.isnan(ma_short[-1]) and not np.isnan(ma_mid[-1]) else False
            previous_short_below_mid = ma_short[-2] <= ma_mid[-2] if not np.isnan(ma_short[-2]) and not np.isnan(ma_mid[-2]) else False
            
            return current_short_above_mid and previous_short_below_mid
            
        except Exception as e:
            self.logger.warning(f"Error detecting golden cross with params: {e}")
            return False
    
    def save_selected_stocks(self, stocks: List[str], golden_cross_flags: Optional[Dict[str, bool]] = None, date: Optional[str] = None, last_data_date: Optional[str] = None) -> bool:
        """
        Save selected stocks to database with year-week as primary key
        
        Args:
            stocks: List of selected stock codes
            golden_cross_flags: Dictionary mapping stock codes to golden cross flags
            date: Selection date
            last_data_date: Last date of stock data used for selection (to determine year-week key)
            
        Returns:
            True if saved successfully, False otherwise
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Use last_data_date to determine year-week key, fallback to selection date
        if last_data_date:
            reference_date = datetime.strptime(last_data_date, '%Y-%m-%d')
        else:
            reference_date = datetime.strptime(date, '%Y-%m-%d')
        
        try:
            # Create a collection for pool
            collection = self.db_manager.db['pool']
            
            # Calculate ISO year and week number based on reference date
            iso_year, iso_week, _ = reference_date.isocalendar()
            year_week_key = f"{iso_year}-{iso_week:02d}"
            
            # Prepare stocks data with golden cross information
            stocks_data = []
            for stock_code in stocks:
                stock_info = {
                    'code': stock_code,
                    'golden_cross': golden_cross_flags.get(stock_code, False) if golden_cross_flags else False
                }
                stocks_data.append(stock_info)
            
            # Save selection record with upsert to ensure only one record per week
            record = {
                '_id': year_week_key,  # Use year-week as primary key
                'year': iso_year,
                'week': iso_week,
                'selection_date': datetime.strptime(date, '%Y-%m-%d') if date else datetime.now(),
                'reference_date': reference_date,
                'stocks': stocks_data,  # Store stocks with golden cross information
                'count': len(stocks),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            # Use upsert to insert or update the record
            result = collection.replace_one(
                {'_id': year_week_key},  # Filter by _id
                record,  # Document to insert/update
                upsert=True  # Create if doesn't exist
            )
            
            if result.upserted_id:
                self.logger.info(f"Inserted new weekly selection record {year_week_key} with {len(stocks)} stocks")
            else:
                self.logger.info(f"Updated existing weekly selection record {year_week_key} with {len(stocks)} stocks")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving weekly selection to pool: {e}")
            return False

# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize components
    db_manager = MongoDBManager()
    data_fetcher = AkshareClient()
    
    # Initialize selector
    selector = WeeklyStockSelector(db_manager, data_fetcher)
    
    # Select stocks
    selected_stocks, last_data_date, golden_cross_flags = selector.select_stocks()
    print(f"Selected stocks: {selected_stocks}")
    
    # Save selection
    selector.save_selected_stocks(selected_stocks, last_data_date=last_data_date)
    
    # Close database connection
    db_manager.close_connection()

