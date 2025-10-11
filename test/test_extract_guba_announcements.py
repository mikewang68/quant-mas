"""
测试程序：提取东方财富股吧公告页面前5条信息
URL: https://guba.eastmoney.com/list,300339,3,f.html
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2
from data.mongodb_manager import MongoDBManager

def test_extract_guba_announcements():
    """测试提取东方财富股吧公告页面前5条信息"""

    print("=== 测试提取东方财富股吧公告页面前5条信息 ===")
    print("URL: https://guba.eastmoney.com/list,300339,3,f.html")
    print()

    # 初始化策略
    strategy_name = "增强型舆情分析策略V2"
    params = {
        "sentiment_threshold": 0.5,
        "news_count_threshold": 1
    }

    try:
        # 初始化数据库管理器
        db_manager = MongoDBManager()

        # 创建策略实例
        strategy = EnhancedPublicOpinionAnalysisStrategyV2(strategy_name, params, db_manager)

        # 测试URL
        test_url = "https://guba.eastmoney.com/list,300339,3,f.html"

        print(f"1. 开始使用FireCrawl爬取URL: {test_url}")

        # 使用FireCrawl爬取数据
        firecrawl_data = strategy._scrape_with_firecrawl(test_url, "东方财富股吧公告")

        print(f"2. FireCrawl爬取结果: {len(firecrawl_data)} 条数据")

        if firecrawl_data:
            print("\n3. 前5条公告信息:")
            for i, item in enumerate(firecrawl_data[:5], 1):
                print(f"\n--- 第{i}条公告 ---")
                print(f"标题: {item.get('title', 'N/A')}")
                print(f"URL: {item.get('url', 'N/A')}")
                print(f"来源: {item.get('source', 'N/A')}")
                print(f"发布时间: {item.get('publishedAt', 'N/A')}")
                print(f"作者: {item.get('author', 'N/A')}")

                # 显示内容（前500字符）
                content = item.get('content', '')
                if content:
                    print(f"内容预览: {content[:500]}{'...' if len(content) > 500 else ''}")
                else:
                    print("内容: 无")

                print("-" * 50)

            # 显示所有数据的统计信息
            print(f"\n4. 数据统计:")
            print(f"总数据条数: {len(firecrawl_data)}")

            # 分析数据质量
            valid_titles = sum(1 for item in firecrawl_data if item.get('title') and item.get('title').strip())
            valid_content = sum(1 for item in firecrawl_data if item.get('content') and len(item.get('content', '').strip()) > 50)

            print(f"有效标题数: {valid_titles}/{len(firecrawl_data)}")
            print(f"有效内容数: {valid_content}/{len(firecrawl_data)}")

        else:
            print("\n3. FireCrawl爬取数据为空")

        print("\n=== 测试完成 ===")

    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_extract_guba_announcements()

