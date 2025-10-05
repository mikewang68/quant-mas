"""
东方财富股吧数据爬取工具
提供统一的函数来爬取和解析东方财富股吧数据
"""

import requests
import json
import re
from typing import List, Dict, Any, Optional
import time
import logging

# 配置日志
logger = logging.getLogger(__name__)


class EastMoneyGubaScraper:
    """东方财富股吧数据爬取器"""

    @staticmethod
    def scrape_eastmoney_guba(
        stock_code: str,
        data_type: str,
        firecrawl_config: Dict[str, Any],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        爬取东方财富股吧数据

        Args:
            stock_code: 股票代码
            data_type: 数据类型，支持：'consultations', 'research_reports', 'announcements', 'hot_posts'
            firecrawl_config: FireCrawl配置
            limit: 提取的条数限制

        Returns:
            爬取到的数据列表
        """
        try:
            logger.info(f"开始爬取东方财富股吧数据: 股票代码={stock_code}, 数据类型={data_type}")

            # 构建URL
            url = EastMoneyGubaScraper._build_guba_url(stock_code, data_type)
            logger.info(f"构建的URL: {url}")

            # 调用FireCrawl API
            firecrawl_data = EastMoneyGubaScraper._call_firecrawl_api(url, firecrawl_config)

            if not firecrawl_data:
                logger.warning(f"FireCrawl API返回空数据: 股票代码={stock_code}, 数据类型={data_type}")
                return []

            # 解析markdown数据
            posts = EastMoneyGubaScraper._parse_guba_markdown(firecrawl_data, limit)
            logger.info(f"解析到 {len(posts)} 条原始数据")

            # 格式化输出
            formatted_posts = EastMoneyGubaScraper._format_posts(posts, data_type)
            logger.info(f"格式化后得到 {len(formatted_posts)} 条数据")

            # 输出结果到控制台
            logger.info(f"=== {data_type} 数据结果 ===")
            for i, post in enumerate(formatted_posts, 1):
                logger.info(f"{i}. {post.get('title', 'N/A')}")
            logger.info(f"=== {data_type} 数据结束 ===")

            return formatted_posts

        except Exception as e:
            logger.error(f"爬取东方财富股吧数据失败: {e}")
            return []

    @staticmethod
    def _build_guba_url(stock_code: str, data_type: str) -> str:
        """
        构建东方财富股吧URL

        Args:
            stock_code: 股票代码
            data_type: 数据类型

        Returns:
            完整的URL
        """
        base_url = "https://guba.eastmoney.com/list"

        url_mapping = {
            "consultations": f"{base_url},{stock_code},1,f.html",      # 近期咨询
            "research_reports": f"{base_url},{stock_code},2,f.html",   # 最新研报
            "announcements": f"{base_url},{stock_code},3,f.html",      # 最新公告
            "hot_posts": f"{base_url},{stock_code},99.html"            # 热门帖子
        }

        if data_type not in url_mapping:
            raise ValueError(f"不支持的数据类型: {data_type}")

        return url_mapping[data_type]

    @staticmethod
    def _call_firecrawl_api(url: str, firecrawl_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        调用FireCrawl API爬取数据

        Args:
            url: 要爬取的URL
            firecrawl_config: FireCrawl配置

        Returns:
            爬取到的数据列表
        """
        try:
            # 如果没有配置，直接返回空列表
            if not firecrawl_config:
                print("FireCrawl配置为空，无法调用API")
                return []

            api_url = firecrawl_config.get("api_url")
            if not api_url:
                print("FireCrawl配置中没有API URL")
                return []

            max_retries = firecrawl_config.get("max_retries", 3)
            timeout = firecrawl_config.get("timeout", 30)

            # 构建FireCrawl v1 API请求
            payload = {"url": url, "formats": ["markdown"], "onlyMainContent": True}

            # 重试机制
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        f"{api_url}/scrape", json=payload, timeout=timeout
                    )

                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success"):
                            # 直接返回FireCrawl数据
                            return [data]
                        else:
                            print(f"FireCrawl API返回失败: {data.get('error', 'Unknown error')}")
                            return []
                    else:
                        print(f"FireCrawl API调用失败 (状态码 {response.status_code}): {response.text}")

                except Exception as e:
                    print(f"FireCrawl API调用异常 (尝试 {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(firecrawl_config.get("retry_delay", 1))
                        continue

            return []

        except Exception as e:
            print(f"调用FireCrawl API失败: {e}")
            return []

    @staticmethod
    def _parse_guba_markdown(firecrawl_data: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
        """
        解析FireCrawl返回的markdown数据

        Args:
            firecrawl_data: FireCrawl返回的数据列表
            limit: 提取的条数限制

        Returns:
            解析后的帖子数据列表
        """
        try:
            posts = []

            if not firecrawl_data:
                return posts

            # 参考程序逻辑：从data['data']['markdown']获取内容
            markdown_content = ""
            for item in firecrawl_data:
                if "data" in item and isinstance(item["data"], dict) and "markdown" in item["data"]:
                    markdown_content = item["data"]["markdown"]
                    break

            if not markdown_content:
                return posts

            lines = markdown_content.split("\n")

            # 查找表格开始位置 - 参考程序逻辑
            table_start = -1
            for i, line in enumerate(lines):
                if "| 阅读  | 评论  | 标题  | 作者  | 最后更新 |" in line:
                    table_start = i
                    break

            if table_start == -1:
                # 尝试其他可能的表头格式
                for i, line in enumerate(lines):
                    if "| 阅读" in line and "| 评论" in line and "| 标题" in line:
                        table_start = i
                        break

            if table_start != -1:
                # 解析表格数据 - 参考程序逻辑
                for i in range(table_start + 2, min(table_start + 2 + limit * 2, len(lines))):
                    if len(posts) >= limit:
                        break
                    line = lines[i].strip()
                    if line.startswith("|") and line.endswith("|"):
                        # 解析表格行
                        cells = [cell.strip() for cell in line.split("|")[1:-1]]
                        if len(cells) >= 5:
                            read_count = cells[0]
                            comment_count = cells[1]
                            title = cells[2]
                            author = cells[3]
                            last_update = cells[4]

                            # 提取标题中的链接文本
                            import re
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

            # 按时间倒序排序，然后取前limit条
            # 首先按last_update字段进行排序（假设格式为"MM-DD HH:MM"）
            sorted_posts = sorted(posts, key=lambda x: EastMoneyGubaScraper._parse_time(x.get('last_update', '')), reverse=True)

            # 取前limit条
            return sorted_posts[:limit]

        except Exception as e:
            print(f"解析markdown数据失败: {e}")
            return []

    @staticmethod
    def _parse_time(time_str: str) -> str:
        """
        解析时间字符串，用于排序

        Args:
            time_str: 时间字符串，格式如 "09-30 04:47"

        Returns:
            解析后的时间字符串，用于排序
        """
        try:
            # 如果时间字符串为空，返回一个很旧的时间
            if not time_str or time_str == "N/A":
                return "0000-00-00 00:00"

            # 假设格式为 "MM-DD HH:MM"
            # 转换为 "2024-MM-DD HH:MM" 格式用于排序
            return f"2024-{time_str}"
        except Exception:
            return "0000-00-00 00:00"


    @staticmethod
    def _format_posts(posts: List[Dict[str, Any]], data_type: str) -> List[Dict[str, Any]]:
        """
        格式化帖子数据 - 简化为"时间：内容"格式

        Args:
            posts: 原始帖子数据
            data_type: 数据类型

        Returns:
            格式化后的帖子数据
        """
        formatted_posts = []

        for post in posts:
            # 直接使用"时间：内容"格式，不添加"标题:"前缀
            formatted_post = {
                "title": f"{post.get('last_update', '')}：{post.get('title', '')}",
                "publishedAt": post.get("last_update", ""),
                "author": post.get("author", ""),
                "read_count": post.get("read_count", ""),
                "comment_count": post.get("comment_count", ""),
            }

            # 根据数据类型添加特定字段
            if data_type == "consultations":
                formatted_post["content"] = ""
            elif data_type == "research_reports":
                formatted_post.update({
                    "institution": "",
                    "rating": "",
                    "target_price": "",
                })
            elif data_type == "announcements":
                formatted_post.update({
                    "content": "",
                    "type": "公告",
                })
            elif data_type == "hot_posts":
                formatted_post.update({
                    "content": "",
                    "like_count": "",
                })

            formatted_posts.append(formatted_post)

        return formatted_posts


# 便捷函数
def scrape_guba_data(
    stock_code: str,
    data_type: str,
    firecrawl_config: Dict[str, Any],
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    爬取东方财富股吧数据的便捷函数

    Args:
        stock_code: 股票代码
        data_type: 数据类型
        firecrawl_config: FireCrawl配置
        limit: 提取的条数限制

    Returns:
        爬取到的数据列表
    """
    return EastMoneyGubaScraper.scrape_eastmoney_guba(stock_code, data_type, firecrawl_config, limit)

def scrape_all_guba_data(
    stock_code: str,
    firecrawl_config: Dict[str, Any],
    limit_per_type: int = 5
) -> Dict[str, List[Dict[str, Any]]]:
    """
    爬取所有类型的东方财富股吧数据

    Args:
        stock_code: 股票代码
        firecrawl_config: FireCrawl配置
        limit_per_type: 每种类型的条数限制

    Returns:
        包含所有类型数据的字典
    """
    data_types = ["consultations", "research_reports", "announcements", "hot_posts"]

    all_data = {}

    for data_type in data_types:
        data = scrape_guba_data(stock_code, data_type, firecrawl_config, limit_per_type)
        all_data[data_type] = data

    return all_data

