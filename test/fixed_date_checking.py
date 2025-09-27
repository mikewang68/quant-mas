#!/usr/bin/env python3
"""
Fixed date checking logic for Guba posts
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

def is_post_within_5_days_fixed(post_content):
    """检查帖子是否在5天内发布 - 修正版本"""
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

        # 多种日期模式
        date_patterns = [
            (r"(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})", "YYYY-MM-DD HH:MM:SS"),
            (r"(\d{4})/(\d{2})/(\d{2})\s+(\d{2}):(\d{2}):(\d{2})", "YYYY/MM/DD HH:MM:SS"),
            (r"(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})", "YYYY-MM-DD HH:MM"),
            (r"(\d{4})/(\d{2})/(\d{2})\s+(\d{2}):(\d{2})", "YYYY/MM/DD HH:MM"),
            (r"(\d{4})-(\d{2})-(\d{2})", "YYYY-MM-DD"),
            (r"(\d{4})/(\d{2})/(\d{2})", "YYYY/MM/DD"),
            (r"(\d{2})-(\d{2})\s+(\d{2}):(\d{2})", "MM-DD HH:MM"),  # 这是我们找到的格式
            (r"(\d{1,2})月(\d{1,2})日\s*(\d{2}):(\d{2})", "M月D日 HH:MM"),
            (r"(\d{1,2})月(\d{1,2})日", "M月D日"),
        ]

        # 查找所有可能的日期匹配
        found_dates = []
        for pattern, description in date_patterns:
            matches = re.findall(pattern, markdown_content)
            if matches:
                for match in matches[:5]:  # 只处理前5个匹配
                    found_dates.append((match, pattern, description))

        print(f"    找到 {len(found_dates)} 个日期匹配")

        if not found_dates:
            print(f"    没有找到任何日期匹配")
            return False

        # 处理找到的日期
        for match, pattern, description in found_dates:
            try:
                print(f"    尝试解析日期: {match} ({description})")

                if description == "MM-DD HH:MM":
                    # 处理 "04-17 09:58" 格式
                    month, day, hour, minute = match
                    # 假设是今年
                    current_year = datetime.now().year
                    post_date_str = f"{current_year}-{month}-{day} {hour}:{minute}:00"
                    post_date = datetime.strptime(post_date_str, "%Y-%m-%d %H:%M:%S")
                elif description == "M月D日":
                    # 处理 "4月17日" 格式
                    month, day = match
                    current_year = datetime.now().year
                    post_date_str = f"{current_year}-{month}-{day} 00:00:00"
                    post_date = datetime.strptime(post_date_str, "%Y-%m-%d %H:%M:%S")
                elif description == "M月D日 HH:MM":
                    # 处理 "4月17日 09:58" 格式
                    month, day, hour, minute = match
                    current_year = datetime.now().year
                    post_date_str = f"{current_year}-{month}-{day} {hour}:{minute}:00"
                    post_date = datetime.strptime(post_date_str, "%Y-%m-%d %H:%M:%S")
                elif "YYYY" in description:
                    # 已经包含年份的格式
                    if isinstance(match, tuple):
                        # 多组匹配
                        if len(match) >= 6:
                            # YYYY-MM-DD HH:MM:SS
                            year, month, day, hour, minute, second = match[:6]
                            post_date_str = f"{year}-{month}-{day} {hour}:{minute}:{second}"
                            post_date = datetime.strptime(post_date_str, "%Y-%m-%d %H:%M:%S")
                        elif len(match) >= 3:
                            # YYYY-MM-DD
                            year, month, day = match[:3]
                            post_date_str = f"{year}-{month}-{day} 00:00:00"
                            post_date = datetime.strptime(post_date_str, "%Y-%m-%d %H:%M:%S")
                    else:
                        # 单个匹配字符串
                        post_date = datetime.strptime(match, "%Y-%m-%d %H:%M:%S")
                else:
                    # 其他格式
                    continue

                # 计算5天前的日期
                five_days_ago = datetime.now() - timedelta(days=5)

                print(f"    解析后的帖子日期: {post_date}")
                print(f"    5天前日期: {five_days_ago}")
                print(f"    比较结果: {post_date >= five_days_ago}")

                # 检查帖子日期是否在5天内
                if post_date >= five_days_ago:
                    return True

            except Exception as e:
                print(f"    解析日期 {match} 时出错: {e}")
                continue

        print(f"    没有找到5日内的帖子")
        return False
    except Exception as e:
        print(f"    检查帖子日期时出错: {e}")
        import traceback
        traceback.print_exc()
        return True  # 出错时默认保留帖子

def fixed_consultation_section():
    """修正后的咨询区数据获取"""
    print("修正后的咨询区(5日内数据)...")
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
    print(f"\n检查前10个帖子的详细内容...")
    recent_posts = []

    for i, post in enumerate(posts[:10]):  # 检查前10个
        print(f"\n  帖子 {i+1}: {post['title']}")
        print(f"  URL: {post['url']}")

        post_data = scrape_url_with_firecrawl(post["url"])
        if post_data:
            print(f"    成功获取帖子内容")
            is_recent = is_post_within_5_days_fixed(post_data)
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
    print("Fixed date checking for Guba posts")
    print("=" * 60)

    fixed_consultation_section()

if __name__ == "__main__":
    main()

