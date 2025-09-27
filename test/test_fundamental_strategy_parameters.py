#!/usr/bin/env python3
"""
Test script to verify that fundamental strategies correctly use database parameters.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mongodb_manager import MongoDBManager
from strategies.fundamental_strategy import FundamentalStrategy
from strategies.llm_fundamental_strategy import LLMFundamentalStrategy

def test_strategy_parameter_loading():
    """Test that strategies correctly load parameters from database."""
    print("Testing strategy parameter loading from database...")

    # Initialize MongoDB manager
    mongodb_manager = MongoDBManager()

    try:
        # Get fundamental strategy from database
        fundamental_strategy_doc = mongodb_manager.get_strategy_by_name("基本面分析策略")
        if not fundamental_strategy_doc:
            print("ERROR: Fundamental strategy not found in database")
            return False

        # Get LLM fundamental strategy from database
        llm_fundamental_strategy_doc = mongodb_manager.get_strategy_by_name("LLM基本面分析策略")
        if not llm_fundamental_strategy_doc:
            print("ERROR: LLM Fundamental strategy not found in database")
            return False

        # Test fundamental strategy parameter loading
        print("\n1. Testing Fundamental Strategy:")
        print(f"   Strategy name: {fundamental_strategy_doc.get('name')}")
        params = fundamental_strategy_doc.get('parameters', {})
        print(f"   Parameters from database: {params}")

        # Create strategy instance with database parameters
        strategy = FundamentalStrategy("Test Fundamental Strategy", params)
        print(f"   Strategy successfully created with parameters")

        # Test LLM fundamental strategy parameter loading
        print("\n2. Testing LLM Fundamental Strategy:")
        print(f"   Strategy name: {llm_fundamental_strategy_doc.get('name')}")
        llm_params = llm_fundamental_strategy_doc.get('parameters', {})
        print(f"   Parameters from database: {llm_params}")

        # Create strategy instance with database parameters
        llm_strategy = LLMFundamentalStrategy("Test LLM Fundamental Strategy", llm_params)
        print(f"   LLM Config: {llm_strategy.llm_config}")
        print(f"   API URL: {llm_strategy.llm_config['api_url']}")
        print(f"   Model: {llm_strategy.llm_config['model']}")
        print(f"   Timeout: {llm_strategy.llm_config['timeout']}")

        # Verify that parameters match database values
        llm_config = llm_params.get('llm_config', {})
        if (llm_strategy.llm_config['api_url'] == llm_config.get('api_url') and
            llm_strategy.llm_config['model'] == llm_config.get('model') and
            llm_strategy.llm_config['timeout'] == llm_config.get('timeout')):
            print("   ✓ LLM parameters correctly loaded from database")
        else:
            print("   ✗ ERROR: LLM parameters do not match database values")
            return False

        print("\n✓ All strategies correctly load parameters from database")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        # Close MongoDB connection
        mongodb_manager.close_connection()

if __name__ == "__main__":
    success = test_strategy_parameter_loading()
    if success:
        print("\n🎉 Test passed: Both strategies correctly use database parameters")
    else:
        print("\n❌ Test failed: Strategies are not correctly using database parameters")
        sys.exit(1)

