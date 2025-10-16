"""
Pullback Buying Strategy
A strategy that identifies pullback opportunities in uptrends for buying.
"""

import pandas as pd
import numpy as np
import talib
import json
from typing import Dict, Tuple, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategies.base_strategy import BaseStrategy


class PullbackBuyingStrategy(BaseStrategy):
    """
    Pullback Buying Strategy
    Identifies pullback opportunities in uptrends for buying.
    """

    def __init__(self, name: str = "回踩低吸型策略", params: Optional[Dict] = None):
        """
        Initialize the Pullback Buying strategy.

        Args:
            name: Strategy name
            params: Strategy parameters
                - ma_period: Trend moving average period (default: 13)
                - kdj_n: KDJ N period (default: 9)
                - rsi_period: RSI period (default: 14)
                - oversold_threshold: Oversold threshold (default: 30)
                - support_band_pct: Support band percentage (default: 0.03)
        """
        # Handle parameter name mapping from database storage format to strategy format
        if params:
            mapped_params = params.copy()

            # Map database parameter names to strategy parameter names
            if "ma_period" in mapped_params and "ma_period" not in mapped_params:
                mapped_params["ma_period"] = int(mapped_params["ma_period"])
            if "kdj_n" in mapped_params and "kdj_n" not in mapped_params:
                mapped_params["kdj_n"] = int(mapped_params["kdj_n"])
            if "rsi_period" in mapped_params and "rsi_period" not in mapped_params:
                mapped_params["rsi_period"] = int(mapped_params["rsi_period"])
            if "oversold_threshold" in mapped_params and "oversold_threshold" not in mapped_params:
                mapped_params["oversold_threshold"] = int(mapped_params["oversold_threshold"])
            if "support_band_pct" in mapped_params and "support_band_pct" not in mapped_params:
                mapped_params["support_band_pct"] = float(mapped_params["support_band_pct"])

            # Ensure existing parameters are correct types
            if "ma_period" in mapped_params:
                mapped_params["ma_period"] = int(mapped_params["ma_period"])
            if "kdj_n" in mapped_params:
                mapped_params["kdj_n"] = int(mapped_params["kdj_n"])
            if "rsi_period" in mapped_params:
                mapped_params["rsi_period"] = int(mapped_params["rsi_period"])
            if "oversold_threshold" in mapped_params:
                mapped_params["oversold_threshold"] = int(mapped_params["oversold_threshold"])
            if "support_band_pct" in mapped_params:
                mapped_params["support_band_pct"] = float(mapped_params["support_band_pct"])

            params = mapped_params

        super().__init__(name, params or {})

        # Strategy parameters
        self.ma_period = self.params.get('ma_period', 13)
        self.kdj_n = self.params.get('kdj_n', 9)
        self.rsi_period = self.params.get('rsi_period', 14)
        self.oversold_threshold = self.params.get('oversold_threshold', 30)
        self.support_band_pct = self.params.get('support_band_pct', 0.03)

        self.logger.info(f"Initialized {self.name} strategy with params: "
                        f"ma_period={self.ma_period}, kdj_n={self.kdj_n}, "
                        f"rsi_period={self.rsi_period}, oversold_threshold={self.oversold_threshold}, "
                        f"support_band_pct={self.support_band_pct}")

    def analyze(self, data: pd.DataFrame, code: str = None) -> Tuple[bool, float, str]:
        """
        Analyze stock data and determine if it meets selection criteria

        Args:
            data: DataFrame with stock data including OHLCV columns
            code: Stock code (optional)

        Returns:
            Tuple of (meets_criteria, score, value)
            value contains JSON string with: {
                "code": code,
                "score": score,
                "selection_reason": reason,
                "technical_analysis": technical_analysis,
                "pullback_signal": pullback_signal,
                "position": position_size
            }
        """

        if data.empty:
            return (
                False,
                0.0,
                json.dumps(
                    {
                        "code": code or "",
                        "score": 0.0,
                        "selection_reason": "数据为空",
                        "technical_analysis": {},
                        "pullback_signal": False,
                        "position": 0.0,
                    }
                ),
            )

        try:
            # Get required data points
            required_data = max(
                self.ma_period, self.kdj_n, self.rsi_period
            )
            if len(data) < required_data:
                return (
                    False,
                    0.0,
                    json.dumps(
                        {
                            "code": code or "",
                            "score": 0.0,
                            "selection_reason": f"数据不足，需要{required_data}条数据",
                            "technical_analysis": {},
                            "pullback_signal": False,
                            "position": 0.0,
                        }
                    ),
                )

            # Convert pandas Series to numpy array for TA-Lib
            close_prices = np.array(data["close"].values, dtype=np.float64)
            high_prices = np.array(data["high"].values, dtype=np.float64)
            low_prices = np.array(data["low"].values, dtype=np.float64)

            # Calculate moving average
            ma_values = talib.SMA(close_prices, timeperiod=self.ma_period)

            # Calculate KDJ
            kdj_k, kdj_d = talib.STOCH(
                high_prices, low_prices, close_prices,
                fastk_period=self.kdj_n, slowk_period=3, slowd_period=3
            )
            # Calculate J value: J = 3*K - 2*D
            kdj_j = 3 * kdj_k - 2 * kdj_d

            # Calculate RSI
            rsi_values = talib.RSI(close_prices, timeperiod=self.rsi_period)

            # Current values
            current_price = close_prices[-1]
            ma_value = ma_values[-1] if not np.isnan(ma_values[-1]) else None
            kdj_j_value = kdj_j[-1] if not np.isnan(kdj_j[-1]) else None
            rsi_value = rsi_values[-1] if not np.isnan(rsi_values[-1]) else None

            # Check if all values are valid
            if (ma_value is None or kdj_j_value is None or rsi_value is None):
                return (
                    False,
                    0.0,
                    json.dumps(
                        {
                            "code": code or "",
                            "score": 0.0,
                            "selection_reason": "技术指标计算无效",
                            "technical_analysis": {},
                            "pullback_signal": False,
                            "position": 0.0,
                        }
                    ),
                )

            # Calculate MA trend (1: upward, 0: flat, -1: downward)
            ma_trend = self._calculate_ma_trend(ma_values)

            # Check pullback conditions
            is_valid_pullback = self._is_valid_pullback(
                current_price, ma_value, kdj_j_value, rsi_value, ma_trend
            )

            # Prepare selection reason
            reason = f"回踩低吸条件: 收盘价={current_price:.2f}, 均线值={ma_value:.2f}, KDJ_J={kdj_j_value:.2f}, RSI={rsi_value:.2f}"
            if is_valid_pullback:
                reason += " (满足有效回踩)"

            # Calculate score using the documented formula
            score = self._calculate_score(
                current_price, ma_value, kdj_j_value, rsi_value
            )
            score = round(score, 2)

            # Get technical analysis data
            technical_analysis = self.get_technical_analysis_data(data)

            # Calculate position size based on score
            position_size = 0.0
            if score >= 0.8:
                position_size = 0.8
            elif score >= 0.7:
                position_size = 0.6
            elif score >= 0.6:
                position_size = 0.4

            # Create value dictionary
            value = {
                "code": code or "",
                "score": score,
                "selection_reason": reason,
                "technical_analysis": technical_analysis,
                "pullback_signal": 1 if is_valid_pullback else 0,
                "position": position_size,
            }

            # Check strength confirmation (score > 0.6)
            if score <= 0.6:
                return False, score, json.dumps(value)

            return True, score, json.dumps(value)

        except Exception as e:
            self.log_error(f"分析错误: {e}")
            return (
                False,
                0.0,
                json.dumps(
                    {
                        "code": code or "",
                        "score": 0.0,
                        "selection_reason": f"分析错误: {e}",
                        "technical_analysis": {},
                        "pullback_signal": False,
                        "position": 0.0,
                    }
                ),
            )

    def get_technical_analysis_data(self, data: pd.DataFrame) -> Dict:
        """
        获取技术分析数据供格式化使用

        Args:
            data: DataFrame with stock data including OHLCV columns

        Returns:
            Dict containing technical analysis data
        """
        if data.empty:
            return {}

        try:
            # Convert pandas Series to numpy array for TA-Lib
            close_prices = np.array(data["close"].values, dtype=np.float64)
            high_prices = np.array(data["high"].values, dtype=np.float64)
            low_prices = np.array(data["low"].values, dtype=np.float64)

            # Calculate moving average
            ma_values = talib.SMA(close_prices, timeperiod=self.ma_period)

            # Calculate KDJ
            kdj_k, kdj_d = talib.STOCH(
                high_prices, low_prices, close_prices,
                fastk_period=self.kdj_n, slowk_period=3, slowd_period=3
            )
            # Calculate J value: J = 3*K - 2*D
            kdj_j = 3 * kdj_k - 2 * kdj_d

            # Calculate RSI
            rsi_values = talib.RSI(close_prices, timeperiod=self.rsi_period)

            # Current values
            current_price = close_prices[-1]
            ma_value = ma_values[-1] if not np.isnan(ma_values[-1]) else None
            kdj_j_value = kdj_j[-1] if not np.isnan(kdj_j[-1]) else None
            rsi_value = rsi_values[-1] if not np.isnan(rsi_values[-1]) else None

            # Calculate MA trend (1: upward, 0: flat, -1: downward)
            ma_trend = self._calculate_ma_trend(ma_values)

            # Check pullback conditions
            is_valid_pullback = self._is_valid_pullback(
                current_price, ma_value, kdj_j_value, rsi_value, ma_trend
            )

            # Prepare technical analysis data in a format specific to Pullback Buying strategy
            technical_analysis_data = {
                'price': round(float(current_price), 2),
                'ma_value': round(float(ma_value), 2) if ma_value is not None else 'N/A',
                'ma_trend': int(ma_trend),
                'kdj_j': round(float(kdj_j_value), 2) if kdj_j_value is not None else 'N/A',
                'rsi_value': round(float(rsi_value), 2) if rsi_value is not None else 'N/A',
                'is_valid_pullback': bool(is_valid_pullback)
            }

            return technical_analysis_data
        except Exception as e:
            self.log_error(f"获取技术分析数据错误: {e}")
            return {}

    def _calculate_ma_trend(self, ma_values):
        """
        Calculate moving average trend direction

        Args:
            ma_values: Array of moving average values

        Returns:
            Trend direction (1: upward, 0: flat, -1: downward)
        """
        if ma_values is None or len(ma_values) < 3:
            return 0

        # Check last 3 values to determine trend
        last_values = ma_values[-3:]

        # Check for None values in the last 3 values
        if any(v is None for v in last_values):
            return 0

        # Check for NaN values in the last 3 values
        try:
            if np.isnan(last_values).any():
                return 0
        except (TypeError, ValueError):
            # If numpy can't handle the data type, return flat trend
            return 0

        # Calculate differences
        diff1 = last_values[2] - last_values[1]  # Most recent difference
        diff2 = last_values[1] - last_values[0]  # Previous difference

        # If both differences are positive, trend is upward
        if diff1 > 0 and diff2 > 0:
            return 1
        # If both differences are negative, trend is downward
        elif diff1 < 0 and diff2 < 0:
            return -1
        # Otherwise, trend is flat
        else:
            return 0

    def _is_valid_pullback(self, close, ma_value, kdj_j, rsi_value, ma_trend):
        """
        Determine if it's a valid pullback

        Args:
            close: Current closing price
            ma_value: Moving average value
            kdj_j: KDJ J value
            rsi_value: RSI value
            ma_trend: Moving average trend direction

        Returns:
            True if valid pullback, False otherwise
        """
        # Check if any required values are None
        if ma_value is None or kdj_j is None or rsi_value is None:
            return False

        # Check if ma_value is zero to avoid division by zero
        if ma_value == 0:
            return False

        # Basic conditions
        price_condition = abs(close - ma_value) / ma_value <= self.support_band_pct  # Price within ±3% of MA
        oversold_condition = (kdj_j < 20) or (rsi_value < 30)  # Oversold state
        trend_condition = ma_trend > 0  # Trend upward

        return price_condition and oversold_condition and trend_condition

    def _calculate_score(self, close, ma_value, kdj_j, rsi_value):
        """
        Calculate pullback opportunity score based on documented formula

        Score calculation formula:
        score = max(
            0,
            min(
                100,
                40 * max(0, (oversold_threshold - kdj_j)) / oversold_threshold  # KDJ oversold degree
              + 30 * max(0, (oversold_threshold - rsi_value)) / oversold_threshold  # RSI oversold degree
              + 30 * max(0, (ma_value - close)) / ma_value  # Pullback depth
            )
        )
        """
        try:
            # Check if any required values are None
            if ma_value is None or kdj_j is None or rsi_value is None:
                return 0

            # Check if ma_value is zero to avoid division by zero
            if ma_value == 0:
                return 0

            # First term: KDJ oversold degree (40%)
            term1 = 40 * max(0, (self.oversold_threshold - kdj_j)) / self.oversold_threshold

            # Second term: RSI oversold degree (30%)
            term2 = 30 * max(0, (self.oversold_threshold - rsi_value)) / self.oversold_threshold

            # Third term: Pullback depth (30%)
            term3 = 30 * max(0, (ma_value - close)) / ma_value

            score = max(0, min(100, term1 + term2 + term3))
            # Divide by 100 and round to 2 decimal places
            return round(score / 100, 2)
        except Exception as e:
            self.log_warning(f"评分计算错误: {e}")
            return 0

    def execute(
        self, stock_data: Dict[str, pd.DataFrame], agent_name: str, db_manager
    ) -> list[Dict]:
        """
        Execute the strategy on provided stock data and automatically save results

        Args:
            stock_data: Dictionary mapping stock codes to their data DataFrames
            agent_name: Name of the agent executing this strategy
            db_manager: Database manager instance

        Returns:
            List of selected stocks with analysis results
        """
        self.log_info(f"执行 {self.name} 策略，处理 {len(stock_data)} 只股票")

        selected_stocks = []

        # Analyze each stock
        for code, data in stock_data.items():
            try:
                meets_criteria, score, value = self.analyze(data, code)

                # Parse the value to extract reason and pullback_signal
                try:
                    value_data = json.loads(value)
                    reason = value_data.get("selection_reason", "")
                    pullback_signal = value_data.get("pullback_signal", False)
                except:
                    reason = ""
                    pullback_signal = False

                if meets_criteria:
                    # Add technical analysis data
                    technical_analysis = {}
                    if not data.empty:
                        close_prices = data["close"].values

                        if len(close_prices) >= max(
                            self.ma_period, self.kdj_n, self.rsi_period
                        ):
                            # Calculate technical indicators for analysis
                            ma_values = talib.SMA(close_prices, timeperiod=self.ma_period)
                            ma_value = ma_values[-1] if not np.isnan(ma_values[-1]) else 0

                            technical_analysis = {
                                "price": float(close_prices[-1]),
                                "ma_value": float(ma_value),
                                # "score": score,
                                # "pullback_signal": pullback_signal,
                            }

                    selected_stocks.append(
                        {
                            "code": code,
                            "score": score,
                            "selection_reason": reason,
                            "technical_analysis": technical_analysis,
                            "pullback_signal": pullback_signal,
                            "position": value_data.get("position", 0.0),
                        }
                    )

            except Exception as e:
                self.log_warning(f"处理股票 {code} 时出错: {e}")
                continue

        self.log_info(f"选中 {len(selected_stocks)} 只股票")

        # Automatically save results to pool collection
        if selected_stocks:
            from datetime import datetime

            current_date = datetime.now().strftime("%Y-%m-%d")

            save_success = self.save_to_pool(
                db_manager=db_manager,
                agent_name=agent_name,
                stocks=selected_stocks,
                date=current_date,
                strategy_params=self.params,
                additional_metadata={
                    "strategy_version": "1.0",
                    "total_stocks_analyzed": len(stock_data),
                },
            )

            if save_success:
                self.log_info("策略结果已自动保存到池中")
            else:
                self.log_error("保存策略结果到池中失败")

        return selected_stocks

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on input data.

        Args:
            data: Input data DataFrame with required columns

        Returns:
            DataFrame with signals
        """
        signals = pd.DataFrame(index=data.index)
        signals["signal"] = "HOLD"
        signals["position"] = 0.0

        if not data.empty:
            try:
                # Convert pandas Series to numpy array for TA-Lib
                close_prices = np.array(data["close"].values, dtype=np.float64)
                high_prices = np.array(data["high"].values, dtype=np.float64)
                low_prices = np.array(data["low"].values, dtype=np.float64)

                # Calculate moving average
                ma_values = talib.SMA(close_prices, timeperiod=self.ma_period)

                # Calculate KDJ
                kdj_k, kdj_d = talib.STOCH(
                    high_prices, low_prices, close_prices,
                    fastk_period=self.kdj_n, slowk_period=3, slowd_period=3
                )
                # Calculate J value: J = 3*K - 2*D
                kdj_j = 3 * kdj_k - 2 * kdj_d

                # Calculate RSI
                rsi_values = talib.RSI(close_prices, timeperiod=self.rsi_period)

                # Calculate MA trend for each point
                ma_trends = np.zeros(len(ma_values))
                for i in range(2, len(ma_values)):
                    if not np.isnan(ma_values[i]) and not np.isnan(ma_values[i-1]) and not np.isnan(ma_values[i-2]):
                        diff1 = ma_values[i] - ma_values[i-1]
                        diff2 = ma_values[i-1] - ma_values[i-2]
                        if diff1 > 0 and diff2 > 0:
                            ma_trends[i] = 1
                        elif diff1 < 0 and diff2 < 0:
                            ma_trends[i] = -1
                        else:
                            ma_trends[i] = 0
                    else:
                        ma_trends[i] = 0

                # Generate buy signals when all conditions are met:
                # 1. Valid pullback conditions
                # 2. Score > 60
                for i in range(len(signals)):
                    # Check if we have valid data
                    if (np.isnan(ma_values[i]) or np.isnan(kdj_j[i]) or np.isnan(rsi_values[i])):
                        continue

                    # Check pullback conditions
                    is_valid_pullback = self._is_valid_pullback(
                        close_prices[i], ma_values[i], kdj_j[i], rsi_values[i], ma_trends[i]
                    )

                    if is_valid_pullback:
                        # Calculate position size based on score
                        score = self._calculate_score(
                            close_prices[i], ma_values[i], kdj_j[i], rsi_values[i]
                        )
                        # Position size based on score thresholds
                        if score >= 80:
                            position_size = 0.8
                        elif score >= 70:
                            position_size = 0.6
                        elif score >= 60:
                            position_size = 0.4
                        else:
                            position_size = 0.0

                        if position_size > 0:
                            signals.loc[signals.index[i], "signal"] = "BUY"
                            signals.loc[signals.index[i], "position"] = round(position_size, 2)

            except Exception as e:
                self.log_warning(f"生成信号时出错: {e}")

        return signals

    def calculate_position_size(self, signal: str, portfolio_value: float,
                              price: float) -> float:
        """
        Calculate position size based on signal and portfolio value.

        Args:
            signal: Trading signal ('BUY', 'SELL', 'HOLD')
            portfolio_value: Current portfolio value
            price: Current asset price

        Returns:
            Position size (number of shares/contracts)
        """
        if signal == "BUY":
            # Calculate position size based on score
            # In a real implementation, this would use the actual score from analysis
            # For now, we'll use a default allocation
            position_ratio = 0.1  # Default 10% of portfolio
            position_value = portfolio_value * position_ratio
            shares = position_value / price

            # Round to nearest 100 shares (common in Chinese market)
            shares = round(shares / 100) * 100
            return float(shares)
        elif signal == "SELL":
            return -100.0  # Sell 100 shares
        else:
            return 0.0  # Hold position

# Example usage
if __name__ == "__main__":
    import logging

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create sample data
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    sample_data = pd.DataFrame({
        'date': dates,
        'open': np.random.uniform(100, 110, 100),
        'high': np.random.uniform(110, 120, 100),
        'low': np.random.uniform(90, 100, 100),
        'close': np.random.uniform(100, 110, 100),
        'volume': np.random.uniform(1000000, 2000000, 100)
    })

    # Initialize strategy
    strategy = PullbackBuyingStrategy()

    # Generate signals
    signals = strategy.generate_signals(sample_data)
    print(f"Generated {len(signals[signals['signal'] != 'HOLD'])} trading signals")
    print(signals.tail(10))

