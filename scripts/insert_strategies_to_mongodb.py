#!/usr/bin/env python3
"""
Script to insert strategy information into MongoDB database.
This script extracts information from strategy classes and inserts them into 
the MongoDB stock database strategies collection.
"""

import sys
import os
import logging
from typing import Dict, Any

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from strategies.ma_crossover_strategy import MACrossoverStrategy
from strategies.rsi_strategy import RSIStrategy
from strategies.bollinger_bands_strategy import BollingerBandsStrategy
from strategies.macd_strategy import MACDStrategy
from strategies.volume_strategy import VolumeStrategy
from strategies.mean_reversion_strategy import MeanReversionStrategy
from strategies.momentum_strategy import MomentumStrategy
from strategies.volatility_strategy import VolatilityStrategy
from strategies.support_resistance_strategy import SupportResistanceStrategy
from strategies.trend_following_strategy import TrendFollowingStrategy
from strategies.breakout_strategy import BreakoutStrategy
from strategies.scalping_strategy import ScalpingStrategy

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_strategy_info():
    """Extract information from all strategy classes."""
    strategies_info = []
    
    # Define all strategies with their classes and additional information
    strategies = [
        {
            "class": MACrossoverStrategy,
            "name": "MA_Crossover",
            "chinese_name": "移动平均线交叉策略",
            "description": "当短期移动平均线向上穿越长期移动平均线时产生买入信号，向下穿越时产生卖出信号。",
            "type": "trend_following",
            "parameters": {
                "short_period": {"default": 5, "description": "短期移动平均周期"},
                "long_period": {"default": 20, "description": "长期移动平均周期"},
                "max_position_ratio": {"default": 0.1, "description": "最大仓位比例"}
            },
            "output_fields": ["signal", "position"],
            "signal_types": ["BUY", "SELL", "HOLD"]
        },
        {
            "class": RSIStrategy,
            "name": "RSI",
            "chinese_name": "RSI相对强弱指数策略",
            "description": "当RSI指标向下穿越超卖区(30)时产生买入信号，向上穿越超买区(70)时产生卖出信号。",
            "type": "mean_reversion",
            "parameters": {
                "period": {"default": 14, "description": "RSI计算周期"},
                "overbought": {"default": 70, "description": "超买阈值"},
                "oversold": {"default": 30, "description": "超卖阈值"},
                "max_position_ratio": {"default": 0.1, "description": "最大仓位比例"}
            },
            "output_fields": ["rsi", "signal", "position"],
            "signal_types": ["BUY", "SELL", "HOLD"]
        },
        {
            "class": BollingerBandsStrategy,
            "name": "Bollinger_Bands",
            "chinese_name": "布林带策略",
            "description": "当价格向下穿越布林带下轨时产生买入信号，向上穿越布林带上轨时产生卖出信号。",
            "type": "volatility",
            "parameters": {
                "period": {"default": 20, "description": "布林带计算周期"},
                "std_dev": {"default": 2, "description": "标准差倍数"},
                "max_position_ratio": {"default": 0.1, "description": "最大仓位比例"}
            },
            "output_fields": ["upper_band", "middle_band", "lower_band", "signal", "position"],
            "signal_types": ["BUY", "SELL", "HOLD"]
        },
        {
            "class": MACDStrategy,
            "name": "MACD",
            "chinese_name": "MACD策略",
            "description": "当MACD线向上穿越信号线时产生买入信号，向下穿越时产生卖出信号。",
            "type": "trend_following",
            "parameters": {
                "fast_period": {"default": 12, "description": "快速EMA周期"},
                "slow_period": {"default": 26, "description": "慢速EMA周期"},
                "signal_period": {"default": 9, "description": "信号线周期"},
                "max_position_ratio": {"default": 0.1, "description": "最大仓位比例"}
            },
            "output_fields": ["macd", "macd_signal", "macd_hist", "signal", "position"],
            "signal_types": ["BUY", "SELL", "HOLD"]
        },
        {
            "class": VolumeStrategy,
            "name": "Volume",
            "chinese_name": "成交量策略",
            "description": "当成交量显著高于平均值时产生买入信号，显著低于平均值时产生卖出信号。",
            "type": "volume",
            "parameters": {
                "period": {"default": 20, "description": "成交量移动平均周期"},
                "threshold": {"default": 1.5, "description": "成交量倍数阈值"},
                "max_position_ratio": {"default": 0.1, "description": "最大仓位比例"}
            },
            "output_fields": ["volume", "volume_ma", "volume_ratio", "signal", "position"],
            "signal_types": ["BUY", "SELL", "HOLD"]
        },
        {
            "class": MeanReversionStrategy,
            "name": "Mean_Reversion",
            "chinese_name": "均值回归策略",
            "description": "当价格显著偏离移动平均线下方时产生买入信号，显著偏离上方时产生卖出信号。",
            "type": "mean_reversion",
            "parameters": {
                "period": {"default": 20, "description": "移动平均周期"},
                "std_dev_multiplier": {"default": 2, "description": "标准差倍数"},
                "max_position_ratio": {"default": 0.1, "description": "最大仓位比例"}
            },
            "output_fields": ["ma", "upper_band", "lower_band", "signal", "position"],
            "signal_types": ["BUY", "SELL", "HOLD"]
        },
        {
            "class": MomentumStrategy,
            "name": "Momentum",
            "chinese_name": "动量策略",
            "description": "当动量指标转正时产生买入信号，转负时产生卖出信号。",
            "type": "momentum",
            "parameters": {
                "period": {"default": 14, "description": "动量计算周期"},
                "threshold": {"default": 0, "description": "动量阈值"},
                "max_position_ratio": {"default": 0.1, "description": "最大仓位比例"}
            },
            "output_fields": ["momentum", "signal", "position"],
            "signal_types": ["BUY", "SELL", "HOLD"]
        },
        {
            "class": VolatilityStrategy,
            "name": "Volatility",
            "chinese_name": "波动率策略",
            "description": "当波动率低时(预期突破)产生买入信号，波动率高时(预期反转)产生卖出信号。",
            "type": "volatility",
            "parameters": {
                "period": {"default": 14, "description": "波动率计算周期"},
                "low_percentile": {"default": 20, "description": "低波动率百分位阈值"},
                "high_percentile": {"default": 80, "description": "高波动率百分位阈值"},
                "max_position_ratio": {"default": 0.1, "description": "最大仓位比例"}
            },
            "output_fields": ["atr", "signal", "position"],
            "signal_types": ["BUY", "SELL", "HOLD"]
        },
        {
            "class": SupportResistanceStrategy,
            "name": "Support_Resistance",
            "chinese_name": "支撑阻力策略",
            "description": "当价格从支撑位反弹时产生买入信号，从阻力位回落时产生卖出信号。",
            "type": "support_resistance",
            "parameters": {
                "period": {"default": 20, "description": "支撑阻力检测回看周期"},
                "threshold": {"default": 0.02, "description": "价格接近度阈值 (2%)"},
                "max_position_ratio": {"default": 0.1, "description": "最大仓位比例"}
            },
            "output_fields": ["support", "resistance", "signal", "position"],
            "signal_types": ["BUY", "SELL", "HOLD"]
        },
        {
            "class": TrendFollowingStrategy,
            "name": "Trend_Following",
            "chinese_name": "趋势跟踪策略",
            "description": "当价格突破移动平均线时产生买入信号，跌破时产生卖出信号。",
            "type": "trend_following",
            "parameters": {
                "period": {"default": 50, "description": "移动平均周期"},
                "max_position_ratio": {"default": 0.1, "description": "最大仓位比例"}
            },
            "output_fields": ["ma", "signal", "position"],
            "signal_types": ["BUY", "SELL", "HOLD"]
        },
        {
            "class": BreakoutStrategy,
            "name": "Breakout",
            "chinese_name": "突破策略",
            "description": "当价格突破阻力位时产生买入信号，跌破支撑位时产生卖出信号。",
            "type": "breakout",
            "parameters": {
                "period": {"default": 20, "description": "支撑阻力计算回看周期"},
                "buffer": {"default": 0.01, "description": "突破确认缓冲百分比 (1%)"},
                "max_position_ratio": {"default": 0.1, "description": "最大仓位比例"}
            },
            "output_fields": ["support", "resistance", "signal", "position"],
            "signal_types": ["BUY", "SELL", "HOLD"]
        },
        {
            "class": ScalpingStrategy,
            "name": "Scalping",
            "chinese_name": "高频交易策略",
            "description": "基于短期价格变动产生交易信号，适用于高频交易。",
            "type": "scalping",
            "parameters": {
                "period": {"default": 5, "description": "动量计算回看周期"},
                "threshold": {"default": 0.005, "description": "价格变动阈值 (0.5%)"},
                "max_position_ratio": {"default": 0.1, "description": "最大仓位比例"}
            },
            "output_fields": ["momentum", "price_change_ratio", "signal", "position"],
            "signal_types": ["BUY", "SELL", "HOLD"]
        }
    ]
    
    # Extract information from each strategy
    for strategy_info in strategies:
        strategy_class = strategy_info["class"]
        strategy_instance = strategy_class()
        
        strategy_data = {
            "name": strategy_info["name"],
            "chinese_name": strategy_info["chinese_name"],
            "description": strategy_info["description"],
            "type": strategy_info["type"],
            "parameters": strategy_info["parameters"],
            "output_fields": strategy_info["output_fields"],
            "signal_types": strategy_info["signal_types"],
            # Adding a new field as requested
            "created_at": "2025-08-15",
            "version": "1.0"
        }
        
        strategies_info.append(strategy_data)
        logger.info(f"Extracted information for strategy: {strategy_info['name']}")
    
    return strategies_info

