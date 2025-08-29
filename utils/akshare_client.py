"""
Akshare Client Module
Provides a simplified interface for fetching stock data using akshare library
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional, Tuple
import time

# 访问计数器和限制
_access_count = 0
_ACCESS_LIMIT = 1
_SLEEP_DURATION = 1


class AkshareClient:
    """
    Akshare client for retrieving stock market data
    """

    def __init__(self, timeout: int = 30):
        """
        Initialize the akshare client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        self.request_count = 0  # 添加请求计数器
        self.logger.info("AkshareClient initialized")
    
    def get_stock_list(self) -> List[str]:
        """
        Get list of all A-share stock codes.
        
        Returns:
            List of stock codes (e.g., ['000001', '000002', ...])
        """
        try:
            # Get stock list from akshare
            stock_list = ak.stock_info_a_code_name()
            
            # Extract stock codes
            codes = stock_list['code'].tolist()
            
            self.logger.info(f"Retrieved {len(codes)} stock codes")
            return codes
        except Exception as e:
            self.logger.error(f"Error getting stock list: {e}")
            return []
    
    def get_stock_info(self, code: str) -> Optional[Dict]:
        """
        Get detailed information for a specific stock.
        
        Args:
            code: Stock code (e.g., '000001')
            
        Returns:
            Dictionary with stock information or None if error
        """
        try:
            # Get stock information
            stock_info = ak.stock_individual_info_em(symbol=code)
            
            # Convert to dictionary
            info_dict = {}
            for _, row in stock_info.iterrows():
                info_dict[row['item']] = row['value']
            
            return info_dict
        except Exception as e:
            self.logger.error(f"Error getting stock info for {code}: {e}")
            return None
    
    def get_daily_k_data(self, code: str, start_date: str, end_date: str, adjust_type: str = "q") -> pd.DataFrame:
        """
        Get daily K-line data for a stock.

        Args:
            code: Stock code (e.g., '000001')
            start_date: Start date in format 'YYYY-MM-DD'
            end_date: End date in format 'YYYY-MM-DD'
            adjust_type: Adjustment type ('none' for no adjust, 'q' for pre-adjust, 'h' for post-adjust)

        Returns:
            DataFrame with K-line data
        """
        try:
            global _access_count

            # 检查访问次数，每200次sleep 3秒
            _access_count += 1
            if _access_count >= _ACCESS_LIMIT:
                self.logger.info(f"Access limit reached ({_access_count}), sleeping for {_SLEEP_DURATION} seconds...")
                time.sleep(_SLEEP_DURATION)
                _access_count = 0  # 重置计数器

            # Format code for akshare (add exchange prefix)
            formatted_code = self._format_stock_code(code)

            # Map adjust_type to akshare format
            adjust_mapping = {
                'none': "",      # 不复权
                'q': "qfq",      # 前复权
                'h': "hfq"       # 后复权
            }
            ak_adjust = adjust_mapping.get(adjust_type, "qfq")  # 默认前复权

            # Get daily K-line data
            k_data = ak.stock_zh_a_hist(
                symbol=formatted_code,
                period="daily",
                start_date=start_date.replace("-", ""),
                end_date=end_date.replace("-", ""),
                adjust=ak_adjust
            )

            if k_data.empty:
                self.logger.warning(f"No daily K-data found for {code} from {start_date} to {end_date}")
                return pd.DataFrame()

            # Rename columns to English
            column_mapping = {
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'pct_change',
                '涨跌额': 'change_amount',
                '换手率': 'turnover_rate'
            }

            k_data = k_data.rename(columns=column_mapping)

            # Select only needed columns (including additional financial metrics)
            needed_columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude', 'pct_change', 'change_amount', 'turnover_rate']
            # Only select columns that actually exist in the data
            available_columns = [col for col in needed_columns if col in k_data.columns]
            k_data = k_data[available_columns]

            # Convert date column to datetime
            k_data['date'] = pd.to_datetime(k_data['date'])

            # Sort by date
            k_data = k_data.sort_values('date').reset_index(drop=True)

            self.logger.info(f"Retrieved {len(k_data)} daily K-data records for {code}")
            return k_data

        except Exception as e:
            self.logger.error(f"Error getting daily K-data for {code}: {e}")
            return pd.DataFrame()
    
    def get_weekly_k_data(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get weekly K-line data for a stock.
        
        Args:
            code: Stock code (e.g., '000001')
            start_date: Start date in format 'YYYY-MM-DD'
            end_date: End date in format 'YYYY-MM-DD'
            
        Returns:
            DataFrame with weekly K-line data
        """
        try:
            # Format code for akshare (add exchange prefix)
            formatted_code = self._format_stock_code(code)
            
            # Get weekly K-line data
            k_data = ak.stock_zh_a_hist(
                symbol=formatted_code,
                period="weekly",
                start_date=start_date.replace("-", ""),
                end_date=end_date.replace("-", ""),
                adjust="qfq"  # 前复权
            )
            
            if k_data.empty:
                self.logger.warning(f"No weekly K-data found for {code} from {start_date} to {end_date}")
                return pd.DataFrame()
            
            # Rename columns to English
            column_mapping = {
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'pct_change',
                '涨跌额': 'change_amount',
                '换手率': 'turnover_rate'
            }
            
            k_data = k_data.rename(columns=column_mapping)
            
            # Select only needed columns
            needed_columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount']
            k_data = k_data[needed_columns]
            
            # Convert date column to datetime
            k_data['date'] = pd.to_datetime(k_data['date'])
            
            # Sort by date
            k_data = k_data.sort_values('date').reset_index(drop=True)
            
            self.logger.info(f"Retrieved {len(k_data)} weekly K-data records for {code}")
            return k_data
            
        except Exception as e:
            self.logger.error(f"Error getting weekly K-data for {code}: {e}")
            return pd.DataFrame()
    
    def _format_stock_code(self, code: str) -> str:
        """
        Format stock code for akshare.

        Args:
            code: Stock code (e.g., '000001')

        Returns:
            Formatted code (e.g., 'sz000001' or 'sh600000')
        """
        # 根据用户要求，直接返回纯数字代码，不添加前缀
        return code
    
    def get_realtime_data(self, codes: List[str]) -> pd.DataFrame:
        """
        Get real-time data for multiple stocks.
        
        Args:
            codes: List of stock codes
            
        Returns:
            DataFrame with real-time data
        """
        try:
            # Format codes for akshare
            formatted_codes = [self._format_stock_code(code) for code in codes]
            
            # Get real-time data
            realtime_data = ak.stock_zh_a_spot_em()
            
            # Filter for requested codes
            filtered_data = realtime_data[realtime_data['代码'].isin(formatted_codes)]
            
            if filtered_data.empty:
                self.logger.warning(f"No real-time data found for codes: {codes}")
                return pd.DataFrame()
            
            # Rename columns
            column_mapping = {
                '代码': 'code',
                '名称': 'name',
                '最新价': 'price',
                '涨跌幅': 'pct_change',
                '涨跌额': 'change_amount',
                '成交量': 'volume',
                '成交额': 'amount',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '昨收': 'prev_close',
                '换手率': 'turnover_rate'
            }
            
            filtered_data = filtered_data.rename(columns=column_mapping)
            
            # Select needed columns
            needed_columns = ['code', 'name', 'price', 'pct_change', 'volume', 'amount', 
                            'open', 'high', 'low', 'prev_close']
            filtered_data = filtered_data[needed_columns]
            
            self.logger.info(f"Retrieved real-time data for {len(filtered_data)} stocks")
            return filtered_data
            
        except Exception as e:
            self.logger.error(f"Error getting real-time data: {e}")
            return pd.DataFrame()


# Global instance for easy access
akshare_client = AkshareClient()

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Initialize akshare client
    client = AkshareClient()
    
    # Test getting stock list
    print("Getting stock list...")
    codes = client.get_stock_list()
    print(f"Found {len(codes)} stocks")
    
    if codes:
        # Test getting data for first stock
        test_code = codes[0]
        print(f"\nGetting info for {test_code}...")
        info = client.get_stock_info(test_code)
        if info:
            print(f"Stock info: {info}")
        
        # Test getting daily K-data
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        print(f"\nGetting daily K-data for {test_code}...")
        daily_data = client.get_daily_k_data(test_code, start_date, end_date)
        print(f"Daily data shape: {daily_data.shape}")
        if not daily_data.empty:
            print(daily_data.head())
        
        # Test getting weekly K-data
        print(f"\nGetting weekly K-data for {test_code}...")
        weekly_data = client.get_weekly_k_data(test_code, start_date, end_date)
        print(f"Weekly data shape: {weekly_data.shape}")
        if not weekly_data.empty:
            print(weekly_data.head())
        
        # Test getting real-time data
        print(f"\nGetting real-time data for {test_code}...")
        realtime_data = client.get_realtime_data([test_code])
        print(f"Real-time data shape: {realtime_data.shape}")
        if not realtime_data.empty:
            print(realtime_data.head())

