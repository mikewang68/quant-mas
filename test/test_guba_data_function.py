"""
测试东方财富股吧数据获取功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2
from data.mongodb_manager import MongoDBManager

def test_guba_data_function():
    """测试东方财富股吧数据获取功能"""

    print("=== 测试东方财富股吧数据获取功能 ===")

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

        # 测试股票代码
        test_stock_code = "000001"  # 平安银行

        print(f"测试股票代码: {test_stock_code}")

        # 测试获取股吧数据
        print("\n1. 测试获取东方财富股吧基础数据...")
        guba_data = strategy._get_guba_data(test_stock_code)

        print(f"\n获取结果:")
        print(f"- 近期咨询: {len(guba_data.get('consultations', []))} 条")
        print(f"- 最新研报: {len(guba_data.get('research_reports', []))} 条")
        print(f"- 最新公告: {len(guba_data.get('announcements', []))} 条")
        print(f"- 热门帖子: {len(guba_data.get('hot_posts', []))} 条")

        # 显示详细数据
        print("\n2. 详细数据:")

        if guba_data.get('consultations'):
            print("\n近期咨询:")
            for i, consultation in enumerate(guba_data['consultations'], 1):
                print(f"  {i}. {consultation.get('title', 'N/A')}")
                print(f"     内容: {consultation.get('content', 'N/A')[:50]}...")
                print(f"     作者: {consultation.get('author', 'N/A')}")
                print(f"     发布时间: {consultation.get('publishedAt', 'N/A')}")

        if guba_data.get('research_reports'):
            print("\n最新研报:")
            for i, report in enumerate(guba_data['research_reports'], 1):
                print(f"  {i}. {report.get('title', 'N/A')}")
                print(f"     机构: {report.get('institution', 'N/A')}")
                print(f"     评级: {report.get('rating', 'N/A')}")
                print(f"     目标价: {report.get('target_price', 'N/A')}")

        if guba_data.get('announcements'):
            print("\n最新公告:")
            for i, announcement in enumerate(guba_data['announcements'], 1):
                print(f"  {i}. {announcement.get('title', 'N/A')}")
                print(f"     类型: {announcement.get('type', 'N/A')}")
                print(f"     内容: {announcement.get('content', 'N/A')[:50]}...")

        if guba_data.get('hot_posts'):
            print("\n热门帖子:")
            for i, post in enumerate(guba_data['hot_posts'], 1):
                print(f"  {i}. {post.get('title', 'N/A')}")
                print(f"     作者: {post.get('author', 'N/A')}")
                print(f"     阅读: {post.get('read_count', 'N/A')}, 评论: {post.get('comment_count', 'N/A')}, 点赞: {post.get('like_count', 'N/A')}")

        print("\n=== 测试完成 ===")

    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_guba_data_function()

