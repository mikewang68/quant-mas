#!/usr/bin/env python3
"""
Check the page structure to understand how to identify 5-day data
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

def analyze_page_structure():
    """分析页面结构以理解如何识别5日数据"""
    print("分析页面结构以理解如何识别5日数据...")
    print("=" * 50)

    url = "https://guba.eastmoney.com/list,300339,1,f.html"
    print(f"URL: {url}")

    # 抓取页面内容
    page_data = scrape_url_with_firecrawl(url)

    if not page_data:
        print("无法抓取页面内容")
        return

    # 检查数据结构
    print(f"数据键: {list(page_data.keys())}")

    if "metadata" in page_data:
        print(f"元数据: {page_data['metadata']}")

    # 检查markdown内容
    if "markdown" in page_data:
        content = page_data["markdown"]
        print(f"\nMarkdown内容长度: {len(content)} 字符")

        # 查找可能的结构模式
        lines = content.split('\n')
        print(f"总行数: {len(lines)}")

        # 查找包含日期的行
        date_lines = []
        for i, line in enumerate(lines[:100]):  # 检查前100行
            if re.search(r'\d{1,2}-\d{1,2}|\d{1,2}月\d{1,2}日', line):
                date_lines.append((i, line.strip()))

        print(f"\n找到包含日期的行 ({len(date_lines)} 行):")
        for i, (line_num, line) in enumerate(date_lines[:10]):  # 显示前10行
            print(f"  {line_num+1}: {line}")

        # 查找表格结构
        table_pattern = r'\|.*\|.*\|.*\|'
        table_lines = []
        for i, line in enumerate(lines):
            if re.match(table_pattern, line.strip()):
                table_lines.append((i, line.strip()))

        print(f"\n找到表格行 ({len(table_lines)} 行):")
        for i, (line_num, line) in enumerate(table_lines[:20]):  # 显示前20行
            print(f"  {line_num+1}: {line}")

        # 查找列表结构
        list_pattern = r'^\s*[*\-]\s+'
        list_lines = []
        for i, line in enumerate(lines):
            if re.match(list_pattern, line):
                list_lines.append((i, line.strip()))

        print(f"\n找到列表行 ({len(list_lines)} 行):")
        for i, (line_num, line) in enumerate(list_lines[:10]):  # 显示前10行
            print(f"  {line_num+1}: {line}")

        # 查找链接结构
        link_pattern = r'\[.*\]\(.*\)'
        link_lines = []
        for i, line in enumerate(lines):
            if re.search(link_pattern, line):
                link_lines.append((i, line.strip()))

        print(f"\n找到包含链接的行 ({len(link_lines)} 行)")

        # 显示包含链接的前几行以分析结构
        for i, (line_num, line) in enumerate(link_lines[:10]):  # 显示前10行
            print(f"  {line_num+1}: {line}")

def check_individual_posts_for_metadata():
    """检查单个帖子是否有元数据包含日期"""
    print("\n检查单个帖子是否有元数据包含日期...")
    print("=" * 50)

    # 使用一个具体的帖子URL
    post_url = "https://guba.eastmoney.com/news,300339,1595905029.html"
    print(f"帖子URL: {post_url}")

    # 抓取帖子内容
    post_data = scrape_url_with_firecrawl(post_url)

    if not post_data:
        print("无法抓取帖子内容")
        return

    print(f"数据键: {list(post_data.keys())}")

    # 检查元数据
    if "metadata" in post_data:
        metadata = post_data["metadata"]
        print(f"\n元数据: {metadata}")

        # 查找发布日期相关字段
        date_fields = []
        for key, value in metadata.items():
            if isinstance(value, str) and re.search(r'\d{4}[-/]\d{2}[-/]\d{2}', value):
                date_fields.append((key, value))

        print(f"\n找到可能的日期字段: {date_fields}")

def main():
    """Main function"""
    print("Checking page structure to understand 5-day data identification")
    print("=" * 70)

    analyze_page_structure()
    check_individual_posts_for_metadata()

if __name__ == "__main__":
    main()

