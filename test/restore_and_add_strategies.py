#!/usr/bin/env python3
"""
Script to restore original strategy information and add new strategies to MongoDB database.
"""

import sys
import os
import logging
from typing import Dict, Any

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_original_strategies_data():
    """Create the original strategies data that was deleted."""
    original_strategies = [
        {
            "name": "周线选股",
            "type": "technical",
            "description": "使用斐波那契数列设置3均线，分别是5,13,34,均线多头排列",
            "parameters": {
                "long": "34",
                "mid": "13",
                "short": "5"
            }
        },
        {
            "name": "趋势跟踪",
            "type": "technical",
            "description": "test",
            "parameters": {}
        },
        {
            "name": "机器学习",
            "type": "ml",
            "description": "test",
            "parameters": {}
        },
        {
            "name": "测试策略1-RSI",
            "type": "rsi",
            "description": "测试RSI策略",
            "parameters": {
                "rsi_period": 14,
                "rsi_min": 30,
                "rsi_max": 70
            }
        },
        {
            "name": "测试策略2-MACD",
            "type": "macd",
            "description": "测试MACD策略",
            "parameters": {}
        },
        {
            "name": "测试策略3-布林带",
            "type": "bollinger",
            "description": "测试布林带策略",
            "parameters": {
                "bb_period": 20,
                "bb_stddev": 2
            }
        }
    ]
    
    return original_strategies

def create_new_strategies_data():
    """Create new strategies data with the additional field."""
    new_strategies = [
        {
            "name": "MA_Crossover",
            "type": "trend_following",
            "description": "移动平均线交叉策略：当短期移动平均线向上穿越长期移动平均线时产生买入信号，向下穿越时产生卖出信号。",
            "parameters": {
                "short_period": 5,
                "long_period": 20,
                "max_position_ratio": 0.1
            },
            "created_at": "2025-08-15"
        },
        {
            "name": "RSI",
            "type": "mean_reversion",
            "description": "RSI相对强弱指数策略：当RSI指标向下穿越超卖区(30)时产生买入信号，向上穿越超买区(70)时产生卖出信号。",
            "parameters": {
                "period": 14,
                "overbought": 70,
                "oversold": 30,
                "max_position_ratio": 0.1
            },
            "created_at": "2025-08-15"
        },
        {
            "name": "Bollinger_Bands",
            "type": "volatility",
            "description": "布林带策略：当价格向下穿越布林带下轨时产生买入信号，向上穿越布林带上轨时产生卖出信号。",
            "parameters": {
                "period": 20,
                "std_dev": 2,
                "max_position_ratio": 0.1
            },
            "created_at": "2025-08-15"
        },
        {
            "name": "MACD",
            "type": "trend_following",
            "description": "MACD策略：当MACD线向上穿越信号线时产生买入信号，向下穿越时产生卖出信号。",
            "parameters": {
                "fast_period": 12,
                "slow_period": 26,
                "signal_period": 9,
                "max_position_ratio": 0.1
            },
            "created_at": "2025-08-15"
        },
        {
            "name": "Volume",
            "type": "volume",
            "description": "成交量策略：当成交量显著高于平均值时产生买入信号，显著低于平均值时产生卖出信号。",
            "parameters": {
                "period": 20,
                "threshold": 1.5,
                "max_position_ratio": 0.1
            },
            "created_at": "2025-08-15"
        },
        {
            "name": "Mean_Reversion",
            "type": "mean_reversion",
            "description": "均值回归策略：当价格显著偏离移动平均线下方时产生买入信号，显著偏离上方时产生卖出信号。",
            "parameters": {
                "period": 20,
                "std_dev_multiplier": 2,
                "max_position_ratio": 0.1
            },
            "created_at": "2025-08-15"
        },
        {
            "name": "Momentum",
            "type": "momentum",
            "description": "动量策略：当动量指标转正时产生买入信号，转负时产生卖出信号。",
            "parameters": {
                "period": 14,
                "threshold": 0,
                "max_position_ratio": 0.1
            },
            "created_at": "2025-08-15"
        },
        {
            "name": "Volatility",
            "type": "volatility",
            "description": "波动率策略：当波动率低时(预期突破)产生买入信号，波动率高时(预期反转)产生卖出信号。",
            "parameters": {
                "period": 14,
                "low_percentile": 20,
                "high_percentile": 80,
                "max_position_ratio": 0.1
            },
            "created_at": "2025-08-15"
        },
        {
            "name": "Support_Resistance",
            "type": "support_resistance",
            "description": "支撑阻力策略：当价格从支撑位反弹时产生买入信号，从阻力位回落时产生卖出信号。",
            "parameters": {
                "period": 20,
                "threshold": 0.02,
                "max_position_ratio": 0.1
            },
            "created_at": "2025-08-15"
        },
        {
            "name": "Trend_Following",
            "type": "trend_following",
            "description": "趋势跟踪策略：当价格突破移动平均线时产生买入信号，跌破时产生卖出信号。",
            "parameters": {
                "period": 50,
                "max_position_ratio": 0.1
            },
            "created_at": "2025-08-15"
        },
        {
            "name": "Breakout",
            "type": "breakout",
            "description": "突破策略：当价格突破阻力位时产生买入信号，跌破支撑位时产生卖出信号。",
            "parameters": {
                "period": 20,
                "buffer": 0.01,
                "max_position_ratio": 0.1
            },
            "created_at": "2025-08-15"
        },
        {
            "name": "Scalping",
            "type": "scalping",
            "description": "高频交易策略：基于短期价格变动产生交易信号，适用于高频交易。",
            "parameters": {
                "period": 5,
                "threshold": 0.005,
                "max_position_ratio": 0.1
            },
            "created_at": "2025-08-15"
        }
    ]
    
    return new_strategies

def restore_and_add_strategies():
    """Restore original strategies and add new strategies to MongoDB."""
    try:
        # Initialize MongoDB manager
        mongodb_manager = MongoDBManager()
        
        # Get original strategies data
        original_strategies = create_original_strategies_data()
        logger.info(f"Created data for {len(original_strategies)} original strategies")
        
        # Get new strategies data
        new_strategies = create_new_strategies_data()
        logger.info(f"Created data for {len(new_strategies)} new strategies")
        
        # Combine all strategies
        all_strategies = original_strategies + new_strategies
        logger.info(f"Total strategies to insert: {len(all_strategies)}")
        
        # Clear existing strategies
        mongodb_manager.strategies_collection.delete_many({})
        logger.info("Cleared existing strategies from database")
        
        # Insert all strategies
        if all_strategies:
            result = mongodb_manager.strategies_collection.insert_many(all_strategies)
            logger.info(f"Inserted {len(result.inserted_ids)} strategies into MongoDB")
            return True
        else:
            logger.warning("No strategies to insert")
            return False
            
    except Exception as e:
        logger.error(f"Error restoring and adding strategies to MongoDB: {e}")
        return False
    finally:
        # Close MongoDB connection
        try:
            mongodb_manager.close_connection()
        except:
            pass

def main():
    """Main function to restore original strategies and add new strategies."""
    logger.info("Starting strategy restoration and addition process")
    
    try:
        # Restore and add strategies
        success = restore_and_add_strategies()
        
        if success:
            logger.info("Successfully restored original strategies and added new strategies to MongoDB")
            print("Successfully restored original strategies and added new strategies to MongoDB")
        else:
            logger.error("Failed to restore and add strategies to MongoDB")
            print("Failed to restore and add strategies to MongoDB")
            
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

