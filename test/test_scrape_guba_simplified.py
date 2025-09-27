#!/usr/bin/env python3
"""
Simplified test of scrape_guba_posts() functionality
"""

import requests
import re
from datetime import datetime, timedelta

# FireCrawl configuration
FIRECRAWL_API_KEY = ""  # Empty for local deployment
FIRECRAWL_API_URL = "http://192.168.1.2:8080/v1"

def scrape_guba_posts():
    """抓取东方财富股吧页面并提取具体帖子信息"""
    print("抓取东方财富股吧页面并提取具体帖子信息...")

    try:
        headers = {
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json",
        }

        # 直接抓取股吧首页
        url = "https://guba.eastmoney.com/list,300339,1,f.html"
        data = {"url": url}

        response = requests.post(
            f"{FIRECRAWL_API_URL}/scrape", headers=headers, json=data
        )

        print(f"抓取请求状态: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("抓取请求成功")

            # 处理抓取结果
            if "data" in result:
                data_content = result["data"]

                # 提取帖子信息
                posts = []

                # 检查数据结构
                if isinstance(data_content, list):
                    page_data = data_content[0] if data_content else {}
                elif isinstance(data_content, dict):
                    page_data = data_content
                else:
                    page_data = {}

                # 从markdown或html中提取帖子信息
                content = ""
                if "markdown" in page_data:
                    content = page_data["markdown"]
                elif "html" in page_data:
                    content = page_data["html"]

                if content:
                    # 打印部分内容以便调试
                    print(f"内容长度: {len(content)} 字符")

                    # 查找帖子链接和标题的模式
                    # 匹配类似 [标题](链接) 的格式（markdown）
                    # 更宽松的匹配模式，但要确保URL是干净的
                    markdown_pattern = r'\[([^\]]+)\]\(([^)"\s]+news[^)"\s]*)'
                    markdown_matches = re.findall(markdown_pattern, content)

                    # 另一种markdown模式
                    markdown_pattern2 = r'\[([^\]]+)\]\((/news[^)"\s]*)'
                    markdown_matches2 = re.findall(markdown_pattern2, content)

                    # 匹配HTML链接模式
                    html_pattern = r'<a[^>]*href="([^"]*news[^"]*)"[^>]*>([^<]+)</a>'
                    html_matches = re.findall(html_pattern, content)

                    # 另一种HTML模式
                    html_pattern2 = r'<a[^>]*href="(/news[^"]*)"[^>]*>([^<]+)</a>'
                    html_matches2 = re.findall(html_pattern2, content)

                    print(f"从markdown找到 {len(markdown_matches)} 个链接")
                    print(f"从markdown2找到 {len(markdown_matches2)} 个链接")
                    print(f"从HTML找到 {len(html_matches)} 个链接")
                    print(f"从HTML2找到 {len(html_matches2)} 个链接")

                    # 处理markdown匹配结果
                    for match in markdown_matches[:10]:  # 取前10个
                        title, url = match
                        # 确保URL是完整的并清理URL
                        clean_url = url.split('"')[
                            0
                        ].strip()  # 移除可能的引号和额外文本
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
                                "type": "markdown_link",
                            }
                        )

                    # 处理markdown2匹配结果
                    for match in markdown_matches2[:10]:  # 取前10个
                        title, url = match
                        # 确保URL是完整的
                        full_url = "https://guba.eastmoney.com" + url

                        posts.append(
                            {
                                "title": title.strip(),
                                "url": full_url,
                                "type": "markdown_link2",
                            }
                        )

                    # 处理HTML匹配结果
                    for match in html_matches[:10]:  # 取前10个
                        url, title = match
                        # 确保URL是完整的并清理URL
                        clean_url = url.split('"')[
                            0
                        ].strip()  # 移除可能的引号和额外文本
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
                                "type": "html_link",
                            }
                        )

                    # 处理HTML2匹配结果
                    for match in html_matches2[:10]:  # 取前10个
                        url, title = match
                        # 确保URL是完整的
                        full_url = "https://guba.eastmoney.com" + url

                        posts.append(
                            {
                                "title": title.strip(),
                                "url": full_url,
                                "type": "html_link2",
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

                    print(f"\n提取到 {len(posts)} 个帖子:")
                    for i, post in enumerate(posts, 1):
                        print(f"{i}. 标题: {post['title']}")
                        print(f"   链接: {post['url']}")
                        print(f"   类型: {post['type']}")
                        print("-" * 50)

                    return posts
                else:
                    print("未能从页面内容中提取到帖子信息")
                    return []
            else:
                print("抓取响应中没有data字段")
                return []
        else:
            print(f"抓取请求失败: {response.text}")
            return []
    except Exception as e:
        print(f"抓取请求异常: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    """Main function"""
    print("Testing scrape_guba_posts functionality")
    print("=" * 50)

    results = scrape_guba_posts()

    print(f"\nFunction returned {len(results)} results")

    if results:
        print("\nFirst 3 results:")
        for i, result in enumerate(results[:3], 1):
            print(f"{i}. Title: {result.get('title', 'N/A')}")
            print(f"   URL: {result.get('url', 'N/A')}")
            print(f"   Type: {result.get('type', 'N/A')}")
    else:
        print("No results returned")

if __name__ == "__main__":
    main()

