#!/usr/bin/env python3
"""
Test to verify the LLM system prompt is being loaded correctly
"""

import os
import sys

# Add project root to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy


def main():
    print("=== Testing LLM System Prompt Loading ===\n")

    # Create LLM Fundamental Strategy instance
    strategy = LLMFundamentalStrategy(
        name="LLM基本面分析策略",
        params={"llm_config_name": "qwen3-4B"}
    )

    # Test system prompt loading
    print("Loading system prompt...")
    system_prompt = strategy._load_system_prompt()

    print("\n=== System Prompt Content ===")
    print(system_prompt.get('content', 'No content found'))
    print("\n=== System Prompt Role ===")
    print(system_prompt.get('role', 'No role found'))

    # Check if the config file exists
    print("\n=== Checking Config File ===")
    config_path = "config/fund_sys_prompt.md"
    if os.path.exists(config_path):
        print(f"Config file exists: {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"Config file content length: {len(content)} characters")
            print(f"First 500 chars:\n{content[:500]}...")
    else:
        print(f"Config file does NOT exist: {config_path}")


if __name__ == "__main__":
    main()

