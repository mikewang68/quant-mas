"""
Trend Following Strategy
A strategy that generates buy/sell signals based on trend following principles.
"""

import pandas as pd
import numpy as np
import talib
from typing import List, Dict, Tuple, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategies.base_strategy import BaseStrategy

class TrendFollowingStrategy(BaseStrategy):
    """
    Trend Following Strategy
    Utilizes moving average bullish arrangement, MACD momentum, and price breakout
    to identify robust trending upward market conditions.
    """

    def __init__(self, name: str = "趋势跟踪策略", params: Optional[Dict] = None):
        """
        Initialize the Trend Following strategy.

        Args:
            name: Strategy name
            params: Strategy parameters
                - ma_fast: Fast moving average period (default: 5)
                - ma_slow: Slow moving average period (default: 13)
                - macd_fast: MACD fast period (default: 12)
                - macd_slow: MACD slow period (default: 26)
                - macd_signal: MACD signal period (default: 9)
                - new_high_period: New high period (default: 20)
        """
        # Handle parameter name mapping from database storage format to strategy format
        if params:
            mapped_params = params.copy()

            # Map database parameter names to strategy parameter names
            if "ma_fast" in mapped_params and "fast" not in mapped_params:
                mapped_params["fast"] = int(mapped_params["ma_fast"])
            if "ma_slow" in mapped_params and "slow" not in mapped_params:
                mapped_params["slow"] = int(mapped_params["ma_slow"])
            if "macd_fast" in mapped_params and "macd_fast" not in mapped_params:
                mapped_params["macd_fast"] = int(mapped_params["macd_fast"])
            if "macd_slow" in mapped_params and "macd_slow" not in mapped_params:
                mapped_params["macd_slow"] = int(mapped_params["macd_slow"])
            if "macd_signal" in mapped_params and "macd_signal" not in mapped_params:
                mapped_params["macd_signal"] = int(mapped_params["macd_signal"])
            if "new_high_period" in mapped_params and "new_high_period" not in mapped_params:
                mapped_params["new_high_period"] = int(mapped_params["new_high_period"])

            # Ensure existing parameters are integers where needed
            if "fast" in mapped_params:
                mapped_params["fast"] = int(mapped_params["fast"])
            if "slow" in mapped_params:
                mapped_params["slow"] = int(mapped_params["slow"])
            if "macd_fast" in mapped_params:
                mapped_params["macd_fast"] = int(mapped_params["macd_fast"])
            if "macd_slow" in mapped_params:
                mapped_params["macd_slow"] = int(mapped_params["macd_slow"])
            if "macd_signal" in mapped_params:
                mapped_params["macd_signal"] = int(mapped_params["macd_signal"])
            if "new_high_period" in mapped_params:
                mapped_params["new_high_period"] = int(mapped_params["new_high_period"])

            params = mapped_params

        super().__init__(name, params or {})

        # Strategy parameters
        self.fast_period = self.params.get('fast', 5)
        self.slow_period = self.params.get('slow', 13)
        self.macd_fast = self.params.get('macd_fast', 12)
        self.macd_slow = self.params.get('macd_slow', 26)
        self.macd_signal = self.params.get('macd_signal', 9)
        self.new_high_period = self.params.get('new_high_period', 5)  # Use 5-period breakout

        self.logger.info(f"Initialized {self.name} strategy with params: "
                        f"fast={self.fast_period}, slow={self.slow_period}, "
                        f"macd_fast={self.macd_fast}, macd_slow={self.macd_slow}, "
                        f"macd_signal={self.macd_signal}, new_high_period={self.new_high_period}")

    def analyze(self, data: pd.DataFrame) -> Tuple[bool, str, Optional[float], bool]:
        """
        Analyze stock data and determine if it meets selection criteria

        Args:
            data: DataFrame with stock data including OHLCV columns

        Returns:
            Tuple of (meets_criteria, selection_reason, score, golden_cross_detected)
        """

        if data.empty:
            return False, "数据为空", None, False

        try:
            # Get required data points
            required_data = max(
                self.fast_period, self.slow_period,
                self.macd_fast, self.macd_slow, self.macd_signal,
                self.new_high_period
            )
            if len(data) < required_data:
                return False, f"数据不足，需要{required_data}条数据", None, False

            # Convert pandas Series to numpy array for TA-Lib
            close_prices = np.array(data["close"].values, dtype=np.float64)
            high_prices = np.array(data["high"].values, dtype=np.float64)

            # Calculate moving averages
            ma_fast = talib.SMA(close_prices, timeperiod=self.fast_period)
            ma_slow = talib.SMA(close_prices, timeperiod=self.slow_period)

            # Calculate MACD
            macd_dif, macd_dea, _ = talib.MACD(
                close_prices,
                fastperiod=self.macd_fast,
                slowperiod=self.macd_slow,
                signalperiod=self.macd_signal
            )

            # Current values
            current_price = close_prices[-1]
            ma_fast_last = ma_fast[-1] if not np.isnan(ma_fast[-1]) else None
            ma_slow_last = ma_slow[-1] if not np.isnan(ma_slow[-1]) else None
            macd_dif_last = macd_dif[-1] if not np.isnan(macd_dif[-1]) else None
            macd_dea_last = macd_dea[-1] if not np.isnan(macd_dea[-1]) else None

            # Check if all values are valid
            if (ma_fast_last is None or ma_slow_last is None or
                macd_dif_last is None or macd_dea_last is None):
                return False, "技术指标计算无效", None, False

            # Calculate historical high for scoring (long-term)
            historical_high = np.max(high_prices[-self.new_high_period:]) if len(high_prices) >= self.new_high_period else None

            # Generate reason based on which conditions are met
            ma_condition = ma_fast_last > ma_slow_last
            macd_condition = macd_dif_last > macd_dea_last
            breakout_condition = historical_high is not None and current_price > historical_high

            # For scoring, we'll use the historical high (5-period)
            score = self._calculate_score(
                ma_fast_last, ma_slow_last,
                macd_dif_last, macd_dea_last,
                current_price, historical_high
            )

            # Check strength confirmation (score > 60) - revert to original strict condition
            if score <= 60:
                return False, f"趋势强度不足，得分{score:.2f} <= 60", score, False

            reason = f"趋势强度得分{score:.2f}"

            if ma_condition:
                reason += f", MA{self.fast_period}({ma_fast_last:.2f}) > MA{self.slow_period}({ma_slow_last:.2f})"
            if macd_condition:
                reason += f", DIF({macd_dif_last:.4f}) > DEA({macd_dea_last:.4f})"
            if breakout_condition:
                reason += f", 价格({current_price:.2f})创{self.new_high_period}周期新高({historical_high:.2f})"

            # Check for golden cross pattern (MA5 crosses above MA13 and MACD DIF crosses above DEA)
            golden_cross_condition = self._detect_golden_cross(data)

            if golden_cross_condition:
                reason += " (检测到金叉)"

            return True, reason, score, golden_cross_condition

        except Exception as e:
            self.log_error(f"分析错误: {e}")
            return False, f"分析错误: {e}", None, False

    def _calculate_score(self, ma_fast, ma_slow, macd_dif, macd_dea, price, historical_high):
        """
        Calculate trend strength score based on documented formula

        Score calculation formula:
        score = max(
            0,
            min(
                100,
                40 * (ma_fast - ma_slow) / ma_slow  # 均线排列强度
              + 30 * (macd_dif - macd_dea) / abs(macd_dea) if macd_dea != 0 else 0  # MACD动量
              + 20 * max(0, (macd_dif - 0)) / max(0.01, macd_dif)  # 零轴之上加分
              + 10 * (price - historical_high) / historical_high  # 突破强度
            )
        )
        """
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
            self.log_warning(f"评分计算错误: {e}")
            return 0

    def _detect_golden_cross(self, data: pd.DataFrame) -> bool:
        """
        Detect golden cross pattern (MA5 crosses above MA13 and MACD DIF crosses above DEA)

        Args:
            data: DataFrame with K-line data

        Returns:
            True if golden cross detected, False otherwise
        """
        if data.empty or len(data) < max(self.fast_period, self.slow_period, self.macd_signal):
            return False

        try:
            # Convert pandas Series to numpy array for TA-Lib
            close_prices = np.asarray(data["close"].values, dtype=np.float64)

            # Calculate moving averages
            ma_fast = talib.SMA(close_prices, timeperiod=self.fast_period)
            ma_slow = talib.SMA(close_prices, timeperiod=self.slow_period)

            # Calculate MACD
            macd_dif, macd_dea, _ = talib.MACD(
                close_prices,
                fastperiod=self.macd_fast,
                slowperiod=self.macd_slow,
                signalperiod=self.macd_signal
            )

            # Check if we have enough data points
            if (len(ma_fast) < 2 or len(ma_slow) < 2 or
                len(macd_dif) < 2 or len(macd_dea) < 2):
                return False

            # Check for golden cross (fast MA crosses above slow MA)
            current_fast_above_slow = (
                ma_fast[-1] > ma_slow[-1]
                if not np.isnan(ma_fast[-1]) and not np.isnan(ma_slow[-1])
                else False
            )
            previous_fast_below_slow = (
                ma_fast[-2] <= ma_slow[-2]
                if not np.isnan(ma_fast[-2]) and not np.isnan(ma_slow[-2])
                else False
            )

            # Check for MACD golden cross (DIF crosses above DEA)
            current_dif_above_dea = (
                macd_dif[-1] > macd_dea[-1]
                if not np.isnan(macd_dif[-1]) and not np.isnan(macd_dea[-1])
                else False
            )
            previous_dif_below_dea = (
                macd_dif[-2] <= macd_dea[-2]
                if not np.isnan(macd_dif[-2]) and not np.isnan(macd_dea[-2])
                else False
            )

            # Both conditions must be met for golden cross
            return (current_fast_above_slow and previous_fast_below_slow and
                    current_dif_above_dea and previous_dif_below_dea)

        except Exception as e:
            self.log_warning(f"金叉检测错误: {e}")
            return False

    def execute(
        self, stock_data: Dict[str, pd.DataFrame], agent_name: str, db_manager
    ) -> List[Dict]:
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
                meets_criteria, reason, score, golden_cross = self.analyze(data)

                if meets_criteria:
                    # Add technical analysis data
                    technical_analysis = {}
                    if not data.empty:
                        close_prices = data["close"].values
                        if len(close_prices) >= max(
                            self.fast_period, self.slow_period,
                            self.macd_fast, self.macd_slow, self.macd_signal,
                            self.new_high_period
                        ):
                            # Calculate technical indicators for analysis
                            ma_fast_val = np.mean(
                                np.array(
                                    close_prices[-self.fast_period:],
                                    dtype=np.float64,
                                )
                            )
                            ma_slow_val = np.mean(
                                np.array(
                                    close_prices[-self.slow_period:],
                                    dtype=np.float64,
                                )
                            )

                            # Calculate MACD for technical analysis
                            macd_dif_arr, macd_dea_arr, _ = talib.MACD(
                                np.array(close_prices, dtype=np.float64),
                                fastperiod=self.macd_fast,
                                slowperiod=self.macd_slow,
                                signalperiod=self.macd_signal
                            )

                            technical_analysis = {
                                "price": float(close_prices[-1]),
                                "moving_averages": {
                                    f"sma_{self.fast_period}": float(ma_fast_val),
                                    f"sma_{self.slow_period}": float(ma_slow_val),
                                },
                                "macd": {
                                    "dif": float(macd_dif_arr[-1]) if not np.isnan(macd_dif_arr[-1]) else 0,
                                    "dea": float(macd_dea_arr[-1]) if not np.isnan(macd_dea_arr[-1]) else 0,
                                },
                                "score": score,
                                "golden_cross": golden_cross,
                            }

                    selected_stocks.append(
                        {
                            "code": code,
                            "selection_reason": reason,
                            "score": score,
                            "technical_analysis": technical_analysis,
                            "golden_cross": golden_cross,
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

                # Calculate moving averages
                ma_fast = talib.SMA(close_prices, timeperiod=self.fast_period)
                ma_slow = talib.SMA(close_prices, timeperiod=self.slow_period)

                # Calculate MACD
                macd_dif, macd_dea, _ = talib.MACD(
                    close_prices,
                    fastperiod=self.macd_fast,
                    slowperiod=self.macd_slow,
                    signalperiod=self.macd_signal
                )

                # Calculate historical high
                historical_high = np.array([np.max(high_prices[max(0, i-self.new_high_period+1):i+1])
                                          for i in range(len(high_prices))])

                # Generate buy signals when all conditions are met:
                # 1. MA5 > MA13
                # 2. DIF > DEA
                # 3. Price breaks historical high
                for i in range(len(signals)):
                    # Check if we have valid data
                    if (np.isnan(ma_fast[i]) or np.isnan(ma_slow[i]) or
                        np.isnan(macd_dif[i]) or np.isnan(macd_dea[i]) or
                        np.isnan(historical_high[i])):
                        continue

                    # Check basic conditions
                    ma_condition = ma_fast[i] > ma_slow[i]
                    macd_condition = macd_dif[i] > macd_dea[i]
                    breakout_condition = close_prices[i] > historical_high[i]

                    # Combined basic condition
                    if ma_condition and macd_condition and breakout_condition:
                        signals.loc[signals.index[i], "signal"] = "BUY"
                        # Calculate position size based on score
                        score = self._calculate_score(
                            ma_fast[i], ma_slow[i],
                            macd_dif[i], macd_dea[i],
                            close_prices[i], historical_high[i]
                        )
                        # Position size is proportional to score (0-1 range)
                        position_size = min(1.0, max(0.0, score / 100.0))
                        signals.loc[signals.index[i], "position"] = position_size

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
    strategy = TrendFollowingStrategy()
    
    # Generate signals
    signals = strategy.generate_signals(sample_data)
    print(f"Generated {len(signals[signals['signal'] != 'HOLD'])} trading signals")
    print(signals.tail(10))

