#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test program to verify Qwen3-4B model's JSON format support
This test will help us understand why the model returns 0.5 scores in the enhanced public opinion analysis strategy
"""

import requests
import json
import os
from datetime import datetime


def test_qwen3_4b_json_response(api_url, api_key=None):
    """
    Test Qwen3-4B model's JSON response format

    Args:
        api_url: Qwen3-4B API endpoint URL
        api_key: API key if required
    """
    print(f"Testing Qwen3-4B model at: {api_url}")

    # Sample prompt similar to what's used in the strategy
    prompt = """
    请分析以下关于股票 东方财富 (300017) 的舆情信息, 并给出0-1分的 sentiment 评分:

    舆情内容:
    股票代码: 300017
    股票名称: 东方财富

    AkShare近5日新闻:
    1. 标题: 东方财富：子公司东方财富证券5月净利润同比下滑20%
       发布时间: 2024-06-10T00:00:00
       内容摘要: 东方财富公告，子公司东方财富证券5月实现营业收入9.8亿元，净利润4.5亿元，同比分别下滑15%和20%...
       来源: AkShare

    2. 标题: 东方财富推出新一代智能投顾系统
       发布时间: 2024-06-08T00:00:00
       内容摘要: 东方财富宣布推出基于AI的新一代智能投顾系统，有望提升用户投资体验...
       来源: AkShare

    分析要求:
    1. 综合评估所有舆情信息的情感倾向(积极, 消极或中性)
    2. 考虑信息的重要性和影响力
    3. 考虑信息的时效性
    4. 给出详细的分析理由

    请严格按照以下JSON格式输出结果:
    {
        "sentiment_score": 0.75,
        "sentiment_trend": "上升",
        "key_events": ["利好消息", "业绩预增"],
        "market_impact": "高",
        "confidence_level": 0.85,
        "analysis_summary": "详细的分析理由...",
        "recommendation": "买入",
        "risk_factors": ["市场波动", "政策风险"]
    }

    其中sentiment_score是0-1之间的数值, 0表示极度负面, 1表示极度正面, 0.5为中性.
    """

    # Prepare headers
    headers = {"Content-Type": "application/json"}

    # Add API key if provided
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # Prepare payload - assuming OpenAI-style API
    payload = {
        "model": "qwen3-4b",  # Model name
        "messages": [
            {
                "role": "system",
                "content": '你是一位专业的舆情分析师，请根据提供的舆情信息进行 sentiment 分析。你需要严格按照以下JSON格式输出结果：{"sentiment_score": 0.75, "sentiment_trend": "上升", "key_events": ["利好消息", "业绩预增"], "market_impact": "高", "confidence_level": 0.85, "analysis_summary": "详细的分析理由...", "recommendation": "买入", "risk_factors": ["市场波动", "政策风险"]}。其中sentiment_score是0-1之间的数值，表示舆情 sentiment 评分，0为最低（极度负面），1为最高（极度正面）；其他字段请根据实际分析填写。请直接输出JSON，不要包含任何其他文字或解释。字数控制在800字以内',
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 2000,  # 增加token数量
    }

    try:
        print("Sending request to Qwen3-4B model...")
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=120,  # Longer timeout for local model
        )

        print(f"Response status code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("Model response received successfully!")
            print(f"Full response: {json.dumps(result, indent=2, ensure_ascii=False)}")

            # Extract content based on response format
            content = None
            if "choices" in result and len(result["choices"]) > 0:
                # OpenAI/DeepSeek style
                content = result["choices"][0].get("message", {}).get("content", "")
            elif "candidates" in result and len(result["candidates"]) > 0:
                # Google Gemini style
                content = result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                content = str(result)

            print(f"\nExtracted content:\n{content}")

            # Try to parse as JSON
            try:
                if content.startswith("```json"):
                    content = content[7:]  # Remove ```json
                    if content.endswith("```"):
                        content = content[:-3]  # Remove ```
                elif content.startswith("```"):
                    content = content[3:]  # Remove ```
                    if content.endswith("```"):
                        content = content[:-3]  # Remove ```

                analysis_result = json.loads(content)
                print(f"\nSuccessfully parsed JSON response:")
                print(json.dumps(analysis_result, indent=2, ensure_ascii=False))

                # Check if sentiment_score is present
                if "sentiment_score" in analysis_result:
                    score = analysis_result["sentiment_score"]
                    print(f"\nSentiment score: {score}")
                    return True, analysis_result
                else:
                    print("\nWarning: sentiment_score field not found in response")
                    return False, {
                        "error": "sentiment_score field missing",
                        "content": content,
                    }

            except json.JSONDecodeError as e:
                print(f"\nFailed to parse JSON response: {e}")
                print(f"Content that failed to parse:\n{content}")

                # Try to extract sentiment_score with regex
                import re

                score_match = re.search(r'"sentiment_score"\s*:\s*(\d+\.?\d*)', content)
                if score_match:
                    score = float(score_match.group(1))
                    print(f"\nExtracted sentiment score using regex: {score}")
                    return True, {"sentiment_score": score, "raw_content": content}
                else:
                    print("\nFailed to extract sentiment score using regex")
                    return False, {"error": "JSON parsing failed", "content": content}
        else:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response text: {response.text}")
            return False, {
                "error": f"HTTP {response.status_code}",
                "response": response.text,
            }

    except requests.exceptions.Timeout:
        print("Error: Request timed out")
        return False, {"error": "timeout"}
    except requests.exceptions.RequestException as e:
        print(f"Error: Request failed - {e}")
        return False, {"error": str(e)}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False, {"error": f"unexpected: {e}"}


def main():
    """Main test function"""
    print("=" * 60)
    print("Qwen3-4B JSON Format Support Test")
    print("=" * 60)

    # Get API configuration from environment variables or use defaults
    api_url = os.getenv("QWEN3_4B_API_URL", "http://localhost:1234/v1/chat/completions")
    api_key = os.getenv("QWEN3_4B_API_KEY", None)

    print(f"Using API URL: {api_url}")
    if api_key:
        print("API key provided")
    else:
        print("No API key provided")

    # Run the test
    success, result = test_qwen3_4b_json_response(api_url, api_key)

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    if success:
        print("✓ Test PASSED: Qwen3-4B correctly returned JSON format")
        if "sentiment_score" in result:
            print(f"  Sentiment Score: {result['sentiment_score']}")
        if "analysis_summary" in result:
            print(f"  Analysis Summary: {result['analysis_summary'][:100]}...")
    else:
        print("✗ Test FAILED: Issues with Qwen3-4B JSON format support")
        print(f"  Error: {result.get('error', 'Unknown error')}")
        if "content" in result:
            print(f"  Response content: {result['content'][:200]}...")


if __name__ == "__main__":
    main()
