"""
测试增强版股吧数据提取功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2
from data.mongodb_manager import MongoDBManager


def test_guba_data_extraction():
    """测试股吧数据提取功能"""

    # 创建策略实例
    strategy = EnhancedPublicOpinionAnalysisStrategyV2(
        name="测试策略",
        params={
            "sentiment_threshold": 0.0,
            "news_count_threshold": 1
        },
        db_manager=None
    )

    # 测试股票代码
    stock_code = "300339"

    print(f"测试股票: {stock_code}")

    try:
        # 获取股吧数据
        guba_data = strategy._get_guba_data(stock_code)

        print(f"\n股吧数据获取结果:")
        print(f"近期咨询: {len(guba_data['consultations'])} 条")
        print(f"最新研报: {len(guba_data['research_reports'])} 条")
        print(f"最新公告: {len(guba_data['announcements'])} 条")
        print(f"热门帖子: {len(guba_data['hot_posts'])} 条")

        # 显示部分数据
        if guba_data['consultations']:
            print(f"\n第一条咨询:")
            print(f"  标题: {guba_data['consultations'][0]['title']}")
            print(f"  时间: {guba_data['consultations'][0]['publishedAt']}")
            print(f"  作者: {guba_data['consultations'][0]['author']}")
            print(f"  阅读: {guba_data['consultations'][0]['read_count']}")
            print(f"  评论: {guba_data['consultations'][0]['comment_count']}")

        if guba_data['research_reports']:
            print(f"\n第一条研报:")
            print(f"  标题: {guba_data['research_reports'][0]['title']}")
            print(f"  时间: {guba_data['research_reports'][0]['publishedAt']}")

        if guba_data['announcements']:
            print(f"\n第一条公告:")
            print(f"  标题: {guba_data['announcements'][0]['title']}")
            print(f"  时间: {guba_data['announcements'][0]['publishedAt']}")

        if guba_data['hot_posts']:
            print(f"\n第一条热门帖子:")
            print(f"  标题: {guba_data['hot_posts'][0]['title']}")
            print(f"  时间: {guba_data['hot_posts'][0]['publishedAt']}")
            print(f"  作者: {guba_data['hot_posts'][0]['author']}")
            print(f"  阅读: {guba_data['hot_posts'][0]['read_count']}")
            print(f"  评论: {guba_data['hot_posts'][0]['comment_count']}")

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_guba_data_extraction()

