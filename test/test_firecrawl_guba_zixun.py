#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用FireCrawl爬取东方财富股吧资讯数据测试脚本
"""

import os
import sys
import json
from typing import Dict, Any, List
import requests

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.firecrawl_client import FirecrawlClient


def test_firecrawl_guba_scraping():
    """测试使用FireCrawl爬取东方财富股吧资讯数据"""

    # FireCrawl配置
    firecrawl_url = "http://192.168.1.2:8080"
    target_url = "https://guba.eastmoney.com/list,300339,1,f.html"

    print(f"初始化FireCrawl客户端: {firecrawl_url}")
    client = FirecrawlClient(base_url=firecrawl_url)

    # 检查FireCrawl服务是否可用
    if not client.is_available():
        print("❌ FireCrawl服务不可用")
        return

    print("✅ FireCrawl服务可用")
    print(f"目标URL: {target_url}")

    # 爬取页面数据
    try:
        print("开始爬取页面数据...")
        result = client.scrape_url(
            url=target_url,
            formats=["markdown"]
        )

        if result:
            print("✅ 页面爬取成功")
            print(f"返回数据结构: {list(result.keys())}")

            # 保存原始结果
            with open('firecrawl_guba_raw_result.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print("已保存原始结果到 firecrawl_guba_raw_result.json")

            # 提取markdown内容
            if 'markdown' in result:
                markdown_content = result['markdown']
                with open('firecrawl_guba_content.md', 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                print("已保存Markdown内容到 firecrawl_guba_content.md")

                # 简单解析前5条数据
                print("\n=== 解析前5条数据 ===")
                lines = markdown_content.split('\n')
                data_lines = [line for line in lines if line.strip() and not line.startswith('#')]

                item_count = 0
                for line in data_lines:
                    if line.strip() and item_count < 5:
                        print(f"{item_count + 1}. {line.strip()}")
                        item_count += 1
            else:
                print("⚠️  返回结果中没有markdown内容")
                print(f"可用的键: {list(result.keys())}")
                if 'content' in result:
                    print(f"Content预览: {result['content'][:200]}...")
        else:
            print("❌ 页面爬取失败，返回结果为空")

    except Exception as e:
        print(f"❌ 爬取过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_firecrawl_guba_scraping()

