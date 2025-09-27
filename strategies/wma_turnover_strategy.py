"""
WMA Price Acceleration with Turnover Filter Strategy
A strategy that selects stocks based on price acceleration confirmed by turnover rate.
"""

import pandas as pd
import numpy as np
import talib
from typing import List, Dict, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategies.base_strategy import BaseStrategy


class WMAPTurnoverStrategy(BaseStrategy):
    """
    WMA Price Acceleration with Turnover Filter Strategy
    Selects stocks based on price acceleration (short > mid and short >= previous value)
    with turnover rate filtering (5-25%).
    """

    def __init__(self, name: str = "均线价格加速换手率过滤策略", params: Optional[Dict] = None):
        """
        Initialize the WMA Price Acceleration with Turnover Filter strategy

        Args:
            name: Strategy name
            params: Strategy parameters
                - short_period: Short WMA period (default: 5)
                - mid_period: Mid WMA period (default: 13)
                - min_turnover: Minimum turnover rate (default: 5.0)
                - max_turnover: Maximum turnover rate (default: 25.0)
        """
        super().__init__(name, params)

        # Strategy parameters
        self.short_period = int(self.params.get('short_period', 5))
        self.mid_period = int(self.params.get('mid_period', 13))
        self.min_turnover = float(self.params.get('min_turnover', 5.0))
        self.max_turnover = float(self.params.get('max_turnover', 25.0))

        self.logger.info(f"Initialized {self.name} strategy with params: "
                        f"short_period={self.short_period}, mid_period={self.mid_period}, "
                        f"min_turnover={self.min_turnover}, max_turnover={self.max_turnover}")

    def analyze(self, data: pd.DataFrame) -> tuple[bool, str, Optional[float]]:
        """
        Analyze stock data and determine if it meets selection criteria

        Args:
            data: DataFrame with stock data including OHLCV and turnover_rate columns

        Returns:
            Tuple of (meets_criteria, selection_reason, score)
        """
        if data.empty:
            return False, "数据为空", None

        try:
            # Check if we have enough data
            required_data = max(self.short_period, self.mid_period)
            if len(data) < required_data:
                return False, f"数据不足，需要{required_data}条数据", None

            # Check if turnover_rate column exists
            if 'turnover_rate' not in data.columns:
                return False, "缺少换手率数据", None

            # Get current turnover rate
            current_turnover = float(data['turnover_rate'].iloc[-1])

            # Check turnover rate filter
            if not (self.min_turnover <= current_turnover <= self.max_turnover):
                return False, f"换手率不符合条件: {current_turnover:.2f}% (要求 {self.min_turnover}-{self.max_turnover}%)", None

            # Convert pandas Series to numpy array for TA-Lib
            close_prices = np.array(data['close'].values, dtype=np.float64)

            # Calculate weighted moving averages
            wma_short = talib.WMA(close_prices, timeperiod=self.short_period)
            wma_mid = talib.WMA(close_prices, timeperiod=self.mid_period)

            # Get current values
            wma_short_current = wma_short[-1] if not np.isnan(wma_short[-1]) else None
            wma_mid_current = wma_mid[-1] if not np.isnan(wma_mid[-1]) else None

            # Get previous short WMA value
            wma_short_previous = wma_short[-2] if len(wma_short) > 1 and not np.isnan(wma_short[-2]) else None

            # Check if all values are valid
            if wma_short_current is None or wma_mid_current is None or wma_short_previous is None:
                return False, "移动平均线计算无效", None

            # Check conditions:
            # 1. short > mid
            # 2. short >= previous short
            condition_1 = wma_short_current > wma_mid_current
            condition_2 = wma_short_current >= wma_short_previous

            if not condition_1 or not condition_2:
                reason = "不满足条件: "
                if not condition_1:
                    reason += f"WMA{self.short_period}({wma_short_current:.2f}) <= WMA{self.mid_period}({wma_mid_current:.2f})"
                if not condition_2:
                    if not condition_1:
                        reason += "; "
                    reason += f"WMA{self.short_period}当前值({wma_short_current:.2f}) < 前值({wma_short_previous:.2f})"
                return False, reason, None

            # Calculate score based on strength of conditions
            # Score components:
            # 1. WMA spread (40% weight)
            # 2. WMA acceleration (30% weight)
            # 3. Turnover rate within optimal range (30% weight)
            wma_spread_score = min(1.0, max(0.0, (wma_short_current - wma_mid_current) / wma_mid_current * 100))
            wma_acceleration_score = min(1.0, max(0.0, (wma_short_current - wma_short_previous) / wma_short_previous * 100))

            # Turnover score is highest in middle of range (15% optimal)
            optimal_turnover = (self.min_turnover + self.max_turnover) / 2
            turnover_deviation = abs(current_turnover - optimal_turnover) / (self.max_turnover - self.min_turnover)
            turnover_score = max(0.0, 1.0 - turnover_deviation)

            # Combine scores (normalize to 0-100 range)
            score = (wma_spread_score * 40 + wma_acceleration_score * 30 + turnover_score * 30)

            reason = (f"满足条件: WMA{self.short_period}({wma_short_current:.2f}) > WMA{self.mid_period}({wma_mid_current:.2f}), "
                     f"WMA{self.short_period}当前值({wma_short_current:.2f}) >= 前值({wma_short_previous:.2f}), "
                     f"换手率{current_turnover:.2f}% ∈ [{self.min_turnover}-{self.max_turnover}]%")

            return True, reason, score

        except Exception as e:
            self.log_error(f"分析错误: {e}")
            return False, f"分析错误: {e}", None

    def execute(self, stock_data: Dict[str, pd.DataFrame], agent_name: str, db_manager) -> List[Dict]:
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
                meets_criteria, reason, score = self.analyze(data)

                if meets_criteria:
                    # Add technical analysis data
                    technical_analysis = {}
                    if not data.empty and len(data) >= max(self.short_period, self.mid_period):
                        close_prices = data['close'].values
                        if len(close_prices) >= max(self.short_period, self.mid_period):
                            # Calculate WMA values for technical analysis
                            wma_short_val = talib.WMA(np.array(close_prices, dtype=np.float64), timeperiod=self.short_period)[-1]
                            wma_mid_val = talib.WMA(np.array(close_prices, dtype=np.float64), timeperiod=self.mid_period)[-1]

                            technical_analysis = {
                                'price': float(close_prices[-1]),
                                'moving_averages': {
                                    f'wma_{self.short_period}': float(wma_short_val),
                                    f'wma_{self.mid_period}': float(wma_mid_val),
                                },
                                'turnover_rate': float(data['turnover_rate'].iloc[-1]) if 'turnover_rate' in data.columns else 0.0
                            }

                    selected_stocks.append({
                        'code': code,
                        'selection_reason': reason,
                        'score': score,
                        'technical_analysis': technical_analysis,
                    })

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
        signals['signal'] = 'HOLD'
        signals['position'] = 0.0

        if not data.empty:
            try:
                meets_criteria, _, _ = self.analyze(data)

                if meets_criteria:
                    signals.loc[signals.index[-1], 'signal'] = 'BUY'
                    signals.loc[signals.index[-1], 'position'] = 1.0

            except Exception as e:
                self.log_warning(f"生成信号时出错: {e}")

        return signals

    def calculate_position_size(self, signal: str, portfolio_value: float, price: float) -> float:
        """
        Calculate position size based on signal and portfolio value.

        Args:
            signal: Trading signal ('BUY', 'SELL', 'HOLD')
            portfolio_value: Current portfolio value
            price: Current asset price

        Returns:
            Position size (number of shares/contracts)
        """
        if signal == 'BUY':
            # Allocate 10% of portfolio value
            return (portfolio_value * 0.1) / price
        elif signal == 'SELL':
            return -100.0  # Sell 100 shares
        else:
            return 0.0  # Hold position


# Example usage
if __name__ == "____main__":
    # This is just an example - in practice, this would be called by an agent
    pass

