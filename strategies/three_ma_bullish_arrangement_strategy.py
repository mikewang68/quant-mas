"""
Three Moving Average Bullish Arrangement Strategy
Strategy that selects stocks based on three moving average bullish arrangement (MA5 > MA13 > MA34)
with additional golden cross detection between MA5 and MA13.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategies.base_strategy import BaseStrategy
import talib

class ThreeMABullishArrangementStrategy(BaseStrategy):
    """
    Three Moving Average Bullish Arrangement Strategy
    Selects stocks based on three moving average bullish arrangement (MA5 > MA13 > MA34)
    with additional golden cross detection between MA5 and MA13.
    """
    
    def __init__(self, name: str = "三均线多头排列策略", params: Optional[Dict] = None):
        """
        Initialize the three moving average bullish arrangement strategy
        
        Args:
            name: Strategy name
            params: Strategy parameters
        """
        # Ensure parameters are integers where needed
        if params:
            # Convert moving average parameters to integers
            if 'short' in params:
                params['short'] = int(params['short'])
            if 'mid' in params:
                params['mid'] = int(params['mid'])
            if 'long' in params:
                params['long'] = int(params['long'])
            if 'rsi_period' in params:
                params['rsi_period'] = int(params['rsi_period'])
            if 'rsi_min' in params:
                params['rsi_min'] = int(params['rsi_min'])
            if 'rsi_max' in params:
                params['rsi_max'] = int(params['rsi_max'])
        
        super().__init__(name, params or {
            'short': 5,
            'mid': 13,
            'long': 34,
            'rsi_period': 14,
            'rsi_min': 30,
            'rsi_max': 70
        })
    
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
            
            # Check if price is above moving averages in specific order (bullish arrangement)
            # Current price > MA5 > MA13 > MA34
            price_condition = (current_price > ma_short_last) and \
                             (ma_short_last > ma_mid_last) and \
                             (ma_mid_last > ma_long_last)
            
            # Check if each moving average is trending upward (current >= previous)
            trend_condition = True
            trend_violations = []
            
            if ma_short_prev is not None and ma_short_last < ma_short_prev:
                trend_condition = False
                trend_violations.append(f"MA{self.params['short']}下降")
            
            if ma_mid_prev is not None and ma_mid_last < ma_mid_prev:
                trend_condition = False
                trend_violations.append(f"MA{self.params['mid']}下降")
            
            if ma_long_prev is not None and ma_long_last < ma_long_prev:
                trend_condition = False
                trend_violations.append(f"MA{self.params['long']}下降")
            
            # Combined condition: price arrangement + upward trends
            if not price_condition or not trend_condition:
                reason = f"不满足条件: "
                if not price_condition:
                    reason += f"价格未形成多头排列(收盘价={current_price:.2f}, MA{self.params['short']}={ma_short_last:.2f}, MA{self.params['mid']}={ma_mid_last:.2f}, MA{self.params['long']}={ma_long_last:.2f})"
                if not trend_condition:
                    if not price_condition:
                        reason += "; "
                    reason += f"均线趋势不符合: {', '.join(trend_violations)}"
                return False, reason, None, False
            
            # Check for golden cross pattern (MA5 crosses above MA13)
            golden_cross_condition = self._detect_golden_cross_with_params(data)
            
            # Calculate score based on how strong the bullish arrangement is
            # Score is based on the percentage above each moving average
            score = min(1.0, ((current_price / ma_long_last - 1) * 10))
            
            reason = f"满足多头排列: 收盘价={current_price:.2f}, MA{self.params['short']}={ma_short_last:.2f}, MA{self.params['mid']}={ma_mid_last:.2f}, MA{self.params['long']}={ma_long_last:.2f}"
            if golden_cross_condition:
                reason += " (检测到金叉)"
            
            return True, reason, score, golden_cross_condition
            
        except Exception as e:
            self.log_error(f"分析错误: {e}")
            return False, f"分析错误: {e}", None, False
    
    def _detect_golden_cross_with_params(self, k_data: pd.DataFrame) -> bool:
        """
        Detect golden cross pattern using strategy parameters (short and mid MA)
        
        Args:
            k_data: DataFrame with K-line data
            
        Returns:
            True if golden cross detected, False otherwise
        """
        if k_data.empty or len(k_data) < max(self.params['short'], self.params['mid']):
            return False
            
        try:
            # Convert pandas Series to numpy array for TA-Lib
            close_prices = np.asarray(k_data['close'].values, dtype=np.float64)
            
            # Calculate moving averages using strategy parameters (short and mid for golden cross)
            ma_short = talib.SMA(close_prices, timeperiod=self.params['short'])
            ma_mid = talib.SMA(close_prices, timeperiod=self.params['mid'])
            
            # Check if we have enough data points
            if len(ma_short) < 2 or len(ma_mid) < 2:
                return False
                
            # Check for golden cross (short MA crosses above mid MA)
            # Current: short MA > mid MA
            # Previous: short MA <= mid MA
            current_short_above_mid = ma_short[-1] > ma_mid[-1] if not np.isnan(ma_short[-1]) and not np.isnan(ma_mid[-1]) else False
            previous_short_below_mid = ma_short[-2] <= ma_mid[-2] if not np.isnan(ma_short[-2]) and not np.isnan(ma_mid[-2]) else False
            
            return current_short_above_mid and previous_short_below_mid
            
        except Exception as e:
            self.log_warning(f"金叉检测错误: {e}")
            return False
    
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
                        close_prices = data['close'].values
                        if len(close_prices) >= max(self.params['short'], self.params['mid'], self.params['long']):
                            # Calculate moving averages for technical analysis
                            ma_short_val = np.mean(close_prices[-self.params['short']:])
                            ma_mid_val = np.mean(close_prices[-self.params['mid']:])
                            ma_long_val = np.mean(close_prices[-self.params['long']:])
                            
                            technical_analysis = {
                                'price': float(close_prices[-1]),
                                'moving_averages': {
                                    f'sma_{self.params["short"]}': float(ma_short_val),
                                    f'sma_{self.params["mid"]}': float(ma_mid_val),
                                    f'sma_{self.params["long"]}': float(ma_long_val)
                                },
                                'golden_cross': golden_cross
                            }
                    
                    selected_stocks.append({
                        'code': code,
                        'selection_reason': reason,
                        'score': score,
                        'technical_analysis': technical_analysis,
                        'golden_cross': golden_cross
                    })
                    
            except Exception as e:
                self.log_warning(f"处理股票 {code} 时出错: {e}")
                continue
        
        self.log_info(f"选中 {len(selected_stocks)} 只股票")
        
        # Automatically save results to pool collection
        if selected_stocks:
            from datetime import datetime
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            save_success = self.save_to_pool(
                db_manager=db_manager,
                agent_name=agent_name,
                stocks=selected_stocks,
                date=current_date,
                strategy_params=self.params,
                additional_metadata={
                    'strategy_version': '1.0',
                    'total_stocks_analyzed': len(stock_data)
                }
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
                # Convert pandas Series to numpy array for TA-Lib
                close_prices = np.array(data['close'].values, dtype=np.float64)
                
                # Calculate moving averages
                ma_short = talib.SMA(close_prices, timeperiod=self.params['short'])
                ma_mid = talib.SMA(close_prices, timeperiod=self.params['mid'])
                
                # Generate buy signals when short MA crosses above mid MA
                if len(ma_short) >= 2 and len(ma_mid) >= 2:
                    # Check for golden cross (short MA crosses above mid MA)
                    current_short_above_mid = ma_short[-1] > ma_mid[-1] if not np.isnan(ma_short[-1]) and not np.isnan(ma_mid[-1]) else False
                    previous_short_below_mid = ma_short[-2] <= ma_mid[-2] if not np.isnan(ma_short[-2]) and not np.isnan(ma_mid[-2]) else False
                    
                    if current_short_above_mid and previous_short_below_mid:
                        signals.loc[signals.index[-1], 'signal'] = 'BUY'
                        signals.loc[signals.index[-1], 'position'] = 1.0
                        
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
        if signal == 'BUY':
            # Allocate 10% of portfolio value
            return (portfolio_value * 0.1) / price
        elif signal == 'SELL':
            return -100.0  # Sell 100 shares
        else:
            return 0.0  # Hold position

# Example usage
if __name__ == "__main__":
    # This is just an example - in practice, this would be called by an agent
    pass

