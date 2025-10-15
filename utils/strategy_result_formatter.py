"""
Strategy Result Formatter Utility
Provides unified interface for formatting strategy results for pool storage
"""

import logging
from typing import Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)


class StrategyResultFormatter:
    """
    Unified formatter for strategy results to ensure consistent pool storage
    """

    @staticmethod
    def format_value_field(
        stock_code: str,
        technical_analysis_data: Optional[Dict] = None,
        reason_text: str = "",
        score: Any = None,
        strategy_name: Optional[str] = None,
    ) -> str:
        """
        Format value field based on technical analysis data or reason text

        Args:
            stock_code: Stock code
            technical_analysis_data: Technical analysis data from strategy
            reason_text: Reason text from strategy analysis
            score: Strategy score

        Returns:
            Formatted value string for pool storage
        """
        try:
            # Priority 1: Use technical analysis data if available
            if technical_analysis_data and isinstance(technical_analysis_data, dict):
                return StrategyResultFormatter._format_from_technical_data(
                    technical_analysis_data
                )

            # Priority 2: Extract from reason text if it contains technical information
            if reason_text and ("收盘价=" in reason_text or "MA" in reason_text):
                extracted_value = StrategyResultFormatter._extract_from_reason_text(
                    reason_text
                )
                if extracted_value:
                    return extracted_value

            # Priority 3: Create generic value text from score
            if score is not None:
                return f"策略得分={float(score):.2f}"

            # Default fallback
            return "收盘价=N/A, MA5=N/A, MA13=N/A, MA34=N/A"

        except Exception as e:
            logger.warning(f"Error formatting value field for stock {stock_code}: {e}")
            return "收盘价=N/A, MA5=N/A, MA13=N/A, MA34=N/A"

    @staticmethod
    def _format_from_technical_data(technical_analysis_data: Dict) -> str:
        """
        Format value field from technical analysis data

        Args:
            technical_analysis_data: Technical analysis data from strategy

        Returns:
            Formatted value string
        """
        try:
            # Try to get price from various possible locations
            price = StrategyResultFormatter._extract_value(
                technical_analysis_data, ["price", "close", "current_price"]
            )

            # Try to get moving averages - handle different naming conventions
            ma5 = StrategyResultFormatter._extract_value(
                technical_analysis_data, ["ma_short", "ma5", "sma_5", "MA5", "short_ma"]
            )
            ma13 = StrategyResultFormatter._extract_value(
                technical_analysis_data, ["ma_mid", "ma13", "sma_13", "MA13", "mid_ma"]
            )
            ma34 = StrategyResultFormatter._extract_value(
                technical_analysis_data,
                ["ma_long", "ma34", "sma_34", "MA34", "long_ma"],
            )

            # Try to get MACD values
            dif = StrategyResultFormatter._extract_value(
                technical_analysis_data, ["dif", "DIF", "macd_dif"]
            )
            dea = StrategyResultFormatter._extract_value(
                technical_analysis_data, ["dea", "DEA", "macd_dea"]
            )

            # If we don't have standard moving averages, try to find any moving averages
            if ma5 is None or ma13 is None or ma34 is None:
                # Look in nested moving_averages dict
                if "moving_averages" in technical_analysis_data and isinstance(
                    technical_analysis_data["moving_averages"], dict
                ):
                    ma_dict = technical_analysis_data["moving_averages"]
                    if ma5 is None:
                        ma5 = StrategyResultFormatter._extract_value(
                            ma_dict,
                            ["ma_short", "ma5", "sma_5", "MA5", "short_ma", "sma_5"],
                        )
                    if ma13 is None:
                        ma13 = StrategyResultFormatter._extract_value(
                            ma_dict,
                            ["ma_mid", "ma13", "sma_13", "MA13", "mid_ma", "sma_13"],
                        )
                    if ma34 is None:
                        ma34 = StrategyResultFormatter._extract_value(
                            ma_dict,
                            ["ma_long", "ma34", "sma_34", "MA34", "long_ma", "sma_34"],
                        )

            # If we don't have MACD values, try to find them in nested macd dict
            if dif is None or dea is None:
                if "macd" in technical_analysis_data and isinstance(
                    technical_analysis_data["macd"], dict
                ):
                    macd_dict = technical_analysis_data["macd"]
                    if dif is None:
                        dif = StrategyResultFormatter._extract_value(
                            macd_dict, ["dif", "DIF", "macd_dif"]
                        )
                    if dea is None:
                        dea = StrategyResultFormatter._extract_value(
                            macd_dict, ["dea", "DEA", "macd_dea"]
                        )

            # Format the values
            price_str = StrategyResultFormatter._format_number(price)
            ma5_str = StrategyResultFormatter._format_number(ma5)
            ma13_str = StrategyResultFormatter._format_number(ma13)
            ma34_str = StrategyResultFormatter._format_number(ma34)
            dif_str = StrategyResultFormatter._format_number(dif)
            dea_str = StrategyResultFormatter._format_number(dea)

            # Check if this is Pullback Buying strategy data (has pullback-specific fields)
            has_pullback_data = any(
                key in technical_analysis_data
                for key in ["ma_value", "kdj_j", "rsi_value", "is_valid_pullback"]
            )

            if has_pullback_data:
                # Format for Pullback Buying strategy
                ma_value = StrategyResultFormatter._extract_value(
                    technical_analysis_data, ["ma_value"]
                )
                kdj_j = StrategyResultFormatter._extract_value(
                    technical_analysis_data, ["kdj_j"]
                )
                rsi_value = StrategyResultFormatter._extract_value(
                    technical_analysis_data, ["rsi_value"]
                )
                is_valid_pullback = technical_analysis_data.get(
                    "is_valid_pullback", False
                )

                ma_value_str = StrategyResultFormatter._format_number(ma_value)
                kdj_j_str = StrategyResultFormatter._format_number(kdj_j)
                rsi_value_str = StrategyResultFormatter._format_number(rsi_value)
                pullback_status = "有效回踩" if is_valid_pullback else "无效回踩"

                # Format with Pullback Buying specific fields
                return f"收盘价={price_str}, 均线值={ma_value_str}, KDJ_J={kdj_j_str}, RSI={rsi_value_str}, 状态={pullback_status}"

            # Check if this is Volume Breakout strategy data (has volume-specific fields)
            has_volume_data = any(
                key in technical_analysis_data
                for key in [
                    "breakout_high",
                    "current_volume",
                    "avg_volume",
                    "volume_ratio",
                ]
            )

            if has_volume_data:
                # Format for Volume Breakout strategy
                breakout_high = StrategyResultFormatter._extract_value(
                    technical_analysis_data, ["breakout_high"]
                )
                current_volume = StrategyResultFormatter._extract_value(
                    technical_analysis_data, ["current_volume"]
                )
                avg_volume = StrategyResultFormatter._extract_value(
                    technical_analysis_data, ["avg_volume"]
                )
                volume_ratio = StrategyResultFormatter._extract_value(
                    technical_analysis_data, ["volume_ratio"]
                )

                breakout_high_str = StrategyResultFormatter._format_number(
                    breakout_high
                )
                current_volume_str = StrategyResultFormatter._format_number(
                    current_volume
                )
                avg_volume_str = StrategyResultFormatter._format_number(avg_volume)
                volume_ratio_str = StrategyResultFormatter._format_number(volume_ratio)

                # Format with Volume Breakout specific fields
                if dif is not None and dea is not None:
                    return f"收盘价={price_str}, 突破高点={breakout_high_str}, 当前成交量={current_volume_str}, 平均成交量={avg_volume_str}, 量比={volume_ratio_str}, DIF={dif_str}, DEA={dea_str}"
                else:
                    return f"收盘价={price_str}, 突破高点={breakout_high_str}, 当前成交量={current_volume_str}, 平均成交量={avg_volume_str}, 量比={volume_ratio_str}"

            # Build value string based on available data
            if dif is not None and dea is not None:
                # Include MACD values if available
                return f"收盘价={price_str}, MA5={ma5_str}, MA13={ma13_str}, DIF={dif_str}, DEA={dea_str}"
            else:
                # Default format with moving averages only
                return f"收盘价={price_str}, MA5={ma5_str}, MA13={ma13_str}, MA34={ma34_str}"

        except Exception as e:
            logger.warning(f"Error formatting from technical data: {e}")
            return "收盘价=N/A, MA5=N/A, MA13=N/A, MA34=N/A"

    @staticmethod
    def _extract_value(data_dict: Dict, possible_keys: list) -> Any:
        """
        Extract value from dictionary using possible keys

        Args:
            data_dict: Dictionary to search in
            possible_keys: List of possible keys to look for

        Returns:
            Value if found, None otherwise
        """
        for key in possible_keys:
            if key in data_dict and data_dict[key] is not None:
                return data_dict[key]
        return None

    @staticmethod
    def _format_number(value: Any) -> str:
        """
        Format number value to string with 2 decimal places

        Args:
            value: Value to format

        Returns:
            Formatted string
        """
        if value is None or (isinstance(value, str) and value.upper() == "N/A"):
            return "N/A"
        try:
            return f"{float(value):.2f}"
        except (ValueError, TypeError):
            return str(value)

    @staticmethod
    def _extract_from_reason_text(reason_text: str) -> Optional[str]:
        """
        Extract technical values from reason text

        Args:
            reason_text: Reason text from strategy

        Returns:
            Extracted value string or None if not found
        """
        try:
            # Look for pattern: "收盘价=..., MA5=..., MA13=..., MA34=..."
            import re

            pattern = r"收盘价=[^,\s]+, MA\d+=[^,\s]+, MA\d+=[^,\s]+, MA\d+=[^,\s]+"
            match = re.search(pattern, reason_text)
            if match:
                return match.group(0)

            # Look for pattern with 收盘价= prefix
            if reason_text.startswith("满足多头排列: "):
                # Extract the technical part
                tech_part = reason_text.replace("满足多头排列: ", "")
                if "收盘价=" in tech_part and "MA" in tech_part:
                    return tech_part

            # Look for any technical data in the text
            if "收盘价=" in reason_text:
                # Try to extract technical data around 收盘价
                parts = reason_text.split()
                for part in parts:
                    if "收盘价=" in part and "MA" in part:
                        return part

            return None

        except Exception as e:
            logger.warning(f"Error extracting from reason text: {e}")
            return None

    @staticmethod
    def format_stock_data_for_pool(
        stock_code: str,
        score: Any = None,
        # golden_cross: bool = False,
        technical_analysis_data: Optional[Dict] = None,
        reason_text: str = "",
    ) -> Dict[str, Any]:
        """
        Format complete stock data for pool storage

        Args:
            stock_code: Stock code
            score: Strategy score
            golden_cross: Golden cross flag
            technical_analysis_data: Technical analysis data from strategy
            reason_text: Reason text from strategy analysis

        Returns:
            Formatted stock data dictionary for pool storage
        """
        # Ensure score is a float or 0.0
        try:
            score_float = float(score) if score is not None else 0.0
        except (ValueError, TypeError):
            score_float = 0.0

        # Format value field
        value_text = StrategyResultFormatter.format_value_field(
            stock_code=stock_code,
            technical_analysis_data=technical_analysis_data,
            reason_text=reason_text,
            score=score,
        )

        return {
            "code": str(stock_code),
            "score": score_float,
            # "golden_cross": bool(golden_cross),
            "value": value_text,
        }


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Example 1: Format from technical analysis data (three MA strategy format)
    tech_data_1 = {"price": 10.50, "ma_short": 9.80, "ma_mid": 9.20, "ma_long": 8.60}

    formatted_value_1 = StrategyResultFormatter.format_value_field(
        stock_code="000001", technical_analysis_data=tech_data_1
    )
    print("Formatted value 1:", formatted_value_1)

    # Example 2: Format from technical analysis data (trend following strategy format)
    tech_data_2 = {
        "price": 12.30,
        "moving_averages": {"sma_5": 11.80, "sma_13": 11.20},
        "macd": {"dif": 0.15, "dea": 0.10},
    }

    formatted_value_2 = StrategyResultFormatter.format_value_field(
        stock_code="000002", technical_analysis_data=tech_data_2
    )
    print("Formatted value 2:", formatted_value_2)

    # Example 3: Format from reason text
    reason_text = "满足多头排列: 收盘价=15.20, MA5=14.80, MA13=14.20, MA34=13.60"
    formatted_value_3 = StrategyResultFormatter.format_value_field(
        stock_code="000003", reason_text=reason_text
    )
    print("Formatted value 3:", formatted_value_3)

    # Example 4: Format complete stock data
    stock_data = StrategyResultFormatter.format_stock_data_for_pool(
        stock_code="000004",
        score=85.5,
        # golden_cross=True,
        technical_analysis_data=tech_data_1,
        reason_text="趋势强度得分85.50, MA5(9.80) > MA13(9.20), DIF(0.1500) > DEA(0.1000)",
    )
    print("Formatted stock data:", stock_data)
