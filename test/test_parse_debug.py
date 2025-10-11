"""
调试解析逻辑问题
"""

import sys
import os
import requests
import json
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_parse_markdown():
    """测试markdown解析逻辑"""

    # FireCrawl配置
    api_url = "http://192.168.1.2:8080/v1"
    target_url = "https://guba.eastmoney.com/list,300339,1,f.html"

    print(f"测试解析逻辑 - 目标URL: {target_url}")

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

                print(f"\n=== markdown内容分析 ===")
                print(f"总行数: {len(lines)}")

                # 查找表格相关的内容
                table_lines = []
                for i, line in enumerate(lines):
                    if "|" in line and ("阅读" in line or "评论" in line or "标题" in line):
                        table_lines.append((i, line))

                print(f"找到 {len(table_lines)} 行可能包含表格的内容")

                # 显示表格相关的内容
                for line_num, line in table_lines:
                    print(f"行 {line_num}: {line[:100]}...")

                # 尝试解析表格
                posts = parse_markdown_table(markdown_content)
                print(f"\n解析结果: {len(posts)} 条记录")

                if posts:
                    for i, post in enumerate(posts, 1):
                        print(f"{i}. 标题: {post['title']}")
                        print(f"   时间: {post['last_update']}")
                        print(f"   作者: {post['author']}")
                        print(f"   阅读: {post['read_count']}, 评论: {post['comment_count']}")
                else:
                    print("❌ 没有解析到任何帖子数据")

                    # 输出更多调试信息
                    print("\n=== 详细调试信息 ===")
                    for i, line in enumerate(lines):
                        if i < 50:  # 只显示前50行
                            print(f"{i:3d}: {line}")

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


def parse_markdown_table(markdown_content: str, limit: int = 5) -> list:
    """解析markdown表格数据"""
    posts = []

    if not markdown_content:
        return posts

    lines = markdown_content.split("\n")

    # 查找表格开始位置
    table_start = -1
    for i, line in enumerate(lines):
        if "| 阅读  | 评论  | 标题  | 作者  | 最后更新 |" in line:
            table_start = i
            print(f"找到标准表格头: 行 {i}")
            break

    if table_start == -1:
        # 尝试其他可能的表头格式
        for i, line in enumerate(lines):
            if "| 阅读" in line and "| 评论" in line and "| 标题" in line:
                table_start = i
                print(f"找到替代表格头: 行 {i}")
                break

    if table_start != -1:
        print(f"表格开始位置: 行 {table_start}")

        # 解析表格数据
        for i in range(table_start + 2, min(table_start + 2 + limit * 2, len(lines))):
            if len(posts) >= limit:
                break
            line = lines[i].strip()
            if line.startswith("|") and line.endswith("|"):
                print(f"解析表格行 {i}: {line}")

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
        print("❌ 没有找到表格头")

    return posts


if __name__ == "__main__":
    test_parse_markdown()

