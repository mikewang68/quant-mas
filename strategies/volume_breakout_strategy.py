"""
Volume Breakout Strategy
A strategy that identifies strong leading stocks by detecting resonance between
price breakout, significant volume increase, and momentum confirmation.
"""

import pandas as pd
import numpy as np
import talib
from typing import Dict, Tuple, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategies.base_strategy import BaseStrategy

class VolumeBreakoutStrategy(BaseStrategy):
    """
    Volume Breakout Strategy
    Identifies strong leading stocks by detecting resonance between
    price breakout, significant volume increase, and momentum confirmation.
    """

    def __init__(self, name: str = "放量突破策略", params: Optional[Dict] = None):
        """
        Initialize the Volume Breakout strategy.

        Args:
            name: Strategy name
            params: Strategy parameters
                - breakout_period: Breakout period (default: 13)
                - volume_ma_period: Volume moving average period (default: 5)
                - volume_multiplier: Volume multiplier (default: 1.8)
                - macd_fast: MACD fast period (default: 12)
                - macd_slow: MACD slow period (default: 26)
                - macd_signal: MACD signal period (default: 9)
        """
        # Handle parameter name mapping from database storage format to strategy format
        if params:
            mapped_params = params.copy()

            # Map database parameter names to strategy parameter names
            if "breakout_period" in mapped_params and "breakout_period" not in mapped_params:
                mapped_params["breakout_period"] = int(mapped_params["breakout_period"])
            if "volume_ma_period" in mapped_params and "volume_ma_period" not in mapped_params:
                mapped_params["volume_ma_period"] = int(mapped_params["volume_ma_period"])
            if "volume_multiplier" in mapped_params and "volume_multiplier" not in mapped_params:
                mapped_params["volume_multiplier"] = float(mapped_params["volume_multiplier"])
            if "macd_fast" in mapped_params and "macd_fast" not in mapped_params:
                mapped_params["macd_fast"] = int(mapped_params["macd_fast"])
            if "macd_slow" in mapped_params and "macd_slow" not in mapped_params:
                mapped_params["macd_slow"] = int(mapped_params["macd_slow"])
            if "macd_signal" in mapped_params and "macd_signal" not in mapped_params:
                mapped_params["macd_signal"] = int(mapped_params["macd_signal"])

            # Ensure existing parameters are correct types
            if "breakout_period" in mapped_params:
                mapped_params["breakout_period"] = int(mapped_params["breakout_period"])
            if "volume_ma_period" in mapped_params:
                mapped_params["volume_ma_period"] = int(mapped_params["volume_ma_period"])
            if "volume_multiplier" in mapped_params:
                mapped_params["volume_multiplier"] = float(mapped_params["volume_multiplier"])
            if "macd_fast" in mapped_params:
                mapped_params["macd_fast"] = int(mapped_params["macd_fast"])
            if "macd_slow" in mapped_params:
                mapped_params["macd_slow"] = int(mapped_params["macd_slow"])
            if "macd_signal" in mapped_params:
                mapped_params["macd_signal"] = int(mapped_params["macd_signal"])

            params = mapped_params

        super().__init__(name, params or {})

        # Strategy parameters
        self.breakout_period = self.params.get('breakout_period', 13)
        self.volume_ma_period = self.params.get('volume_ma_period', 5)
        self.volume_multiplier = self.params.get('volume_multiplier', 1.8)
        self.macd_fast = self.params.get('macd_fast', 12)
        self.macd_slow = self.params.get('macd_slow', 26)
        self.macd_signal = self.params.get('macd_signal', 9)

        self.logger.info(f"Initialized {self.name} strategy with params: "
                        f"breakout_period={self.breakout_period}, volume_ma_period={self.volume_ma_period}, "
                        f"volume_multiplier={self.volume_multiplier}, macd_fast={self.macd_fast}, "
                        f"macd_slow={self.macd_slow}, macd_signal={self.macd_signal}")

    def analyze(self, data: pd.DataFrame) -> Tuple[bool, str, Optional[float], bool]:
        """
        Analyze stock data and determine if it meets selection criteria

        Args:
            data: DataFrame with stock data including OHLCV columns

        Returns:
            Tuple of (meets_criteria, selection_reason, score, breakout_signal)
        """

        if data.empty:
            return False, "数据为空", None, False

        try:
            # Get required data points
            required_data = max(
                self.breakout_period, self.volume_ma_period,
                self.macd_fast, self.macd_slow, self.macd_signal
            )
            if len(data) < required_data:
                return False, f"数据不足，需要{required_data}条数据", None, False

            # Convert pandas Series to numpy array for TA-Lib
            close_prices = np.array(data["close"].values, dtype=np.float64)
            high_prices = np.array(data["high"].values, dtype=np.float64)
            volume_data = np.array(data["volume"].values, dtype=np.float64)

            # Calculate breakout high (historical high)
            breakout_high = np.max(high_prices[-self.breakout_period:]) if len(high_prices) >= self.breakout_period else None

            # Calculate volume moving average
            volume_ma = talib.SMA(volume_data, timeperiod=self.volume_ma_period)

            # Calculate MACD
            macd_dif, macd_dea, _ = talib.MACD(
                close_prices,
                fastperiod=self.macd_fast,
                slowperiod=self.macd_slow,
                signalperiod=self.macd_signal
            )

            # Current values
            current_price = close_prices[-1]
            current_volume = volume_data[-1] if not np.isnan(volume_data[-1]) else None
            avg_volume = volume_ma[-1] if not np.isnan(volume_ma[-1]) else None
            macd_dif_last = macd_dif[-1] if not np.isnan(macd_dif[-1]) else None

            # Check if all values are valid
            if (breakout_high is None or current_volume is None or
                avg_volume is None or macd_dif_last is None):
                return False, "技术指标计算无效", None, False

            # Calculate volume ratio
            volume_ratio = current_volume / avg_volume if avg_volume != 0 else 0

            # Check breakout conditions
            # 1. Price breaks historical high with 1.5% buffer
            price_breakout_condition = current_price > breakout_high * 1.015

            # 2. Volume significantly increases
            volume_condition = volume_ratio >= self.volume_multiplier

            # 3. MACD maintains bullish momentum (DIF > 0 and upward)
            macd_condition = macd_dif_last > 0

            # Combined condition - all three must be met
            breakout_signal = price_breakout_condition and volume_condition and macd_condition

            # Prepare selection reason
            reason = f"放量突破条件: 收盘价={current_price:.2f}, 突破高点={breakout_high:.2f}, 当前成交量={current_volume:.0f}, 平均成交量={avg_volume:.0f}, 量比={volume_ratio:.2f}, DIF={macd_dif_last:.4f}"
            if breakout_signal:
                reason += " (满足放量突破)"

            # Calculate score using the documented formula
            score = self._calculate_score(
                volume_ratio, current_price, breakout_high, macd_dif_last
            )

            # Check strength confirmation (score > 60)
            if score <= 60:
                return False, f"突破强度不足，得分={score:.2f}", score, False

            return True, reason, score, breakout_signal

        except Exception as e:
            self.log_error(f"分析错误: {e}")
            return False, f"分析错误: {e}", None, False

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
            volume_data = np.array(data["volume"].values, dtype=np.float64)

            # Calculate breakout high (historical high)
            breakout_high = np.amax(high_prices[-self.breakout_period:]) if len(high_prices) >= self.breakout_period else None

            # Calculate volume moving average
            volume_ma = talib.SMA(volume_data, timeperiod=self.volume_ma_period)

            # Calculate MACD
            macd_dif, macd_dea, _ = talib.MACD(
                close_prices,
                fastperiod=self.macd_fast,
                slowperiod=self.macd_slow,
                signalperiod=self.macd_signal
            )

            # Current values
            current_price = close_prices[-1]
            current_volume = volume_data[-1] if not np.isnan(volume_data[-1]) else None
            avg_volume = volume_ma[-1] if not np.isnan(volume_ma[-1]) else None
            macd_dif_last = macd_dif[-1] if not np.isnan(macd_dif[-1]) else None
            volume_ratio = current_volume / avg_volume if avg_volume and avg_volume != 0 and current_volume is not None and avg_volume is not None else 0

            # Prepare technical analysis data in a format specific to Volume Breakout strategy
            technical_analysis_data = {
                'price': float(current_price),
                'breakout_high': float(breakout_high) if breakout_high is not None else 'N/A',
                'current_volume': float(current_volume) if current_volume is not None else 'N/A',
                'avg_volume': float(avg_volume) if avg_volume is not None else 'N/A',
                'volume_ratio': float(volume_ratio) if volume_ratio is not None else 'N/A',
                'macd': {
                    'dif': float(macd_dif_last) if macd_dif_last is not None else 'N/A',
                    'dea': float(macd_dea[-1]) if not np.isnan(macd_dea[-1]) else 'N/A',
                }
            }

            return technical_analysis_data
        except Exception as e:
            self.log_error(f"获取技术分析数据错误: {e}")
            return {}

    def _calculate_score(self, volume_ratio, price, breakout_high, macd_dif):
        """
        Calculate breakout strength score based on documented formula

        Score calculation formula:
        score = max(
            0,
            min(
                100,
                40 * min(2.0, (volume_ratio - 1)) / 1.0  # 量能放大强度
              + 35 * (price - breakout_high) / breakout_high  # 突破幅度强度
              + 25 * max(0, macd_dif) / max(0.01, abs(macd_dif))  # 动量确认强度
            )
        )
        """
        try:
            # First term: Volume amplification strength (40%)
            term1 = 40 * min(2.0, (volume_ratio - 1)) / 1.0

            # Second term: Breakout magnitude strength (35%)
            term2 = 35 * (price - breakout_high) / breakout_high if breakout_high != 0 else 0

            # Third term: Momentum confirmation strength (25%)
            term3 = 25 * max(0, macd_dif) / max(0.01, abs(macd_dif)) if macd_dif != 0 else 0

            score = max(0, min(100, term1 + term2 + term3))
            return score
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
                meets_criteria, reason, score, breakout_signal = self.analyze(data)

                if meets_criteria:
                    # Add technical analysis data
                    technical_analysis = {}
                    if not data.empty:
                        close_prices = data["close"].values
                        high_prices = data["high"].values
                        volume_data = data["volume"].values

                        if len(close_prices) >= max(
                            self.breakout_period, self.volume_ma_period,
                            self.macd_fast, self.macd_slow, self.macd_signal
                        ):
                            # Calculate technical indicators for analysis
                            breakout_high = np.max(high_prices[-self.breakout_period:])
                            volume_ma_val = np.mean(volume_data[-self.volume_ma_period:])
                            volume_ratio = volume_data[-1] / volume_ma_val if volume_ma_val != 0 else 0

                            # Calculate MACD for technical analysis
                            macd_dif_arr, macd_dea_arr, _ = talib.MACD(
                                np.array(close_prices, dtype=np.float64),
                                fastperiod=self.macd_fast,
                                slowperiod=self.macd_slow,
                                signalperiod=self.macd_signal
                            )

                            technical_analysis = {
                                "price": float(close_prices[-1]),
                                "breakout_high": float(breakout_high),
                                "current_volume": float(volume_data[-1]),
                                "avg_volume": float(volume_ma_val),
                                "volume_ratio": float(volume_ratio),
                                "macd": {
                                    "dif": float(macd_dif_arr[-1]) if not np.isnan(macd_dif_arr[-1]) else 0,
                                    "dea": float(macd_dea_arr[-1]) if not np.isnan(macd_dea_arr[-1]) else 0,
                                },
                                "score": score,
                                "breakout_signal": breakout_signal,
                            }

                    selected_stocks.append(
                        {
                            "code": code,
                            "selection_reason": reason,
                            "score": score,
                            "technical_analysis": technical_analysis,
                            "breakout_signal": breakout_signal,
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
                volume_data = np.array(data["volume"].values, dtype=np.float64)

                # Calculate breakout high
                breakout_high = np.array([np.max(high_prices[max(0, i-self.breakout_period+1):i+1])
                                          for i in range(len(high_prices))])

                # Calculate volume moving average
                volume_ma = talib.SMA(volume_data, timeperiod=self.volume_ma_period)

                # Calculate MACD
                macd_dif, macd_dea, _ = talib.MACD(
                    close_prices,
                    fastperiod=self.macd_fast,
                    slowperiod=self.macd_slow,
                    signalperiod=self.macd_signal
                )

                # Calculate volume ratio
                volume_ratio = np.zeros(len(volume_data))
                for i in range(len(volume_data)):
                    if volume_ma[i] != 0 and not np.isnan(volume_ma[i]):
                        volume_ratio[i] = volume_data[i] / volume_ma[i]
                    else:
                        volume_ratio[i] = 0

                # Generate buy signals when all conditions are met:
                # 1. Price breaks historical high with 1.5% buffer
                # 2. Volume significantly increases
                # 3. MACD maintains bullish momentum
                for i in range(len(signals)):
                    # Check if we have valid data
                    if (np.isnan(breakout_high[i]) or np.isnan(volume_ratio[i]) or
                        np.isnan(macd_dif[i]) or np.isnan(macd_dea[i])):
                        continue

                    # Check basic conditions
                    price_breakout_condition = close_prices[i] > breakout_high[i] * 1.015
                    volume_condition = volume_ratio[i] >= self.volume_multiplier
                    macd_condition = macd_dif[i] > 0

                    # Combined basic condition
                    if price_breakout_condition and volume_condition and macd_condition:
                        signals.loc[signals.index[i], "signal"] = "BUY"
                        # Calculate position size based on score
                        score = self._calculate_score(
                            volume_ratio[i], close_prices[i], breakout_high[i], macd_dif[i]
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
    strategy = VolumeBreakoutStrategy()

    # Generate signals
    signals = strategy.generate_signals(sample_data)
    print(f"Generated {len(signals[signals['signal'] != 'HOLD'])} trading signals")
    print(signals.tail(10))

