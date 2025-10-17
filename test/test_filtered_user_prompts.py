#!/usr/bin/env python
# coding=utf-8

import sys
import os

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy

def test_filtered_user_prompts():
    """Test that user prompts don't contain stock code and stock name fields"""
    print("Testing filtered user prompts...")

    # Create an instance of the strategy
    strategy = LLMFundamentalStrategy()

    # Test with a sample stock code
    stock_code = "000001"  # 平安银行

    try:
        # Get financial data
        financial_data = strategy.get_financial_data(stock_code)
        print(f"Retrieved financial data for {stock_code}")

        # Test the _filter_financial_data_fields method
        filtered_financial_data = strategy._filter_financial_data_fields(financial_data)
        print(f"Filtered financial data: {len(filtered_financial_data)} sections")

        # Check if stock code and stock name fields are removed
        for section_name, section_data in filtered_financial_data.items():
            if isinstance(section_data, dict):
                excluded_fields = ["股票代码", "股票简称", "代码", "名称"]
                for field in excluded_fields:
                    if field in section_data:
                        print(f"ERROR: Field '{field}' found in {section_name} section")
                    else:
                        print(f"OK: Field '{field}' not found in {section_name} section")

        # Get profit forecast data
        profit_forecast = strategy.get_profit_forecast(stock_code)
        print(f"Retrieved profit forecast data for {stock_code}")

        # Test the _filter_profit_forecast_fields method
        filtered_profit_forecast = strategy._filter_profit_forecast_fields(profit_forecast)
        print(f"Filtered profit forecast data: {len(filtered_profit_forecast)} periods")

        # Check if stock code and stock name fields are removed from profit forecast
        for period, period_data in filtered_profit_forecast.items():
            if isinstance(period_data, dict):
                excluded_fields = ["股票代码", "股票简称", "代码", "名称"]
                for field in excluded_fields:
                    if field in period_data:
                        print(f"ERROR: Field '{field}' found in profit forecast period {period}")
                    else:
                        print(f"OK: Field '{field}' not found in profit forecast period {period}")

        # Test the create_analysis_prompt method
        stock_info = strategy.get_stock_info(stock_code)
        financial_ratios = strategy.calculate_financial_ratios(financial_data)
        industry_info = strategy.get_industry_info(stock_code)

        user_prompt = strategy.create_analysis_prompt(
            stock_info, financial_data, financial_ratios, industry_info, profit_forecast
        )

        print(f"Created user prompt with {len(user_prompt.get('content', ''))} characters")

        # Check if the user prompt content contains stock code and stock name fields
        user_prompt_content = user_prompt.get("content", "")
        excluded_fields = ["股票代码", "股票简称", "代码", "名称"]

        for field in excluded_fields:
            if field in user_prompt_content:
                print(f"ERROR: Field '{field}' found in user prompt content")
            else:
                print(f"OK: Field '{field}' not found in user prompt content")

    except Exception as e:
        print(f"Error testing filtered user prompts: {e}")

if __name__ == "__main__":
    print("Testing filtered user prompts without stock code and stock name fields...")
    test_filtered_user_prompts()
    print("\nTest completed!")

