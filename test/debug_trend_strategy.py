#!/usr/bin/env python3
"""
Test script to debug the trend following strategy and see why no stocks are selected.
"""

import sys
import os
import pandas as pd
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from utils.akshare_client import AkshareClient

def debug_trend_strategy():
    """Debug the trend following strategy to see why no stocks are selected"""
    try:
        # Initialize components
        db_manager = MongoDBManager()
        data_fetcher = AkshareClient()

        # Get a sample stock to test
        all_codes = db_manager.get_stock_codes()
        if not all_codes:
            all_codes = data_fetcher.get_stock_list()

        if not all_codes:
            print("No stock codes found!")
            return False

        # Test with first few stocks
        test_codes = all_codes[:5]
        print(f"Testing with stocks: {test_codes}")

        # Get strategy parameters
        strategies = db_manager.get_strategies()
        trend_strategy = None
        for strategy in strategies:
            if "趋势跟踪策略（稳健型）" in strategy.get('name', ''):
                trend_strategy = strategy
                break

        if not trend_strategy:
            print("Trend Following Strategy not found!")
            return False

        params = trend_strategy.get('parameters', {})
        fast_period = int(params.get('ma_fast', 5))
        slow_period = int(params.get('ma_slow', 13))
        macd_fast = int(params.get('macd_fast', 12))
        macd_slow = int(params.get('macd_slow', 26))
        macd_signal = int(params.get('macd_signal', 9))
        new_high_period = int(params.get('new_high_period', 20))

        print(f"\nStrategy Parameters:")
        print(f"  MA Fast: {fast_period}")
        print(f"  MA Slow: {slow_period}")
        print(f"  MACD Fast: {macd_fast}")
        print(f"  MACD Slow: {macd_slow}")
        print(f"  MACD Signal: {macd_signal}")
        print(f"  New High Period: {new_high_period}")

        # Calculate date range (1 year of data)
        from datetime import datetime, timedelta
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d')

        for code in test_codes:
            print(f"\n--- Testing Stock {code} ---")

            # Get adjusted daily K-line data
            daily_k_data = db_manager.get_adjusted_k_data(code, start_date, end_date, frequency='daily')

            # If no data in DB, fetch from data source
            if daily_k_data.empty:
                daily_k_data = data_fetcher.get_daily_k_data(code, start_date, end_date)

            if daily_k_data.empty:
                print(f"No data for {code}")
                continue

            # Convert to weekly data
            weekly_data = convert_daily_to_weekly(daily_k_data)
            if weekly_data.empty:
                print(f"No weekly data for {code}")
                continue

            print(f"Got {len(weekly_data)} weeks of data")

            # Apply the trend following strategy logic
            result = analyze_stock(weekly_data, fast_period, slow_period, macd_fast, macd_slow, macd_signal, new_high_period)
            meets_criteria, reason, score, golden_cross = result

            print(f"Meets criteria: {meets_criteria}")
            print(f"Reason: {reason}")
            print(f"Score: {score}")
            print(f"Golden Cross: {golden_cross}")

            # Show some data points
            if len(weekly_data) > 0:
                last_row = weekly_data.iloc[-1]
                print(f"Last price: {last_row['close']}")

        return True

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            db_manager.close_connection()
        except:
            pass

def convert_daily_to_weekly(daily_data):
    """Convert daily K-line data to weekly K-line data"""
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
        print(f"Error converting daily to weekly data: {e}")
        return pd.DataFrame()

