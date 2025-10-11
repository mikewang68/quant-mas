"""
详细调试解析逻辑 - 为什么找不到表格
"""

import sys
import os
import requests
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def debug_parse_logic():
    """详细调试解析逻辑"""

    # FireCrawl配置
    api_url = "http://192.168.1.2:8080/v1"
    target_url = "https://guba.eastmoney.com/list,000985,1,f.html"

    print(f"调试解析逻辑 - 目标URL: {target_url}")

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
                markdown_content = data["data"].get("markdown", "")

                print(f"获取到markdown内容，长度: {len(markdown_content)} 字符")

                # 分析markdown内容结构
                lines = markdown_content.split("\n")

                print(f"\n=== markdown内容详细分析 ===")
                print(f"总行数: {len(lines)}")

                # 查找所有可能包含表格的行
                table_candidates = []
                for i, line in enumerate(lines):
                    if "|" in line:
                        table_candidates.append((i, line))

                print(f"找到 {len(table_candidates)} 行包含'|'的内容")

                # 显示前20行可能包含表格的内容
                print(f"\n=== 前20行包含'|'的内容 ===")
                for i, (line_num, line) in enumerate(table_candidates[:20]):
                    print(f"行 {line_num}: {line[:150]}...")

                # 查找特定的表格头
                print(f"\n=== 查找表格头 ===")
                table_headers = [
                    "| 阅读  | 评论  | 标题  | 作者  | 最后更新 |",
                    "| 阅读 | 评论 | 标题 | 作者 | 最后更新 |",
                    "| 阅读",
                    "| 评论",
                    "| 标题",
                    "| 作者",
                    "| 最后更新"
                ]

                found_headers = []
                for i, line in enumerate(lines):
                    for header in table_headers:
                        if header in line:
                            found_headers.append((i, header, line))

                print(f"找到 {len(found_headers)} 个可能的表格头")
                for line_num, header, line in found_headers:
                    print(f"行 {line_num}: 匹配 '{header}' -> {line[:100]}...")

                # 如果没有找到标准表格头，尝试查找其他表格模式
                if not found_headers:
                    print(f"\n=== 尝试查找其他表格模式 ===")
                    # 查找包含多个'|'的行
                    multi_pipe_lines = []
                    for i, line in enumerate(lines):
                        if line.count("|") >= 4:  # 至少4个|表示可能有表格
                            multi_pipe_lines.append((i, line))

                    print(f"找到 {len(multi_pipe_lines)} 行包含多个'|'的内容")
                    for i, (line_num, line) in enumerate(multi_pipe_lines[:10]):
                        print(f"行 {line_num}: {line[:150]}...")

                # 尝试解析表格
                print(f"\n=== 尝试解析表格 ===")
                posts = parse_markdown_table_debug(markdown_content)
                print(f"解析结果: {len(posts)} 条记录")

    except Exception as e:
        print(f"调试失败: {e}")
        import traceback
        traceback.print_exc()


def parse_markdown_table_debug(markdown_content: str, limit: int = 5) -> list:
    """调试版本的表格解析函数"""
    import re
    posts = []

    if not markdown_content:
        return posts

    lines = markdown_content.split("\n")

    print(f"解析函数开始，总行数: {len(lines)}")

    # 查找表格开始位置
    table_start = -1
    for i, line in enumerate(lines):
        if "| 阅读  | 评论  | 标题  | 作者  | 最后更新 |" in line:
            table_start = i
            print(f"✅ 找到标准表格头: 行 {i}")
            break

    if table_start == -1:
        print("❌ 没有找到标准表格头")
        # 尝试其他可能的表头格式
        for i, line in enumerate(lines):
            if "| 阅读" in line and "| 评论" in line and "| 标题" in line:
                table_start = i
                print(f"✅ 找到替代表格头: 行 {i}")
                break

    if table_start == -1:
        print("❌ 没有找到任何表格头")
        return posts

    print(f"表格开始位置: 行 {table_start}")

    # 解析表格数据
    for i in range(table_start + 2, min(table_start + 2 + limit * 2, len(lines))):
        if len(posts) >= limit:
            break
        line = lines[i].strip()

        if line.startswith("|") and line.endswith("|"):
            print(f"✅ 解析表格行 {i}: {line[:100]}...")

            # 解析表格行
            cells = [cell.strip() for cell in line.split("|")[1:-1]]
            print(f"解析出的单元格: {cells}")

            if len(cells) >= 5:
                read_count = cells[0]
                comment_count = cells[1]
                title = cells[2]
                author = cells[3]
                last_update = cells[4]

                # 提取标题中的链接文本
                title_match = re.search(r'\[(.*?)\]', title)
                if title_match:
                    title_text = title_match.group(1)
                else:
                    title_text = title

                posts.append({
                    "read_count": read_count,
                    "comment_count": comment_count,
                    "title": title_text,
                    "author": author,
                    "last_update": last_update,
                    "type": "table_post"
                })
                print(f"✅ 成功解析帖子: {title_text}")
            else:
                print(f"❌ 单元格数量不足: {len(cells)} < 5")
        else:
            print(f"❌ 行 {i} 不是有效的表格行: {line[:50]}...")

    return posts


if __name__ == "__main__":
    debug_parse_logic()

