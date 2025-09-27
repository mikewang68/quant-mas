#!/usr/bin/env python3
"""
Correct implementation for getting 5-day data from Guba pages
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

def parse_table_row(row):
    """解析表格行，提取帖子信息"""
    # 表格行格式示例:
    # | 301 | 2   | [A股：大家做好心理准备了，A股，很可能要迎来大级别的行情](https://caifuhao.eastmoney.com/news/20250417095822088945980) | [穆哥看市](https://i.eastmoney.com/5478112807610928) | 04-17 09:58 |

    # 使用正则表达式提取信息
    pattern = r'\|\s*\d+\s*\|\s*\d+\s*\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*\[([^\]]+)\]\([^)]+\)\s*\|\s*([^|]+)\s*\|'
    match = re.match(pattern, row.strip())

    if match:
        title = match.group(1).strip()
        url = match.group(2).strip()
        author = match.group(3).strip()
        time_str = match.group(4).strip()

        return {
            "title": title,
            "url": url,
            "author": author,
            "time": time_str
        }

    return None

def is_time_within_5_days(time_str):
    """检查时间是否在5天内"""
    try:
        # 处理 "04-17 09:58" 格式
        if ':' in time_str and '-' in time_str:
            # 假设是今年
            current_year = datetime.now().year
            # 解析月日时分
            parts = time_str.split(' ')
            if len(parts) == 2:
                date_part, time_part = parts
                month_day_parts = date_part.split('-')
                if len(month_day_parts) == 2:
                    month, day = month_day_parts
                    hour_minute_parts = time_part.split(':')
                    if len(hour_minute_parts) == 2:
                        hour, minute = hour_minute_parts

                        # 构造完整日期时间
                        date_time_str = f"{current_year}-{month}-{day} {hour}:{minute}:00"
                        post_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")

                        # 计算5天前的时间
                        five_days_ago = datetime.now() - timedelta(days=5)

                        # 检查是否在5天内
                        return post_time >= five_days_ago

        return False
    except Exception as e:
        print(f"解析时间时出错: {e}")
        return False

def get_5_days_data_from_page(url, section_name, data_type="5_days"):
    """从页面获取5日内的数据或前N条数据"""
    print(f"\n获取 {section_name} 的数据...")
    print(f"URL: {url}")

    # 抓取页面内容
    page_data = scrape_url_with_firecrawl(url)

    if not page_data:
        print(f"  无法抓取页面内容")
        return []

    if "markdown" not in page_data:
        print(f"  页面内容中没有markdown格式")
        return []

    content = page_data["markdown"]
    print(f"  页面内容长度: {len(content)} 字符")

    # 查找表格行
    lines = content.split('\n')
    table_rows = []

    # 查找表格开始标记
    in_table = False
    for line in lines:
        if line.strip().startswith('|') and not line.strip().startswith('| ---'):
            # 检查是否是数据行（不是表头）
            if re.match(r'\|\s*\d+\s*\|', line.strip()):
                table_rows.append(line.strip())

    print(f"  找到 {len(table_rows)} 行数据")

    # 解析表格行并提取帖子信息
    posts = []
    for row in table_rows:
        post_info = parse_table_row(row)
        if post_info:
            posts.append(post_info)

    print(f"  解析出 {len(posts)} 个帖子")

    # 根据需求筛选数据
    if data_type == "5_days":
        # 筛选5日内的数据
        recent_posts = []
        for post in posts:
            if is_time_within_5_days(post["time"]):
                recent_posts.append(post)

        print(f"  筛选出 {len(recent_posts)} 个5日内的帖子")
        return recent_posts
    elif data_type == "first_5":
        # 返回前5条数据
        result = posts[:5]
        print(f"  返回前5条数据")
        return result
    elif data_type == "first_10":
        # 返回前10条数据
        result = posts[:10]
        print(f"  返回前10条数据")
        return result

    # 默认返回前5条
    return posts[:5]

def main():
    """Main function"""
    print("Correct implementation for getting data from Guba pages")
    print("=" * 60)

    # URLs to test with specific requirements
    urls_to_test = [
        {
            "url": "https://guba.eastmoney.com/list,300339,1,f.html",
            "description": "Consultation section, 5 days data",
            "section_name": "咨询区",
            "data_type": "5_days"
        },
        {
            "url": "https://guba.eastmoney.com/list,300339,2,f.html",
            "description": "Research reports section, first 5 items",
            "section_name": "研报区",
            "data_type": "first_5"
        },
        {
            "url": "https://guba.eastmoney.com/list,300339,3,f.html",
            "description": "Announcements section, 5 days data",
            "section_name": "公告区",
            "data_type": "5_days"
        },
        {
            "url": "https://guba.eastmoney.com/list,300339,99.html",
            "description": "Hot posts section, 5 days data",
            "section_name": "热帖区",
            "data_type": "5_days"
        },
        {
            "url": "https://guba.eastmoney.com/list,300339.html",
            "description": "Main page, first 10 items",
            "section_name": "主页",
            "data_type": "first_10"
        }
    ]

    results = {}

    for i, test_item in enumerate(urls_to_test, 1):
        url = test_item["url"]
        description = test_item["description"]
        section_name = test_item["section_name"]
        data_type = test_item["data_type"]

        print(f"\n{i}. 测试URL: {url}")
        print(f"   描述: {description}")

        try:
            data = get_5_days_data_from_page(url, section_name, data_type)
            results[url] = {
                "status": "success",
                "data": data,
                "count": len(data)
            }
            print(f"   成功获取 {len(data)} 条数据")

            # 显示前几条数据作为示例
            for j, post in enumerate(data[:3], 1):
                print(f"     {j}. {post['title'][:50]}... ({post['time']})")

        except Exception as e:
            print(f"   错误: {e}")
            results[url] = {
                "status": "error",
                "error": str(e),
                "count": 0
            }

    # Summary
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

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

    print("\n" + "=" * 60)
    print("测试完成!")

if __name__ == "__main__":
    main()

