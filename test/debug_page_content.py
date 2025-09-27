#!/usr/bin/env python3
"""
Debug the page content to find date information
"""

import requests
import re
from datetime import datetime, timedelta

# FireCrawl configuration
FIRECRAWL_API_KEY = ""  # Empty for local deployment
FIRECRAWL_API_URL = "http://192.168.1.2:8080/v1"

def scrape_url_with_formats(url):
    """使用FireCrawl抓取单个URL，尝试不同的格式"""
    try:
        headers = {
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json",
        }

        # 尝试不同的格式
        formats_to_try = [
            {"url": url},  # 默认格式
            {"url": url, "formats": ["markdown"]},  # 只要markdown
            {"url": url, "formats": ["html"]},  # 只要html
            {"url": url, "formats": ["markdown", "html"]},  # 要markdown和html
        ]

        for i, data in enumerate(formats_to_try):
            print(f"  尝试格式 {i+1}: {data}")
            response = requests.post(
                f"{FIRECRAWL_API_URL}/scrape", headers=headers, json=data
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success") and "data" in result:
                    print(f"    成功获取数据")
                    return result["data"]
            else:
                print(f"    请求失败: {response.status_code}")

        return None
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def find_date_patterns(content):
    """在内容中查找各种日期模式"""
    if not content:
        return []

    print(f"  搜索内容长度: {len(content)} 字符")

    # 多种日期模式
    date_patterns = [
        (r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}", "YYYY-MM-DD HH:MM:SS"),
        (r"\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}", "YYYY/MM/DD HH:MM:SS"),
        (r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}", "YYYY-MM-DD HH:MM"),
        (r"\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}", "YYYY/MM/DD HH:MM"),
        (r"\d{4}-\d{2}-\d{2}", "YYYY-MM-DD"),
        (r"\d{4}/\d{2}/\d{2}", "YYYY/MM/DD"),
        (r"\d{2}-\d{2}\s+\d{2}:\d{2}", "MM-DD HH:MM"),
        (r"\d{1,2}月\d{1,2}日\s*\d{2}:\d{2}", "M月D日 HH:MM"),
        (r"\d{1,2}月\d{1,2}日", "M月D日"),
        (r"(\d{1,2})-(\d{1,2})", "M-D"),
    ]

    found_dates = []

    for pattern, description in date_patterns:
        matches = re.findall(pattern, content)
        if matches:
            print(f"    找到 {description} 格式的日期: {matches[:5]}")  # 只显示前5个
            for match in matches[:10]:  # 最多处理10个匹配
                found_dates.append((match, pattern, description))

    return found_dates

def debug_page_content():
    """调试页面内容以查找日期信息"""
    print("调试页面内容以查找日期信息...")
    print("=" * 50)

    url = "https://guba.eastmoney.com/list,300339,1,f.html"
    print(f"URL: {url}")

    # 抓取页面内容
    page_data = scrape_url_with_formats(url)

    if not page_data:
        print("无法抓取页面内容")
        return

    print(f"获取到的数据键: {list(page_data.keys())}")

    # 检查不同格式的内容
    for format_type in ["markdown", "html"]:
        if format_type in page_data:
            content = page_data[format_type]
            print(f"\n检查 {format_type} 内容...")
            if content:
                print(f"  内容长度: {len(content)} 字符")
                # 查找日期模式
                dates = find_date_patterns(content)
                if dates:
                    print(f"  总共找到 {len(dates)} 个日期匹配")
                else:
                    print(f"  没有找到日期匹配")
            else:
                print(f"  内容为空")
        else:
            print(f"\n没有找到 {format_type} 内容")

    # 如果有HTML内容，特别检查
    if "html" in page_data and page_data["html"]:
        html_content = page_data["html"]
        print(f"\n特别检查HTML内容中的日期信息...")

        # 查找可能包含日期的特定标签或模式
        # 查找包含时间信息的div或其他标签
        time_patterns = [
            r'<span[^>]*class="[^"]*time[^"]*"[^>]*>([^<]+)</span>',
            r'<div[^>]*class="[^"]*time[^"]*"[^>]*>([^<]+)</div>',
            r'<time[^>]*>([^<]+)</time>',
            r'发表于[：:]([^<\n\r]+)',
            r'发布时间[：:]([^<\n\r]+)',
        ]

        for pattern in time_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                print(f"  找到时间信息: {matches[:5]}")

def debug_individual_post():
    """调试单个帖子页面以查找日期信息"""
    print("\n调试单个帖子页面...")
    print("=" * 50)

    # 使用一个具体的帖子URL
    post_url = "https://guba.eastmoney.com/news,300339,1595905029.html"
    print(f"帖子URL: {post_url}")

    # 抓取帖子内容
    post_data = scrape_url_with_formats(post_url)

    if not post_data:
        print("无法抓取帖子内容")
        return

    print(f"获取到的数据键: {list(post_data.keys())}")

    # 检查不同格式的内容
    for format_type in ["markdown", "html"]:
        if format_type in post_data:
            content = post_data[format_type]
            print(f"\n检查帖子 {format_type} 内容...")
            if content:
                print(f"  内容长度: {len(content)} 字符")
                # 查找日期模式
                dates = find_date_patterns(content)
                if dates:
                    print(f"  总共找到 {len(dates)} 个日期匹配")
                    # 显示前几个匹配
                    for i, (match, pattern, description) in enumerate(dates[:5]):
                        print(f"    {i+1}. {description}: {match}")
                else:
                    print(f"  没有找到日期匹配")

                # 显示内容的前1000字符用于调试
                print(f"  内容预览: {content[:1000]}...")
            else:
                print(f"  内容为空")
        else:
            print(f"\n没有找到 {format_type} 内容")

def main():
    """Main function"""
    print("Debugging page content to find date information")
    print("=" * 60)

    debug_page_content()
    debug_individual_post()

if __name__ == "__main__":
    main()

