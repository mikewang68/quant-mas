"""
详细调试格式化函数
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.eastmoney_guba_scraper import EastMoneyGubaScraper


def debug_format_function():
    """调试格式化函数"""

    # 模拟解析出的帖子数据
    sample_posts = [
        {
            "read_count": "278",
            "comment_count": "0",
            "title": "大庆华科龙虎榜：营业部净卖出3053.15万元",
            "author": "[大庆华科资讯](https://guba.eastmoney.com/list,000985.html)",
            "last_update": "09-30 04:47",
            "type": "table_post"
        },
        {
            "read_count": "2075",
            "comment_count": "26",
            "title": "大庆华科(000985)龙虎榜数据(09-30)",
            "author": "[大庆华科资讯](https://guba.eastmoney.com/list,000985.html)",
            "last_update": "09-30 04:26",
            "type": "table_post"
        }
    ]

    data_type = "consultations"

    print(f"测试格式化函数 - 数据类型: {data_type}")
    print(f"输入帖子数量: {len(sample_posts)}")

    try:
        # 直接调用格式化函数
        formatted_posts = EastMoneyGubaScraper._format_posts(sample_posts, data_type)

        print(f"格式化结果: {len(formatted_posts)} 条记录")

        if formatted_posts:
            for i, post in enumerate(formatted_posts, 1):
                print(f"\n记录 {i}:")
                print(f"  标题: {post['title']}")
                print(f"  时间: {post['publishedAt']}")
                print(f"  作者: {post.get('author', 'N/A')}")
                print(f"  阅读: {post.get('read_count', 'N/A')}")
                print(f"  评论: {post.get('comment_count', 'N/A')}")
                print(f"  所有字段: {list(post.keys())}")
        else:
            print("❌ 格式化后没有记录")

    except Exception as e:
        print(f"格式化失败: {e}")
        import traceback
        traceback.print_exc()


def debug_complete_scraper():
    """调试完整的爬取器"""

    firecrawl_config = {
        "api_url": "http://192.168.1.2:8080/v1",
        "max_retries": 3,
        "timeout": 30,
        "retry_delay": 1
    }

    stock_code = "000985"
    data_type = "consultations"

    print(f"\n=== 调试完整爬取器 ===")
    print(f"股票: {stock_code}, 数据类型: {data_type}")

    try:
        # 1. 爬取数据
        firecrawl_data = EastMoneyGubaScraper._call_firecrawl_api(
            f"https://guba.eastmoney.com/list,{stock_code},1,f.html",
            firecrawl_config
        )
        print(f"API调用结果: {len(firecrawl_data)} 条数据")

        # 2. 解析数据
        if firecrawl_data:
            posts = EastMoneyGubaScraper._parse_guba_markdown(firecrawl_data, 5)
            print(f"解析结果: {len(posts)} 条帖子")

            # 3. 格式化数据
            if posts:
                formatted_posts = EastMoneyGubaScraper._format_posts(posts, data_type)
                print(f"格式化结果: {len(formatted_posts)} 条记录")

                # 4. 完整流程
                final_result = EastMoneyGubaScraper.scrape_eastmoney_guba(
                    stock_code, data_type, firecrawl_config, 5
                )
                print(f"完整流程结果: {len(final_result)} 条记录")

    except Exception as e:
        print(f"完整流程失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_format_function()
    debug_complete_scraper()

