#!/usr/bin/env python
# coding=utf-8

import sys
import os

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy

def test_financial_data():
    """Test the modified get_financial_data function"""
    print("Testing get_financial_data function...")

    # Create an instance of the strategy
    strategy = LLMFundamentalStrategy()

    # Test with a sample stock code
    stock_code = "000001"  # 平安银行

    try:
        financial_data = strategy.get_financial_data(stock_code)
        print(f"Successfully retrieved financial data for {stock_code}")

        # Check if data was retrieved
        if financial_data["performance_report"]:
            print(f"Performance report data: {len(financial_data['performance_report'])} fields")
        else:
            print("No performance report data found")

        if financial_data["balance_sheet"]:
            print(f"Balance sheet data: {len(financial_data['balance_sheet'])} fields")
        else:
            print("No balance sheet data found")

        if financial_data["income_statement"]:
            print(f"Income statement data: {len(financial_data['income_statement'])} fields")
        else:
            print("No income statement data found")

        if financial_data["cash_flow"]:
            print(f"Cash flow data: {len(financial_data['cash_flow'])} fields")
        else:
            print("No cash flow data found")

    except Exception as e:
        print(f"Error testing get_financial_data: {e}")

def test_profit_forecast():
    """Test the modified get_profit_forecast function"""
    print("\nTesting get_profit_forecast function...")

    # Create an instance of the strategy
    strategy = LLMFundamentalStrategy()

    # Test with a sample stock code
    stock_code = "000001"  # 平安银行

    try:
        profit_forecast = strategy.get_profit_forecast(stock_code)
        print(f"Successfully retrieved profit forecast data for {stock_code}")

        # Check if data was retrieved
        if profit_forecast:
            print(f"Profit forecast data: {len(profit_forecast)} periods")
            for period, data in profit_forecast.items():
                print(f"  Period {period}: {len(data)} fields")
        else:
            print("No profit forecast data found")

    except Exception as e:
        print(f"Error testing get_profit_forecast: {e}")

if __name__ == "__main__":
    print("Testing modified financial data functions with MongoDB collections...")
    test_financial_data()
    test_profit_forecast()
    print("\nTest completed!")

