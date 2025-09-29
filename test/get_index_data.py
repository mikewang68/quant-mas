"""
Utility functions for fetching index data using akshare
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def get_index_daily_data(index_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Get daily K-line data for an index.

    Args:
        index_code: Index code (e.g., 'sh000016' for 上证50)
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'

    Returns:
        DataFrame with index daily K-line data
    """
    try:
        # Get daily index K-line data
        k_data = ak.stock_zh_index_daily(
            symbol=index_code,
            start_date=start_date.replace("-", ""),
            end_date=end_date.replace("-", "")
        )

        if k_data.empty:
            logger.warning(f"No daily K-data found for index {index_code} from {start_date} to {end_date}")
            return pd.DataFrame()

        # Rename columns to English
        column_mapping = {
            'date': 'date',
            'open': 'open',
            'close': 'close',
            'high': 'high',
            'low': 'low',
            'volume': 'volume',
            'amount': 'amount'
        }

        k_data = k_data.rename(columns=column_mapping)

        # Select only needed columns
        needed_columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount']
        # Only select columns that actually exist in the data
        available_columns = [col for col in needed_columns if col in k_data.columns]
        k_data = k_data[available_columns]

        # Convert date column to datetime
        k_data['date'] = pd.to_datetime(k_data['date'])

        # Sort by date
        k_data = k_data.sort_values('date').reset_index(drop=True)

        logger.info(f"Retrieved {len(k_data)} daily K-data records for index {index_code}")
        return k_data

    except Exception as e:
        logger.error(f"Error getting daily K-data for index {index_code}: {e}")
        return pd.DataFrame()


def get_multiple_index_data() -> dict:
    """
    Get data for major indices: 上证50, 沪深300, 中证500

    Returns:
        Dictionary with index data
    """
    # Define index codes
    indices = {
        'sh000016': '上证50',
        'sz399300': '沪深300',
        'sh000905': '中证500'
    }

    # Get date range (last 2 years)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')

    # Get data for each index
    result = {}
    for code, name in indices.items():
        try:
            data = get_index_daily_data(code, start_date, end_date)
            result[code] = {
                'name': name,
                'data': data
            }
        except Exception as e:
            logger.error(f"Error getting data for index {code}: {e}")
            result[code] = {
                'name': name,
                'data': pd.DataFrame()
            }

    return result


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    # Get index data
    index_data = get_multiple_index_data()

    # Print summary
    for code, info in index_data.items():
        print(f"{info['name']} ({code}): {len(info['data'])} records")

