"""
Test script to verify LLM configuration loading from database
"""

import sys
import os

# Add project root to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from strategies.llm_fundamental_strategy import LLMFundamentalStrategy

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_llm_config_loading():
    """Test LLM configuration loading from database"""
    print("Testing LLM configuration loading from database...")

    # Test with default configuration (no config name specified)
    print("\n1. Testing with default configuration:")
    strategy1 = LLMFundamentalStrategy()
    print(f"   LLM Config: {strategy1.llm_config}")

    # Test with specific configuration name
    print("\n2. Testing with specific configuration name:")
    strategy2 = LLMFundamentalStrategy(params={"llm_config_name": "default"})
    print(f"   LLM Config: {strategy2.llm_config}")

    # Test with non-existent configuration name (should fallback to default)
    print("\n3. Testing with non-existent configuration name:")
    strategy3 = LLMFundamentalStrategy(params={"llm_config_name": "non_existent"})
    print(f"   LLM Config: {strategy3.llm_config}")

    print("\nTest completed!")

if __name__ == "__main__":
    test_llm_config_loading()

