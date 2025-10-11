"""
详细调试表格数据行解析逻辑
"""

import sys
import os
import requests
import json
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def debug_table_row_parsing():
    """详细调试表格数据行解析"""

    # FireCrawl配置
    api_url = "http://192.168.1.2:8080/v1"
    target_url = "https://guba.eastmoney.com/list,000985,1,f.html"

    print(f"详细调试表格数据行解析 - 目标URL: {target_url}")

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
                markdown_content = data["data"]["markdown"]
                lines = markdown_content.split("\n")

                print(f"总行数: {len(lines)}")

                # 查找表格头
                table_start = -1
                for i, line in enumerate(lines):
                    clean_line = line.strip()
                    if "| 阅读  | 评论  | 标题  | 作者  | 最后更新 |" in clean_line:
                        table_start = i
                        print(f"✅ 找到表格头: 行 {i}")
                        print(f"表格头内容: {clean_line}")
                        break

                if table_start != -1:
                    print(f"\n=== 分析表格数据行 ===")

                    # 检查表格分隔符行
                    separator_line = lines[table_start + 1]
                    print(f"分隔符行 {table_start + 1}: {separator_line}")

                    # 分析表格数据行
                    for i in range(table_start + 2, min(table_start + 2 + 10, len(lines))):
                        line = lines[i]
                        clean_line = line.strip()

                        print(f"\n行 {i}:")
                        print(f"  原始内容: {line}")
                        print(f"  清理后: {clean_line}")

                        # 检查是否是表格行
                        is_table_row = clean_line.startswith("|") and clean_line.endswith("|")
                        print(f"  是否是表格行: {is_table_row}")

                        if is_table_row:
                            # 解析表格行
                            cells = [cell.strip() for cell in clean_line.split("|")[1:-1]]
                            print(f"  解析出的单元格: {cells}")
                            print(f"  单元格数量: {len(cells)}")

                            if len(cells) >= 5:
                                read_count = cells[0]
                                comment_count = cells[1]
                                title = cells[2]
                                author = cells[3]
                                last_update = cells[4]

                                print(f"  阅读: {read_count}")
                                print(f"  评论: {comment_count}")
                                print(f"  标题: {title}")
                                print(f"  作者: {author}")
                                print(f"  时间: {last_update}")

                                # 提取标题中的链接文本
                                title_match = re.search(r'\[(.*?)\]', title)
                                if title_match:
                                    title_text = title_match.group(1)
                                    print(f"  提取的标题: {title_text}")
                                else:
                                    title_text = title
                                    print(f"  无链接标题: {title_text}")
                            else:
                                print(f"  ❌ 单元格数量不足: {len(cells)} < 5")
                        else:
                            print(f"  ❌ 不是有效的表格行")

    except Exception as e:
        print(f"调试失败: {e}")
        import traceback
        traceback.print_exc()


def test_public_function_with_debug():
    """测试公共函数并添加调试信息"""

    # 临时修改公共函数以添加调试信息
    import utils.eastmoney_guba_scraper as scraper_module

    # 保存原始方法
    original_parse_method = scraper_module.EastMoneyGubaScraper._parse_guba_markdown

    def debug_parse_method(firecrawl_data, limit=5):
        print("=== 公共函数解析方法调试 ===")
        result = original_parse_method(firecrawl_data, limit)
        print(f"解析结果: {len(result)} 条记录")
        return result

    # 临时替换方法
    scraper_module.EastMoneyGubaScraper._parse_guba_markdown = debug_parse_method

    firecrawl_config = {
        "api_url": "http://192.168.1.2:8080/v1",
        "max_retries": 3,
        "timeout": 30,
        "retry_delay": 1
    }

    stock_code = "000985"
    data_type = "consultations"

    print(f"\n=== 测试公共函数（带调试） ===")
    print(f"股票: {stock_code}, 数据类型: {data_type}")

    try:
        result = scraper_module.EastMoneyGubaScraper.scrape_eastmoney_guba(
            stock_code, data_type, firecrawl_config, 5
        )
        print(f"最终结果: {len(result)} 条记录")

        # 恢复原始方法
        scraper_module.EastMoneyGubaScraper._parse_guba_markdown = original_parse_method

    except Exception as e:
        print(f"测试失败: {e}")
        # 确保恢复原始方法
        scraper_module.EastMoneyGubaScraper._parse_guba_markdown = original_parse_method
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_table_row_parsing()
    test_public_function_with_debug()

