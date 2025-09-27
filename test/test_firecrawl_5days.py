#!/usr/bin/env python3
"""
Test FireCrawl to get 5 days of data from Eastmoney Guba
"""

import requests
import re
from datetime import datetime, timedelta

# FireCrawl configuration
FIRECRAWL_API_KEY = ""  # Empty for local deployment
FIRECRAWL_API_URL = "http://192.168.1.2:8080/v1"

def is_post_within_5_days(post_content):
    """检查帖子是否在5天内发布"""
    try:
        # 从markdown内容中提取日期
        markdown_content = ""
        if isinstance(post_content, dict) and "markdown" in post_content:
            markdown_content = post_content["markdown"]
        elif isinstance(post_content, str):
            markdown_content = post_content

        if not markdown_content:
            return False

        # 查找日期模式 (例如: 2025-09-05 10:17:51)
        date_pattern = r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}"
        date_matches = re.findall(date_pattern, markdown_content)

        if not date_matches:
            return False

        # 获取最新的日期（通常是发帖日期）
        post_date_str = date_matches[0]
        post_date = datetime.strptime(post_date_str, "%Y-%m-%d %H:%M:%S")

        # 计算5天前的日期
        five_days_ago = datetime.now() - timedelta(days=5)

        # 检查帖子日期是否在5天内
        return post_date >= five_days_ago
    except Exception as e:
        print(f"检查帖子日期时出错: {e}")
        return True  # 出错时默认保留帖子

def scrape_guba_5days_data():
    """爬取东方财富股吧指定页面5日内的数据"""
    print("爬取东方财富股吧指定页面5日内的数据...")

    # 目标URL
    url = "https://guba.eastmoney.com/list,300339,1,f.html"

    # 计算5天前的日期
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5)

    # 格式化日期为YYYY-MM-DD
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    print(f"爬取URL: {url}")
    print(f"日期范围: {start_date_str} 到 {end_date_str}")

    try:
        headers = {
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json",
        }

        # 使用Firecrawl v1 API进行爬取
        data = {
            "url": url,
        }

        response = requests.post(
            f"{FIRECRAWL_API_URL}/scrape", headers=headers, json=data
        )

        print(f"爬取请求状态: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("爬取请求成功")

            # 处理爬取结果
            if "data" in result:
                data_content = result["data"]

                # 提取帖子链接
                posts = []

                # 从markdown或html中提取帖子信息
                content = ""
                if "markdown" in data_content:
                    content = data_content["markdown"]
                elif "html" in data_content:
                    content = data_content["html"]

                if content:
                    # 查找帖子链接和标题的模式
                    markdown_pattern = r'\[([^\]]+)\]\(([^)"\s]+news[^)"\s]*)'
                    markdown_matches = re.findall(markdown_pattern, content)

                    # 处理匹配结果
                    for match in markdown_matches[:20]:  # 取前20个
                        title, url = match
                        # 确保URL是完整的并清理URL
                        clean_url = url.split('"')[0].strip()
                        if clean_url.startswith("/"):
                            full_url = "https://guba.eastmoney.com" + clean_url
                        elif clean_url.startswith("http"):
                            full_url = clean_url
                        else:
                            full_url = "https://guba.eastmoney.com/" + clean_url

                        posts.append(
                            {
                                "title": title.strip(),
                                "url": full_url,
                            }
                        )

                    # 去重
                    unique_posts = []
                    seen_urls = set()
                    for post in posts:
                        if post["url"] not in seen_urls:
                            unique_posts.append(post)
                            seen_urls.add(post["url"])

                    posts = unique_posts[:10]  # 最多保留10个

                    print(f"\n提取到 {len(posts)} 个帖子链接:")
                    for i, post in enumerate(posts, 1):
                        print(f"{i}. 标题: {post['title']}")
                        print(f"   链接: {post['url']}")

                    # 尝试抓取前几个帖子的详细内容并检查日期
                    print(f"\n尝试抓取前5个帖子的详细内容并检查日期...")
                    recent_posts = []
                    for i, post in enumerate(posts[:5]):  # 只抓取前5个
                        print(f"\n抓取第 {i + 1} 个帖子: {post['title']}")

                        post_data = {"url": post["url"]}

                        post_response = requests.post(
                            f"{FIRECRAWL_API_URL}/scrape",
                            headers=headers,
                            json=post_data,
                        )

                        if post_response.status_code == 200:
                            post_result = post_response.json()
                            if "data" in post_result:
                                post_content = post_result["data"]
                                # 检查帖子是否在5天内
                                if is_post_within_5_days(post_content):
                                    recent_posts.append(
                                        {
                                            "title": post["title"],
                                            "url": post["url"],
                                            "content": post_content,
                                        }
                                    )
                                    print(f"  成功抓取帖子内容(5天内)")
                                else:
                                    print(f"  帖子不在5天内，跳过")
                            else:
                                print(f"  抓取帖子内容失败: 没有data字段")
                        else:
                            print(f"  抓取帖子失败: {post_response.status_code}")

                    print(f"\n找到 {len(recent_posts)} 个5日内的帖子")
                    return recent_posts
                else:
                    print("未能从页面内容中提取到帖子信息")
                    return []
            else:
                print("爬取响应中没有data字段")
                return []
        else:
            print(f"爬取请求失败: {response.text}")
            return []
    except Exception as e:
        print(f"爬取请求异常: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    """Main function"""
    print("Testing FireCrawl to get 5 days of data from Eastmoney Guba")
    print("=" * 60)

    results = scrape_guba_5days_data()

    print(f"\nFunction returned {len(results)} recent posts")

    if results:
        print("\n5日内的帖子:")
        for i, result in enumerate(results, 1):
            print(f"{i}. 标题: {result.get('title', 'N/A')}")
            print(f"   链接: {result.get('url', 'N/A')}")
    else:
        print("没有找到5日内的帖子")

if __name__ == "__main__":
    main()

