"""
测试增强型舆情分析策略V2的输出格式
"""

import sys
import os
sys.path.append('.')

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2

# 创建测试数据
test_guba_data = {
    "consultations": [
        {"title": "09-30 04:47：大庆华科龙虎榜：营业部净卖出3053.15万元", "publishedAt": "09-30 04:47"},
        {"title": "09-29 15:30：投资者咨询公司未来发展", "publishedAt": "09-29 15:30"}
    ],
    "research_reports": [
        {"title": "09-28 10:00：中信证券研报：维持买入评级", "publishedAt": "09-28 10:00"},
        {"title": "09-27 14:20：华泰证券：目标价上调至25元", "publishedAt": "09-27 14:20"}
    ],
    "announcements": [
        {"title": "09-26 09:00：关于2024年第三季度业绩预告", "publishedAt": "09-26 09:00"},
        {"title": "09-25 16:45：董事会决议公告", "publishedAt": "09-25 16:45"}
    ],
    "hot_posts": [
        {"title": "09-24 11:30：这只股票明天会涨停吗？", "publishedAt": "09-24 11:30"},
        {"title": "09-23 13:15：机构资金大幅流入", "publishedAt": "09-23 13:15"}
    ]
}

# 测试格式化函数
def test_format_data():
    strategy = EnhancedPublicOpinionAnalysisStrategyV2("test", {})

    # 创建测试数据
    all_data = {
        "guba_data": test_guba_data
    }

    # 调用格式化函数
    formatted_text = strategy._format_data_for_llm(all_data)

    print("=== 格式化后的输出 ===")
    print(formatted_text)
    print("=== 输出结束 ===")

    # 检查是否还有"发布时间:"前缀
    if "发布时间:" in formatted_text:
        print("❌ 错误：输出中仍然包含'发布时间:'前缀")
    else:
        print("✅ 正确：输出中不包含'发布时间:'前缀")

    # 检查格式是否正确
    lines = formatted_text.split('\n')
    for line in lines:
        if line.strip().startswith('1.') or line.strip().startswith('2.'):
            print(f"检查行: {line}")
            if "：" in line and not line.startswith("    ") and not "标题:" in line:
                print("✅ 格式正确：时间：内容")
            else:
                print("❌ 格式错误")

if __name__ == "__main__":
    test_format_data()