def analyze_stock(data, fast_period, slow_period, macd_fast, macd_slow, macd_signal, new_high_period):
    """Apply trend following strategy logic to a stock"""
    if data.empty:
        return False, "数据为空", None, False

    try:
        # Get required data points
        required_data = max(fast_period, slow_period, macd_fast, macd_slow, macd_signal, new_high_period)
        if len(data) < required_data:
            return False, f"数据不足，需要{required_data}条数据", None, False

        # Convert pandas Series to numpy array for TA-Lib
        close_prices = np.array(data["close"].values, dtype=np.float64)
        high_prices = np.array(data["high"].values, dtype=np.float64)

        # Calculate moving averages
        import talib
        ma_fast = talib.SMA(close_prices, timeperiod=fast_period)
        ma_slow = talib.SMA(close_prices, timeperiod=slow_period)

        # Calculate MACD
        macd_dif, macd_dea, macd_histogram = talib.MACD(
            close_prices,
            fastperiod=macd_fast,
            slowperiod=macd_slow,
            signalperiod=macd_signal
        )

        # Current values
        current_price = close_prices[-1]
        ma_fast_last = ma_fast[-1] if not np.isnan(ma_fast[-1]) else None
        ma_slow_last = ma_slow[-1] if not np.isnan(ma_slow[-1]) else None
        macd_dif_last = macd_dif[-1] if not np.isnan(macd_dif[-1]) else None
        macd_dea_last = macd_dea[-1] if not np.isnan(macd_dea[-1]) else None
        macd_histogram_last = macd_histogram[-1] if not np.isnan(macd_histogram[-1]) else None

        # Check if all values are valid
        if (ma_fast_last is None or ma_slow_last is None or
            macd_dif_last is None or macd_dea_last is None or macd_histogram_last is None):
            return False, "技术指标计算无效", None, False

        # Check basic conditions: MA5 > MA13 && DIF > DEA && 价格创20周期新高
        ma_condition = ma_fast_last > ma_slow_last
        macd_condition = macd_dif_last > macd_dea_last

        # Calculate historical high
        historical_high = np.max(high_prices[-new_high_period:]) if len(high_prices) >= new_high_period else None
        breakout_condition = historical_high is not None and current_price > historical_high

        # Combined basic condition
        basic_condition = ma_condition and macd_condition and breakout_condition

        print(f"  MA Condition (MA{fast_period} > MA{slow_period}): {ma_fast_last:.2f} > {ma_slow_last:.2f} = {ma_condition}")
        print(f"  MACD Condition (DIF > DEA): {macd_dif_last:.4f} > {macd_dea_last:.4f} = {macd_condition}")
        print(f"  Breakout Condition (Price > High): {current_price:.2f} > {historical_high:.2f} = {breakout_condition}")

        if not basic_condition:
            reason = "不满足基础条件: "
            if not ma_condition:
                reason += f"MA{fast_period}({ma_fast_last:.2f}) <= MA{slow_period}({ma_slow_last:.2f})"
            if not macd_condition:
                if not ma_condition:
                    reason += "; "
                reason += f"DIF({macd_dif_last:.4f}) <= DEA({macd_dea_last:.4f})"
            if not breakout_condition:
                if not ma_condition or not macd_condition:
                    reason += "; "
                reason += f"价格({current_price:.2f})未创{new_high_period}周期新高({historical_high:.2f})"
            return False, reason, None, False

        # Calculate score according to the documented formula
        score = calculate_score(
            ma_fast_last, ma_slow_last,
            macd_dif_last, macd_dea_last,
            current_price, historical_high
        )

        print(f"  Score: {score:.2f}")

        # Check strength confirmation (score > 0)
        if score <= 0:
            return False, f"趋势强度不足，得分{score:.2f} <= 0", score, False

        # Check for golden cross pattern (MA5 crosses above MA13 and MACD DIF crosses above DEA)
        golden_cross_condition = False  # Simplified for debugging

        reason = (f"满足趋势跟踪条件: MA{fast_period}({ma_fast_last:.2f}) > MA{slow_period}({ma_slow_last:.2f}), "
                 f"DIF({macd_dif_last:.4f}) > DEA({macd_dea_last:.4f}), "
                 f"价格({current_price:.2f})创{new_high_period}周期新高({historical_high:.2f}), "
                 f"趋势强度得分{score:.2f}")

        if golden_cross_condition:
            reason += " (检测到金叉)"

        return True, reason, score, golden_cross_condition

    except Exception as e:
        return False, f"分析错误: {e}", None, False

def calculate_score(ma_fast, ma_slow, macd_dif, macd_dea, price, historical_high):
    """Calculate trend strength score based on documented formula"""
    try:
        # First term: Moving average arrangement strength (40%)
        term1 = 40 * (ma_fast - ma_slow) / ma_slow if ma_slow != 0 else 0

        # Second term: MACD momentum (30%)
        term2 = 30 * (macd_dif - macd_dea) / abs(macd_dea) if macd_dea != 0 else 0

        # Third term: Above zero axis bonus (20%)
        term3 = 20 * max(0, macd_dif) / max(0.01, abs(macd_dif)) if macd_dif != 0 else 0

        # Fourth term: Breakout strength (10%)
        term4 = 10 * (price - historical_high) / historical_high if historical_high != 0 else 0

        score = max(0, min(100, term1 + term2 + term3 + term4))
        return score
    except Exception as e:
        return 0

if __name__ == "__main__":
    success = debug_trend_strategy()
    if not success:
        sys.exit(1)

