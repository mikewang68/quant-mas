"""
Weekly Strategy Formatter Utility
Provides unified interface for formatting strategy results in weekly selector
"""

import logging
from typing import Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)


class WeeklyStrategyFormatter:
    """
    Unified formatter for strategy results in weekly selector
    Ensures consistent value field formatting for different strategies
    """

    @staticmethod
    def format_strategy_value(
        strategy_name: str,
        technical_analysis_data: Optional[Dict] = None,
        reason: str = "",
        score: Any = None
    ) -> str:
        """
        Format value field based on strategy type and available technical analysis data

        Args:
            strategy_name: Name of the strategy
            technical_analysis_data: Technical analysis data from strategy
            reason: Reason text from strategy analysis
            score: Score from strategy analysis

        Returns:
            Formatted value string for pool storage
        """
        try:
            # Handle different strategy types
            if "三均线" in strategy_name or "多头排列" in strategy_name:
                return WeeklyStrategyFormatter._format_three_ma_value(technical_analysis_data, reason)
            elif "趋势跟踪" in strategy_name:
                return WeeklyStrategyFormatter._format_trend_following_value(technical_analysis_data, reason)
            elif "移动平均线交叉" in strategy_name:
                return WeeklyStrategyFormatter._format_ma_crossover_value(technical_analysis_data, reason)
            elif "MACD" in strategy_name:
                return WeeklyStrategyFormatter._format_macd_value(technical_analysis_data, reason)
            elif "RSI" in strategy_name:
                return WeeklyStrategyFormatter._format_rsi_value(technical_analysis_data, reason)
            else:
                # Generic formatter - try to extract from reason or technical data
                return WeeklyStrategyFormatter._format_generic_value(
                    technical_analysis_data, reason, strategy_name
                )

        except Exception as e:
            logger.warning(f"Error formatting value for strategy {strategy_name}: {e}")
            return "收盘价=N/A, MA5=N/A, MA13=N/A, MA34=N/A"

    @staticmethod
    def _format_three_ma_value(technical_analysis_data: Optional[Dict], reason: str) -> str:
        """Format value for three moving average strategies"""
        # Try to extract from technical analysis data first
        if technical_analysis_data and isinstance(technical_analysis_data, dict):
            price = technical_analysis_data.get('price', 'N/A')
            ma_short = technical_analysis_data.get('ma_short', 'N/A')
            ma_mid = technical_analysis_data.get('ma_mid', 'N/A')
            ma_long = technical_analysis_data.get('ma_long', 'N/A')

            # Format values
            price_str = f"{float(price):.2f}" if isinstance(price, (int, float)) else str(price)
            ma5_str = f"{float(ma_short):.2f}" if isinstance(ma_short, (int, float)) else str(ma_short)
            ma13_str = f"{float(ma_mid):.2f}" if isinstance(ma_mid, (int, float)) else str(ma_mid)
            ma34_str = f"{float(ma_long):.2f}" if isinstance(ma_long, (int, float)) else str(ma_long)

            return f"收盘价={price_str}, MA5={ma5_str}, MA13={ma13_str}, MA34={ma34_str}"

        # Fallback to reason text extraction
        if reason and "收盘价=" in reason:
            import re
            pattern = r"收盘价=[^,]+, MA\d+=[^,]+, MA\d+=[^,]+, MA\d+=[^,]+"
            match = re.search(pattern, reason)
            if match:
                return match.group(0)

        return "收盘价=N/A, MA5=N/A, MA13=N/A, MA34=N/A"

    @staticmethod
    def _format_trend_following_value(technical_analysis_data: Optional[Dict], reason: str) -> str:
        """Format value for trend following strategies"""
        # Try to extract from technical analysis data
        if technical_analysis_data and isinstance(technical_analysis_data, dict):
            price = technical_analysis_data.get('price', 'N/A')

            # Try different possible MA field names
            ma_fast = (technical_analysis_data.get('moving_averages', {}).get('sma_5') or
                      technical_analysis_data.get('moving_averages', {}).get('ma_fast') or
                      technical_analysis_data.get('ma_fast', 'N/A'))

            ma_slow = (technical_analysis_data.get('moving_averages', {}).get('sma_13') or
                      technical_analysis_data.get('moving_averages', {}).get('ma_slow') or
                      technical_analysis_data.get('ma_slow', 'N/A'))

            # Format values
            price_str = f"{float(price):.2f}" if isinstance(price, (int, float)) else str(price)
            ma5_str = f"{float(ma_fast):.2f}" if isinstance(ma_fast, (int, float)) else str(ma_fast)
            ma13_str = f"{float(ma_slow):.2f}" if isinstance(ma_slow, (int, float)) else str(ma_slow)

            # For trend following, we might not have MA34, so use N/A
            return f"收盘价={price_str}, MA5={ma5_str}, MA13={ma13_str}, MA34=N/A"

        # Fallback to reason text extraction
        if reason:
            import re
            # Look for price and MA values in reason text
            price_match = re.search(r"价格[=(](\d+\.?\d*)", reason)
            ma5_match = re.search(r"MA\d+[=(](\d+\.?\d*)", reason)
            ma13_match = re.search(r"MA\d+[=(](\d+\.?\d*)[^,]*MA\d+[=(](\d+\.?\d*)", reason)

            if price_match or ma5_match:
                price_str = price_match.group(1) if price_match else "N/A"
                ma5_str = ma5_match.group(1) if ma5_match else "N/A"
                ma13_str = ma13_match.group(2) if ma13_match else "N/A"
                return f"收盘价={price_str}, MA5={ma5_str}, MA13={ma13_str}, MA34=N/A"

        return "收盘价=N/A, MA5=N/A, MA13=N/A, MA34=N/A"

    @staticmethod
    def _format_ma_crossover_value(technical_analysis_data: Optional[Dict], reason: str) -> str:
        """Format value for moving average crossover strategies"""
        # Similar to three MA but might have different field names
        if technical_analysis_data and isinstance(technical_analysis_data, dict):
            price = technical_analysis_data.get('price', 'N/A')
            ma_short = (technical_analysis_data.get('moving_averages', {}).get('ma_short') or
                       technical_analysis_data.get('ma_short', 'N/A'))
            ma_long = (technical_analysis_data.get('moving_averages', {}).get('ma_long') or
                      technical_analysis_data.get('ma_long', 'N/A'))

            price_str = f"{float(price):.2f}" if isinstance(price, (int, float)) else str(price)
            ma5_str = f"{float(ma_short):.2f}" if isinstance(ma_short, (int, float)) else str(ma_short)
            ma13_str = f"{float(ma_long):.2f}" if isinstance(ma_long, (int, float)) else str(ma_long)

            return f"收盘价={price_str}, MA5={ma5_str}, MA13={ma13_str}, MA34=N/A"

        # Fallback to reason text
        if reason and "收盘价=" in reason:
            import re
            pattern = r"收盘价=[^,]+, MA\d+=[^,]+, MA\d+=[^,]+"
            match = re.search(pattern, reason)
            if match:
                # Add MA34=N/A to complete the format
                return match.group(0) + ", MA34=N/A"

        return "收盘价=N/A, MA5=N/A, MA13=N/A, MA34=N/A"

    @staticmethod
    def _format_macd_value(technical_analysis_data: Optional[Dict], reason: str) -> str:
        """Format value for MACD strategies"""
        if technical_analysis_data and isinstance(technical_analysis_data, dict):
            price = technical_analysis_data.get('price', 'N/A')
            macd_data = technical_analysis_data.get('macd', {})
            macd_line = macd_data.get('macd_line', 'N/A') if isinstance(macd_data, dict) else 'N/A'
            signal_line = macd_data.get('signal_line', 'N/A') if isinstance(macd_data, dict) else 'N/A'

            price_str = f"{float(price):.2f}" if isinstance(price, (int, float)) else str(price)
            macd_str = f"{float(macd_line):.4f}" if isinstance(macd_line, (int, float)) else str(macd_line)
            signal_str = f"{float(signal_line):.4f}" if isinstance(signal_line, (int, float)) else str(signal_line)

            return f"收盘价={price_str}, MACD={macd_str}, 信号线={signal_str}, 柱状图=N/A"

        # Fallback to reason text
        if reason and ("MACD" in reason or "收盘价=" in reason):
            import re
            # Try to extract price and MACD info
            price_match = re.search(r"收盘价[=(](\d+\.?\d*)", reason)
            if price_match:
                price_str = price_match.group(1)
                return f"收盘价={price_str}, MACD=N/A, 信号线=N/A, 柱状图=N/A"

        return "收盘价=N/A, MACD=N/A, 信号线=N/A, 柱状图=N/A"

    @staticmethod
    def _format_rsi_value(technical_analysis_data: Optional[Dict], reason: str) -> str:
        """Format value for RSI strategies"""
        if technical_analysis_data and isinstance(technical_analysis_data, dict):
            price = technical_analysis_data.get('price', 'N/A')
            rsi_value = technical_analysis_data.get('rsi', 'N/A')

            price_str = f"{float(price):.2f}" if isinstance(price, (int, float)) else str(price)
            rsi_str = f"{float(rsi_value):.2f}" if isinstance(rsi_value, (int, float)) else str(rsi_value)

            return f"收盘价={price_str}, RSI={rsi_str}, 超买=70, 超卖=30"

        # Fallback to reason text
        if reason and ("RSI" in reason or "收盘价=" in reason):
            import re
            price_match = re.search(r"收盘价[=(](\d+\.?\d*)", reason)
            rsi_match = re.search(r"RSI[=(](\d+\.?\d*)", reason)

            price_str = price_match.group(1) if price_match else "N/A"
            rsi_str = rsi_match.group(1) if rsi_match else "N/A"

            return f"收盘价={price_str}, RSI={rsi_str}, 超买=70, 超卖=30"

        return "收盘价=N/A, RSI=N/A, 超买=70, 超卖=30"

    @staticmethod
    def _format_generic_value(
        technical_analysis_data: Optional[Dict],
        reason: str,
        strategy_name: str
    ) -> str:
        """Generic formatter for other strategies"""
        # Try to extract any available technical data
        if technical_analysis_data and isinstance(technical_analysis_data, dict):
            price = technical_analysis_data.get('price', 'N/A')
            price_str = f"{float(price):.2f}" if isinstance(price, (int, float)) else str(price)

            # Try to find any moving average data
            ma_data = technical_analysis_data.get('moving_averages', {})
            if isinstance(ma_data, dict) and ma_data:
                ma_keys = list(ma_data.keys())
                if len(ma_keys) >= 2:
                    ma1_val = ma_data[ma_keys[0]]
                    ma2_val = ma_data[ma_keys[1]]
                    ma1_str = f"{float(ma1_val):.2f}" if isinstance(ma1_val, (int, float)) else str(ma1_val)
                    ma2_str = f"{float(ma2_val):.2f}" if isinstance(ma2_val, (int, float)) else str(ma2_val)
                    return f"收盘价={price_str}, MA1={ma1_str}, MA2={ma2_str}, 其他=N/A"

            # Try direct MA fields
            ma_short = technical_analysis_data.get('ma_short', technical_analysis_data.get('sma_5', 'N/A'))
            ma_mid = technical_analysis_data.get('ma_mid', technical_analysis_data.get('sma_13', 'N/A'))

            if ma_short != 'N/A' or ma_mid != 'N/A':
                ma5_str = f"{float(ma_short):.2f}" if isinstance(ma_short, (int, float)) else str(ma_short)
                ma13_str = f"{float(ma_mid):.2f}" if isinstance(ma_mid, (int, float)) else str(ma_mid)
                return f"收盘价={price_str}, MA5={ma5_str}, MA13={ma13_str}, MA34=N/A"

            # Default to price only
            return f"收盘价={price_str}, 其他技术指标=N/A"

        # Try to extract from reason text
        if reason and "收盘价=" in reason:
            import re
            # Look for basic pattern
            price_match = re.search(r"收盘价[=(](\d+\.?\d*)", reason)
            if price_match:
                price_str = price_match.group(1)
                return f"收盘价={price_str}, 技术指标来自策略分析"

        # Last resort - generic format
        return "收盘价=N/A, 技术指标=N/A, 策略=" + strategy_name


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Example 1: Three MA strategy
    tech_data_3ma = {
        'price': 10.50,
        'ma_short': 9.80,
        'ma_mid': 9.20,
        'ma_long': 8.60
    }

    value_3ma = WeeklyStrategyFormatter.format_strategy_value(
        strategy_name="三均线多头排列策略",
        technical_analysis_data=tech_data_3ma,
        reason="满足多头排列: 收盘价=10.50, MA5=9.80, MA13=9.20, MA34=8.60"
    )

    print("Three MA Strategy Value:", value_3ma)

    # Example 2: Trend following strategy
    tech_data_trend = {
        'price': 15.20,
        'moving_averages': {
            'sma_5': 14.80,
            'sma_13': 14.20
        },
        'macd': {
            'dif': 0.1234,
            'dea': 0.0987
        }
    }

    value_trend = WeeklyStrategyFormatter.format_strategy_value(
        strategy_name="趋势跟踪策略",
        technical_analysis_data=tech_data_trend,
        reason="趋势强度得分85.50, MA5(14.80) > MA13(14.20), DIF(0.1234) > DEA(0.0987)"
    )

    print("Trend Following Strategy Value:", value_trend)

    # Example 3: MACD strategy
    tech_data_macd = {
        'price': 20.10,
        'macd': {
            'macd_line': 0.4567,
            'signal_line': 0.3456,
            'histogram': 0.1111
        }
    }

    value_macd = WeeklyStrategyFormatter.format_strategy_value(
        strategy_name="MACD策略",
        technical_analysis_data=tech_data_macd
    )

    print("MACD Strategy Value:", value_macd)

