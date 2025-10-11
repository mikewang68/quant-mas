"""
详细调试公共函数中的解析逻辑
"""

import sys
import os
import requests
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.eastmoney_guba_scraper import EastMoneyGubaScraper


def debug_parse_function_detailed():
    """详细调试解析函数"""

    # FireCrawl配置
    api_url = "http://192.168.1.2:8080/v1"
    target_url = "https://guba.eastmoney.com/list,000985,1,f.html"

    print(f"详细调试解析函数 - 目标URL: {target_url}")

    # 构建请求
    payload = {
        "url": target_url,
        "formats": ["markdown"],
        "onlyMainContent": True
    }

    try:
        # 调用FireCrawl API
        response = requests.post(
            f"{api_url}/scrape",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            if data.get("success"):
                firecrawl_data = [data]

                print(f"FireCrawl数据获取成功")
                print(f"数据键: {list(firecrawl_data[0].keys())}")

                # 直接调用公共函数中的解析方法
                print(f"\n=== 调用公共函数解析方法 ===")
                posts = EastMoneyGubaScraper._parse_guba_markdown(firecrawl_data, 5)
                print(f"解析结果: {len(posts)} 条帖子")

                if not posts:
                    print("❌ 公共函数解析失败")

                    # 手动调试解析逻辑
                    print(f"\n=== 手动调试解析逻辑 ===")
                    markdown_content = firecrawl_data[0]["data"]["markdown"]
                    lines = markdown_content.split("\n")

                    print(f"总行数: {len(lines)}")

                    # 查找表格头
                    table_start = -1
                    for i, line in enumerate(lines):
                        clean_line = line.strip()
                        if "| 阅读  | 评论  | 标题  | 作者  | 最后更新 |" in clean_line:
                            table_start = i
                            print(f"✅ 找到表格头: 行 {i}, 内容: {clean_line[:100]}")
                            break

                    if table_start == -1:
                        print("❌ 没有找到表格头")
                        # 显示前50行
                        print(f"\n前50行内容:")
                        for i, line in enumerate(lines[:50]):
                            print(f"{i:3d}: {line}")

    except Exception as e:
        print(f"调试失败: {e}")
        import traceback
        traceback.print_exc()


def test_public_function_directly():
    """直接测试公共函数"""

    firecrawl_config = {
        "api_url": "http://192.168.1.2:8080/v1",
        "max_retries": 3,
        "timeout": 30,
        "retry_delay": 1
    }

    stock_code = "000985"
    data_type = "consultations"

    print(f"\n=== 直接测试公共函数 ===")
    print(f"股票: {stock_code}, 数据类型: {data_type}")

    try:
        result = EastMoneyGubaScraper.scrape_eastmoney_guba(
            stock_code, data_type, firecrawl_config, 5
        )
        print(f"公共函数结果: {len(result)} 条记录")

        if result:
            for i, item in enumerate(result, 1):
                print(f"{i}. 标题: {item['title']}")
        else:
            print("❌ 公共函数返回空结果")

    except Exception as e:
        print(f"公共函数测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_parse_function_detailed()
    test_public_function_directly()

