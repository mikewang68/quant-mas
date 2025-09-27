#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for SignalGenerationV1Strategy LLM functionality
"""

import sys
import os
import logging

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.signal_generation_v1_strategy import SignalGenerationV1Strategy
from config.mongodb_config import MongoDBConfig
from pymongo import MongoClient
from data.database_operations import DatabaseOperations

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_llm_config_loading():
    """Test LLM configuration loading"""
    print("Testing LLM configuration loading...")

    # Create strategy instance
    strategy = SignalGenerationV1Strategy()

    # Check if LLM config is loaded
    print(f"LLM Config: {strategy.llm_config}")
    print(f"LLM Name: {strategy.llm_name}")

    # Verify config has required fields
    required_fields = ['api_url', 'api_key', 'model', 'timeout', 'provider', 'name']
    for field in required_fields:
        if field in strategy.llm_config:
            print(f"  {field}: {strategy.llm_config[field]}")
        else:
            print(f"  {field}: MISSING")

    return strategy.llm_config

def test_llm_analysis():
    """Test LLM analysis functionality"""
    print("\nTesting LLM analysis...")

    # Create strategy instance
    strategy = SignalGenerationV1Strategy()

    # Sample strategy data for testing
    sample_strategy_data = [
        {
            'strategy': 'technical_macd',
            'score': 0.85,
            'value': 'MACD金叉，上涨趋势强劲，建议买入'
        },
        {
            'strategy': 'fundamental_pe_ratio',
            'score': 0.65,
            'value': '市盈率合理，在行业中等水平'
        },
        {
            'strategy': 'public_opinion_sentiment',
            'score': 0.90,
            'value': '舆情积极，市场关注度高'
        }
    ]

    # Test AI analysis
    try:
        ai_result = strategy._analyze_with_ai(sample_strategy_data)
        print(f"AI Analysis Result: {ai_result}")
        return ai_result
    except Exception as e:
        print(f"Error in AI analysis: {e}")
        return None

def test_database_connection():
    """Test database connection and strategy config retrieval"""
    print("\nTesting database connection...")

    try:
        # Load MongoDB configuration
        mongodb_config = MongoDBConfig()
        config = mongodb_config.get_mongodb_config()
        print(f"MongoDB Config: {config}")

        # Connect to MongoDB
        if config.get("username") and config.get("password"):
            # With authentication
            uri = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?authSource={config.get('auth_database', 'admin')}"
        else:
            # Without authentication
            uri = f"mongodb://{config['host']}:{config['port']}/"

        client = MongoClient(uri)
        db = client[config["database"]]

        # Get strategies collection
        strategies_collection = db[mongodb_config.get_collection_name("strategies")]

        # Find signal generation strategy
        strategy_record = strategies_collection.find_one({"name": "信号生成V1"})
        if strategy_record:
            print(f"Strategy Record: {strategy_record}")
            if "parameters" in strategy_record:
                print(f"Strategy Parameters: {strategy_record['parameters']}")
                if "llm_name" in strategy_record["parameters"]:
                    print(f"LLM Name in DB: {strategy_record['parameters']['llm_name']}")
        else:
            print("Strategy record not found")

        # Get config collection
        config_collection = db[mongodb_config.get_collection_name("config")]

        # Get LLM configurations
        config_record = config_collection.find_one()
        if config_record and "llm_configs" in config_record:
            print(f"LLM Configs in DB: {config_record['llm_configs']}")

    except Exception as e:
        print(f"Error in database connection: {e}")

if __name__ == "__main__":
    print("Running SignalGenerationV1Strategy LLM tests...")

    # Test database connection and config retrieval
    test_database_connection()

    # Test LLM config loading
    llm_config = test_llm_config_loading()

    # Test LLM analysis
    ai_result = test_llm_analysis()

    print("\nTest completed.")

