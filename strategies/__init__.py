"""
Strategies module for the quant trading system.
Contains various trading strategies implementation.
"""

from .base_strategy import BaseStrategy
from .ma_crossover_strategy import MACrossoverStrategy
from .rsi_strategy import RSIStrategy
from .bollinger_bands_strategy import BollingerBandsStrategy
from .macd_strategy import MACDStrategy
from .volume_strategy import VolumeStrategy
from .mean_reversion_strategy import MeanReversionStrategy
from .momentum_strategy import MomentumStrategy
from .volatility_strategy import VolatilityStrategy
from .support_resistance_strategy import SupportResistanceStrategy
from .trend_following_strategy import TrendFollowingStrategy

__all__ = [
    "BaseStrategy",
    "MACrossoverStrategy",
    "RSIStrategy",
    "BollingerBandsStrategy",
    "MACDStrategy",
    "VolumeStrategy",
    "MeanReversionStrategy",
    "MomentumStrategy",
    "VolatilityStrategy",
    "SupportResistanceStrategy",
    "TrendFollowingStrategy"
]

