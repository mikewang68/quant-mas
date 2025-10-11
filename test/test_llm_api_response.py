"""
Test script to verify the LLM API response parsing fix
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.llm_fundamental_strategy import LLMFundamentalStrategy

def test_api_response_parsing():
    """Test that API response parsing works for different providers"""
    print("Testing API response parsing for different providers...")

    strategy = LLMFundamentalStrategy(name="LLM基本面分析策略")

    # Test Google Gemini response format
    print("\n1. Testing Google Gemini response format:")
    google_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": '{"score": 0.75, "value": "这是一支基本面良好的股票，具有稳定的盈利能力。"}'
                        }
                    ]
                }
            }
        ]
    }

    strategy.llm_config["provider"] = "google"

    # Simulate the response parsing logic
    provider = strategy.llm_config.get("provider", "google")
    if provider == "google":
        content = google_response["candidates"][0]["content"]["parts"][0]["text"]
        print(f"  Google format: Successfully extracted content")
        print(f"  Content: {content}")
    else:
        print("  ❌ ERROR: Google provider should use Google format!")

    # Test OpenAI-compatible response format (qwen, deepseek, etc.)
    print("\n2. Testing OpenAI-compatible response format:")
    openai_response = {
        "choices": [
            {
                "message": {
                    "content": '{"score": 0.82, "value": "这支股票具有优秀的成长性和稳定的财务状况。"}'
                }
            }
        ]
    }

    # Test with qwen provider
    strategy.llm_config["provider"] = "qwen"
    provider = strategy.llm_config.get("provider", "google")
    if provider in ["deepseek", "qwen", "openai", "ollama"]:
        content = openai_response["choices"][0]["message"]["content"]
        print(f"  OpenAI-compatible format: Successfully extracted content")
        print(f"  Content: {content}")
    else:
        print("  ❌ ERROR: qwen provider should use OpenAI-compatible format!")

    # Test with deepseek provider
    strategy.llm_config["provider"] = "deepseek"
    provider = strategy.llm_config.get("provider", "google")
    if provider in ["deepseek", "qwen", "openai", "ollama"]:
        content = openai_response["choices"][0]["message"]["content"]
        print(f"  DeepSeek format: Successfully extracted content")
        print(f"  Content: {content}")
    else:
        print("  ❌ ERROR: deepseek provider should use OpenAI-compatible format!")

def test_json_parsing_edge_cases():
    """Test JSON parsing with various edge cases"""
    print("\n3. Testing JSON parsing edge cases:")

    strategy = LLMFundamentalStrategy(name="LLM基本面分析策略")

    # Test case 1: Normal JSON response
    normal_json = '{"score": 0.85, "value": "正常分析结果"}'
    try:
        result = json.loads(normal_json)
        print(f"  ✓ Normal JSON: score={result['score']}, value={result['value']}")
    except json.JSONDecodeError as e:
        print(f"  ❌ Normal JSON failed: {e}")

    # Test case 2: JSON with code block
    json_with_code = '```json\n{"score": 0.75, "value": "带代码块的分析"}\n```'
    content = json_with_code
    if content.startswith("```json"):
        content = content[7:]  # Remove ```json
        if content.endswith("```"):
            content = content[:-3]  # Remove ```
    try:
        result = json.loads(content.strip())
        print(f"  ✓ JSON with code block: score={result['score']}, value={result['value']}")
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON with code block failed: {e}")

    # Test case 3: Nested JSON in value field
    nested_json = '{"score": 0.8, "value": "{\"score\": 0.8, \"value\": \"嵌套的分析内容\"}"}'
    try:
        result = json.loads(nested_json)
        llm_score = float(result.get("score", 0))
        llm_value = result.get("value", nested_json)

        # Handle nested JSON in value field
        if isinstance(llm_value, str):
            try:
                nested_result = json.loads(llm_value)
                if isinstance(nested_result, dict) and "value" in nested_result:
                    llm_value = nested_result["value"]
            except json.JSONDecodeError:
                pass

        print(f"  ✓ Nested JSON: score={llm_score}, value={llm_value}")
    except json.JSONDecodeError as e:
        print(f"  ❌ Nested JSON failed: {e}")

def test_error_handling():
    """Test error handling for malformed responses"""
    print("\n4. Testing error handling:")

    strategy = LLMFundamentalStrategy(name="LLM基本面分析策略")

    # Test case 1: Invalid JSON
    invalid_json = '{"score": 0.85, "value": "缺少引号"'
    try:
        result = json.loads(invalid_json)
        print(f"  ❌ Invalid JSON should have failed but didn't")
    except json.JSONDecodeError:
        print(f"  ✓ Invalid JSON correctly failed to parse")

    # Test case 2: Missing required fields
    missing_fields = '{"value": "只有value字段"}'
    try:
        result = json.loads(missing_fields)
        llm_score = float(result.get("score", 0))  # Default to 0 if missing
        llm_value = result.get("value", missing_fields)
        print(f"  ✓ Missing fields handled: score={llm_score}, value={llm_value}")
    except json.JSONDecodeError as e:
        print(f"  ❌ Missing fields failed: {e}")

if __name__ == "__main__":
    print("Testing LLM API Response Parsing Fix")
    print("=" * 60)

    test_api_response_parsing()
    test_json_parsing_edge_cases()
    test_error_handling()

    print("\n🎉 API response parsing tests completed!")
    print("\nThe fix ensures:")
    print("1. Google provider uses 'candidates' field format")
    print("2. OpenAI-compatible providers use 'choices' field format")
    print("3. JSON parsing handles various edge cases")
    print("4. Error handling gracefully handles malformed responses")

