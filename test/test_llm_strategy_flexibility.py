#!/usr/bin/env python3
"""
Comprehensive test script to verify LLM strategy flexibility with different providers.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy

def test_llm_provider_flexibility():
    """Test that LLM strategy can work with different providers."""
    print("Testing LLM strategy flexibility with different providers...")

    # Test 1: Google Gemini
    print("\n1. Testing Google Gemini configuration:")
    gemini_params = {
        'llm_config': {
            'api_url': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-pro:generateContent',
            'api_key_env_var': 'GEMINI_API_KEY',
            'model': 'gemini-2.0-pro',
            'timeout': 60
        }
    }

    # Set test API key
    os.environ['GEMINI_API_KEY'] = 'test_gemini_key_12345'

    gemini_strategy = LLMFundamentalStrategy('Test Gemini Strategy', gemini_params)
    print(f"   API URL: {gemini_strategy.llm_config['api_url']}")
    print(f"   Model: {gemini_strategy.llm_config['model']}")
    print(f"   API Key: {gemini_strategy.llm_config['api_key']}")

    # Test 2: OpenAI
    print("\n2. Testing OpenAI configuration:")
    openai_params = {
        'llm_config': {
            'api_url': 'https://api.openai.com/v1/chat/completions',
            'api_key_env_var': 'OPENAI_API_KEY',
            'model': 'gpt-4',
            'timeout': 60
        }
    }

    # Set test API key
    os.environ['OPENAI_API_KEY'] = 'test_openai_key_67890'

    openai_strategy = LLMFundamentalStrategy('Test OpenAI Strategy', openai_params)
    print(f"   API URL: {openai_strategy.llm_config['api_url']}")
    print(f"   Model: {openai_strategy.llm_config['model']}")
    print(f"   API Key: {openai_strategy.llm_config['api_key']}")

    # Test 3: Anthropic
    print("\n3. Testing Anthropic configuration:")
    anthropic_params = {
        'llm_config': {
            'api_url': 'https://api.anthropic.com/v1/messages',
            'api_key_env_var': 'ANTHROPIC_API_KEY',
            'model': 'claude-3-opus',
            'timeout': 60
        }
    }

    # Set test API key
    os.environ['ANTHROPIC_API_KEY'] = 'test_anthropic_key_abcde'

    anthropic_strategy = LLMFundamentalStrategy('Test Anthropic Strategy', anthropic_params)
    print(f"   API URL: {anthropic_strategy.llm_config['api_url']}")
    print(f"   Model: {anthropic_strategy.llm_config['model']}")
    print(f"   API Key: {anthropic_strategy.llm_config['api_key']}")

    # Verify all strategies correctly read their respective API keys
    if (gemini_strategy.llm_config['api_key'] == 'test_gemini_key_12345' and
        openai_strategy.llm_config['api_key'] == 'test_openai_key_67890' and
        anthropic_strategy.llm_config['api_key'] == 'test_anthropic_key_abcde'):
        print("\n✓ All strategies correctly read API keys from their respective environment variables")
        return True
    else:
        print("\n✗ ERROR: Strategies did not read API keys correctly")
        return False

def test_database_configuration_integration():
    """Test that strategy correctly uses database configuration."""
    print("\n\nTesting database configuration integration...")

    # Simulate database configuration
    database_params = {
        'llm_config': {
            'api_url': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-pro:generateContent',
            'api_key_env_var': 'GEMINI_API_KEY',
            'model': 'gemini-2.0-pro',
            'timeout': 60
        }
    }

    strategy = LLMFundamentalStrategy('Database Config Test', database_params)

    # Verify configuration matches database values
    llm_config = database_params['llm_config']
    if (strategy.llm_config['api_url'] == llm_config['api_url'] and
        strategy.llm_config['model'] == llm_config['model'] and
        strategy.llm_config['timeout'] == llm_config['timeout']):
        print("✓ Strategy correctly uses database configuration parameters")
        return True
    else:
        print("✗ ERROR: Strategy does not match database configuration")
        return False

if __name__ == "__main__":
    print("=== LLM Strategy Flexibility Test ===")

    success1 = test_llm_provider_flexibility()
    success2 = test_database_configuration_integration()

    if success1 and success2:
        print("\n🎉 All tests passed! LLM strategy is flexible and correctly configured.")
        print("\nKey improvements:")
        print("1. API key environment variable name is configurable via database")
        print("2. Strategy can work with different LLM providers")
        print("3. Configuration is fully dynamic from database")
        print("4. No hardcoded values except for default fallbacks")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

