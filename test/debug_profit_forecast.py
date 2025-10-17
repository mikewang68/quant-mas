#!/usr/bin/env python
# coding=utf-8

import sys
import os

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy
from config.mongodb_config import MongoDBConfig
from pymongo import MongoClient
import pandas as pd

def debug_profit_forecast():
    """Debug why profit forecast data is empty"""
    print("Debugging profit forecast data retrieval...")

    # Test with a sample stock code
    stock_code = "000001"  # 平安银行

    try:
        # First, let's check if there's any data in the fin_forecast collection
        print("\n1. Checking fin_forecast collection directly...")
        mongodb_config = MongoDBConfig()
        config = mongodb_config.get_mongodb_config()

        if config.get("username") and config.get("password"):
            uri = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?authSource={config.get('auth_database', 'admin')}"
        else:
            uri = f"mongodb://{config['host']}:{config['port']}/"

        client = MongoClient(uri)
        db = client["stock"]

        # Check total documents in fin_forecast collection
        total_docs = db["fin_forecast"].count_documents({})
        print(f"Total documents in fin_forecast collection: {total_docs}")

        # Check if specific stock code exists
        stock_doc = db["fin_forecast"].find_one({"_id": stock_code})
        if stock_doc:
            print(f"Found document for stock {stock_code} in fin_forecast:")
            for key, value in stock_doc.items():
                print(f"  {key}: {value}")
        else:
            print(f"No document found for stock {stock_code} in fin_forecast")

            # Check what stock codes are available
            print("\nChecking available stock codes in fin_forecast...")
            sample_docs = db["fin_forecast"].find().limit(5)
            for doc in sample_docs:
                print(f"  Available stock: {doc.get('_id', 'N/A')} - {doc.get('股票简称', 'N/A')}")

        # Now test the get_profit_forecast method
        print("\n2. Testing get_profit_forecast method...")
        strategy = LLMFundamentalStrategy()

        # Check if _profit_forecast_data is loaded
        if hasattr(strategy, '_profit_forecast_data'):
            print(f"_profit_forecast_data exists: {strategy._profit_forecast_data is not None}")
            if strategy._profit_forecast_data is not None:
                print(f"_profit_forecast_data shape: {strategy._profit_forecast_data.shape}")
                print(f"_profit_forecast_data columns: {list(strategy._profit_forecast_data.columns)}")
        else:
            print("_profit_forecast_data attribute does not exist")

        # Call get_profit_forecast
        profit_forecast = strategy.get_profit_forecast(stock_code)
        print(f"\n3. get_profit_forecast result: {profit_forecast}")
        print(f"Profit forecast data type: {type(profit_forecast)}")
        print(f"Profit forecast length: {len(profit_forecast)}")

        # Check if _profit_forecast_data was loaded after the call
        if hasattr(strategy, '_profit_forecast_data') and strategy._profit_forecast_data is not None:
            print(f"\n4. _profit_forecast_data after call:")
            print(f"Shape: {strategy._profit_forecast_data.shape}")
            print(f"Columns: {list(strategy._profit_forecast_data.columns)}")

            # Check if our stock code exists in the data
            code_column = None
            possible_code_columns = ["股票代码", "代码", "symbol", "stock_code"]
            for col in possible_code_columns:
                if col in strategy._profit_forecast_data.columns:
                    code_column = col
                    break

            if code_column:
                stock_data = strategy._profit_forecast_data[strategy._profit_forecast_data[code_column] == stock_code]
                print(f"\n5. Stock data in _profit_forecast_data:")
                print(f"Found {len(stock_data)} records for {stock_code}")
                if not stock_data.empty:
                    print("First record:")
                    print(stock_data.iloc[0])
            else:
                print("No valid stock code column found in _profit_forecast_data")

        # Test create_analysis_prompt
        print("\n6. Testing create_analysis_prompt...")
        stock_info = strategy.get_stock_info(stock_code)
        financial_data = strategy.get_financial_data(stock_code)
        financial_ratios = strategy.calculate_financial_ratios(financial_data)
        industry_info = strategy.get_industry_info(stock_code)

        user_prompt = strategy.create_analysis_prompt(
            stock_info, financial_data, financial_ratios, industry_info, profit_forecast
        )

        user_prompt_content = user_prompt.get("content", "")
        print(f"User prompt content length: {len(user_prompt_content)}")

        # Extract just the profit forecast section from the user prompt
        lines = user_prompt_content.split('\n')
        in_profit_forecast_section = False
        profit_forecast_lines = []

        for line in lines:
            if "盈利预测:" in line:
                in_profit_forecast_section = True
                profit_forecast_lines.append(line)
            elif in_profit_forecast_section:
                if line.strip() and not line.startswith("完整财务数据:"):
                    profit_forecast_lines.append(line)
                else:
                    break

        print("\n7. Profit forecast section in user prompt:")
        for line in profit_forecast_lines:
            print(f"  {line}")

    except Exception as e:
        print(f"Error debugging profit forecast: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Debugging profit forecast data retrieval...")
    debug_profit_forecast()
    print("\nDebug completed!")

