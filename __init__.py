import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import core modules
from agents.weekly_selector import WeeklyStockSelector
from agents.daily_trader import DailyTrader
from utils.mongodb_client import MongoDBClient
from utils.akshare_client import AkshareClient
from strategies.base_strategy import BaseStrategy
from backtesting.backtester import Backtester
from web.app import create_app

__version__ = "1.0.0"
__author__ = "Quant Trading Team"

# Expose main classes for easy import
__all__ = [
    "WeeklyStockSelector",
    "DailyTrader",
    "MongoDBClient",
    "AkshareClient",
    "BaseStrategy",
    "Backtester",
    "create_app",
]
