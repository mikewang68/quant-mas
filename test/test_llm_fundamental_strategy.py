#!/usr/bin/env python3
"""
Test program for LLM Fundamental Strategy
Analyzes stock 300339 using LLM-based fundamental analysis
"""

import os
import sys
import json

# Add project root to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy


def main():
    # Set up LLM configuration
    # Note: You need to set the GEMINI_API_KEY environment variable
    # Example: export GEMINI_API_KEY="your_api_key_here"

    if not os.getenv("GEMINI_API_KEY"):
        print("Warning: GEMINI_API_KEY environment variable not set")
        print("Please set it with: export GEMINI_API_KEY='your_api_key_here'")
        # For testing purposes, we can still create the strategy but it won't work without the API key

    # Create LLM Fundamental Strategy instance
    strategy_params = {
        "llm_config": {
            "api_url": "https://api.deepseek.com",
            "api_key_env_var": "DEEPSEEK_API_KEY",
            "model": "deepseek-chat",
            "timeout": 60,
        }
    }

    strategy = LLMFundamentalStrategy(
        name="Test LLM Fundamental Strategy", params=strategy_params
    )

    # Analyze stock 300339
    stock_code = "300339"
    print(f"Analyzing stock {stock_code} using LLM Fundamental Strategy...")

    try:
        result = strategy.analyze_stock_fundamentals(stock_code)

        # Output score and value
        print(f"\n--- Analysis Results for {stock_code} ---")
        print(f"Score: {result.get('score', 'N/A')}")
        print(f"Value: {result.get('value', 'N/A')}")
        print("----------------------------------------")

        # Also output the full result for debugging
        print("\nFull result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"Error analyzing stock {stock_code}: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
