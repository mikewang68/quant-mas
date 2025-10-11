#!/usr/bin/env python3
"""
Direct test to get LLM JSON response for fundamental analysis
"""

import os
import sys
import json
import requests

# Add project root to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_llm_directly():
    """Test LLM API directly with the exact system prompt"""
    print("=== Testing LLM API Directly ===\n")

    # Load the system prompt
    with open("../config/fund_sys_prompt.md", "r", encoding="utf-8") as f:
        system_prompt = f.read()

    # Create a simple user prompt
    user_prompt = """
股票代码: 300339
股票名称: 润和软件
行业: 软件开发

关键财务比率:
{
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

行业对比:
{
  "行业": "软件开发",
  "行业平均水平": {
    "roe": 0.08,
    "pe": 15.0,
    "debt_to_equity": 0.5
  }
}

最近财务数据:
{
  "关键财务指标": {
    "每股净资产": "4.50",
    "净资产收益率": "1.71%",
    "净利润": "5981.78万"
  },
  "资产负债表关键项目": {
    "负债合计": "6024.16万",
    "流动资产": "",
    "流动负债": ""
  },
  "利润表关键项目": {}
}

请基于以上数据进行专业分析，并严格按照系统提示词的要求输出JSON格式。
"""

    # LLM configuration
    api_url = "http://192.168.1.177:1234/v1/chat/completions"
    model = "qwen/qwen3-4b-thinking-2507"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,  # Lower temperature for more consistent output
        "max_tokens": 2000,
    }

    print(f"System prompt length: {len(system_prompt)} characters")
    print(f"User prompt length: {len(user_prompt)} characters")
    print(f"API URL: {api_url}")
    print(f"Model: {model}")
    print()

    try:
        response = requests.post(api_url, json=payload, timeout=120)

        print(f"Response status code: {response.status_code}")

        if response.status_code == 200:
            response_data = response.json()

            if 'choices' in response_data and len(response_data['choices']) > 0:
                choice = response_data['choices'][0]

                if 'message' in choice:
                    message = choice['message']
                    content = message.get('content', '')

                    print("\n=== LLM Response Content ===")
                    print(f"Content length: {len(content)} characters")
                    print(f"Content:\n{content}")

                    # Check for think tags
                    if "<think>" in content:
                        print("\n⚠️  WARNING: Response contains <think> tags")
                    else:
                        print("\n✅ Response does not contain <think> tags")

                    # Check if it's valid JSON
                    try:
                        parsed_json = json.loads(content)
                        print("\n✅ Response is valid JSON")
                        print("\n=== Parsed JSON Structure ===")
                        print(json.dumps(parsed_json, indent=2, ensure_ascii=False))

                        # Check if it has the required fields
                        required_fields = ["score", "reason", "details", "weights", "confidence_level",
                                         "analysis_summary", "recommendation", "risk_factors", "key_strengths"]
                        missing_fields = [field for field in required_fields if field not in parsed_json]

                        if missing_fields:
                            print(f"\n⚠️  Missing required fields: {missing_fields}")
                        else:
                            print("\n✅ All required fields present")

                    except json.JSONDecodeError as e:
                        print(f"\n❌ Response is not valid JSON: {e}")

                        # Try to extract JSON from the content
                        import re
                        json_pattern = r'\{.*\}'
                        matches = re.findall(json_pattern, content, re.DOTALL)
                        if matches:
                            print("\n=== Attempting to extract JSON from content ===")
                            for match in matches:
                                try:
                                    extracted_json = json.loads(match)
                                    print("✅ Found valid JSON in content:")
                                    print(json.dumps(extracted_json, indent=2, ensure_ascii=False))
                                    break
                                except json.JSONDecodeError:
                                    continue

                else:
                    print("❌ No message in response")
            else:
                print("❌ No choices in response")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"Response text: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Request exception: {e}")
    except Exception as e:
        print(f"❌ Other exception: {e}")


if __name__ == "__main__":
    test_llm_directly()

