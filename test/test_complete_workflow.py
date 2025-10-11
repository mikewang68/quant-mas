"""
最终测试 - 验证整个爬取和解析流程
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.eastmoney_guba_scraper import scrape_all_guba_data


def test_complete_workflow():
    """测试完整的爬取和解析流程"""

    # FireCrawl配置
    firecrawl_config = {
        "api_url": "http://192.168.1.2:8080/v1",
        "max_retries": 3,
        "timeout": 30,
        "retry_delay": 1
    }

    stock_code = "300339"

    print(f"测试股票: {stock_code}")
    print(f"FireCrawl配置: {firecrawl_config['api_url']}")

    try:
        # 使用公共函数爬取所有类型的数据
        all_data = scrape_all_guba_data(stock_code, firecrawl_config, limit_per_type=5)

        print(f"\n=== 爬取结果 ===")
        print(f"近期咨询: {len(all_data['consultations'])} 条")
        print(f"最新研报: {len(all_data['research_reports'])} 条")
        print(f"最新公告: {len(all_data['announcements'])} 条")
        print(f"热门帖子: {len(all_data['hot_posts'])} 条")

        # 显示详细结果
        for data_type, data_list in all_data.items():
            if data_list:
                print(f"\n=== {data_type} 详情 ===")
                for i, item in enumerate(data_list[:3], 1):  # 只显示前3条
                    print(f"{i}. 标题: {item['title']}")
                    print(f"   发布时间: {item['publishedAt']}")
                    if 'author' in item and item['author']:
                        print(f"   作者: {item['author']}")
                    if 'read_count' in item and item['read_count']:
                        print(f"   阅读: {item['read_count']}, 评论: {item['comment_count']}")

        # 验证数据格式
        print(f"\n=== 数据格式验证 ===")
        for data_type, data_list in all_data.items():
            if data_list:
                first_item = data_list[0]
                print(f"{data_type} 第一条记录的字段: {list(first_item.keys())}")
                print(f"{data_type} 第一条记录的内容:")
                print(f"  标题: {first_item['title']}")
                print(f"  时间: {first_item['publishedAt']}")

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_complete_workflow()

