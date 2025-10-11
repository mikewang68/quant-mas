#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的LLM响应处理逻辑
"""

import sys
import os
import json

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2

def test_llm_response_extraction():
    """测试LLM响应提取功能"""

    # 创建策略实例
    strategy = EnhancedPublicOpinionAnalysisStrategyV2("测试策略", {"sentiment_threshold": 0.0, "news_count_threshold": 1})

    # 测试用例1: 包含<think>标签的响应
    think_response = '''
<think>
首先，我需要根据提供的舆情信息进行 sentiment 分析。

基于分析，我认为该股票舆情整体偏正面。

现在输出JSON：
{"score": 0.75, "reason": "舆情整体偏正面", "details": {"policy": {"score": 0.5, "reason": "信息不足"}, "finance": {"score": 0.8, "reason": "业绩良好"}, "industry": {"score": 0.7, "reason": "行业稳定"}, "price_action": {"score": 0.6, "reason": "走势平稳"}, "sentiment": {"score": 0.8, "reason": "情绪积极"}}, "weights": {"finance": 0.30, "industry": 0.25, "policy": 0.15, "price_action": 0.20, "sentiment": 0.10}, "sentiment_score": 0.8, "sentiment_trend": "上升", "key_events": ["业绩预增"], "market_impact": "中", "confidence_level": 0.8, "analysis_summary": "舆情整体偏正面", "recommendation": "买入", "risk_factors": ["市场波动"]}
</think>
'''

    # 测试用例2: 包含```标签的响应
    code_block_response = '''
```json
{"score": 0.65, "reason": "舆情中性", "details": {"policy": {"score": 0.5, "reason": "信息不足"}, "finance": {"score": 0.7, "reason": "业绩稳定"}, "industry": {"score": 0.6, "reason": "行业一般"}, "price_action": {"score": 0.5, "reason": "走势震荡"}, "sentiment": {"score": 0.7, "reason": "情绪中性"}}, "weights": {"finance": 0.30, "industry": 0.25, "policy": 0.15, "price_action": 0.20, "sentiment": 0.10}, "sentiment_score": 0.7, "sentiment_trend": "震荡", "key_events": ["无重大事件"], "market_impact": "弱", "confidence_level": 0.7, "analysis_summary": "舆情中性", "recommendation": "观望", "risk_factors": ["行业风险"]}
```
'''

    # 测试用例3: 纯JSON响应
    pure_json_response = '''
{"score": 0.85, "reason": "舆情积极", "details": {"policy": {"score": 0.6, "reason": "政策支持"}, "finance": {"score": 0.9, "reason": "业绩优秀"}, "industry": {"score": 0.8, "reason": "行业景气"}, "price_action": {"score": 0.7, "reason": "走势向上"}, "sentiment": {"score": 0.9, "reason": "情绪高涨"}}, "weights": {"finance": 0.30, "industry": 0.25, "policy": 0.15, "price_action": 0.20, "sentiment": 0.10}, "sentiment_score": 0.9, "sentiment_trend": "上升", "key_events": ["业绩超预期"], "market_impact": "强", "confidence_level": 0.9, "analysis_summary": "舆情积极", "recommendation": "买入", "risk_factors": ["估值偏高"]}
'''

    test_cases = [
        ("包含<think>标签", think_response),
        ("包含```标签", code_block_response),
        ("纯JSON", pure_json_response)
    ]

    for test_name, response in test_cases:
        print(f"\n=== 测试: {test_name} ===")
        print(f"原始响应长度: {len(response)} 字符")
        print(f"原始响应前100字符: {response[:100]}")

        try:
            # 模拟策略中的JSON解析过程
            content = response

            # 处理包含<think>标签的情况
            if "<think>" in content:
                print("检测到<think>标签，尝试提取JSON部分")
                # 查找<think>和</think>之间的内容
                think_start = content.find("<think>")
                think_end = content.find("</think>")

                if think_start != -1 and think_end != -1:
                    # 提取<think>标签之间的内容
                    think_content = content[think_start+7:think_end]  # len("<think>") = 7
                    # 在think内容中查找JSON
                    json_start = think_content.find('{')
                    json_end = think_content.rfind('}')
                    if json_start != -1 and json_end != -1:
                        content = think_content[json_start:json_end+1]
                        print(f"从<think>标签中提取的JSON内容: {content[:100]}...")

            # 处理包含```标签的情况
            elif "```" in content:
                print("检测到```标签，尝试提取JSON部分")
                # 查找```json和```之间的内容
                json_start_marker = content.find("```json")
                if json_start_marker != -1:
                    # 从```json之后开始查找
                    json_start = json_start_marker + 7  # len("```json") = 7
                else:
                    # 查找普通的```标记
                    json_start_marker = content.find("```")
                    json_start = json_start_marker + 3 if json_start_marker != -1 else -1

                json_end_marker = content.find("```", json_start)

                if json_start != -1 and json_end_marker != -1:
                    # 提取```标签之间的内容
                    content = content[json_start:json_end_marker].strip()
                    print(f"提取的JSON内容: {content[:100]}...")

            # 解析JSON
            print(f"最终解析内容: {content[:100]}...")
            analysis_result = json.loads(content)

            print("✅ JSON解析成功")
            print(f"综合评分: {analysis_result.get('score')}")
            print(f"情感分数: {analysis_result.get('sentiment_score')}")
            print(f"投资建议: {analysis_result.get('recommendation')}")

        except Exception as e:
            print(f"❌ 解析失败: {e}")

if __name__ == "__main__":
    print("开始测试修复后的LLM响应处理逻辑...")
    test_llm_response_extraction()
    print("\n测试完成！")

