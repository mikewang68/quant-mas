#!/usr/bin/env python3
"""
Test script to verify fixed financial data fetching and calculation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_financial_data_fix():
    """Test the fixed financial data fetching and calculation"""
    print("=== Testing Fixed Financial Data Fetching ===")

    # Create strategy instance
    strategy = LLMFundamentalStrategy(name="Test Strategy")

    # Test with a stock that has data
    test_stock = "000985"  # 大庆华科

    print(f"\n1. Testing financial data fetching for {test_stock}")

    # Get financial data
    financial_data = strategy.get_financial_data(test_stock)

    print(f"Financial indicators keys: {list(financial_data['financial_indicators'].keys())[:10]}")
    print(f"Balance sheet keys: {list(financial_data['balance_sheet'].keys())[:10]}")
    print(f"Income statement keys: {list(financial_data['income_statement'].keys())[:10]}")

    # Test get_latest_value function
    print(f"\n2. Testing get_latest_value function")

    # Test with financial indicators
    if '净利润' in financial_data['financial_indicators']:
        net_income = strategy.get_latest_value(financial_data['financial_indicators'], '净利润')
        print(f"Latest net income: {net_income}")

    if '营业收入' in financial_data['financial_indicators']:
        revenue = strategy.get_latest_value(financial_data['financial_indicators'], '营业收入')
        print(f"Latest revenue: {revenue}")

    # Test with balance sheet
    if '资产总计' in financial_data['balance_sheet']:
        total_assets = strategy.get_latest_value(financial_data['balance_sheet'], '资产总计')
        print(f"Latest total assets: {total_assets}")

    # Test financial ratios calculation
    print(f"\n3. Testing financial ratios calculation")

    financial_ratios = strategy.calculate_financial_ratios(financial_data)
    print(f"Calculated financial ratios: {financial_ratios}")

    # Test analysis prompt creation
    print(f"\n4. Testing analysis prompt creation")

    stock_info = strategy.get_stock_info(test_stock)
    industry_info = strategy.get_industry_info(test_stock)

    user_prompt = strategy.create_analysis_prompt(
        stock_info, financial_data, financial_ratios, industry_info
    )

    print(f"User prompt type: {type(user_prompt)}")
    print(f"User prompt keys: {user_prompt.keys()}")
    print(f"User prompt content preview: {user_prompt['content'][:200]}...")

    print(f"\n=== Test Completed ===")

if __name__ == "__main__":
    test_financial_data_fix()

