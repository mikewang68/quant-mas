"""
简单LLM API测试脚本
直接测试LLM API响应
"""

import requests
import json
import re

def test_llm_api_directly():
    """直接测试LLM API"""

    # LLM配置
    llm_url = "http://192.168.1.177:1234/v1/chat/completions"

    # 简单的测试提示词
    prompt = """请直接输出以下JSON格式的内容，不要包含任何其他文字：
{
    "score": 0.75,
    "reason": "测试原因",
    "details": {
        "policy": {"score": 0.5, "reason": "政策稳定"},
        "finance": {"score": 0.8, "reason": "财务良好"},
        "industry": {"score": 0.7, "reason": "行业前景好"},
        "price_action": {"score": 0.6, "reason": "价格走势稳定"},
        "sentiment": {"score": 0.75, "reason": "情绪积极"}
    },
    "weights": {"finance": 0.3, "industry": 0.25, "policy": 0.15, "price_action": 0.2, "sentiment": 0.1},
    "sentiment_score": 0.75,
    "sentiment_trend": "上升",
    "key_events": ["业绩增长", "行业利好"],
    "market_impact": "中",
    "confidence_level": 0.8,
    "analysis_summary": "测试分析摘要",
    "recommendation": "买入",
    "risk_factors": ["市场风险", "政策风险"]
}"""

    payload = {
        "model": "qwen2.5-7b-instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 2000
    }

    try:
        print("=== 发送请求到LLM API ===")
        print(f"URL: {llm_url}")
        print(f"提示词长度: {len(prompt)} 字符")

        response = requests.post(llm_url, json=payload, timeout=30)

        print(f"\n=== LLM响应状态码 ===")
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            response_data = response.json()

            if 'choices' in response_data and len(response_data['choices']) > 0:
                choice = response_data['choices'][0]

                if 'message' in choice:
                    content = choice['message'].get('content', '')

                    print(f"\n=== LLM响应内容 ===")
                    print(f"内容长度: {len(content)} 字符")
                    print(f"完整内容:\n{content}")

                    # 尝试解析JSON
                    print(f"\n=== JSON解析测试 ===")
                    try:
                        parsed_json = json.loads(content)
                        print("✅ 直接JSON解析成功")
                        print(f"解析结果: {json.dumps(parsed_json, ensure_ascii=False, indent=2)}")
                        return True
                    except json.JSONDecodeError as e:
                        print(f"❌ 直接JSON解析失败: {e}")

                        # 尝试提取JSON部分
                        print(f"\n=== 尝试提取JSON部分 ===")

                        # 查找JSON对象
                        json_start = content.find('{')
                        json_end = content.rfind('}')

                        if json_start != -1 and json_end != -1:
                            json_str = content[json_start:json_end+1]
                            print(f"提取的JSON: {json_str}")

                            try:
                                parsed = json.loads(json_str)
                                print("✅ 提取的JSON解析成功")
                                print(f"解析结果: {json.dumps(parsed, ensure_ascii=False, indent=2)}")
                                return True
                            except json.JSONDecodeError as e2:
                                print(f"❌ 提取的JSON解析失败: {e2}")
                        else:
                            print("未找到JSON对象")

                        return False
                else:
                    print("❌ 响应中没有'message'字段")
                    return False
            else:
                print("❌ 响应中没有'choices'字段或为空")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应文本: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他异常: {e}")
        return False

if __name__ == "__main__":
    print("开始直接测试LLM API...")
    success = test_llm_api_directly()
    if success:
        print("\n=== 测试成功 ===")
    else:
        print("\n=== 测试失败 ===")

