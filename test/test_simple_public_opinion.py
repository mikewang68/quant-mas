#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化测试脚本：验证数据组合和LLM分析功能
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_data_formatting():
    """测试数据格式化功能"""
    print("=== 测试数据格式化功能 ===")

    try:
        # 模拟收集到的数据
        test_data = {
            "stock_info": {"code": "000985", "name": "大庆华科"},
            "industry_info": {"行业": "化工行业", "细分": "基础化工"},
            "qian_gu_qian_ping_data": {
                "最新价": 18.78,
                "涨跌幅": -9.84,
                "换手率": 17.61,
                "市盈率": 107.55,
                "综合得分": 58.33
            },
            "detailed_guba_data": {
                "user_focus": [
                    {"date": "2024-09-20", "focus_index": 61.2},
                    {"date": "2024-09-21", "focus_index": 60.0},
                    {"date": "2024-09-22", "focus_index": 68.0}
                ],
                "institutional_participation": [
                    {"date": "2024-09-04", "participation": 14.248},
                    {"date": "2024-09-08", "participation": 11.525}
                ]
            },
            "akshare_news": [
                {
                    "title": "大庆华科发布业绩预告",
                    "publishedAt": "2024-09-29",
                    "content": "公司预计前三季度净利润同比增长50%-70%",
                    "source": "公司公告"
                },
                {
                    "title": "化工行业政策利好",
                    "publishedAt": "2024-09-28",
                    "content": "国家出台支持化工行业转型升级政策",
                    "source": "行业新闻"
                }
            ],
            "guba_data": {
                "consultations": [
                    {"title": "请问公司未来发展前景如何", "publishedAt": "2024-09-30"},
                    {"title": "近期股价波动较大，是否正常", "publishedAt": "2024-09-29"}
                ]
            },
            "professional_sites_data": [
                {
                    "title": "专业机构分析报告",
                    "publishedAt": "2024-09-25",
                    "content": "机构认为公司基本面良好，但短期存在波动风险",
                    "source": "专业分析网站"
                }
            ],
            "firecrawl_data": [
                {
                    "title": "网络分析文章",
                    "publishedAt": "2024-09-26",
                    "content": "投资者对大庆华科关注度较高，市场情绪积极",
                    "source": "财经网站"
                }
            ]
        }

        # 手动格式化数据
        formatted_text = ""

        # Add stock information
        formatted_text += f"股票代码: {test_data['stock_info']['code']}\n"
        formatted_text += f"股票名称: {test_data['stock_info']['name']}\n\n"

        # Add industry information
        if test_data["industry_info"]:
            formatted_text += "行业信息:\n"
            for key, value in test_data["industry_info"].items():
                formatted_text += f"  {key}: {value}\n"
            formatted_text += "\n"

        # Add qian gu qian ping data
        if test_data.get("qian_gu_qian_ping_data"):
            formatted_text += "千股千评综合数据:\n"
            qgqp_data = test_data["qian_gu_qian_ping_data"]
            for key, value in qgqp_data.items():
                if key != "_id":  # Skip MongoDB _id field
                    formatted_text += f"  {key}: {value}\n"
            formatted_text += "\n"

        # Add detailed Guba data
        if test_data.get("detailed_guba_data"):
            formatted_text += "东方财富股吧详细数据:\n"
            detailed_guba = test_data["detailed_guba_data"]

            # Add user focus data
            if detailed_guba.get("user_focus"):
                formatted_text += "  用户关注指数:\n"
                for i, item in enumerate(detailed_guba["user_focus"][:5], 1):
                    formatted_text += f"    {i}. 日期: {item.get('date', 'N/A')}, 关注指数: {item.get('focus_index', 'N/A')}\n"

            # Add institutional participation data
            if detailed_guba.get("institutional_participation"):
                formatted_text += "  机构参与度:\n"
                for i, item in enumerate(
                    detailed_guba["institutional_participation"][:5], 1
                ):
                    formatted_text += f"    {i}. 日期: {item.get('date', 'N/A')}, 参与度: {item.get('participation', 'N/A')}\n"

            formatted_text += "\n"

        # Add AkShare news (5-day)
        if test_data["akshare_news"]:
            formatted_text += "AkShare近5日新闻:\n"
            for i, news in enumerate(test_data["akshare_news"][:10], 1):
                formatted_text += f"  {i}. 标题: {news.get('title', 'N/A')}\n"
                formatted_text += f"     发布时间: {news.get('publishedAt', 'N/A')}\n"
                formatted_text += f"     内容摘要: {news.get('content', 'N/A')[:200]}...\n"
                formatted_text += f"     来源: {news.get('source', 'N/A')}\n"
            formatted_text += "\n"

        print(f"格式化数据长度: {len(formatted_text)} 字符")
        print(f"格式化数据预览:\n{formatted_text[:800]}...")

        print("\n✅ 数据格式化测试完成")

    except Exception as e:
        print(f"❌ 数据格式化测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_llm_prompt():
    """测试LLM提示词生成"""
    print("\n=== 测试LLM提示词生成 ===")

    try:
        # 模拟格式化数据
        formatted_data = """股票代码: 000985
股票名称: 大庆华科

行业信息:
  行业: 化工行业
  细分: 基础化工

千股千评综合数据:
  最新价: 18.78
  涨跌幅: -9.84
  换手率: 17.61
  市盈率: 107.55
  综合得分: 58.33

东方财富股吧详细数据:
  用户关注指数:
    1. 日期: 2024-09-20, 关注指数: 61.2
    2. 日期: 2024-09-21, 关注指数: 60.0
    3. 日期: 2024-09-22, 关注指数: 68.0
  机构参与度:
    1. 日期: 2024-09-04, 参与度: 14.248
    2. 日期: 2024-09-08, 参与度: 11.525

AkShare近5日新闻:
  1. 标题: 大庆华科发布业绩预告
     发布时间: 2024-09-29
     内容摘要: 公司预计前三季度净利润同比增长50%-70%...
     来源: 公司公告
  2. 标题: 化工行业政策利好
     发布时间: 2024-09-28
     内容摘要: 国家出台支持化工行业转型升级政策...
     来源: 行业新闻
"""

        # 创建LLM提示词
        prompt = f"""
你是一个专业的舆情分析师。请根据提供的舆情信息进行 sentiment 分析。

## 重要要求：
1. 请基于实际提供的舆情数据进行综合分析，不要复制示例值
2. 请直接输出JSON，不要包含任何其他文字或解释，不要输出思考过程
3. sentiment_score 必须是基于实际数据分析得出的0-1之间的数值

## 输出格式：
必须是严格的JSON格式：
{{
    "sentiment_score": 0.75,
    "sentiment_trend": "上升",
    "key_events": ["利好消息", "业绩预增"],
    "market_impact": "高",
    "confidence_level": 0.85,
    "analysis_summary": "详细的分析理由...",
    "recommendation": "买入",
    "risk_factors": ["市场波动", "政策风险"]
}}

## 舆情信息：
股票代码：000985 (大庆华科)

{formatted_data}

## 分析说明：
请基于以上实际舆情信息进行 sentiment 分析：
- sentiment_score: 基于新闻情感、股吧热度、机构参与度等综合评估（0-1，0表示极度负面，1表示极度正面）
- sentiment_trend: 基于近期数据变化趋势（上升/下降/震荡）
- key_events: 提取最重要的3-5个关键事件
- market_impact: 评估舆情对市场的影响程度（高/中/低）
- confidence_level: 分析结果的置信度（0-1）
- analysis_summary: 详细的分析理由（200-500字）
- recommendation: 投资建议（买入/持有/观望/卖出）
- risk_factors: 主要风险因素（2-4个）

请直接输出JSON结果。
"""

        print(f"提示词长度: {len(prompt)} 字符")
        print(f"提示词预览:\n{prompt[:500]}...")

        print("\n✅ LLM提示词测试完成")

    except Exception as e:
        print(f"❌ LLM提示词测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("开始测试修复后的增强型舆情分析策略V2...")

    # 测试数据格式化
    test_data_formatting()

    # 测试LLM提示词
    test_llm_prompt()

    print("\n=== 所有测试完成 ===")

