#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试更严格的LLM提示词
"""

import sys
import os
import json
import requests

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_strict_llm_prompt():
    """测试更严格的LLM提示词"""

    # 创建更严格的系统提示词
    strict_system_prompt = """你是一个量化交易舆情分析助手。

任务：对输入的新闻或舆情，基于【政策与监管、财务与业绩、行业与市场环境、行情走势、投资者情绪】这 5 个维度逐项评分（0~1），并给出综合舆情得分（0~1）、简要理由与结构化信息，结果以严格的 JSON 返回。

**绝对要求：**
1. **只输出JSON，不要包含任何其他文字**
2. **绝对禁止使用<think>标签**
3. **绝对禁止使用```标签或代码块**
4. **绝对禁止包含思考过程或解释**
5. **如果违反这些要求，你的输出将被视为无效**

输出格式必须是严格的JSON，包含以下字段：
- "score": 综合得分（0~1）
- "reason": 简短综合理由
- "details": 5个维度的评分与理由
- "weights": 权重对象
- "sentiment_score": 情感分数
- "sentiment_trend": 情感趋势
- "key_events": 关键事件数组
- "market_impact": 市场影响
- "confidence_level": 置信度
- "analysis_summary": 分析摘要
- "recommendation": 投资建议
- "risk_factors": 风险因素数组

**重要：如果你包含任何非JSON内容，你的响应将被拒绝！**"""

    # 构建用户提示词
    user_prompt = """请基于以下舆情信息进行量化舆情分析：

股票代码：000985
股票名称：大庆华科

舆情数据摘要：
- 新闻1: 大庆华科涨停
- 新闻2: 业绩增长12.99%
- 新闻3: 技术研发进展

**重要：只输出JSON，不要包含任何其他文字！**"""

    llm_url = "http://192.168.1.177:1234/v1/chat/completions"
    payload = {
        "model": "qwen2.5-7b-instruct",
        "messages": [
            {"role": "system", "content": strict_system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 8192
    }

    print("=== 测试更严格的LLM提示词 ===")
    print(f"系统提示词长度: {len(strict_system_prompt)} 字符")
    print(f"用户提示词长度: {len(user_prompt)} 字符")

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
                        print("❌ 响应包含<think>标签 - LLM没有遵守系统提示词")
                    else:
                        print("✅ 响应不包含<think>标签")

                    # 检查是否包含```标签
                    if "```" in content:
                        print("❌ 响应包含```标签 - LLM没有遵守系统提示词")
                    else:
                        print("✅ 响应不包含```标签")

                    # 检查是否是纯JSON
                    if content.strip().startswith('{') and content.strip().endswith('}'):
                        print("✅ 响应看起来是纯JSON")
                        try:
                            parsed_json = json.loads(content)
                            print("✅ JSON解析成功")
                            print(f"综合评分: {parsed_json.get('score')}")
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
    test_strict_llm_prompt()

