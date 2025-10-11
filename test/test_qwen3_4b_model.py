#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试qwen3-4b模型的行为
"""

import sys
import os
import json
import requests

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_qwen3_4b_model():
    """测试qwen3-4b模型的行为"""

    # 加载系统提示词
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'pub_opinion_prompt.md')
    with open(prompt_path, 'r', encoding='utf-8') as f:
        system_prompt = f.read()

    # 构建用户提示词
    user_prompt = """请基于以下舆情信息进行量化舆情分析：

股票代码：000985
股票名称：大庆华科

舆情数据摘要：
- 新闻1: 大庆华科涨停
- 新闻2: 业绩增长12.99%
- 新闻3: 技术研发进展

请严格按照系统提示词的要求输出JSON格式的分析结果。

重要提醒：
1. 请直接输出JSON，不要包含任何思考过程或解释
2. 不要使用<think>标签
3. 基于实际舆情数据计算分数，不要使用示例值
4. 输出必须是严格的JSON格式"""

    llm_url = "http://192.168.1.177:1234/v1/chat/completions"
    payload = {
        "model": "qwen3-4b-instruct",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 8192
    }

    print("=== 测试qwen3-4b模型行为 ===")
    print(f"系统提示词长度: {len(system_prompt)} 字符")
    print(f"用户提示词长度: {len(user_prompt)} 字符")
    print(f"使用模型: {payload['model']}")

    try:
        response = requests.post(llm_url, json=payload, timeout=120)

        print(f"\n=== LLM响应状态码 ===")
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            response_data = response.json()

            if 'choices' in response_data and len(response_data['choices']) > 0:
                choice = response_data['choices'][0]

                if 'message' in choice:
                    message = choice['message']
                    content = message.get('content', '')

                    print(f"\n=== LLM响应内容 ===")
                    print(f"内容长度: {len(content)} 字符")
                    print(f"内容前500字符: {content[:500]}")

                    # 检查是否包含<think>标签
                    if "<think>" in content:
                        print("❌ 响应包含<think>标签")
                    else:
                        print("✅ 响应不包含<think>标签")

                    # 检查是否包含```标签
                    if "```" in content:
                        print("❌ 响应包含```标签")
                    else:
                        print("✅ 响应不包含```标签")

                    # 检查是否是纯JSON
                    if content.strip().startswith('{') and content.strip().endswith('}'):
                        print("✅ 响应看起来是纯JSON")
                        try:
                            parsed_json = json.loads(content)
                            print("✅ JSON解析成功")
                            print(f"综合评分: {parsed_json.get('score')}")
                            print(f"情感分数: {parsed_json.get('sentiment_score')}")
                        except json.JSONDecodeError as e:
                            print(f"❌ JSON解析失败: {e}")
                    else:
                        print("❌ 响应不是纯JSON")

                else:
                    print("❌ 响应中没有'message'字段")
            else:
                print("❌ 响应中没有'choices'字段或为空")
        else:
            print(f"❌ HTTP错误: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
    except Exception as e:
        print(f"❌ 其他异常: {e}")

if __name__ == "__main__":
    test_qwen3_4b_model()

