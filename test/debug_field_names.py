#!/usr/bin/env python3
"""
Debug script to check actual field names in financial data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def debug_field_names():
    """Debug actual field names in financial data"""
    print("=== Debugging Field Names ===")

    # Create strategy instance
    strategy = LLMFundamentalStrategy(name="Debug Strategy")

    # Test with a stock
    test_stock = "000985"  # 大庆华科

    # Get financial data
    financial_data = strategy.get_financial_data(test_stock)

    print("\n1. Financial Indicators Fields:")
    indicators = financial_data['financial_indicators']
    print(f"Available fields: {list(indicators.keys())}")

    # Check specific fields we need
    needed_indicators = ['净利润', '营业收入', '营业成本', '资产总计', '股东权益合计', '流动资产', '流动负债', '负债合计']
    for field in needed_indicators:
        if field in indicators:
            print(f"  {field}: {list(indicators[field].values())[-3:]}")  # Last 3 values
        else:
            print(f"  {field}: NOT FOUND")

    print("\n2. Balance Sheet Fields:")
    balance_sheet = financial_data['balance_sheet']
    print(f"Available fields: {list(balance_sheet.keys())[:20]}")  # First 20 fields

    # Check specific balance sheet fields
    needed_balance = ['*资产合计', '*负债合计', '*所有者权益（或股东权益）合计', '流动资产', '流动负债']
    for field in needed_balance:
        if field in balance_sheet:
            print(f"  {field}: {list(balance_sheet[field].values())[-3:]}")
        else:
            print(f"  {field}: NOT FOUND")

    print("\n3. Income Statement Fields:")
    income_statement = financial_data['income_statement']
    print(f"Available fields: {list(income_statement.keys())[:20]}")

    # Check specific income statement fields
    needed_income = ['*净利润', '*营业总收入', '其中：营业收入', '其中：营业成本']
    for field in needed_income:
        if field in income_statement:
            print(f"  {field}: {list(income_statement[field].values())[-3:]}")
        else:
            print(f"  {field}: NOT FOUND")

    print("\n4. Testing get_latest_value with actual fields:")

    # Test with actual field names
    test_fields = [
        ('净利润', indicators),
        ('营业收入', indicators),
        ('*资产合计', balance_sheet),
        ('*负债合计', balance_sheet),
        ('*所有者权益（或股东权益）合计', balance_sheet),
        ('流动资产', balance_sheet),
        ('流动负债', balance_sheet),
        ('*净利润', income_statement),
        ('*营业总收入', income_statement),
        ('其中：营业收入', income_statement),
        ('其中：营业成本', income_statement)
    ]

    for field_name, data_dict in test_fields:
        if field_name in data_dict:
            value = strategy.get_latest_value(data_dict, field_name)
            print(f"  {field_name}: {value}")

if __name__ == "__main__":
    debug_field_names()

