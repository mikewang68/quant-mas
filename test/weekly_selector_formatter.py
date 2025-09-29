"""
Weekly Selector Formatter Utility
Provides unified interface for formatting stock data from different strategies for weekly selector
"""

import logging
from typing import Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)


class WeeklySelectorFormatter:
    """
    Unified formatter for stock data from different strategies in weekly selector
    Ensures consistent structure for Stocks array items in pool collection
    """

    @staticmethod
    def format_stock_value(
        stock_code: str,
        technical_analysis_data: Optional[Dict] = None,
        score_info: Optional[Any] = None,
        strategy_name: str = ""
    ) -> str:
        """
        Format the value field for a stock based on technical analysis data from different strategies

        Args:
            stock_code: Stock code
            technical_analysis_data: Technical analysis data from strategy
            score_info: Score information or reason text from strategy
            strategy_name: Name of the strategy (for logging purposes)

        Returns:
            Formatted string for the value field
        """
        try:
            # If we have technical analysis data, use it to create value text
            if technical_analysis_data and isinstance(technical_analysis_data, dict):
                return WeeklySelectorFormatter._format_from_technical_analysis(
                    technical_analysis_data, stock_code
                )

            # If we have score_info/reason text, try to extract technical data from it
            if score_info:
                return WeeklySelectorFormatter._format_from_score_info(
                    score_info, stock_code
                )

            # Default fallback
            return "收盘价=N/A, MA5=N/A, MA13=N/A, MA34=N/A"

        except Exception as e:
            logger.warning(f"Error formatting value for stock {stock_code} in {strategy_name}: {e}")
            return "收盘价=N/A, MA5=N/A, MA13=N/A, MA34=N/A"

    @staticmethod
    def _format_from_technical_analysis(technical_analysis: Dict, stock_code: str) -> str:
        """
        Format value text from technical analysis data

        Args:
            technical_analysis: Technical analysis data from strategy
            stock_code: Stock code (for logging)

        Returns:
            Formatted string with technical indicator values
        """
        try:
            # Try to get price
            price = "N/A"
            if 'price' in technical_analysis:
                price_val = technical_analysis['price']
                if isinstance(price_val, (int, float)) and not np.isnan(price_val):
                    price = f"{float(price_val):.2f}"
            elif 'close' in technical_analysis:
                close_val = technical_analysis['close']
                if isinstance(close_val, (int, float)) and not np.isnan(close_val):
                    price = f"{float(close_val):.2f}"

            # Try to get moving averages - handle different naming conventions
            ma5, ma13, ma34 = "N/A", "N/A", "N/A"

            # Look for moving averages in various possible locations and names
            ma_data = technical_analysis.get('moving_averages', {})
            if isinstance(ma_data, dict):
                # Try different naming conventions for MA5
                ma5_val = (
                    ma_data.get('ma5') or
                    ma_data.get('ma_short') or
                    ma_data.get('sma_5') or
                    ma_data.get('MA5') or
                    ma_data.get('short')
                )
                if ma5_val is not None and isinstance(ma5_val, (int, float)) and not np.isnan(ma5_val):
                    ma5 = f"{float(ma5_val):.2f}"

                # Try different naming conventions for MA13
                ma13_val = (
                    ma_data.get('ma13') or
                    ma_data.get('ma_mid') or
                    ma_data.get('sma_13') or
                    ma_data.get('MA13') or
                    ma_data.get('mid')
                )
                if ma13_val is not None and isinstance(ma13_val, (int, float)) and not np.isnan(ma13_val):
                    ma13 = f"{float(ma13_val):.2f}"

                # Try different naming conventions for MA34
                ma34_val = (
                    ma_data.get('ma34') or
                    ma_data.get('ma_long') or
                    ma_data.get('sma_34') or
                    ma_data.get('MA34') or
                    ma_data.get('long')
                )
                if ma34_val is not None and isinstance(ma34_val, (int, float)) and not np.isnan(ma34_val):
                    ma34 = f"{float(ma34_val):.2f}"

            # If we didn't find moving averages in moving_averages dict, look in top level
            if ma5 == "N/A":
                ma5_val = (
                    technical_analysis.get('ma5') or
                    technical_analysis.get('ma_short') or
                    technical_analysis.get('sma_5') or
                    technical_analysis.get('MA5') or
                    technical_analysis.get('short')
                )
                if ma5_val is not None and isinstance(ma5_val, (int, float)) and not np.isnan(ma5_val):
                    ma5 = f"{float(ma5_val):.2f}"

            if ma13 == "N/A":
                ma13_val = (
                    technical_analysis.get('ma13') or
                    technical_analysis.get('ma_mid') or
                    technical_analysis.get('sma_13') or
                    technical_analysis.get('MA13') or
                    technical_analysis.get('mid')
                )
                if ma13_val is not None and isinstance(ma13_val, (int, float)) and not np.isnan(ma13_val):
                    ma13 = f"{float(ma13_val):.2f}"

            if ma34 == "N/A":
                ma34_val = (
                    technical_analysis.get('ma34') or
                    technical_analysis.get('ma_long') or
                    technical_analysis.get('sma_34') or
                    technical_analysis.get('MA34') or
                    technical_analysis.get('long')
                )
                if ma34_val is not None and isinstance(ma34_val, (int, float)) and not np.isnan(ma34_val):
                    ma34 = f"{float(ma34_val):.2f}"

            return f"收盘价={price}, MA5={ma5}, MA13={ma13}, MA34={ma34}"

        except Exception as e:
            logger.warning(f"Error formatting from technical analysis for stock {stock_code}: {e}")
            return "收盘价=N/A, MA5=N/A, MA13=N/A, MA34=N/A"

    @staticmethod
    def _format_from_score_info(score_info: Any, stock_code: str) -> str:
        """
        Format value text from score information or reason text

        Args:
            score_info: Score information or reason text from strategy
            stock_code: Stock code (for logging)

        Returns:
            Formatted string with technical indicator values
        """
        try:
            # Convert to string if it's not already
            score_text = str(score_info) if score_info is not None else ""

            # If it contains technical information, extract it
            if "收盘价=" in score_text and ("MA" in score_text or "ma" in score_text):
                # Extract the technical part from score text
                import re
                pattern = r"收盘价=[^,]+, MA5=[^,]+, MA13=[^,]+, MA34=[^,]+"
                match = re.search(pattern, score_text)
                if match:
                    return match.group(0)

                # Try a more flexible pattern
                pattern2 = r"收盘价=[\d.]+.*?(?:MA|ma)[\d\w=., ]+"
                match2 = re.search(pattern2, score_text)
                if match2:
                    # Try to parse and format properly
                    extracted = match2.group(0)
                    if "MA5=" in extracted and "MA13=" in extracted and "MA34=" in extracted:
                        return extracted
                    # If partial match, try to complete it
                    return WeeklySelectorFormatter._complete_value_text(extracted)

            # If it's just a simple reason without technical data, use a generic format
            if score_text and not ("收盘价=" in score_text):
                return f"收盘价=N/A, MA5=N/A, MA13=N/A, MA34=N/A (原因: {score_text[:50]}...)"

            # Default fallback
            return "收盘价=N/A, MA5=N/A, MA13=N/A, MA34=N/A"

        except Exception as e:
            logger.warning(f"Error formatting from score info for stock {stock_code}: {e}")
            return "收盘价=N/A, MA5=N/A, MA13=N/A, MA34=N/A"

    @staticmethod
    def _complete_value_text(partial_text: str) -> str:
        """
        Complete partial value text with missing fields

        Args:
            partial_text: Partial value text

        Returns:
            Completed value text
        """
        try:
            # Add missing MA fields if not present
            result = partial_text
            if "MA5=" not in result:
                result += ", MA5=N/A"
            if "MA13=" not in result:
                result += ", MA13=N/A"
            if "MA34=" not in result:
                result += ", MA34=N/A"
            return result
        except Exception:
            return partial_text


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Example 1: Format from technical analysis data (trend following strategy format)
    tech_analysis_trend = {
        'price': 10.50,
        'moving_averages': {
            'sma_5': 9.80,
            'sma_13': 9.20,
        },
        'macd': {
            'dif': 0.15,
            'dea': 0.10,
        }
    }

    formatted_value1 = WeeklySelectorFormatter.format_stock_value(
        stock_code="000001",
        technical_analysis_data=tech_analysis_trend,
        strategy_name="TrendFollowingStrategy"
    )

    print("Formatted value (trend following format):")
    print(formatted_value1)

    # Example 2: Format from technical analysis data (three MA strategy format)
    tech_analysis_three_ma = {
        'price': 10.50,
        'ma_short': 9.80,
        'ma_mid': 9.20,
        'ma_long': 8.60
    }

    formatted_value2 = WeeklySelectorFormatter.format_stock_value(
        stock_code="000002",
        technical_analysis_data=tech_analysis_three_ma,
        strategy_name="ThreeMABullishArrangementStrategy"
    )

    print("\nFormatted value (three MA format):")
    print(formatted_value2)

    # Example 3: Format from score info with technical data
    score_info = "满足多头排列: 收盘价=10.50, MA5=9.80, MA13=9.20, MA34=8.60 (检测到金叉)"

    formatted_value3 = WeeklySelectorFormatter.format_stock_value(
        stock_code="000003",
        score_info=score_info,
        strategy_name="ThreeMABullishArrangementStrategy"
    )

    print("\nFormatted value (from score info):")
    print(formatted_value3)

