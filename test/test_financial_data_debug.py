#!/usr/bin/env python3
"""
Debug script to check financial data fetching and calculation issues
"""

import akshare as ak
import pandas as pd
import json
from typing import Dict, Any


def debug_financial_data(stock_code: str = "000985"):
    """Debug financial data fetching for a specific stock"""
    print(f"=== Debugging financial data for stock {stock_code} ===")

    # Test stock individual info
    print("\n1. Stock individual info:")
    try:
        stock_info = ak.stock_individual_info_em(symbol=stock_code)
        print(f"Stock info shape: {stock_info.shape}")
        print(f"Stock info columns: {stock_info.columns.tolist()}")
        print(f"Stock info sample:\n{stock_info.head()}")
    except Exception as e:
        print(f"Error getting stock info: {e}")

    # Test financial indicators
    print("\n2. Financial indicators:")
    try:
        financial_indicators = ak.stock_financial_abstract_ths(symbol=stock_code)
        print(f"Financial indicators shape: {financial_indicators.shape}")
        print(f"Financial indicators columns: {financial_indicators.columns.tolist()}")
        print(f"Financial indicators sample:\n{financial_indicators.head()}")
        if not financial_indicators.empty:
            print(f"Available indicators: {financial_indicators['item'].tolist()}")
    except Exception as e:
        print(f"Error getting financial indicators: {e}")

    # Test balance sheet
    print("\n3. Balance sheet:")
    try:
        balance_sheet = ak.stock_financial_debt_ths(symbol=stock_code)
        print(f"Balance sheet shape: {balance_sheet.shape}")
        print(f"Balance sheet columns: {balance_sheet.columns.tolist()}")
        print(f"Balance sheet sample:\n{balance_sheet.head()}")
        if not balance_sheet.empty:
            print(f"Available balance sheet items: {balance_sheet['item'].tolist()}")
    except Exception as e:
        print(f"Error getting balance sheet: {e}")

    # Test income statement
    print("\n4. Income statement:")
    try:
        income_statement = ak.stock_financial_benefit_ths(symbol=stock_code)
        print(f"Income statement shape: {income_statement.shape}")
        print(f"Income statement columns: {income_statement.columns.tolist()}")
        print(f"Income statement sample:\n{income_statement.head()}")
        if not income_statement.empty:
            print(f"Available income statement items: {income_statement['item'].tolist()}")
    except Exception as e:
        print(f"Error getting income statement: {e}")

    # Test cash flow
    print("\n5. Cash flow:")
    try:
        cash_flow = ak.stock_financial_cash_ths(symbol=stock_code)
        print(f"Cash flow shape: {cash_flow.shape}")
        print(f"Cash flow columns: {cash_flow.columns.tolist()}")
        print(f"Cash flow sample:\n{cash_flow.head()}")
        if not cash_flow.empty:
            print(f"Available cash flow items: {cash_flow['item'].tolist()}")
    except Exception as e:
        print(f"Error getting cash flow: {e}")


def test_data_structure():
    """Test the data structure returned by akshare"""
    print("\n=== Testing data structure ===")

    # Test with a known working stock
    test_stock = "000001"  # 平安银行

    try:
        # Get financial indicators
        indicators = ak.stock_financial_abstract_ths(symbol=test_stock)
        print(f"Financial indicators for {test_stock}:")
        print(f"Shape: {indicators.shape}")
        print(f"Columns: {indicators.columns.tolist()}")

        if not indicators.empty:
            # Check the structure
            print(f"\nFirst few rows:")
            for i, row in indicators.head().iterrows():
                print(f"Row {i}: {row['item']} - {row.to_dict()}")

            # Check if we have the expected columns
            expected_columns = ['item', '2023-12-31', '2022-12-31', '2021-12-31']
            actual_columns = indicators.columns.tolist()
            print(f"\nExpected columns: {expected_columns}")
            print(f"Actual columns: {actual_columns}")

            # Check specific items
            key_items = ['每股收益', '每股净资产', '净资产收益率', '营业收入', '净利润']
            for item in key_items:
                if item in indicators['item'].values:
                    item_data = indicators[indicators['item'] == item]
                    print(f"\n{item}: {item_data.iloc[0].to_dict()}")
                else:
                    print(f"\n{item}: NOT FOUND")
    except Exception as e:
        print(f"Error testing data structure: {e}")


if __name__ == "__main__":
    debug_financial_data("000985")  # 大庆华科
    test_data_structure()

