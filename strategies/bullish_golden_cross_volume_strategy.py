"""
Bullish Golden Cross Volume Strategy
A strategy that identifies bullish golden cross opportunities with volume confirmation.
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


class BullishGoldenCrossVolumeStrategy(BaseStrategy):
    """
    Bullish Golden Cross Volume Strategy
    Identifies bullish golden cross opportunities with volume confirmation.
    """

    def __init__(
        self, name: str = "趋势-多头金叉放量策略", params: Optional[Dict] = None
    ):
        """
        Initialize the Bullish Golden Cross Volume strategy.

        Args:
            name: Strategy name
            params: Strategy parameters
                - ma_fast: Fast moving average period (default: 5)
                - ma_mid: Middle moving average period (default: 10)
                - ma_slow: Slow moving average period (default: 20)
                - volume_ma_period: Volume moving average period (default: 5)
                - volume_multiplier: Volume multiplier (default: 1.5)
        """
        # Handle parameter name mapping from database storage format to strategy format
        if params:
            mapped_params = params.copy()

            # Map database parameter names to strategy parameter names
            if "ma_fast" in mapped_params and "ma_fast" not in mapped_params:
                mapped_params["ma_fast"] = int(mapped_params["ma_fast"])
            if "ma_mid" in mapped_params and "ma_mid" not in mapped_params:
                mapped_params["ma_mid"] = int(mapped_params["ma_mid"])
            if "ma_slow" in mapped_params and "ma_slow" not in mapped_params:
                mapped_params["ma_slow"] = int(mapped_params["ma_slow"])
            if (
                "volume_ma_period" in mapped_params
                and "volume_ma_period" not in mapped_params
            ):
                mapped_params["volume_ma_period"] = int(
                    mapped_params["volume_ma_period"]
                )
            if (
                "volume_multiplier" in mapped_params
                and "volume_multiplier" not in mapped_params
            ):
                mapped_params["volume_multiplier"] = float(
                    mapped_params["volume_multiplier"]
                )

            # Ensure existing parameters are correct types
            if "ma_fast" in mapped_params:
                mapped_params["ma_fast"] = int(mapped_params["ma_fast"])
            if "ma_mid" in mapped_params:
                mapped_params["ma_mid"] = int(mapped_params["ma_mid"])
            if "ma_slow" in mapped_params:
                mapped_params["ma_slow"] = int(mapped_params["ma_slow"])
            if "volume_ma_period" in mapped_params:
                mapped_params["volume_ma_period"] = int(
                    mapped_params["volume_ma_period"]
                )
            if "volume_multiplier" in mapped_params:
                mapped_params["volume_multiplier"] = float(
                    mapped_params["volume_multiplier"]
                )

            params = mapped_params

        super().__init__(name, params or {})

        # Strategy parameters
        self.ma_fast = self.params.get("ma_fast", 5)
        self.ma_mid = self.params.get("ma_mid", 13)
        self.ma_slow = self.params.get("ma_slow", 34)
        self.volume_ma_period = self.params.get("volume_ma_period", 5)
        self.volume_multiplier = self.params.get("volume_multiplier", 1.5)

        self.logger.info(
            f"Initialized {self.name} strategy with params: "
            f"ma_fast={self.ma_fast}, ma_mid={self.ma_mid}, ma_slow={self.ma_slow}, "
            f"volume_ma_period={self.volume_ma_period}, volume_multiplier={self.volume_multiplier}"
        )

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
                "golden_cross_signal": golden_cross_signal,
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
                        "golden_cross_signal": False,
                        "position": 0.0,
                    }
                ),
            )

        try:
            # Get required data points
            required_data = max(
                self.ma_fast,
                self.ma_mid,
                self.ma_slow,
                self.volume_ma_period,
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
                            "golden_cross_signal": False,
                            "position": 0.0,
                        }
                    ),
                )

            # Convert pandas Series to numpy array for TA-Lib
            close_prices = np.array(data["close"].values, dtype=np.float64)
            volume_data = np.array(data["volume"].values, dtype=np.float64)

            # Calculate moving averages
            ma_fast = talib.SMA(close_prices, timeperiod=self.ma_fast)
            ma_mid = talib.SMA(close_prices, timeperiod=self.ma_mid)
            ma_slow = talib.SMA(close_prices, timeperiod=self.ma_slow)

            # Calculate volume moving average
            volume_ma = talib.SMA(volume_data, timeperiod=self.volume_ma_period)

            # Current values
            current_price = close_prices[-1]
            ma_fast_last = ma_fast[-1] if not np.isnan(ma_fast[-1]) else None
            ma_mid_last = ma_mid[-1] if not np.isnan(ma_mid[-1]) else None
            ma_slow_last = ma_slow[-1] if not np.isnan(ma_slow[-1]) else None
            current_volume = volume_data[-1] if not np.isnan(volume_data[-1]) else None
            avg_volume = volume_ma[-1] if not np.isnan(volume_ma[-1]) else None

            # Check if all values are valid
            if (
                ma_fast_last is None
                or ma_mid_last is None
                or ma_slow_last is None
                or current_volume is None
                or avg_volume is None
            ):
                return (
                    False,
                    0.0,
                    json.dumps(
                        {
                            "code": code or "",
                            "score": 0.0,
                            "selection_reason": "技术指标计算无效",
                            "technical_analysis": {},
                            "golden_cross_signal": False,
                            "position": 0.0,
                        }
                    ),
                )

            # Check golden cross conditions
            golden_cross_condition = self._detect_golden_cross(data)

            # Check volume condition
            volume_ratio = current_volume / avg_volume if avg_volume != 0 else 0
            volume_condition = volume_ratio >= self.volume_multiplier

            # Prepare selection reason
            reason = f"金叉放量启动信号: 收盘价={current_price:.2f}, MA{self.ma_fast}={ma_fast_last:.2f}, MA{self.ma_mid}={ma_mid_last:.2f}, MA{self.ma_slow}={ma_slow_last:.2f}, 成交量={current_volume:.0f}, 平均成交量={avg_volume:.0f}, 量比={volume_ratio:.2f}"
            if golden_cross_condition:
                reason += " (检测到金叉)"
            if volume_condition:
                reason += " (成交量放大)"

            # 核心条件：必须有金叉和成交量放大
            if not golden_cross_condition or not volume_condition:
                return (
                    False,
                    0.0,
                    json.dumps(
                        {
                            "code": code or "",
                            "score": 0.0,
                            "selection_reason": f"未满足金叉放量启动条件: 金叉={golden_cross_condition}, 成交量放大={volume_condition}",
                            "technical_analysis": {},
                            "golden_cross_signal": False,
                            "position": 0.0,
                        }
                    ),
                )

            # Calculate score
            score = self._calculate_score(
                ma_fast_last,
                ma_mid_last,
                ma_slow_last,
                volume_ratio,
                golden_cross_condition,
            )

            # Get technical analysis data
            technical_analysis = self.get_technical_analysis_data(data)

            # Calculate position size based on score
            position_size = 0.0
            if score >= 0.8:
                position_size = 1.0
            elif score >= 0.7:
                position_size = 0.7
            elif score >= 0.6:
                position_size = 0.4

            # Create value dictionary
            value = {
                "code": code or "",
                "score": score,
                "selection_reason": reason,
                "technical_analysis": technical_analysis,
                "golden_cross_signal": 1 if golden_cross_condition else 0,
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
                        "golden_cross_signal": False,
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
            volume_data = np.array(data["volume"].values, dtype=np.float64)

            # Calculate moving averages
            ma_fast = talib.SMA(close_prices, timeperiod=self.ma_fast)
            ma_mid = talib.SMA(close_prices, timeperiod=self.ma_mid)
            ma_slow = talib.SMA(close_prices, timeperiod=self.ma_slow)

            # Calculate volume moving average
            volume_ma = talib.SMA(volume_data, timeperiod=self.volume_ma_period)

            # Current values
            current_price = close_prices[-1]
            ma_fast_last = ma_fast[-1] if not np.isnan(ma_fast[-1]) else None
            ma_mid_last = ma_mid[-1] if not np.isnan(ma_mid[-1]) else None
            ma_slow_last = ma_slow[-1] if not np.isnan(ma_slow[-1]) else None
            current_volume = volume_data[-1] if not np.isnan(volume_data[-1]) else None
            avg_volume = volume_ma[-1] if not np.isnan(volume_ma[-1]) else None

            # Calculate volume ratio
            volume_ratio = (
                current_volume / avg_volume
                if avg_volume and avg_volume != 0 and current_volume is not None
                else 0
            )

            # Check golden cross conditions
            golden_cross_condition = self._detect_golden_cross(data)

            # Check bullish arrangement
            bullish_arrangement = (
                ma_fast_last > ma_mid_last and ma_mid_last > ma_slow_last
            )

            # Prepare technical analysis data
            technical_analysis_data = {
                "price": round(float(current_price), 2),
                "moving_averages": {
                    f"sma_{self.ma_fast}": round(float(ma_fast_last), 2)
                    if ma_fast_last is not None
                    else "N/A",
                    f"sma_{self.ma_mid}": round(float(ma_mid_last), 2)
                    if ma_mid_last is not None
                    else "N/A",
                    f"sma_{self.ma_slow}": round(float(ma_slow_last), 2)
                    if ma_slow_last is not None
                    else "N/A",
                },
                "volume": {
                    "current": round(float(current_volume), 2)
                    if current_volume is not None
                    else "N/A",
                    "average": round(float(avg_volume), 2)
                    if avg_volume is not None
                    else "N/A",
                    "ratio": round(float(volume_ratio), 2)
                    if volume_ratio is not None
                    else "N/A",
                },
                "golden_cross": bool(golden_cross_condition),
                "bullish_arrangement": bool(bullish_arrangement),
            }

            return technical_analysis_data
        except Exception as e:
            self.log_error(f"获取技术分析数据错误: {e}")
            return {}

    def _calculate_score(
        self,
        ma_fast,
        ma_mid,
        ma_slow,
        volume_ratio,
        golden_cross_condition,
    ):
        """
        Calculate golden cross volume startup signal strength score

        Score calculation formula:
        - If no golden cross: score = 0
        - If golden cross: score = 60 + 40 * min(2.0, (volume_ratio - 1)) / 1.0
        (金叉权重60%，成交量放大权重40%)
        """
        try:
            # If no golden cross, score is 0
            if not golden_cross_condition:
                return 0.0

            # Calculate volume amplification strength (0-40 points)
            volume_strength = 40 * min(2.0, (volume_ratio - 1)) / 1.0

            # Golden cross gives 60 points, volume gives up to 40 points
            score = 60 + volume_strength
            # Divide by 100 and round to 2 decimal places
            return round(score / 100, 2)
        except Exception as e:
            self.log_warning(f"评分计算错误: {e}")
            return 0

    def _detect_golden_cross(self, data: pd.DataFrame) -> bool:
        """
        Detect golden cross pattern (MA5 crosses above MA10 and MA10 crosses above MA20)
        Focus on detecting the startup signal when the cross happens

        Args:
            data: DataFrame with K-line data

        Returns:
            True if golden cross detected, False otherwise
        """
        if data.empty or len(data) < max(self.ma_fast, self.ma_mid, self.ma_slow):
            return False

        try:
            # Convert pandas Series to numpy array for TA-Lib
            close_prices = np.asarray(data["close"].values, dtype=np.float64)

            # Calculate moving averages
            ma_fast = talib.SMA(close_prices, timeperiod=self.ma_fast)
            ma_mid = talib.SMA(close_prices, timeperiod=self.ma_mid)
            ma_slow = talib.SMA(close_prices, timeperiod=self.ma_slow)

            # Check if we have enough data points
            if len(ma_fast) < 2 or len(ma_mid) < 2 or len(ma_slow) < 2:
                return False

            # Check for golden cross (fast MA crosses above middle MA)
            current_fast_above_mid = (
                ma_fast[-1] > ma_mid[-1]
                if not np.isnan(ma_fast[-1]) and not np.isnan(ma_mid[-1])
                else False
            )
            previous_fast_below_mid = (
                ma_fast[-2] <= ma_mid[-2]
                if not np.isnan(ma_fast[-2]) and not np.isnan(ma_mid[-2])
                else False
            )

            # Check for golden cross (middle MA crosses above slow MA)
            current_mid_above_slow = (
                ma_mid[-1] > ma_slow[-1]
                if not np.isnan(ma_mid[-1]) and not np.isnan(ma_slow[-1])
                else False
            )
            previous_mid_below_slow = (
                ma_mid[-2] <= ma_slow[-2]
                if not np.isnan(ma_mid[-2]) and not np.isnan(ma_slow[-2])
                else False
            )

            # Both conditions must be met for golden cross
            return (
                current_fast_above_mid
                and previous_fast_below_mid
                and current_mid_above_slow
                and previous_mid_below_slow
            )

        except Exception as e:
            self.log_warning(f"金叉检测错误: {e}")
            return False

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

                # Parse the value to extract reason and golden_cross_signal
                try:
                    value_data = json.loads(value)
                    reason = value_data.get("selection_reason", "")
                    golden_cross_signal = value_data.get("golden_cross_signal", False)
                except:
                    reason = ""
                    golden_cross_signal = False

                if meets_criteria:
                    # Add technical analysis data
                    technical_analysis = {}
                    if not data.empty:
                        close_prices = data["close"].values
                        volume_data = data["volume"].values

                        if len(close_prices) >= max(
                            self.ma_fast,
                            self.ma_mid,
                            self.ma_slow,
                            self.volume_ma_period,
                        ):
                            # Calculate technical indicators for analysis
                            ma_fast_val = np.mean(
                                np.array(
                                    close_prices[-self.ma_fast :],
                                    dtype=np.float64,
                                )
                            )
                            ma_mid_val = np.mean(
                                np.array(
                                    close_prices[-self.ma_mid :],
                                    dtype=np.float64,
                                )
                            )
                            ma_slow_val = np.mean(
                                np.array(
                                    close_prices[-self.ma_slow :],
                                    dtype=np.float64,
                                )
                            )
                            avg_volume = np.mean(
                                np.array(
                                    volume_data[-self.volume_ma_period :],
                                    dtype=np.float64,
                                )
                            )

                            technical_analysis = {
                                "price": float(close_prices[-1]),
                                "moving_averages": {
                                    f"sma_{self.ma_fast}": float(ma_fast_val),
                                    f"sma_{self.ma_mid}": float(ma_mid_val),
                                    f"sma_{self.ma_slow}": float(ma_slow_val),
                                },
                                "volume": {
                                    "current": float(volume_data[-1]),
                                    "average": float(avg_volume),
                                },
                            }

                    selected_stocks.append(
                        {
                            "code": code,
                            "score": score,
                            "selection_reason": reason,
                            "technical_analysis": technical_analysis,
                            "golden_cross_signal": golden_cross_signal,
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
                volume_data = np.array(data["volume"].values, dtype=np.float64)

                # Calculate moving averages
                ma_fast = talib.SMA(close_prices, timeperiod=self.ma_fast)
                ma_mid = talib.SMA(close_prices, timeperiod=self.ma_mid)
                ma_slow = talib.SMA(close_prices, timeperiod=self.ma_slow)

                # Calculate volume moving average
                volume_ma = talib.SMA(volume_data, timeperiod=self.volume_ma_period)

                # Calculate volume ratio
                volume_ratio = np.zeros(len(volume_data))
                for i in range(len(volume_data)):
                    if volume_ma[i] != 0 and not np.isnan(volume_ma[i]):
                        volume_ratio[i] = volume_data[i] / volume_ma[i]
                    else:
                        volume_ratio[i] = 0

                # Generate buy signals when all conditions are met:
                # 1. Golden cross detected
                # 2. Volume ratio >= multiplier
                for i in range(len(signals)):
                    # Check if we have valid data
                    if (
                        np.isnan(ma_fast[i])
                        or np.isnan(ma_mid[i])
                        or np.isnan(ma_slow[i])
                        or np.isnan(volume_ratio[i])
                    ):
                        continue

                    # Check golden cross
                    golden_cross_condition = False
                    if i >= 1:
                        current_fast_above_mid = ma_fast[i] > ma_mid[i]
                        previous_fast_below_mid = ma_fast[i - 1] <= ma_mid[i - 1]
                        current_mid_above_slow = ma_mid[i] > ma_slow[i]
                        previous_mid_below_slow = ma_mid[i - 1] <= ma_slow[i - 1]
                        golden_cross_condition = (
                            current_fast_above_mid
                            and previous_fast_below_mid
                            and current_mid_above_slow
                            and previous_mid_below_slow
                        )

                    # Check volume condition
                    volume_condition = volume_ratio[i] >= self.volume_multiplier

                    # Combined condition - only golden cross and volume
                    if golden_cross_condition and volume_condition:
                        signals.loc[signals.index[i], "signal"] = "BUY"
                        # Calculate position size based on score
                        score = self._calculate_score(
                            ma_fast[i],
                            ma_mid[i],
                            ma_slow[i],
                            volume_ratio[i],
                            golden_cross_condition,
                        )
                        # Position size based on score thresholds
                        if score >= 80:
                            position_size = 1.0
                        elif score >= 70:
                            position_size = 0.7
                        elif score >= 60:
                            position_size = 0.4
                        else:
                            position_size = 0.0
                        signals.loc[signals.index[i], "position"] = position_size

            except Exception as e:
                self.log_warning(f"生成信号时出错: {e}")

        return signals

    def calculate_position_size(
        self, signal: str, portfolio_value: float, price: float
    ) -> float:
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
    dates = pd.date_range("2023-01-01", periods=100, freq="D")
    sample_data = pd.DataFrame(
        {
            "date": dates,
            "open": np.random.uniform(100, 110, 100),
            "high": np.random.uniform(110, 120, 100),
            "low": np.random.uniform(90, 100, 100),
            "close": np.random.uniform(100, 110, 100),
            "volume": np.random.uniform(1000000, 2000000, 100),
        }
    )

    # Initialize strategy
    strategy = BullishGoldenCrossVolumeStrategy()

    # Generate signals
    signals = strategy.generate_signals(sample_data)
    print(f"Generated {len(signals[signals['signal'] != 'HOLD'])} trading signals")
    print(signals.tail(10))
