#!/usr/bin/env python3
"""
Debug the date checking logic for Guba posts
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

    return unique_posts

def is_post_within_5_days_debug(post_content):
    """检查帖子是否在5天内发布 - 调试版本"""
    try:
        print(f"  检查帖子日期...")

        # 从markdown内容中提取日期
        markdown_content = ""
        if isinstance(post_content, dict) and "markdown" in post_content:
            markdown_content = post_content["markdown"]
        elif isinstance(post_content, str):
            markdown_content = post_content

        print(f"    Markdown内容长度: {len(markdown_content) if markdown_content else 0}")

        if not markdown_content:
            print(f"    没有找到markdown内容")
            return False

        # 打印前1000字符用于调试
        print(f"    内容预览: {markdown_content[:1000]}...")

        # 查找日期模式 (例如: 2025-09-05 10:17:51)
        date_pattern = r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}"
        date_matches = re.findall(date_pattern, markdown_content)

        print(f"    找到日期匹配: {date_matches}")

        if not date_matches:
            # 尝试其他日期模式
            print(f"    尝试其他日期模式...")

            # 模式2: YYYY-MM-DD
            date_pattern2 = r"\d{4}-\d{2}-\d{2}"
            date_matches2 = re.findall(date_pattern2, markdown_content)
            print(f"    模式2找到日期匹配: {date_matches2}")

            if date_matches2:
                # 使用第一个找到的日期
                post_date_str = date_matches2[0]
                # 假设时间为00:00:00
                post_date_str = post_date_str + " 00:00:00"
            else:
                print(f"    没有找到任何日期匹配")
                return False
        else:
            # 获取最新的日期（通常是发帖日期）
            post_date_str = date_matches[0]

        print(f"    解析日期字符串: {post_date_str}")
        post_date = datetime.strptime(post_date_str, "%Y-%m-%d %H:%M:%S")

        # 计算5天前的日期
        five_days_ago = datetime.now() - timedelta(days=5)

        print(f"    帖子日期: {post_date}")
        print(f"    5天前日期: {five_days_ago}")
        print(f"    比较结果: {post_date >= five_days_ago}")

        # 检查帖子日期是否在5天内
        return post_date >= five_days_ago
    except Exception as e:
        print(f"    检查帖子日期时出错: {e}")
        import traceback
        traceback.print_exc()
        return True  # 出错时默认保留帖子

def debug_consultation_section():
    """调试咨询区数据获取"""
    print("调试咨询区(5日内数据)...")
    print("=" * 50)

    url = "https://guba.eastmoney.com/list,300339,1,f.html"
    print(f"URL: {url}")

    # 抓取页面内容
    page_data = scrape_url_with_firecrawl(url)

    if not page_data:
        print("无法抓取页面内容")
        return

    # 从markdown或html中提取内容
    content = ""
    if "markdown" in page_data:
        content = page_data["markdown"]
    elif "html" in page_data:
        content = page_data["html"]

    if not content:
        print("页面内容为空")
        return

    print(f"页面内容长度: {len(content)} 字符")

    # 提取帖子链接
    posts = extract_posts_from_content(content)
    print(f"提取到 {len(posts)} 个帖子链接")

    # 检查前几个帖子的详细内容
    print(f"\n检查前5个帖子的详细内容...")
    recent_posts = []

    for i, post in enumerate(posts[:5]):  # 检查前5个
        print(f"\n  帖子 {i+1}: {post['title']}")
        print(f"  URL: {post['url']}")

        post_data = scrape_url_with_firecrawl(post["url"])
        if post_data:
            print(f"    成功获取帖子内容")
            is_recent = is_post_within_5_days_debug(post_data)
            if is_recent:
                recent_posts.append(post)
                print(f"    >>> 这是一个5日内的帖子 <<<")
            else:
                print(f"    这不是一个5日内的帖子")
        else:
            print(f"    无法获取帖子内容")

    print(f"\n总共找到 {len(recent_posts)} 个5日内的帖子")
    for post in recent_posts:
        print(f"  - {post['title']}")

def main():
    """Main function"""
    print("Debugging date checking for Guba posts")
    print("=" * 60)

    debug_consultation_section()

if __name__ == "__main__":
    main()

