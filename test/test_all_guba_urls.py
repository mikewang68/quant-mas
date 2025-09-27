#!/usr/bin/env python3
"""
Test FireCrawl scraping for all the specific Eastmoney Guba URLs mentioned in the task
"""

import requests
import re
from datetime import datetime, timedelta

# FireCrawl configuration
FIRECRAWL_API_KEY = ""  # Empty for local deployment
FIRECRAWL_API_URL = "http://192.168.1.2:8080/v1"

def scrape_url_with_firecrawl(url):
    """使用FireCrawl抓取单个URL"""
    try:
        headers = {
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json",
        }

        data = {"url": url}

        response = requests.post(
            f"{FIRECRAWL_API_URL}/scrape", headers=headers, json=data
        )

        if response.status_code == 200:
            result = response.json()
            if result.get("success") and "data" in result:
                return result["data"]
        return None
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def extract_posts_from_content(content):
    """从页面内容中提取帖子链接"""
    if not content:
        return []

    posts = []

    # 查找帖子链接和标题的模式
    markdown_pattern = r'\[([^\]]+)\]\(([^)"\s]+news[^)"\s]*)'
    markdown_matches = re.findall(markdown_pattern, content)

    # 处理匹配结果
    for match in markdown_matches:
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

    return unique_posts

def get_5_days_data(url, section_name):
    """获取指定URL的5日内数据"""
    print(f"\n获取 {section_name} 的5日内数据...")
    print(f"URL: {url}")

    # 抓取页面内容
    page_data = scrape_url_with_firecrawl(url)

    if not page_data:
        print(f"  无法抓取页面内容")
        return []

    # 从markdown或html中提取内容
    content = ""
    if "markdown" in page_data:
        content = page_data["markdown"]
    elif "html" in page_data:
        content = page_data["html"]

    if not content:
        print(f"  页面内容为空")
        return []

    print(f"  页面内容长度: {len(content)} 字符")

    # 提取帖子链接
    posts = extract_posts_from_content(content)
    print(f"  提取到 {len(posts)} 个帖子链接")

    # 对于需要5日内数据的页面，检查帖子日期
    if "5日内数据" in section_name:
        # 抓取前几个帖子的详细内容并检查日期
        recent_posts = []
        for i, post in enumerate(posts[:10]):  # 抓取前10个
            print(f"  检查帖子 {i+1}: {post['title'][:50]}...")

            post_data = scrape_url_with_firecrawl(post["url"])
            if post_data and is_post_within_5_days(post_data):
                recent_posts.append(post)

            # 限制检查数量以避免过多请求
            if len(recent_posts) >= 5:
                break

        print(f"  找到 {len(recent_posts)} 个5日内的帖子")
        return recent_posts[:5]  # 返回最多5个
    else:
        # 对于需要前N条数据的页面，直接返回前N个
        if "前5条" in section_name:
            return posts[:5]
        elif "前10条" in section_name:
            return posts[:10]

    return posts[:5]  # 默认返回前5个

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
        return True  # 出错时默认保留帖子

def main():
    """Main function"""
    print("Testing FireCrawl scraping for all specified Eastmoney Guba URLs")
    print("=" * 70)

    # URLs to test with specific requirements
    urls_to_test = [
        {
            "url": "https://guba.eastmoney.com/list,300339,1,f.html",
            "description": "Consultation section, 5 days data",
            "section_name": "咨询区(5日内数据)"
        },
        {
            "url": "https://guba.eastmoney.com/list,300339,2,f.html",
            "description": "Research reports section, first 5 items",
            "section_name": "研报区(前5条数据)"
        },
        {
            "url": "https://guba.eastmoney.com/list,300339,3,f.html",
            "description": "Announcements section, 5 days data",
            "section_name": "公告区(5日内数据)"
        },
        {
            "url": "https://guba.eastmoney.com/list,300339,99.html",
            "description": "Hot posts section, 5 days data",
            "section_name": "热帖区(5日内数据)"
        },
        {
            "url": "https://guba.eastmoney.com/list,300339.html",
            "description": "Main page, first 10 items",
            "section_name": "主页(前10条数据)"
        }
    ]

    results = {}

    for i, test_item in enumerate(urls_to_test, 1):
        url = test_item["url"]
        description = test_item["description"]
        section_name = test_item["section_name"]

        print(f"\n{i}. 测试URL: {url}")
        print(f"   描述: {description}")

        try:
            data = get_5_days_data(url, section_name)
            results[url] = {
                "status": "success",
                "data": data,
                "count": len(data)
            }
            print(f"   成功获取 {len(data)} 条数据")

            # 显示前几条数据作为示例
            for j, post in enumerate(data[:3], 1):
                print(f"     {j}. {post['title'][:60]}...")

        except Exception as e:
            print(f"   错误: {e}")
            results[url] = {
                "status": "error",
                "error": str(e),
                "count": 0
            }

    # Summary
    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)

    success_count = sum(1 for r in results.values() if r["status"] == "success")
    total_items = sum(r["count"] for r in results.values())

    print(f"成功抓取: {success_count}/{len(urls_to_test)} 个URL")
    print(f"总共获取数据: {total_items} 条")

    for url, result in results.items():
        # Get short URL for display
        short_url = url.replace("https://guba.eastmoney.com/", "")
        print(f"\n{short_url}")
        print(f"  状态: {result['status'].upper()}")
        print(f"  数据条数: {result['count']}")
        if result["status"] == "error":
            print(f"  错误: {result['error']}")

    print("\n" + "=" * 70)
    print("测试完成!")

if __name__ == "__main__":
    main()

