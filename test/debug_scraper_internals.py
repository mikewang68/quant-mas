"""
详细调试公共函数中的解析和格式化逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.eastmoney_guba_scraper import EastMoneyGubaScraper


def debug_scraper_internals():
    """调试爬取器内部逻辑"""

    # FireCrawl配置
    firecrawl_config = {
        "api_url": "http://192.168.1.2:8080/v1",
        "max_retries": 3,
        "timeout": 30,
        "retry_delay": 1
    }

    stock_code = "000985"
    data_type = "consultations"

    print(f"调试股票: {stock_code}")
    print(f"数据类型: {data_type}")

    try:
        # 1. 测试URL构建
        print(f"\n=== 1. URL构建测试 ===")
        url = EastMoneyGubaScraper._build_guba_url(stock_code, data_type)
        print(f"构建的URL: {url}")

        # 2. 测试API调用
        print(f"\n=== 2. API调用测试 ===")
        firecrawl_data = EastMoneyGubaScraper._call_firecrawl_api(url, firecrawl_config)
        print(f"API调用结果: {len(firecrawl_data)} 条数据")

        if firecrawl_data:
            print(f"第一条数据键: {list(firecrawl_data[0].keys())}")
            if "markdown" in firecrawl_data[0]:
                markdown_content = firecrawl_data[0]["markdown"]
                print(f"markdown内容长度: {len(markdown_content)} 字符")
                print(f"markdown预览: {markdown_content[:200]}...")

        # 3. 测试解析逻辑
        print(f"\n=== 3. 解析逻辑测试 ===")
        if firecrawl_data:
            posts = EastMoneyGubaScraper._parse_guba_markdown(firecrawl_data, limit=5)
            print(f"解析结果: {len(posts)} 条帖子")

            if posts:
                for i, post in enumerate(posts, 1):
                    print(f"  {i}. 标题: {post['title']}")
                    print(f"     时间: {post['last_update']}")
                    print(f"     作者: {post['author']}")
                    print(f"     阅读: {post['read_count']}, 评论: {post['comment_count']}")
            else:
                print("❌ 没有解析到任何帖子")

        # 4. 测试格式化逻辑
        print(f"\n=== 4. 格式化逻辑测试 ===")
        if posts:
            formatted_posts = EastMoneyGubaScraper._format_posts(posts, data_type)
            print(f"格式化结果: {len(formatted_posts)} 条记录")

            if formatted_posts:
                for i, post in enumerate(formatted_posts, 1):
                    print(f"  {i}. 标题: {post['title']}")
                    print(f"     时间: {post['publishedAt']}")
                    print(f"     作者: {post.get('author', 'N/A')}")
                    print(f"     阅读: {post.get('read_count', 'N/A')}, 评论: {post.get('comment_count', 'N/A')}")
                    print(f"     所有字段: {list(post.keys())}")
            else:
                print("❌ 格式化后没有记录")

        # 5. 测试完整流程
        print(f"\n=== 5. 完整流程测试 ===")
        final_result = EastMoneyGubaScraper.scrape_eastmoney_guba(
            stock_code, data_type, firecrawl_config, 5
        )
        print(f"最终结果: {len(final_result)} 条记录")

    except Exception as e:
        print(f"调试失败: {e}")
        import traceback
        traceback.print_exc()


def debug_all_data_types():
    """调试所有数据类型"""

    firecrawl_config = {
        "api_url": "http://192.168.1.2:8080/v1",
        "max_retries": 3,
        "timeout": 30,
        "retry_delay": 1
    }

    stock_code = "000985"
    data_types = ["consultations", "research_reports", "announcements", "hot_posts"]

    print(f"\n=== 调试所有数据类型 ===")
    print(f"股票: {stock_code}")

    for data_type in data_types:
        print(f"\n--- {data_type} ---")
        try:
            result = EastMoneyGubaScraper.scrape_eastmoney_guba(
                stock_code, data_type, firecrawl_config, 3
            )
            print(f"结果: {len(result)} 条记录")

            if result:
                print(f"第一条记录字段: {list(result[0].keys())}")
        except Exception as e:
            print(f"错误: {e}")


if __name__ == "__main__":
    debug_scraper_internals()
    debug_all_data_types()

