"""
Crypto data fetcher module using Binance API.
Handles fetching cryptocurrency data from Binance.
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional, Tuple
import time

# Configure logging
logger = logging.getLogger(__name__)

class CryptoDataFetcher:
    """
    Crypto data fetcher class for retrieving cryptocurrency market data using Binance API.
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the crypto data fetcher.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.base_url = "https://api.binance.com"
        logger.info("CryptoDataFetcher initialized with Binance API")
    
    def get_crypto_list(self) -> List[str]:
        """
        Get list of all available cryptocurrency symbols from Binance.
        
        Returns:
            List of cryptocurrency symbols (e.g., ['BTCUSDT', 'ETHUSDT', ...])
        """
        try:
            # Get exchange info to retrieve all symbols
            url = f"{self.base_url}/api/v3/exchangeInfo"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            symbols = [symbol['symbol'] for symbol in data['symbols'] if symbol['status'] == 'TRADING']
            
            logger.info(f"Retrieved {len(symbols)} cryptocurrency symbols")
            return symbols
        except Exception as e:
            logger.error(f"Error getting cryptocurrency list: {e}")
            return []
    
    def get_crypto_info(self, symbol: str) -> Optional[Dict]:
        """
        Get detailed information for a specific cryptocurrency.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTCUSDT')
            
        Returns:
            Dictionary with cryptocurrency information or None if error
        """
        try:
            # Get symbol information from exchange info
            url = f"{self.base_url}/api/v3/exchangeInfo"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            symbols = [s for s in data['symbols'] if s['symbol'] == symbol]
            
            if symbols:
                return symbols[0]
            else:
                logger.warning(f"No information found for symbol {symbol}")
                return None
        except Exception as e:
            logger.error(f"Error getting cryptocurrency info for {symbol}: {e}")
            return None
    
    def get_daily_k_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get daily K-line data for a cryptocurrency.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTCUSDT')
            start_date: Start date in format 'YYYY-MM-DD'
            end_date: End date in format 'YYYY-MM-DD'
            
        Returns:
            DataFrame with K-line data
        """
        try:
            # Convert dates to timestamps
            start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
            end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)
            
            # Get daily K-line data from Binance
            url = f"{self.base_url}/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': '1d',  # Daily interval
                'startTime': start_timestamp,
                'endTime': end_timestamp,
                'limit': 1000  # Maximum limit
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                logger.warning(f"No daily K-data found for {symbol} from {start_date} to {end_date}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            k_data = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Convert timestamp to datetime
            k_data['date'] = pd.to_datetime(k_data['timestamp'], unit='ms')
            
            # Convert numeric columns
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                k_data[col] = pd.to_numeric(k_data[col])
            
            # Select only needed columns
            needed_columns = ['date', 'open', 'close', 'high', 'low', 'volume']
            k_data = k_data[needed_columns]
            
            # Sort by date
            k_data = k_data.sort_values('date').reset_index(drop=True)
            
            logger.info(f"Retrieved {len(k_data)} daily K-data records for {symbol}")
            return k_data
            
        except Exception as e:
            logger.error(f"Error getting daily K-data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_hourly_k_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get hourly K-line data for a cryptocurrency.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., 'BTCUSDT')
            start_date: Start date in format 'YYYY-MM-DD'
            end_date: End date in format 'YYYY-MM-DD'
            
        Returns:
            DataFrame with hourly K-line data
        """
        try:
            # Convert dates to timestamps
            start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
            end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)
            
            # Get hourly K-line data from Binance
            url = f"{self.base_url}/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': '1h',  # Hourly interval
                'startTime': start_timestamp,
                'endTime': end_timestamp,
                'limit': 1000  # Maximum limit
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                logger.warning(f"No hourly K-data found for {symbol} from {start_date} to {end_date}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            k_data = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Convert timestamp to datetime
            k_data['date'] = pd.to_datetime(k_data['timestamp'], unit='ms')
            
            # Convert numeric columns
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                k_data[col] = pd.to_numeric(k_data[col])
            
            # Select only needed columns
            needed_columns = ['date', 'open', 'close', 'high', 'low', 'volume']
            k_data = k_data[needed_columns]
            
            # Sort by date
            k_data = k_data.sort_values('date').reset_index(drop=True)
            
            logger.info(f"Retrieved {len(k_data)} hourly K-data records for {symbol}")
            return k_data
            
        except Exception as e:
            logger.error(f"Error getting hourly K-data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_realtime_data(self, symbols: List[str]) -> pd.DataFrame:
        """
        Get real-time data for multiple cryptocurrencies.
        
        Args:
            symbols: List of cryptocurrency symbols
            
        Returns:
            DataFrame with real-time data
        """
        try:
            # Get current prices for all symbols
            url = f"{self.base_url}/api/v3/ticker/price"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to DataFrame
            price_data = pd.DataFrame(data)
            price_data['price'] = pd.to_numeric(price_data['price'])
            
            # Filter for requested symbols
            filtered_data = price_data[price_data['symbol'].isin(symbols)]
            
            if filtered_data.empty:
                logger.warning(f"No real-time data found for symbols: {symbols}")
                return pd.DataFrame()
            
            # Get 24hr statistics for additional data
            stats_url = f"{self.base_url}/api/v3/ticker/24hr"
            stats_response = requests.get(stats_url, timeout=self.timeout)
            stats_response.raise_for_status()
            
            stats_data = stats_response.json()
            stats_df = pd.DataFrame(stats_data)
            
            # Convert numeric columns
            numeric_columns = ['priceChange', 'priceChangePercent', 'weightedAvgPrice', 
                             'prevClosePrice', 'lastPrice', 'lastQty', 'bidPrice', 
                             'bidQty', 'askPrice', 'askQty', 'openPrice', 'highPrice', 
                             'lowPrice', 'volume', 'quoteVolume', 'openTime', 'closeTime']
            for col in numeric_columns:
                if col in stats_df.columns:
                    stats_df[col] = pd.to_numeric(stats_df[col], errors='coerce')
            
            # Filter for requested symbols
            stats_filtered = stats_df[stats_df['symbol'].isin(symbols)]
            
            # Merge price and statistics data
            if not stats_filtered.empty:
                merged_data = filtered_data.merge(stats_filtered[['symbol', 'priceChange', 'priceChangePercent', 
                                                                'volume', 'quoteVolume', 'highPrice', 'lowPrice']], 
                                                on='symbol', how='left')
            else:
                merged_data = filtered_data.copy()
                # Add empty columns for consistency
                merged_data['priceChange'] = np.nan
                merged_data['priceChangePercent'] = np.nan
                merged_data['volume'] = np.nan
                merged_data['quoteVolume'] = np.nan
                merged_data['highPrice'] = np.nan
                merged_data['lowPrice'] = np.nan
            
            # Rename columns
            merged_data = merged_data.rename(columns={
                'symbol': 'symbol',
                'price': 'price',
                'priceChange': 'change_amount',
                'priceChangePercent': 'pct_change',
                'volume': 'volume',
                'quoteVolume': 'amount',
                'highPrice': 'high',
                'lowPrice': 'low'
            })
            
            logger.info(f"Retrieved real-time data for {len(merged_data)} cryptocurrencies")
            return merged_data
            
        except Exception as e:
            logger.error(f"Error getting real-time data: {e}")
            return pd.DataFrame()

# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize crypto data fetcher
    fetcher = CryptoDataFetcher()
    
    # Test getting crypto list
    print("Getting cryptocurrency list...")
    symbols = fetcher.get_crypto_list()
    print(f"Found {len(symbols)} cryptocurrencies")
    
    if symbols:
        # Test getting data for first symbol
        test_symbol = symbols[0]
        print(f"\nGetting info for {test_symbol}...")
        info = fetcher.get_crypto_info(test_symbol)
        if info:
            print(f"Cryptocurrency info: {info['symbol']}")
        
        # Test getting daily K-data
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        print(f"\nGetting daily K-data for {test_symbol}...")
        daily_data = fetcher.get_daily_k_data(test_symbol, start_date, end_date)
        print(f"Daily data shape: {daily_data.shape}")
        if not daily_data.empty:
            print(daily_data.head())
        
        # Test getting real-time data
        print(f"\nGetting real-time data for {test_symbol}...")
        realtime_data = fetcher.get_realtime_data([test_symbol])
        print(f"Real-time data shape: {realtime_data.shape}")
        if not realtime_data.empty:
            print(realtime_data.head())

