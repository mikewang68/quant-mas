"""
测试AkShare新闻输出格式
"""

import sys
sys.path.append('.')

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2

# 创建测试数据
test_akshare_news = [
    {"日期": "2024-09-30", "摘要": "公司发布2024年第三季度业绩预告，预计净利润同比增长50%"},
    {"日期": "2024-09-29", "摘要": "机构调研报告显示公司基本面良好，维持买入评级"},
    {"日期": "2024-09-28", "摘要": "行业政策利好，公司有望受益于新一轮发展机遇"}
]

def test_akshare_format():
    strategy = EnhancedPublicOpinionAnalysisStrategyV2("test", {})

    # 创建测试数据
    all_data = {
        "akshare_news": test_akshare_news
    }

    # 调用格式化函数
    formatted_text = strategy._format_data_for_llm(all_data)

    print("=== AkShare新闻格式化后的输出 ===")
    print(formatted_text)
    print("=== 输出结束 ===")

    # 检查格式是否正确
    lines = formatted_text.split('\n')
    for line in lines:
        if line.strip().startswith('1.') or line.strip().startswith('2.') or line.strip().startswith('3.'):
            print(f"检查行: {line}")
            if "：" in line and not "日期:" in line and not "摘要:" in line:
                print("✅ 格式正确：时间：内容")
            else:
                print("❌ 格式错误")

if __name__ == "__main__":
    test_akshare_format()

