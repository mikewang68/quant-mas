#!/usr/bin/env python3
"""
More lenient version of the strategy to see if we can select more stocks
"""

import sys
import os
import pandas as pd
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.three_ma_bullish_arrangement_strategy import ThreeMABullishArrangementStrategy
import talib

class MoreLenientThreeMAStrategy(ThreeMABullishArrangementStrategy):
    """More lenient version of the three MA strategy"""

    def analyze(self, data: pd.DataFrame) -> tuple:
        """
        More lenient analysis - allow some violations of the strict criteria
        """
        if data.empty:
            return False, "数据为空", None, False

        try:
            # Get required data points
            required_data = max(self.params['short'], self.params['mid'], self.params['long'])
            if len(data) < required_data:
                return False, f"数据不足，需要{required_data}条数据", None, False

            # Convert pandas Series to numpy array for TA-Lib
            close_prices = np.array(data['close'].values, dtype=np.float64)

            # Calculate moving averages using strategy parameters
            ma_short = talib.SMA(close_prices, timeperiod=self.params['short'])
            ma_mid = talib.SMA(close_prices, timeperiod=self.params['mid'])
            ma_long = talib.SMA(close_prices, timeperiod=self.params['long'])

            # Current price relative to moving averages
            current_price = close_prices[-1]
            ma_short_last = ma_short[-1] if len(ma_short) > 0 and not np.isnan(ma_short[-1]) else None
            ma_mid_last = ma_mid[-1] if len(ma_mid) > 0 and not np.isnan(ma_mid[-1]) else None
            ma_long_last = ma_long[-1] if len(ma_long) > 0 and not np.isnan(ma_long[-1]) else None

            # Previous moving averages (for trend check)
            ma_short_prev = ma_short[-2] if len(ma_short) > 1 and not np.isnan(ma_short[-2]) else None
            ma_mid_prev = ma_mid[-2] if len(ma_mid) > 1 and not np.isnan(ma_mid[-2]) else None
            ma_long_prev = ma_long[-2] if len(ma_long) > 1 and not np.isnan(ma_long[-2]) else None

            # Check if all moving averages are valid (not None)
            if ma_short_last is None or ma_mid_last is None or ma_long_last is None:
                return False, "移动平均线计算无效", None, False

            # More lenient price condition - allow small violations
            price_condition_strict = (current_price > ma_short_last) and \
                                   (ma_short_last > ma_mid_last) and \
                                   (ma_mid_last > ma_long_last)

            # Lenient condition - allow one violation
            price_violations = 0
            violation_details = []

            if not (current_price > ma_short_last):
                price_violations += 1
                violation_details.append(f"价格未高于MA{self.params['short']}")

            if not (ma_short_last > ma_mid_last):
                price_violations += 1
                violation_details.append(f"MA{self.params['short']}未高于MA{self.params['mid']}")

            if not (ma_mid_last > ma_long_last):
                price_violations += 1
                violation_details.append(f"MA{self.params['mid']}未高于MA{self.params['long']}")

            # Allow up to 1 violation
            price_condition_lenient = price_violations <= 1

            # Check if moving averages have generally positive trend
            trend_violations = []
            trend_score = 0
            total_trends = 0

            if ma_short_prev is not None:
                total_trends += 1
                if ma_short_last > ma_short_prev:
                    trend_score += 1
                else:
                    trend_violations.append(f"MA{self.params['short']}未上升")

            if ma_mid_prev is not None:
                total_trends += 1
                if ma_mid_last > ma_mid_prev:
                    trend_score += 1
                else:
                    trend_violations.append(f"MA{self.params['mid']}未上升")

            if ma_long_prev is not None:
                total_trends += 1
                if ma_long_last > ma_long_prev:
                    trend_score += 1
                else:
                    trend_violations.append(f"MA{self.params['long']}未上升")

            # Require at least 1 out of 3 trends to be positive (more lenient)
            trend_condition = trend_score >= 1 if total_trends >= 3 else True

            # Combined condition: lenient price arrangement + at least 1 positive trend
            if price_condition_strict and trend_condition:
                # Strict criteria met
                reason = f"满足多头排列: 收盘价={current_price:.2f}, MA{self.params['short']}={ma_short_last:.2f}, MA{self.params['mid']}={ma_mid_last:.2f}, MA{self.params['long']}={ma_long_last:.2f}"
                score = min(1.0, ((current_price / ma_long_last - 1) * 10))
                return True, reason, score, False
            elif price_condition_lenient and trend_condition:
                # Lenient criteria met
                reason = f"基本满足多头排列(允许{price_violations}个违反): 收盘价={current_price:.2f}, MA{self.params['short']}={ma_short_last:.2f}, MA{self.params['mid']}={ma_mid_last:.2f}, MA{self.params['long']}={ma_long_last:.2f}"
                score = min(0.8, ((current_price / ma_long_last - 1) * 5))  # Lower score for lenient
                return True, reason, score, False
            else:
                # Neither criteria met
                reason = f"不满足条件: "
                if not price_condition_lenient:
                    reason += f"价格排列违反过多({price_violations}个违反: {', '.join(violation_details)}); "
                if not trend_condition:
                    reason += f"均线趋势不符合: {trend_score}/{total_trends}个趋势为正 ({', '.join(trend_violations)})"
                return False, reason.strip("; "), None, False

        except Exception as e:
            self.log_error(f"分析错误: {e}")
            return False, f"分析错误: {e}", None, False