def insert_strategies_to_mongodb(strategies_info: list):
    """Insert strategies information into MongoDB."""
    try:
        # Initialize MongoDB manager
        mongodb_manager = MongoDBManager()
        
        # Clear existing strategies (optional)
        mongodb_manager.strategies_collection.delete_many({})
        logger.info("Cleared existing strategies from database")
        
        # Insert new strategies
        if strategies_info:
            result = mongodb_manager.strategies_collection.insert_many(strategies_info)
            logger.info(f"Inserted {len(result.inserted_ids)} strategies into MongoDB")
            return True
        else:
            logger.warning("No strategies to insert")
            return False
            
    except Exception as e:
        logger.error(f"Error inserting strategies to MongoDB: {e}")
        return False
    finally:
        # Close MongoDB connection
        try:
            mongodb_manager.close_connection()
        except:
            pass

def main():
    """Main function to extract and insert strategy information."""
    logger.info("Starting strategy information extraction and insertion process")
    
    try:
        # Extract strategy information
        strategies_info = extract_strategy_info()
        logger.info(f"Extracted information for {len(strategies_info)} strategies")
        
        # Insert into MongoDB
        success = insert_strategies_to_mongodb(strategies_info)
        
        if success:
            logger.info("Successfully inserted all strategies into MongoDB")
            print("Successfully inserted all strategies into MongoDB")
        else:
            logger.error("Failed to insert strategies into MongoDB")
            print("Failed to insert strategies into MongoDB")
            
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

