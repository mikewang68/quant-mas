"""
Data Interface Module
Defines standard data formats and interfaces for the quant trading system.
"""

import pandas as pd
from typing import Dict, List, Optional
from abc import ABC, abstractmethod


class StandardDataFormat:
    """
    Standard data format for all strategies and agents.
    """

    REQUIRED_COLUMNS = ['date', 'open', 'high', 'low', 'close', 'volume']

    @staticmethod
    def validate_data(data: pd.DataFrame) -> bool:
        """
        Validate that the data has the required columns.

        Args:
            data: DataFrame to validate

        Returns:
            True if data is valid, False otherwise
        """
        if data.empty:
            return False

        for col in StandardDataFormat.REQUIRED_COLUMNS:
            if col not in data.columns:
                return False

        return True

    @staticmethod
    def create_empty_dataframe() -> pd.DataFrame:
        """
        Create an empty DataFrame with the standard column structure.

        Returns:
            Empty DataFrame with required columns
        """
        return pd.DataFrame(columns=StandardDataFormat.REQUIRED_COLUMNS)


class DataProviderInterface(ABC):
    """
    Abstract interface for data providers (agents).
    """

    @abstractmethod
    def get_standard_data(self, stock_codes: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Get standard format data for the specified stock codes.

        Args:
            stock_codes: List of stock codes to get data for

        Returns:
            Dictionary mapping stock codes to standard format DataFrames
        """
        pass

    @abstractmethod
    def get_data_for_stock(self, stock_code: str) -> pd.DataFrame:
        """
        Get standard format data for a single stock.

        Args:
            stock_code: Stock code to get data for

        Returns:
            Standard format DataFrame with stock data
        """
        pass


class StrategyInterface(ABC):
    """
    Abstract interface for trading strategies.
    """

    @abstractmethod
    def analyze_dataset(self, df_select: pd.DataFrame) -> Dict:
        """
        Analyze a standard format dataset.

        Args:
            df_select: Standard format DataFrame with stock data

        Returns:
            Analysis results dictionary
        """
        pass

    @abstractmethod
    def analyze_multiple_stocks(self, stock_data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """
        Analyze multiple stocks with standard format data.

        Args:
            stock_data: Dictionary mapping stock codes to standard format DataFrames

        Returns:
            List of analysis results for each stock
        """
        pass