def test_lenient_strategy():
    """Test the lenient strategy with different data"""
    print("=== Testing More Lenient Strategy ===\n")

    # Create test data that fails strict criteria but might pass lenient
    dates = pd.date_range('2023-01-01', periods=50, freq='W')

    # Create sideways data that might pass lenient criteria
    close_prices = 100 + np.sin(np.arange(50) * 0.3) * 5 + np.arange(50) * 0.1

    test_data = pd.DataFrame({
        'date': dates,
        'open': close_prices * 0.99,
        'high': close_prices * 1.01,
        'low': close_prices * 0.99,
        'close': close_prices,
        'volume': np.ones(50) * 1000000
    })

    # Test both strategies
    strict_strategy = ThreeMABullishArrangementStrategy(params={'ma_short': 5, 'ma_mid': 13, 'ma_long': 34})
    lenient_strategy = MoreLenientThreeMAStrategy(params={'ma_short': 5, 'ma_mid': 13, 'ma_long': 34})

    print("Testing sideways data:")
    print(f"Close prices range: {close_prices.min():.2f} to {close_prices.max():.2f}")

    strict_result = strict_strategy.analyze(test_data)
    lenient_result = lenient_strategy.analyze(test_data)

    print(f"\nStrict strategy: {strict_result[0]} - {strict_result[1]}")
    print(f"Lenient strategy: {lenient_result[0]} - {lenient_result[1]}")

    # Test with realistic stock data
    print("\n" + "="*50)
    print("Testing realistic stock data:")

    returns = np.random.normal(0.001, 0.02, 52)
    prices = [100]
    for ret in returns:
        prices.append(prices[-1] * (1 + ret))
    prices = np.array(prices[1:])

    realistic_data = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=52, freq='W'),
        'open': prices * 0.99,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': np.ones(52) * 1000000
    })

    strict_result2 = strict_strategy.analyze(realistic_data)
    lenient_result2 = lenient_strategy.analyze(realistic_data)

    print(f"Price range: {prices.min():.2f} to {prices.max():.2f}")
    print(f"Strict strategy: {strict_result2[0]} - {strict_result2[1][:60]}...")
    print(f"Lenient strategy: {lenient_result2[0]} - {lenient_result2[1][:60]}...")

if __name__ == "__main__":
    test_lenient_strategy()

