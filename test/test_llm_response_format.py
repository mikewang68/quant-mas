#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test to understand the exact LLM response format from Qwen3-4B
"""

import json
import re

# Sample response that includes thinking process before JSON
test_response = """<think>
首先，我需要根据用户提供的舆情信息进行sentiment分析。用户要求输出特定的JSON格式，所以我必须严格按照这个格式来。

用户提供的舆情信息包括：
- 股票代码：001209，股票名称：洪兴股份
  - 行业信息：能源金属、小金属、航天航空、半导体、有色金属
    - 千股千评综合数据：最新价18.78，涨跌幅-9.84（下降），换手率17.61，市盈率107.55，主力成本19.129，机构参与度0.254，综合得分58.33，上升-1234，排名2698，关注指数80.4
      - 东方财富股吧数据：关注指数在8月20日到26日有波动（从61.2降到60.0，再升到68.0，然后又降），机构参与度在8月4日到8日有变化（从14.248降到11.525），历史评分在8月20日到26日有波动（从59.4升到66.4，然后降）
        - 日度市场参与意愿：9月24日到30日有波动（当日意愿上升：8.58, -14.88, -33.68, 24.99, -1.63）
          - AkShare近5日新闻：9月29日有涨停、快速回调、快速上涨、打开涨停等新闻；9月30日上榜龙虎榜（日跌幅偏离值7%）...

现在我需要分析这些信息并给出sentiment评分。

分析要点：
1. 股票表现：最新价18.78，涨跌幅-9.84（下降），换手率17.61（较高），市盈率107.55（较高）
2. 机构参与度：0.254（较低），综合得分58.33（中等偏低）
3. 股吧数据：关注指数有波动，机构参与度下降，历史评分波动
4. 市场参与意愿：有正有负的波动
5. 新闻：有涨停、快速回调等波动性较大的事件

综合来看，股票近期表现波动较大，有涨停也有回调，机构参与度不高，综合得分中等偏低。
整体舆情偏向中性偏负面，但由于有涨停等积极事件，评分不会太低。

sentiment_score应该在0.4-0.6之间，考虑到波动性较大，给0.45比较合适。
</think>

{
    "sentiment_score": 0.45,
    "sentiment_trend": "波动",
    "key_events": ["涨停事件", "龙虎榜上榜"],
    "market_impact": "中等",
    "confidence_level": 0.75,
    "analysis_summary": "洪兴股份近期舆情信息显示股票表现波动较大，有涨停和快速回调等事件，换手率较高显示交易活跃，但机构参与度较低，综合得分中等偏低。整体舆情偏向中性偏负面，但由于存在积极事件，评分不会过低。",
    "recommendation": "观望",
    "risk_factors": ["高波动性", "机构参与度低"]
}"""

def test_extraction_methods(content):
    """Test different extraction methods"""
    print("=" * 60)
    print("Testing LLM Response Extraction Methods")
    print("=" * 60)

    # Method 1: Extract JSON after </think> tag
    if "</think>" in content:
        json_start = content.find("</think>") + len("</think>")
        json_content = content[json_start:].strip()
        print(f"Method 1 - After </think> tag: {json_content[:200]}...")

        try:
            result = json.loads(json_content)
            print(f"✓ Method 1 SUCCESS: sentiment_score = {result.get('sentiment_score')}")
            return result.get('sentiment_score')
        except json.JSONDecodeError as e:
            print(f"✗ Method 1 FAILED: {e}")

    # Method 2: Find JSON object with sentiment_score
    json_matches = re.findall(r'\{[^{}]*"sentiment_score"[^{}]*\}', content)
    for json_match in json_matches:
        try:
            result = json.loads(json_match)
            print(f"✓ Method 2 SUCCESS: sentiment_score = {result.get('sentiment_score')}")
            return result.get('sentiment_score')
        except json.JSONDecodeError:
            continue

    # Method 3: Regex extraction
    score_match = re.search(r'"sentiment_score"\s*:\s*(\d+\.?\d*)', content)
    if score_match:
        score = float(score_match.group(1))
        print(f"✓ Method 3 SUCCESS: sentiment_score = {score}")
        return score

    print("✗ All methods failed")
    return None

# Test the extraction methods
sentiment_score = test_extraction_methods(test_response)
print(f"\nFinal extracted sentiment score: {sentiment_score}")

