#!/usr/bin/env python
# coding=utf-8

import sys
import os

# Add the project root to the Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy

def trace_profit_forecast_flow():
    """Trace the exact flow of profit forecast data"""
    print("Tracing profit forecast data flow...")

    # Test with a sample stock code
    stock_code = "000001"  # 平安银行

    try:
        # Create an instance of the strategy
        strategy = LLMFundamentalStrategy()

        print("\n1. Calling get_profit_forecast directly...")
        profit_forecast = strategy.get_profit_forecast(stock_code)
        print(f"get_profit_forecast result: {profit_forecast}")
        print(f"Type: {type(profit_forecast)}")
        print(f"Length: {len(profit_forecast)}")

        print("\n2. Testing _filter_profit_forecast_fields...")
        filtered_profit_forecast = strategy._filter_profit_forecast_fields(profit_forecast)
        print(f"Filtered result: {filtered_profit_forecast}")
        print(f"Type: {type(filtered_profit_forecast)}")
        print(f"Length: {len(filtered_profit_forecast)}")

        print("\n3. Testing create_analysis_prompt with actual data...")
        stock_info = strategy.get_stock_info(stock_code)
        financial_data = strategy.get_financial_data(stock_code)
        financial_ratios = strategy.calculate_financial_ratios(financial_data)
        industry_info = strategy.get_industry_info(stock_code)

        print(f"Profit forecast passed to create_analysis_prompt: {profit_forecast}")

        user_prompt = strategy.create_analysis_prompt(
            stock_info, financial_data, financial_ratios, industry_info, profit_forecast
        )

        user_prompt_content = user_prompt.get("content", "")
        print(f"\n4. User prompt content length: {len(user_prompt_content)}")

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

        print("\n5. Profit forecast section in user prompt:")
        for line in profit_forecast_lines:
            print(f"  {line}")

        # Check if the profit forecast data is actually in the JSON
        import json
        try:
            # Find the JSON part after "盈利预测:"
            profit_forecast_json_str = ""
            in_json = False
            for line in profit_forecast_lines:
                if line.strip() == "{":
                    in_json = True
                if in_json:
                    profit_forecast_json_str += line
                if line.strip() == "}":
                    break

            if profit_forecast_json_str:
                parsed_json = json.loads(profit_forecast_json_str)
                print(f"\n6. Parsed profit forecast JSON: {parsed_json}")
            else:
                print("\n6. No JSON found in profit forecast section")

        except json.JSONDecodeError as e:
            print(f"\n6. JSON decode error: {e}")

    except Exception as e:
        print(f"Error tracing profit forecast flow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Tracing profit forecast data flow...")
    trace_profit_forecast_flow()
    print("\nTrace completed!")

