#!/usr/bin/env python
# coding=utf-8

import sys
import os

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy

def test_actual_execution():
    """Test the actual execution flow to see why profit forecast is empty"""
    print("Testing actual execution flow...")

    # Create an instance of the strategy
    strategy = LLMFundamentalStrategy()

    # Test with a sample stock code
    stock_code = "000001"  # 平安银行

    try:
        # Simulate the actual execution flow
        print("\n1. Simulating analyze_stock_fundamentals method...")

        # Get all the data that would be used in analyze_stock_fundamentals
        stock_info = strategy.get_stock_info(stock_code)
        financial_data = strategy.get_financial_data(stock_code)
        financial_ratios = strategy.calculate_financial_ratios(financial_data)
        industry_info = strategy.get_industry_info(stock_code)
        profit_forecast = strategy.get_profit_forecast(stock_code)

        print(f"Stock info: {stock_info.get('代码', 'N/A')} - {stock_info.get('名称', 'N/A')}")
        print(f"Financial data sections: {list(financial_data.keys())}")
        print(f"Financial ratios: {len(financial_ratios)} ratios")
        print(f"Industry info: {industry_info}")
        print(f"Profit forecast: {profit_forecast}")
        print(f"Profit forecast length: {len(profit_forecast)}")

        # Now test create_analysis_prompt with the actual data
        print("\n2. Testing create_analysis_prompt with actual data...")
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

        print("\n3. Profit forecast section in user prompt:")
        for line in profit_forecast_lines:
            print(f"  {line}")

        # Check if the profit forecast data is actually empty
        if profit_forecast:
            print(f"\n4. Profit forecast data is NOT empty, it contains:")
            for period, data in profit_forecast.items():
                print(f"  Period '{period}': {len(data)} fields")
                for key, value in list(data.items())[:5]:  # Show first 5 fields
                    print(f"    {key}: {value}")
        else:
            print(f"\n4. Profit forecast data IS empty: {profit_forecast}")

        # Let's also check what happens when we filter the profit forecast
        print("\n5. Testing profit forecast filtering...")
        filtered_profit_forecast = strategy._filter_profit_forecast_fields(profit_forecast)
        print(f"Filtered profit forecast: {filtered_profit_forecast}")
        print(f"Filtered profit forecast length: {len(filtered_profit_forecast)}")

    except Exception as e:
        print(f"Error testing actual execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing actual execution flow to debug profit forecast...")
    test_actual_execution()
    print("\nTest completed!")

