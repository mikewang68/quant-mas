#!/usr/bin/env python3
"""
Script to insert strategy information into MongoDB database.
This script extracts information from strategy classes and inserts them into 
the MongoDB stock database strategies collection, following the existing structure.
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

def create_strategies_data():
    """Create strategies data following the existing MongoDB structure."""
    strategies_data = [
        {
            "name": "MA_Crossover",
            "type": "trend_following",
            "description": "移动平均线交叉策略：当短期移动平均线向上穿越长期移动平均线时产生买入信号，向下穿越时产生卖出信号。",
            "parameters": {
                "short_period": 5,
                "long_period": 20,
                "max_position_ratio": 0.1
            }
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
            }
        },
        {
            "name": "Bollinger_Bands",
            "type": "volatility",
            "description": "布林带策略：当价格向下穿越布林带下轨时产生买入信号，向上穿越布林带上轨时产生卖出信号。",
            "parameters": {
                "period": 20,
                "std_dev": 2,
                "max_position_ratio": 0.1
            }
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
            }
        },
        {
            "name": "Volume",
            "type": "volume",
            "description": "成交量策略：当成交量显著高于平均值时产生买入信号，显著低于平均值时产生卖出信号。",
            "parameters": {
                "period": 20,
                "threshold": 1.5,
                "max_position_ratio": 0.1
            }
        },
        {
            "name": "Mean_Reversion",
            "type": "mean_reversion",
            "description": "均值回归策略：当价格显著偏离移动平均线下方时产生买入信号，显著偏离上方时产生卖出信号。",
            "parameters": {
                "period": 20,
                "std_dev_multiplier": 2,
                "max_position_ratio": 0.1
            }
        },
        {
            "name": "Momentum",
            "type": "momentum",
            "description": "动量策略：当动量指标转正时产生买入信号，转负时产生卖出信号。",
            "parameters": {
                "period": 14,
                "threshold": 0,
                "max_position_ratio": 0.1
            }
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
            }
        },
        {
            "name": "Support_Resistance",
            "type": "support_resistance",
            "description": "支撑阻力策略：当价格从支撑位反弹时产生买入信号，从阻力位回落时产生卖出信号。",
            "parameters": {
                "period": 20,
                "threshold": 0.02,
                "max_position_ratio": 0.1
            }
        },
        {
            "name": "Trend_Following",
            "type": "trend_following",
            "description": "趋势跟踪策略：当价格突破移动平均线时产生买入信号，跌破时产生卖出信号。",
            "parameters": {
                "period": 50,
                "max_position_ratio": 0.1
            }
        },
        {
            "name": "Breakout",
            "type": "breakout",
            "description": "突破策略：当价格突破阻力位时产生买入信号，跌破支撑位时产生卖出信号。",
            "parameters": {
                "period": 20,
                "buffer": 0.01,
                "max_position_ratio": 0.1
            }
        },
        {
            "name": "Scalping",
            "type": "scalping",
            "description": "高频交易策略：基于短期价格变动产生交易信号，适用于高频交易。",
            "parameters": {
                "period": 5,
                "threshold": 0.005,
                "max_position_ratio": 0.1
            }
        }
    ]
    
    # Adding a new field as requested in the task
    for strategy in strategies_data:
        strategy["created_at"] = "2025-08-15"
    
    return strategies_data

def insert_strategies_to_mongodb(strategies_data: list):
    """Insert strategies information into MongoDB."""
    try:
        # Initialize MongoDB manager
        mongodb_manager = MongoDBManager()
        
        # Clear existing strategies (optional, to avoid duplicates)
        mongodb_manager.strategies_collection.delete_many({})
        logger.info("Cleared existing strategies from database")
        
        # Insert new strategies
        if strategies_data:
            result = mongodb_manager.strategies_collection.insert_many(strategies_data)
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
    """Main function to create and insert strategy information."""
    logger.info("Starting strategy information creation and insertion process")
    
    try:
        # Create strategies data
        strategies_data = create_strategies_data()
        logger.info(f"Created data for {len(strategies_data)} strategies")
        
        # Insert into MongoDB
        success = insert_strategies_to_mongodb(strategies_data)
        
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

