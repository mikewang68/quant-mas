#!/usr/bin/env python3
"""
Test to verify exactly what system prompt is being sent to the LLM
"""

import os
import sys

# Add project root to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy


def main():
    print("=== System Prompt Verification Test ===\n")

    # Create LLM Fundamental Strategy instance
    strategy = LLMFundamentalStrategy(
        name="LLM基本面分析策略",
        params={"llm_config_name": "qwen3-4B"}
    )

    # Test loading system prompt
    print("1. Testing _load_system_prompt method...")
    system_prompt = strategy._load_system_prompt()

    print(f"System prompt role: {system_prompt.get('role', 'N/A')}")
    print(f"System prompt content length: {len(system_prompt.get('content', ''))} characters")
    print(f"System prompt content:\n{system_prompt.get('content', 'N/A')}")
    print("\n" + "="*80 + "\n")

    # Test creating user prompt
    print("2. Testing create_analysis_prompt method...")
    stock_info = {"股票代码": "300339", "股票简称": "润和软件", "行业": "软件开发"}
    financial_data = {}
    financial_ratios = {
        "roe": 0.22169035153328348,
        "roa": 0.10360884955752214,
        "gross_margin": 0.33976742086646805,
        "net_margin": 0.19216584188886426,
        "current_ratio": 1.0748082707785698,
        "quick_ratio": 0.7164778732283678,
        "debt_to_equity": 1.1406909479942815,
        "asset_turnover": 0.3413193277310924,
        "revenue_growth": -0.4306028037383178,
        "earnings_growth": -0.562475709288768
    }
    industry_info = {
        "行业": "软件开发",
        "行业平均水平": {
            "roe": 0.08,
            "pe": 15.0,
            "debt_to_equity": 0.5
        }
    }

    user_prompt = strategy.create_analysis_prompt(stock_info, financial_data, financial_ratios, industry_info)

    print(f"User prompt role: {user_prompt.get('role', 'N/A')}")
    print(f"User prompt content length: {len(user_prompt.get('content', ''))} characters")
    print(f"User prompt content:\n{user_prompt.get('content', 'N/A')}")
    print("\n" + "="*80 + "\n")

    # Test the actual LLM call
    print("3. Testing actual LLM call...")
    try:
        result = strategy.get_llm_analysis(user_prompt)
        print(f"LLM result score: {result.get('score', 'N/A')}")
        print(f"LLM result value type: {type(result.get('value', 'N/A'))}")
        print(f"LLM result value length: {len(result.get('value', ''))} characters")
        print(f"LLM result value preview:\n{str(result.get('value', 'N/A'))[:500]}...")
    except Exception as e:
        print(f"LLM call failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

