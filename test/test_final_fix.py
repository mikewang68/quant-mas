#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终测试：验证修复后的LLM响应处理
"""

import sys
import os
import json

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2

def test_final_fix():
    """最终测试修复效果"""

    # 创建策略实例
    strategy = EnhancedPublicOpinionAnalysisStrategyV2(
        "增强型舆情分析策略V2",
        {"sentiment_threshold": 0.0, "news_count_threshold": 1}
    )

    # 测试用例：模拟实际LLM返回的不完整JSON响应
    incomplete_json_response = '''
<think>
首先，我需要仔细阅读用户提供的舆情信息...

现在输出JSON：
{"score": 0.685,
"reason": "银行板块业绩转正，技术面短期调整，情绪偏积极。",
"details": {
  "policy": {"score": 0.50, "reason": "未涉平安银行具体政策信息"},
  "finance": {"score": 0.70, "reason": "业绩稳定，基本面良好"},
  "industry": {"score": 0.80, "reason": "银行板块业绩转正，机构看好"},
  "price_action": {"score": 0.60, "reason": "技术面短期调整，中长期向好"},
  "sentiment": {"score": 0.75, "reason": "机构买入评级增多，情绪偏积极"}
},
"weights": {"finance": 0.30, "industry": 0.25, "policy": 0.15, "price_action": 0.20, "sentiment": 0.10},
"sentiment_score": 0.75,
"sentiment_trend": "上涨",
"key_events": ["银行ETF指数上涨", "银行上半年营收利润转正", "技术面短期调整", "机构买入评级增多", "银行板块价值重估", "平安银行被提及"],
"market_impact": "中",
"confidence_level": 0.80,
"analysis_summary": "平安银行近期业绩稳定，银行板块业绩转正，技术面短期调整，机构买入评级增多。",
"recommendation": "观望",
"risk_factors": ["技术面调整压力
'''

    print("=== 测试：不完整的JSON响应 ===")
    print(f"原始响应长度: {len(incomplete_json_response)} 字符")
    print(f"原始响应前200字符: {incomplete_json_response[:200]}")

    try:
        content = incomplete_json_response

        # 处理包含<think>标签的情况
        if "<think>" in content:
            print("检测到<think>标签，尝试提取JSON部分")

            # 方法1: 尝试直接在整个内容中查找JSON
            json_start = content.find('{')
            json_end = content.rfind('}')

            if json_start != -1 and json_end != -1 and json_end > json_start:
                # 提取JSON内容
                extracted_json = content[json_start:json_end+1]
                # 验证提取的JSON是否有效
                try:
                    json.loads(extracted_json)
                    content = extracted_json
                    print(f"✅ 从<think>标签中直接提取JSON成功: {content[:200]}...")
                except json.JSONDecodeError:
                    print("❌ 直接提取的JSON无效，尝试更精确的提取")
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
                            print(f"✅ 从<think>标签内容中提取的JSON: {content[:200]}...")
                        else:
                            # 如果仍然找不到完整的JSON，尝试使用robust extraction
                            print("尝试使用robust extraction提取情感分数...")
                            sentiment_score = strategy._extract_sentiment_score_robust(content)
                            if sentiment_score is not None:
                                print(f"✅ 使用robust extraction获取sentiment_score: {sentiment_score}")
                                # 返回默认结果但使用提取的分数
                                default_result = strategy._get_default_analysis_result()
                                default_result["score"] = sentiment_score
                                default_result["sentiment_score"] = sentiment_score
                                print(f"✅ 成功返回默认结果，分数: {sentiment_score}")
                            else:
                                print("❌ robust extraction也失败了")
                    else:
                        print("❌ 无法找到完整的<think>标签")

        # 尝试解析JSON
        try:
            print(f"最终解析内容: {content[:200]}...")
            analysis_result = json.loads(content)
            print("✅ JSON解析成功")
            print(f"综合评分: {analysis_result.get('score')}")
            print(f"情感分数: {analysis_result.get('sentiment_score')}")
            print(f"投资建议: {analysis_result.get('recommendation')}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print("尝试使用robust extraction...")
            sentiment_score = strategy._extract_sentiment_score_robust(content)
            if sentiment_score is not None:
                print(f"✅ 使用robust extraction获取sentiment_score: {sentiment_score}")
            else:
                print("❌ 所有方法都失败了")

    except Exception as e:
        print(f"❌ 处理失败: {e}")

if __name__ == "__main__":
    print("开始最终测试修复效果...")
    test_final_fix()
    print("\n测试完成！")

