"""
Momentum Strategy
A strategy that selects stocks based on momentum indicators with score-based analysis.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategies.base_strategy import BaseStrategy
from utils.strategy_utils import calculate_position_from_score
import talib

class MomentumStrategy(BaseStrategy):
    """
    Momentum Strategy
    Selects stocks based on momentum indicators with score-based analysis.
    """

    def __init__(self, name: str = "动量策略", params: Optional[Dict] = None):
        """
        Initialize the Momentum strategy.

        Args:
            name: Strategy name
            params: Strategy parameters
                - period: Momentum calculation period (default: 14)
                - threshold: Momentum threshold (default: 0)
                - lookback_period: Period for calculating momentum (default: 20)
        """
        super().__init__(name, params or {
            'period': 14,
            'threshold': 0,
            'lookback_period': 20
        })

        # Strategy parameters
        self.period = self.params.get('period', 14)
        self.threshold = self.params.get('threshold', 0)
        self.lookback_period = self.params.get('lookback_period', 20)

        self.logger.info(f"Initialized {self.name} strategy with params: "
                        f"period={self.period}, threshold={self.threshold}, "
                        f"lookback_period={self.lookback_period}")

    def analyze(self, data: pd.DataFrame) -> Tuple[bool, str, Optional[float], bool]:
        """
        Analyze stock data and determine if it meets selection criteria

        Args:
            data: DataFrame with stock data including OHLCV columns

        Returns:
            Tuple of (meets_criteria, selection_reason, score, momentum_positive)
        """
        if data.empty:
            return False, "数据为空", None, False

        try:
            # Check if we have enough data
            if len(data) < self.lookback_period:
                return False, f"数据不足，需要{self.lookback_period}条数据", None, False

            # Calculate momentum
            close_prices = data['close'].values.astype(float)
            momentum_values = talib.MOM(close_prices, timeperiod=self.period)

            # Get the most recent momentum value
            current_momentum = momentum_values[-1] if len(momentum_values) > 0 else 0

            # Check if momentum meets threshold
            if current_momentum <= self.threshold:
                return False, f"动量值({current_momentum:.2f})未达到阈值({self.threshold})", None, False

            # Calculate score based on momentum strength
            score = self._calculate_score(current_momentum)

            reason = f"符合条件: 动量值({current_momentum:.2f}) > 阈值({self.threshold})"

            return True, reason, score, True

        except Exception as e:
            self.log_error(f"分析错误: {e}")
            return False, f"分析错误: {e}", None, False

    def _calculate_score(self, momentum: float) -> float:
        """
        Calculate selection score based on momentum strength

        Args:
            momentum: Current momentum value

        Returns:
            Score between 0 and 1
        """
        try:
            # Normalize momentum to a score between 0 and 1
            # Assuming typical momentum values range from -5 to 5
            normalized_score = (np.tanh(momentum / 5) + 1) / 2
            return max(0.0, min(1.0, normalized_score))

        except Exception as e:
            self.log_warning(f"计算分数时出错: {e}")
            return 0.0

    def execute(self, stock_data: Dict[str, pd.DataFrame],
                agent_name: str, db_manager) -> List[Dict]:
        """
        Execute the strategy on provided stock data and automatically save results

        Args:
            stock_data: Dictionary mapping stock codes to their data DataFrames
            agent_name: Name of the agent executing this strategy
            db_manager: Database manager instance

        Returns:
            List of selected stocks with analysis results
        """
        from datetime import datetime
        start_time = datetime.now()
        self.log_info(f"执行 {self.name} 策略，处理 {len(stock_data)} 只股票")

        selected_stocks = []

        # Analyze each stock
        for code, data in stock_data.items():
            try:
                meets_criteria, reason, score, momentum_positive = self.analyze(data)

                if meets_criteria:
                    # Add technical analysis data
                    technical_analysis = {}
                    if not data.empty and len(data) >= 5:
                        # Calculate additional technical indicators
                        close_prices = data['close'].values.astype(float)
                        momentum_values = talib.MOM(close_prices, timeperiod=self.period)

                        technical_analysis = {
                            'price': float(close_prices[-1]),
                            'momentum': float(momentum_values[-1]) if len(momentum_values) > 0 else 0,
                            'volume': float(data['volume'].iloc[-1]) if not data.empty else 0
                        }

                    # Calculate position based on score
                    position = calculate_position_from_score(score)

                    selected_stocks.append({
                        'code': code,
                        'selection_reason': reason,
                        'score': score,
                        'position': position,  # Add position field based on score
                        'strategy_name': self.name,  # Add strategy name
                        'technical_analysis': technical_analysis,
                        'momentum_positive': momentum_positive
                    })

            except Exception as e:
                self.log_warning(f"处理股票 {code} 时出错: {e}")
                continue

        self.log_info(f"选中 {len(selected_stocks)} 只股票")

        # Automatically save results to pool collection
        if selected_stocks:
            from datetime import datetime
            current_date = datetime.now().strftime('%Y-%m-%d')

            # 记录策略运行结束时间
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            save_success = self.save_to_pool(
                db_manager=db_manager,
                agent_name=agent_name,
                stocks=selected_stocks,
                date=current_date,
                strategy_params=self.params,
                additional_metadata={
                    'strategy_execution_time': execution_time,
                    'selected_stocks_count': len(selected_stocks)
                }
            )

            if save_success:
                self.log_info("策略结果已自动保存到池中")
            else:
                self.log_error("保存策略结果到池中失败")

        return selected_stocks

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate momentum trading signals.

        Args:
            data: DataFrame with columns ['date', 'open', 'high', 'low', 'close', 'volume']

        Returns:
            DataFrame with signals
        """
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 'HOLD'
        signals['position'] = 0.0

        if not self.validate_data(data):
            return signals

        try:
            # Calculate momentum
            close_prices = data['close'].values
            momentum = talib.MOM(close_prices, timeperiod=self.period)

            # Generate signals
            for i in range(1, len(signals)):
                # Buy signal: Momentum crosses above threshold
                if (momentum[i-1] <= self.threshold and
                    momentum[i] > self.threshold):
                    signals.loc[signals.index[i], 'signal'] = 'BUY'
                    # Calculate score for position sizing
                    score = self._calculate_score(momentum[i])
                    signals.loc[signals.index[i], 'position'] = calculate_position_from_score(score)

                # Sell signal: Momentum crosses below threshold
                elif (momentum[i-1] >= self.threshold and
                      momentum[i] < self.threshold):
                    signals.loc[signals.index[i], 'signal'] = 'SELL'
                    # Calculate score for position sizing
                    score = self._calculate_score(momentum[i])
                    signals.loc[signals.index[i], 'position'] = -calculate_position_from_score(score)

                # Hold signal: maintain previous position
                else:
                    signals.loc[signals.index[i], 'signal'] = 'HOLD'
                    signals.loc[signals.index[i], 'position'] = signals.loc[signals.index[i-1], 'position']

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
        # For this strategy, we'll use a fixed position size based on signal
        if signal == 'BUY':
            # Use a moderate position size for buy signals
            return 100.0
        elif signal == 'SELL':
            return -100.0  # Sell 100 shares
        else:
            return 0.0

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
    strategy = MomentumStrategy()

    # Generate signals
    signals = strategy.generate_signals(sample_data)
    print(f"Generated {len(signals[signals['signal'] != 'HOLD'])} trading signals")
    print(signals.tail(10))

