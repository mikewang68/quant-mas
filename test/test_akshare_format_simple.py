"""
测试AkShare新闻输出格式 - 简化版本
"""

import sys
sys.path.append('.')

# 直接测试格式化逻辑
def test_akshare_format():
    # 创建测试数据
    test_akshare_news = [
        {"日期": "2024-09-30", "摘要": "公司发布2024年第三季度业绩预告，预计净利润同比增长50%"},
        {"日期": "2024-09-29", "摘要": "机构调研报告显示公司基本面良好，维持买入评级"},
        {"日期": "2024-09-28", "摘要": "行业政策利好，公司有望受益于新一轮发展机遇"}
    ]

    # 模拟格式化逻辑
    formatted_text = ""

    # 添加AkShare新闻
    if test_akshare_news:
        formatted_text += "AkShare近5日新闻:\n"
        for i, news in enumerate(test_akshare_news[:10], 1):
            formatted_text += f"    {i}. {news.get('日期', 'N/A')}：{news.get('摘要', 'N/A')[:60]}...\n"
        formatted_text += "\n"

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

