"""
Accelerating Uptrend Strategy
A strategy that selects stocks based on accelerating upward price momentum with angle analysis.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategies.base_strategy import BaseStrategy
import talib

class AcceleratingUptrendStrategy(BaseStrategy):
    """
    Accelerating Uptrend Strategy
    Selects stocks based on price momentum with increasing angle of ascent.
    """
    
    def __init__(self, name: str = "加速上涨策略", params: Optional[Dict] = None):
        """
        Initialize the accelerating uptrend strategy
        
        Args:
            name: Strategy name
            params: Strategy parameters
                - angle_threshold: Minimum angle for uptrend (default: 30 degrees)
                - lookback_period: Period for calculating moving average angle (default: 20)
                - volume_ratio_threshold: Minimum volume ratio vs average (default: 1.2)
                - acceleration_window: Window for calculating angle acceleration (default: 2)
        """
        super().__init__(name, params or {
            'angle_threshold': 30,
            'lookback_period': 20,
            'volume_ratio_threshold': 1.2,
            'acceleration_window': 2
        })
        
        # Strategy parameters
        self.angle_threshold = self.params.get('angle_threshold', 30)
        self.lookback_period = self.params.get('lookback_period', 20)
        self.volume_ratio_threshold = self.params.get('volume_ratio_threshold', 1.2)
        self.acceleration_window = self.params.get('acceleration_window', 2)
        
        self.logger.info(f"Initialized {self.name} strategy with params: "
                        f"angle_threshold={self.angle_threshold}, "
                        f"lookback_period={self.lookback_period}, "
                        f"volume_ratio_threshold={self.volume_ratio_threshold}")
    
    def analyze(self, data: pd.DataFrame) -> Tuple[bool, str, Optional[float], bool]:
        """
        Analyze stock data and determine if it meets selection criteria
        
        Args:
            data: DataFrame with stock data including OHLCV columns
            
        Returns:
            Tuple of (meets_criteria, selection_reason, score, uptrend_accelerating)
        """
        if data.empty:
            return False, "数据为空", None, False
            
        try:
            # Check if we have enough data
            required_data = self.lookback_period + self.acceleration_window
            if len(data) < required_data:
                return False, f"数据不足，需要{required_data}条数据", None, False
            
            # Calculate price angle and acceleration
            angle_current, angle_previous = self._calculate_price_angles(data)
            
            # Check if current angle meets threshold
            if angle_current < self.angle_threshold:
                return False, f"上涨角度({angle_current:.2f}°)未达到阈值({self.angle_threshold}°)", None, False
            
            # Check if angle is accelerating (current > previous)
            if angle_current <= angle_previous:
                return False, f"上涨角度未加速: 当前({angle_current:.2f}°) <= 之前({angle_previous:.2f}°)", None, False
            
            # Check volume confirmation
            volume_confirmed = self._check_volume_confirmation(data)
            if not volume_confirmed:
                return False, "成交量未确认价格上涨", None, True  # Angle criteria met but volume not confirmed
            
            # Calculate score based on angle and acceleration
            score = self._calculate_score(angle_current, angle_previous)
            
            reason = f"符合条件: 上涨角度({angle_current:.2f}°) > 阈值({self.angle_threshold}°), " \
                    f"加速中(当前{angle_current:.2f}° > 之前{angle_previous:.2f}°)"
            
            return True, reason, score, True
            
        except Exception as e:
            self.log_error(f"分析错误: {e}")
            return False, f"分析错误: {e}", None, False
    
    def _calculate_price_angles(self, data: pd.DataFrame) -> Tuple[float, float]:
        """
        Calculate current and previous price angles using linear regression
        
        Args:
            data: DataFrame with stock data
            
        Returns:
            Tuple of (current_angle, previous_angle)
        """
        try:
            # Get closing prices for lookback period
            prices = data['close'].tail(self.lookback_period).values
            
            # Calculate current angle using all available prices
            current_angle = self._calculate_angle_from_prices(prices)
            
            # Calculate previous angle using prices excluding the most recent
            if len(prices) > 1:
                previous_prices = prices[:-1]
                previous_angle = self._calculate_angle_from_prices(previous_prices)
            else:
                previous_angle = current_angle
                
            return current_angle, previous_angle
            
        except Exception as e:
            self.log_warning(f"计算价格角度时出错: {e}")
            return 0.0, 0.0
    
    def _calculate_angle_from_prices(self, prices: np.ndarray) -> float:
        """
        Calculate angle from price array using linear regression slope
        
        Args:
            prices: Array of prices
            
        Returns:
            Angle in degrees
        """
        if len(prices) < 2:
            return 0.0
            
        # Create time indices
        x = np.arange(len(prices))
        y = prices
        
        # Calculate linear regression slope
        # Using numpy's polyfit for linear regression (degree=1)
        slope, _ = np.polyfit(x, y, 1)
        
        # Convert slope to angle in degrees
        # Angle = arctan(slope) * (180/pi)
        angle_rad = np.arctan(slope)
        angle_deg = np.degrees(angle_rad)
        
        # Normalize angle to be positive for uptrends
        return abs(angle_deg) if slope > 0 else 0.0
    
    def _check_volume_confirmation(self, data: pd.DataFrame) -> bool:
        """
        Check if volume confirms the price uptrend
        
        Args:
            data: DataFrame with stock data
            
        Returns:
            True if volume confirms uptrend, False otherwise
        """
        try:
            if len(data) < 10:
                return True  # Not enough data, skip volume check
            
            # Get recent volume data
            recent_volumes = data['volume'].tail(5).values
            avg_volume = data['volume'].tail(20).mean()
            
            # Check if recent volume is above average
            if avg_volume > 0:
                recent_avg_volume = np.mean(recent_volumes)
                volume_ratio = recent_avg_volume / avg_volume
                return volume_ratio >= self.volume_ratio_threshold
            
            return True  # Skip volume check if average volume is zero
            
        except Exception as e:
            self.log_warning(f"检查成交量确认时出错: {e}")
            return True  # Default to True if there's an error
    
    def _calculate_score(self, current_angle: float, previous_angle: float) -> float:
        """
        Calculate selection score based on angle and acceleration
        
        Args:
            current_angle: Current price angle
            previous_angle: Previous price angle
            
        Returns:
            Score between 0 and 1
        """
        try:
            # Score based on angle magnitude (normalized to 0-0.5)
            angle_score = min(1.0, current_angle / 60.0) * 0.5
            
            # Score based on acceleration (normalized to 0-0.5)
            if previous_angle > 0:
                acceleration_ratio = current_angle / previous_angle
                acceleration_score = min(1.0, (acceleration_ratio - 1) * 2) * 0.5
            else:
                acceleration_score = 0.0
            
            # Combine scores
            total_score = min(1.0, angle_score + acceleration_score)
            return total_score
            
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
        self.log_info(f"执行 {self.name} 策略，处理 {len(stock_data)} 只股票")
        
        selected_stocks = []
        
        # Analyze each stock
        for code, data in stock_data.items():
            try:
                meets_criteria, reason, score, uptrend_accelerating = self.analyze(data)
                
                if meets_criteria:
                    # Add technical analysis data
                    technical_analysis = {}
                    if not data.empty and len(data) >= 5:
                        # Calculate additional technical indicators
                        close_prices = data['close'].values
                        
                        # Calculate price angles for technical analysis
                        current_angle, previous_angle = self._calculate_price_angles(data)
                        
                        technical_analysis = {
                            'price': float(close_prices[-1]),
                            'current_angle': current_angle,
                            'previous_angle': previous_angle,
                            'acceleration': current_angle - previous_angle,
                            'volume_confirmed': self._check_volume_confirmation(data)
                        }
                    
                    selected_stocks.append({
                        'code': code,
                        'selection_reason': reason,
                        'score': score,
                        'technical_analysis': technical_analysis,
                        'uptrend_accelerating': uptrend_accelerating
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
        
        if not data.empty and len(data) >= self.lookback_period + self.acceleration_window:
            try:
                # Calculate angles for each point in the data
                angles = []
                for i in range(self.lookback_period, len(data)):
                    # Get price data for lookback period
                    price_window = data['close'].iloc[i-self.lookback_period:i+1].values
                    angle = self._calculate_angle_from_prices(price_window)
                    angles.append(angle)
                
                # Pad angles to match data length
                angles = [0] * self.lookback_period + angles
                
                # Calculate previous angles (shifted by acceleration_window)
                previous_angles = [0] * (self.lookback_period + self.acceleration_window) + \
                                angles[self.lookback_period:-self.acceleration_window] if \
                                len(angles) > self.lookback_period + self.acceleration_window else [0] * len(angles)
                
                # Generate buy signals when angle criteria are met
                for i in range(len(signals)):
                    if i < len(angles) and i < len(previous_angles):
                        current_angle = angles[i]
                        previous_angle = previous_angles[i] if i < len(previous_angles) else 0
                        
                        # Buy signal: angle above threshold and accelerating
                        if current_angle >= self.angle_threshold and current_angle > previous_angle:
                            signals.loc[signals.index[i], 'signal'] = 'BUY'
                            signals.loc[signals.index[i], 'position'] = 1.0
                        # Sell signal: angle below threshold or not accelerating
                        elif current_angle < self.angle_threshold or current_angle <= previous_angle:
                            signals.loc[signals.index[i], 'signal'] = 'SELL'
                            signals.loc[signals.index[i], 'position'] = -1.0
                
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

