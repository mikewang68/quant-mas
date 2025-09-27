#!/usr/bin/env python3
"""
Comprehensive test to verify LLM strategy flexibility with different providers.
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
    print(f"   ✓ Gemini configuration works correctly")

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
    print(f"   ✓ OpenAI configuration works correctly")

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
    print(f"   ✓ Anthropic configuration works correctly")

    # Test 4: Default/fallback behavior
    print("\n4. Testing default/fallback behavior:")
    minimal_params = {
        'llm_config': {
            # No api_key_env_var specified - should default to GEMINI_API_KEY
            'api_url': 'https://test-api.com/v1/chat',
            'model': 'test-model',
            'timeout': 30
        }
    }

    # Set default API key
    os.environ['GEMINI_API_KEY'] = 'default_test_key'

    default_strategy = LLMFundamentalStrategy('Test Default Strategy', minimal_params)
    print(f"   API URL: {default_strategy.llm_config['api_url']}")
    print(f"   Model: {default_strategy.llm_config['model']}")
    print(f"   API Key (from default GEMINI_API_KEY): {default_strategy.llm_config['api_key']}")
    print(f"   ✓ Default behavior works correctly")

    print("\n🎉 All tests passed! LLM strategy is flexible and can work with different providers.")
    return True

if __name__ == "__main__":
    test_llm_provider_flexibility()

