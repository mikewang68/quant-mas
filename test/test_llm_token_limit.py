#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试LLM API的token限制问题
"""

import sys
import os
import json
import requests

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_llm_token_limit():
    """测试LLM API的token限制"""

    # 构建与舆情分析策略相同的提示词
    prompt = """你是一个专业的舆情分析师。请根据提供的舆情信息进行 sentiment 分析。

请直接输出JSON，不要包含任何其他文字或解释。

输出格式必须是严格的JSON格式：
{
    "score": 0.75,
    "reason": "舆情整体偏正面",
    "details": {
        "policy": {"score": 0.5, "reason": "信息不足"},
        "finance": {"score": 0.8, "reason": "业绩良好"},
        "industry": {"score": 0.7, "reason": "行业稳定"},
        "price_action": {"score": 0.6, "reason": "走势平稳"},
        "sentiment": {"score": 0.8, "reason": "情绪积极"}
    },
    "weights": {"finance": 0.30, "industry": 0.25, "policy": 0.15, "price_action": 0.20, "sentiment": 0.10},
    "sentiment_score": 0.8,
    "sentiment_trend": "上升",
    "key_events": ["业绩预增"],
    "market_impact": "中",
    "confidence_level": 0.8,
    "analysis_summary": "舆情整体偏正面",
    "recommendation": "买入",
    "risk_factors": ["市场波动"]
}

舆情信息：
股票代码：000985 (大庆华科)
行业：石油石化

AkShare新闻数据（最近5天）：
- 新闻1: 大庆华科发布业绩预告
- 新闻2: 化工行业政策利好
- 新闻3: 公司技术研发进展

东方财富股吧数据：
- 用户关注指数: 85.2
- 机构参与度: 78.5
- 历史评分: 82.1
- 日度市场参与意愿: 76.8

专业网站数据：
- 专业分析文章1
- 专业分析文章2

千股千评数据：
- 综合评分: 80
- 技术面: 良好
- 基本面: 稳定

请基于以上舆情信息进行 sentiment 分析，并输出JSON结果。"""

    llm_url = "http://192.168.1.177:1234/v1/chat/completions"
    payload = {
        "model": "qwen2.5-7b-instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 8192
    }

    print("=== 测试LLM API token限制 ===")
    print(f"提示词长度: {len(prompt)} 字符")
    print(f"max_tokens设置: {payload['max_tokens']}")

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
                        print("⚠️  响应包含<think>标签")

                    # 检查是否包含```标签
                    if "```" in content:
                        print("⚠️  响应包含```标签")

                    # 检查JSON是否完整
                    if content.strip().endswith('}'):
                        print("✅ JSON看起来是完整的")
                    else:
                        print("❌ JSON可能被截断了")
                        print(f"最后100字符: {content[-100:]}")

                    # 尝试解析JSON
                    try:
                        parsed_json = json.loads(content)
                        print("✅ JSON解析成功")
                        print(f"综合评分: {parsed_json.get('score')}")
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON解析失败: {e}")

                else:
                    print("❌ 响应中没有'message'字段")
            else:
                print("❌ 响应中没有'choices'字段或为空")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应文本: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
    except Exception as e:
        print(f"❌ 其他异常: {e}")

if __name__ == "__main__":
    test_llm_token_limit()

