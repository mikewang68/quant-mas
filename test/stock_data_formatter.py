"""
Stock Data Formatter Utility
Provides unified interface for formatting stock data from different strategies
"""

import logging
from typing import Dict, List, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)


class StockDataFormatter:
    """
    Unified formatter for stock data from different strategies
    Ensures consistent structure for Stocks array items
    """

    @staticmethod
    def format_stock_data(
        code: str,
        strategy_result: tuple,
        technical_analysis: Optional[Dict] = None,
        strategy_params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Format stock data from strategy result into standardized structure

        Args:
            code: Stock code
            strategy_result: Tuple returned by strategy analyze() method
            technical_analysis: Technical analysis data from strategy
            strategy_params: Strategy parameters used

        Returns:
            Dict with standardized stock data structure:
            {
                'code': str,
                'score': float,
                'golden_cross': bool,
                'value': str
            }
        """
        # Extract data from strategy result
        meets_criteria = strategy_result[0] if len(strategy_result) > 0 else False
        reason = strategy_result[1] if len(strategy_result) > 1 else ""
        score = strategy_result[2] if len(strategy_result) > 2 else 0.0
        golden_cross = strategy_result[3] if len(strategy_result) > 3 else False

        # Ensure data types are correct
        score = float(score) if score is not None else 0.0
        golden_cross = bool(golden_cross) if golden_cross is not None else False

        # Format technical indicator values into value string
        value_text = StockDataFormatter._format_technical_values(
            code=code,
            technical_analysis=technical_analysis,
            strategy_params=strategy_params,
            reason=reason
        )

        # Create standardized stock data structure
        stock_data = {
            'code': str(code),
            'score': score,
            'golden_cross': golden_cross,
            'value': value_text
        }

        return stock_data

    @staticmethod
    def _format_technical_values(
        code: str,
        technical_analysis: Optional[Dict] = None,
        strategy_params: Optional[Dict] = None,
        reason: str = ""
    ) -> str:
        """
        Format technical indicator values into standardized string

        Args:
            code: Stock code
            technical_analysis: Technical analysis data from strategy
            strategy_params: Strategy parameters used
            reason: Reason text from strategy (fallback source)

        Returns:
            Formatted string with technical indicator values
        """
        try:
            # If we have technical analysis data, use it
            if technical_analysis and isinstance(technical_analysis, dict):
                return StockDataFormatter._extract_from_technical_analysis(technical_analysis)

            # If we have reason text with technical data, extract from it
            if reason and "收盘价=" in reason:
                # Extract technical data from reason text
                return StockDataFormatter._extract_from_reason_text(reason)

            # Default fallback
            return "收盘价=N/A, MA5=N/A, MA13=N/A, MA34=N/A"

        except Exception as e:
            logger.warning(f"Error formatting technical values for stock {code}: {e}")
            return "收盘价=N/A, MA5=N/A, MA13=N/A, MA34=N/A"

    @staticmethod
    def _extract_from_technical_analysis(technical_analysis: Dict) -> str:
        """
        Extract technical values from technical_analysis dictionary

        Args:
            technical_analysis: Technical analysis data

        Returns:
            Formatted string with technical indicator values
        """
        try:
            # Try to get price
            price = "N/A"
            if 'price' in technical_analysis:
                price = f"{float(technical_analysis['price']):.2f}"
            elif 'close' in technical_analysis:
                price = f"{float(technical_analysis['close']):.2f}"

            # Try to get moving averages
            ma5, ma13, ma34 = "N/A", "N/A", "N/A"

            # Check for moving averages in different possible locations
            if 'moving_averages' in technical_analysis:
                ma_data = technical_analysis['moving_averages']
                if isinstance(ma_data, dict):
                    ma5 = f"{float(ma_data.get('ma5', ma_data.get('ma_short', ma_data.get('sma_5', 'N/A')))): .2f}" if ma_data.get('ma5') or ma_data.get('ma_short') or ma_data.get('sma_5') else "N/A"
                    ma13 = f"{float(ma_data.get('ma13', ma_data.get('ma_mid', ma_data.get('sma_13', 'N/A')))): .2f}" if ma_data.get('ma13') or ma_data.get('ma_mid') or ma_data.get('sma_13') else "N/A"
                    ma34 = f"{float(ma_data.get('ma34', ma_data.get('ma_long', ma_data.get('sma_34', 'N/A')))): .2f}" if ma_data.get('ma34') or ma_data.get('ma_long') or ma_data.get('sma_34') else "N/A"

            # Check for direct MA values
            if ma5 == "N/A" and 'ma_short' in technical_analysis:
                ma5 = f"{float(technical_analysis['ma_short']):.2f}"
            if ma13 == "N/A" and 'ma_mid' in technical_analysis:
                ma13 = f"{float(technical_analysis['ma_mid']):.2f}"
            if ma34 == "N/A" and 'ma_long' in technical_analysis:
                ma34 = f"{float(technical_analysis['ma_long']):.2f}"

            return f"收盘价={price}, MA5={ma5}, MA13={ma13}, MA34={ma34}"

        except Exception as e:
            logger.warning(f"Error extracting from technical analysis: {e}")
            return "收盘价=N/A, MA5=N/A, MA13=N/A, MA34=N/A"

    @staticmethod
    def _extract_from_reason_text(reason: str) -> str:
        """
        Extract technical values from reason text

        Args:
            reason: Reason text from strategy

        Returns:
            Formatted string with technical indicator values
        """
        try:
            # If reason already contains formatted technical data, return it
            if "收盘价=" in reason and "MA" in reason:
                # Extract the technical part from reason text
                import re
                pattern = r"收盘价=[^,]+, MA5=[^,]+, MA13=[^,]+, MA34=[^,]+"
                match = re.search(pattern, reason)
                if match:
                    return match.group(0)

            # Try to parse technical data from reason text
            # This is a simplified parser - in practice, this would be more robust
            return reason if reason else "收盘价=N/A, MA5=N/A, MA13=N/A, MA34=N/A"

        except Exception as e:
            logger.warning(f"Error extracting from reason text: {e}")
            return "收盘价=N/A, MA5=N/A, MA13=N/A, MA34=N/A"

    @staticmethod
    def format_multiple_stocks(
        stock_results: List[Dict],
        strategy_params: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Format multiple stock results into standardized structure

        Args:
            stock_results: List of stock result dictionaries from strategies
            strategy_params: Strategy parameters used

        Returns:
            List of standardized stock data dictionaries
        """
        formatted_stocks = []

        for stock_result in stock_results:
            try:
                # Extract required fields
                code = stock_result.get('code', '')
                if not code:
                    continue

                # Handle different strategy result formats
                if 'meets_criteria' in stock_result:
                    # Format: {'code': ..., 'meets_criteria': ..., 'reason': ..., 'score': ..., 'golden_cross': ...}
                    strategy_result = (
                        stock_result.get('meets_criteria', False),
                        stock_result.get('reason', ''),
                        stock_result.get('score', 0.0),
                        stock_result.get('golden_cross', False)
                    )
                elif 'selection_reason' in stock_result:
                    # Format: {'code': ..., 'selection_reason': ..., 'score': ..., 'golden_cross': ...}
                    strategy_result = (
                        True,  # Assume selected if in results
                        stock_result.get('selection_reason', ''),
                        stock_result.get('score', 0.0),
                        stock_result.get('golden_cross', False)
                    )
                else:
                    # Minimal format: {'code': ..., 'score': ...}
                    strategy_result = (
                        True,
                        "",
                        stock_result.get('score', 0.0),
                        stock_result.get('golden_cross', False)
                    )

                # Get technical analysis data if present
                technical_analysis = stock_result.get('technical_analysis', {})

                # Format the stock data
                formatted_stock = StockDataFormatter.format_stock_data(
                    code=code,
                    strategy_result=strategy_result,
                    technical_analysis=technical_analysis,
                    strategy_params=strategy_params
                )

                formatted_stocks.append(formatted_stock)

            except Exception as e:
                logger.warning(f"Error formatting stock data for {stock_result.get('code', 'unknown')}: {e}")
                continue

        return formatted_stocks


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Example 1: Format data from a strategy result
    strategy_result = (True, "满足多头排列: 收盘价=10.50, MA5=9.80, MA13=9.20, MA34=8.60", 85.5, True)
    technical_analysis = {
        'price': 10.50,
        'moving_averages': {
            'ma_short': 9.80,
            'ma_mid': 9.20,
            'ma_long': 8.60
        }
    }

    formatted_stock = StockDataFormatter.format_stock_data(
        code="000001",
        strategy_result=strategy_result,
        technical_analysis=technical_analysis
    )

    print("Formatted stock data:")
    print(formatted_stock)

    # Example 2: Format multiple stocks
    stock_results = [
        {
            'code': '000001',
            'selection_reason': '满足多头排列: 收盘价=10.50, MA5=9.80, MA13=9.20, MA34=8.60',
            'score': 85.5,
            'golden_cross': True,
            'technical_analysis': {
                'price': 10.50,
                'moving_averages': {
                    'ma_short': 9.80,
                    'ma_mid': 9.20,
                    'ma_long': 8.60
                }
            }
        },
        {
            'code': '000002',
            'score': 72.3,
            'golden_cross': False
        }
    ]

    formatted_stocks = StockDataFormatter.format_multiple_stocks(stock_results)

    print("\nFormatted multiple stocks:")
    for stock in formatted_stocks:
        print(stock)

