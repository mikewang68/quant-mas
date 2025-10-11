"""
测试策略value字段修改
验证LLM JSON是否正确写入value字段
"""

import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2

def test_value_field():
    """测试value字段生成"""
    try:
        print("=== 测试value字段生成 ===")

        # 创建策略实例
        strategy_params = {
            "data_sources": ["akshare", "firecrawl", "professional_sites", "guba"],
            "llm_name": "qwen3-4B",
            "news_count_threshold": 5,
            "sentiment_threshold": 0.6,
            "time_window_hours": 24
        }

        strategy = EnhancedPublicOpinionAnalysisStrategyV2(
            name="增强型舆情分析策略V2",
            params=strategy_params,
            db_manager=None
        )

        print("策略实例化成功")

        # 模拟LLM分析结果
        full_analysis = {
            "score": 0.490,
            "reason": "股价短期强势但业绩下滑，行业热点存风险。",
            "details": {
                "policy": {"score": 0.40, "reason": "有风险提示但无重大政策变动"},
                "finance": {"score": 0.35, "reason": "上半年净利降近三成"},
                "industry": {"score": 0.70, "reason": "消费旺季叠加跨界热点"},
                "price_action": {"score": 0.45, "reason": "近期涨停后出现回调"},
                "sentiment": {"score": 0.60, "reason": "机构活跃但投资未收益引发谨慎"}
            },
            "weights": {"finance": 0.30, "industry": 0.25, "policy": 0.15, "price_action": 0.20, "sentiment": 0.10},
            "sentiment_score": 0.60,
            "sentiment_trend": "震荡",
            "key_events": ["三连板", "16亿半导体投资", "上半年净利降三成", "风险提示", "消费ETF领涨", "技术面调整"],
            "market_impact": "中",
            "confidence_level": 0.85,
            "analysis_summary": "养元饮品近期股价强势，但业绩下滑及投资未见效引发担忧，行业热点支撑短期表现。",
            "recommendation": "观望",
            "risk_factors": ["业绩下滑", "跨界投资未收益", "市场波动"]
        }

        # 测试_create_detailed_value方法
        basic_reason = "符合条件: 舆情 sentiment 分数(0.63) >= 阈值(0.6), 相关信息106条"
        all_data = {}

        value_output = strategy._create_detailed_value(basic_reason, all_data, full_analysis)

        print(f"\n=== value字段输出 ===")
        print(f"输出类型: {type(value_output)}")
        print(f"输出长度: {len(value_output)} 字符")
        print(f"输出内容:\n{value_output}")

        # 验证是否为JSON格式
        try:
            parsed_json = json.loads(value_output)
            print(f"\n✅ JSON解析成功")
            print(f"score字段值: {parsed_json.get('score')}")
            print(f"reason字段值: {parsed_json.get('reason')}")
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON解析失败: {e}")

        return True

    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_value_field()
    if success:
        print("\n=== 测试完成 ===")
    else:
        print("\n=== 测试失败 ===")

