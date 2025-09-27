import requests
import os
from datetime import datetime, timedelta

from config import FIRECRAWL_API_KEY, FIRECRAWL_API_URL

# from config import FIRECRAWL_API_KEY, FIRECRAWL_API_URL
FIRECRAWL_API_KEY = "fc-6501e89ba7e64593aeb9bc1d954a2fcc"
# FIRECRAWL_API_URL = "https://api.firecrawl.dev"
FIRECRAWL_API_URL = "http://192.168.1.2:8080/v1"


def test_firecrawl_connection():
    """测试Firecrawl连接"""
    print("测试Firecrawl连接...")
    print(f"API URL: {FIRECRAWL_API_URL}")

    # 测试健康检查端点
    try:
        response = requests.get(f"{FIRECRAWL_API_URL}/health/liveness")
        print(f"健康检查响应状态: {response.status_code}")
        if response.status_code == 200:
            print("Firecrawl服务正常运行")
            print(f"响应内容: {response.json()}")
        else:
            print(f"健康检查失败: {response.text}")
    except Exception as e:
        print(f"健康检查异常: {e}")


def test_firecrawl_crawl():
    """测试Firecrawl爬取功能"""
    print("\n测试Firecrawl爬取功能...")

    # 测试爬取东方财富网的一个简单页面
    url = "https://www.eastmoney.com/"

    try:
        headers = {
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json",
        }

        data = {"url": url}

        response = requests.post(
            f"{FIRECRAWL_API_URL}/crawl", headers=headers, json=data
        )

        print(f"爬取请求状态: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("爬取请求成功")
            print(f"响应内容: {result}")
        else:
            print(f"爬取请求失败: {response.text}")
    except Exception as e:
        print(f"爬取请求异常: {e}")


def crawl_guba_5days_data():
    """爬取东方财富股吧指定页面5日内的数据"""
    print("\n爬取东方财富股吧指定页面5日内的数据...")

    # 目标URL
    url = "https://guba.eastmoney.com/list,300339,1,f.html"

    # 计算5天前的日期
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5)

    # 格式化日期为YYYY-MM-DD
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    print(f"爬取URL: {url}")
    print(f"日期范围: {start_date_str} 到 {end_date_str}")

    try:
        headers = {
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json",
        }

        # 使用Firecrawl v2 API进行爬取
        # 使用v2 API支持的参数
        data = {
            "url": url,
            "limit": 20,  # 限制爬取的页面数量到20个
        }

        response = requests.post(
            f"{FIRECRAWL_API_URL}/crawl", headers=headers, json=data
        )

        print(f"爬取请求状态: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("爬取请求成功")
            print(f"初始响应: {result}")

            # 检查是否有job ID
            if "id" in result:
                job_id = result["id"]
                print(f"任务ID: {job_id}")

                # 轮询检查任务状态
                max_attempts = 30  # 最多尝试30次
                attempt = 0

                while attempt < max_attempts:
                    attempt += 1
                    print(f"检查任务状态 (尝试 {attempt}/{max_attempts})...")

                    # 构造状态检查URL
                    status_url = f"{FIRECRAWL_API_URL}/v2/crawl/{job_id}"
                    status_response = requests.get(status_url, headers=headers)

                    if status_response.status_code == 200:
                        status_result = status_response.json()
                        print(f"状态响应: {status_result}")

                        # 检查任务是否完成
                        if "status" in status_result:
                            status = status_result["status"]
                            print(f"任务状态: {status}")

                            if status == "completed":
                                # 任务完成，获取数据
                                if "data" in status_result:
                                    crawled_data = status_result["data"]
                                    print(f"\n爬取到的数据 (共{len(crawled_data)}条):")

                                    # 解析并显示具体信息
                                    for i, item in enumerate(crawled_data, 1):
                                        # 添加类型检查
                                        if not isinstance(item, dict):
                                            print(
                                                f"{i}. 数据格式不正确: {type(item)} - {item}"
                                            )
                                            continue

                                        # 提取基本信息
                                        page_url = item.get("url", "N/A")

                                        # 从metadata中提取信息
                                        metadata = (
                                            item.get("metadata", {})
                                            if isinstance(item.get("metadata"), dict)
                                            else {}
                                        )
                                        title = metadata.get("title", "N/A")
                                        author = metadata.get("author", "N/A")
                                        published_at = metadata.get(
                                            "publishedAt", "N/A"
                                        )

                                        # 从HTML内容中提取信息
                                        html_content = (
                                            item.get("html", "")
                                            if isinstance(item.get("html"), str)
                                            else ""
                                        )

                                        # 尝试从HTML内容中提取阅读数和评论数
                                        import re

                                        # 查找阅读和评论数的模式（更灵活的匹配）
                                        read_count = "N/A"
                                        comment_count = "N/A"

                                        # 尝试多种模式匹配阅读数
                                        read_patterns = [
                                            r"阅读[:\s]*([0-9,]+)",
                                            r"阅读量[:\s]*([0-9,]+)",
                                            r"浏览[:\s]*([0-9,]+)",
                                            r"(\d+[,\d]*)\s*次阅读",
                                        ]

                                        for pattern in read_patterns:
                                            read_match = re.search(
                                                pattern, html_content
                                            )
                                            if read_match:
                                                read_count = read_match.group(
                                                    1
                                                ).replace(",", "")
                                                break

                                        # 尝试多种模式匹配评论数
                                        comment_patterns = [
                                            r"评论[:\s]*([0-9,]+)",
                                            r"(\d+[,\d]*)\s*条评论",
                                            r"评论\s*\((\d+[,\d]*)\)",
                                        ]

                                        for pattern in comment_patterns:
                                            comment_match = re.search(
                                                pattern, html_content
                                            )
                                            if comment_match:
                                                comment_count = comment_match.group(
                                                    1
                                                ).replace(",", "")
                                                break

                                        print(f"{i}. 标题: {title}")
                                        print(f"   作者: {author}")
                                        print(f"   发帖时间: {published_at}")
                                        print(f"   阅读: {read_count}")
                                        print(f"   评论: {comment_count}")
                                        print(f"   链接: {page_url}")
                                        print("-" * 50)
                                    return crawled_data
                                else:
                                    print("任务完成但没有数据返回")
                                    print(
                                        f"完成响应结构: {status_result.keys() if isinstance(status_result, dict) else 'Not a dict'}"
                                    )
                                    return status_result
                            elif status == "failed":
                                print("爬取任务失败")
                                if "error" in status_result:
                                    print(f"错误信息: {status_result['error']}")
                                return None
                            else:
                                # 任务仍在进行中，等待一段时间后重试
                                import time

                                time.sleep(5)  # 等待5秒后重试
                        else:
                            print("状态响应中没有status字段")
                            print(
                                f"响应结构: {status_result.keys() if isinstance(status_result, dict) else 'Not a dict'}"
                            )
                            break
                    else:
                        print(
                            f"状态检查失败: {status_response.status_code} - {status_response.text}"
                        )
                        break
                else:
                    print("超过最大尝试次数，任务可能仍在进行中")
                    return None
            else:
                print("响应中没有任务ID")
                return result

            # 检查是否有job ID
            if "id" in result:
                job_id = result["id"]
                print(f"任务ID: {job_id}")

                # 轮询检查任务状态
                max_attempts = 30  # 最多尝试30次
                attempt = 0

                while attempt < max_attempts:
                    attempt += 1
                    print(f"检查任务状态 (尝试 {attempt}/{max_attempts})...")

                    # 构造状态检查URL
                    status_url = f"{FIRECRAWL_API_URL}/v2/crawl/{job_id}"
                    status_response = requests.get(status_url, headers=headers)

                    if status_response.status_code == 200:
                        status_result = status_response.json()
                        print(f"状态响应: {status_result}")

                        # 检查任务是否完成
                        if "status" in status_result:
                            status = status_result["status"]
                            print(f"任务状态: {status}")

                            if status == "completed":
                                # 任务完成，获取数据
                                if "data" in status_result:
                                    crawled_data = status_result["data"]
                                    print(f"\n爬取到的数据 (共{len(crawled_data)}条):")

                                    for i, item in enumerate(crawled_data, 1):
                                        # 添加类型检查
                                        if not isinstance(item, dict):
                                            print(
                                                f"{i}. 数据格式不正确: {type(item)} - {item}"
                                            )
                                            continue

                                        title = (
                                            item.get("metadata", {}).get("title", "N/A")
                                            if isinstance(item.get("metadata"), dict)
                                            else "N/A"
                                        )
                                        page_url = item.get("url", "N/A")
                                        markdown_content = (
                                            item.get("markdown", "")
                                            if isinstance(item.get("markdown"), str)
                                            else ""
                                        )
                                        content_length = len(markdown_content)

                                        print(f"{i}. 标题: {title}")
                                        print(f"   链接: {page_url}")
                                        print(f"   内容长度: {content_length} 字符")
                                        print("-" * 50)
                                    return crawled_data
                                else:
                                    print("任务完成但没有数据返回")
                                    print(
                                        f"完成响应结构: {status_result.keys() if isinstance(status_result, dict) else 'Not a dict'}"
                                    )
                                    return status_result
                            elif status == "failed":
                                print("爬取任务失败")
                                if "error" in status_result:
                                    print(f"错误信息: {status_result['error']}")
                                return None
                            else:
                                # 任务仍在进行中，等待一段时间后重试
                                import time

                                time.sleep(5)  # 等待5秒后重试
                        else:
                            print("状态响应中没有status字段")
                            print(
                                f"响应结构: {status_result.keys() if isinstance(status_result, dict) else 'Not a dict'}"
                            )
                            break
                    else:
                        print(
                            f"状态检查失败: {status_response.status_code} - {status_response.text}"
                        )
                        break
                else:
                    print("超过最大尝试次数，任务可能仍在进行中")
                    return None
            else:
                print("响应中没有任务ID")
                return result
        else:
            print(f"爬取请求失败: {response.text}")
            return None
    except Exception as e:
        print(f"爬取请求异常: {e}")
        import traceback

        traceback.print_exc()
        return None


def crawl_guba_targeted_5days():
    """针对指定链接爬取5日内的股吧数据"""
    print("\n针对指定链接爬取5日内的股吧数据...")

    # 目标URL
    url = "https://guba.eastmoney.com/list,300339,2,f.html"

    print(f"爬取目标URL: {url}")

    try:
        headers = {
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json",
        }

        # 使用Firecrawl v2 API进行爬取
        # 使用v2 API支持的参数
        data = {
            "url": url,
            "limit": 20,  # 爬取20个页面
        }

        response = requests.post(
            f"{FIRECRAWL_API_URL}/crawl", headers=headers, json=data
        )

        print(f"爬取请求状态: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("爬取请求成功")

            # 处理爬取结果
            if "data" in result:
                crawled_data = result["data"]
                print(f"\n爬取到的数据 (共{len(crawled_data)}条):")

                # 由于crawl功能是爬取页面链接，我们无法直接通过API过滤5天内的数据
                # 需要通过后续处理来筛选5天内的数据
                for i, item in enumerate(crawled_data, 1):
                    title = item.get("metadata", {}).get("title", "N/A")
                    page_url = item.get("url", "N/A")
                    content_length = len(item.get("markdown", ""))

                    print(f"{i}. 标题: {title}")
                    print(f"   链接: {page_url}")
                    print(f"   内容长度: {content_length} 字符")
                    print("-" * 50)

                # 返回所有爬取到的数据
                return crawled_data
            return result
        else:
            print(f"爬取请求失败: {response.text}")
            return None
    except Exception as e:
        print(f"爬取请求异常: {e}")
        import traceback

        traceback.print_exc()
        return None


def crawl_guba_5days_filtered():
    """针对指定链接爬取并筛选5日内的股吧数据"""
    print("\n针对指定链接爬取并筛选5日内的股吧数据...")

    # 目标URL
    url = "https://guba.eastmoney.com/list,300339,2,f.html"

    # 计算5天前的日期
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5)

    print(f"爬取目标URL: {url}")
    print(
        f"筛选日期范围: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}"
    )

    try:
        headers = {
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json",
        }

        # 使用Firecrawl v2 API进行爬取
        data = {
            "url": url,
            "limit": 25,  # 爬取25个页面以获取更多数据
        }

        response = requests.post(
            f"{FIRECRAWL_API_URL}/crawl", headers=headers, json=data
        )

        print(f"爬取请求状态: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("爬取请求成功")

            # 处理爬取结果
            if "data" in result:
                crawled_data = result["data"]
                print(f"\n原始爬取数据 (共{len(crawled_data)}条):")

                # 筛选5天内的数据
                filtered_data = []
                for item in crawled_data:
                    # 尝试从metadata中获取发布日期
                    publish_date_str = item.get("metadata", {}).get("publishedAt")
                    if publish_date_str:
                        try:
                            # 解析发布日期
                            publish_date = datetime.fromisoformat(
                                publish_date_str.replace("Z", "+00:00")
                            )
                            # 检查是否在5天范围内
                            if publish_date >= start_date:
                                filtered_data.append(item)
                        except Exception as e:
                            # 如果日期解析失败，保留数据但标记日期未知
                            filtered_data.append(item)
                    else:
                        # 如果没有发布日期，保留数据但标记日期未知
                        filtered_data.append(item)

                print(f"\n筛选后的5日内数据 (共{len(filtered_data)}条):")
                for i, item in enumerate(filtered_data, 1):
                    title = item.get("metadata", {}).get("title", "N/A")
                    page_url = item.get("url", "N/A")
                    content_length = len(item.get("markdown", ""))
                    publish_date_str = item.get("metadata", {}).get(
                        "publishedAt", "未知"
                    )

                    print(f"{i}. 标题: {title}")
                    print(f"   链接: {page_url}")
                    print(f"   发布日期: {publish_date_str}")
                    print(f"   内容长度: {content_length} 字符")
                    print("-" * 50)

                # 返回筛选后的数据
                return filtered_data
            return result
        else:
            print(f"爬取请求失败: {response.text}")
            return None
    except Exception as e:
        print(f"爬取请求异常: {e}")
        import traceback

        traceback.print_exc()
        return None


def test_firecrawl_scrape():
    """测试Firecrawl scrape功能"""
    print("\n测试Firecrawl scrape功能...")

    # 测试爬取东方财富网的一个简单页面
    url = "https://www.eastmoney.com/"

    try:
        headers = {
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json",
        }

        data = {"url": url, "formats": ["markdown"]}

        response = requests.post(
            f"{FIRECRAWL_API_URL}/scrape", headers=headers, json=data
        )

        print(f"Scrape请求状态: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Scrape请求成功")
            print(f"响应内容: {result}")
        else:
            print(f"Scrape请求失败: {response.text}")
    except Exception as e:
        print(f"Scrape请求异常: {e}")


def test_firecrawl_search_guba():
    """测试Firecrawl搜索东方财富股吧5天内数据，返回所有结果"""
    print("\n测试Firecrawl搜索东方财富股吧5天内数据，返回所有结果...")

    # 目标URL关键词 - 搜索东方财富股吧中的具体帖子
    keyword = "site:guba.eastmoney.com 300339"

    # 计算5天前的日期
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5)

    # 格式化日期为YYYY-MM-DD
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    print(f"搜索关键词: {keyword}")
    print(f"日期范围: {start_date_str} 到 {end_date_str}")

    try:
        headers = {
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json",
        }

        # 首先尝试使用site:语法搜索东方财富股吧
        print("\n1. 尝试使用site:语法搜索东方财富股吧...")
        data_site = {
            "query": keyword,
        }

        response_site = requests.post(
            f"{FIRECRAWL_API_URL}/search", headers=headers, json=data_site
        )

        print(f"site:语法搜索请求状态: {response_site.status_code}")
        if response_site.status_code == 200:
            result_site = response_site.json()
            print("site:语法搜索请求成功")
            print(f"site:语法搜索响应内容: {result_site}")

            # 检查返回的数据结构
            if not isinstance(result_site, dict):
                print("返回结果格式不正确")
                print(f"结果类型: {type(result_site)}")
                print(f"结果内容: {result_site}")
                return None

            # 检查是否有data字段
            if "data" not in result_site:
                print("返回结果中没有data字段")
                print(f"完整响应: {result_site}")
                return None

            data_content = result_site["data"]
            print(f"data字段类型: {type(data_content)}")

            # 处理不同的数据结构
            data_list = []
            if isinstance(data_content, list):
                data_list = data_content
            elif isinstance(data_content, dict):
                # 如果data是字典，检查是否有web键或其他包含实际数据的字段
                if "web" in data_content and isinstance(data_content["web"], list):
                    data_list = data_content["web"]
                elif "results" in data_content and isinstance(
                    data_content["results"], list
                ):
                    data_list = data_content["results"]
                else:
                    # 尝试将字典转换为列表
                    data_list = [data_content]
            else:
                # 其他情况，尝试包装成列表
                data_list = [data_content]

            print(f"处理后的数据列表长度: {len(data_list)}")

            # 如果site:搜索没有结果，尝试直接搜索URL
            if len(data_list) == 0:
                print("\n2. site:搜索没有结果，尝试直接搜索URL...")
                url = "https://guba.eastmoney.com/list,300339.html"
                data_url = {
                    "query": url,
                }

                response_url = requests.post(
                    f"{FIRECRAWL_API_URL}/v2/search", headers=headers, json=data_url
                )

                print(f"URL搜索请求状态: {response_url.status_code}")
                if response_url.status_code == 200:
                    result_url = response_url.json()
                    print("URL搜索请求成功")

                    # 检查返回的数据结构
                    if "data" in result_url:
                        data_content_url = result_url["data"]

                        # 处理不同的数据结构
                        if isinstance(data_content_url, list):
                            data_list = data_content_url
                        elif isinstance(data_content_url, dict):
                            if "web" in data_content_url and isinstance(
                                data_content_url["web"], list
                            ):
                                data_list = data_content_url["web"]
                            else:
                                data_list = [data_content_url]
                        else:
                            data_list = [data_content_url]

                        print(f"URL搜索处理后的数据列表长度: {len(data_list)}")

            # 获取前5条数据（或所有数据，如果少于5条）
            top_5_results = data_list[:5] if len(data_list) >= 5 else data_list
            print(f"\n找到{len(top_5_results)}条数据:")

            if len(top_5_results) == 0:
                print("没有找到相关数据")
            else:
                for i, item in enumerate(top_5_results, 1):
                    # 确保item是字典类型
                    if not isinstance(item, dict):
                        print(f"{i}. 数据格式不正确: {item} (类型: {type(item)})")
                        continue

                    # 安全地提取字段
                    title = item.get("title", "N/A")
                    url = item.get("url", "N/A")
                    description = item.get("description", "N/A")

                    print(f"{i}. 标题: {title}")
                    print(f"   链接: {url}")
                    # 确保description是字符串类型再进行切片
                    if isinstance(description, str):
                        print(f"   描述: {description[:100]}...")
                    else:
                        print(f"   描述: {description}")
                    print("-" * 50)

            # 返回结果（如果有数据则返回前5条，否则返回空列表）
            return top_5_results if top_5_results else []
        else:
            print(f"搜索请求失败: {response_site.text}")
            return None
    except Exception as e:
        print(f"搜索请求异常: {e}")
        import traceback

        traceback.print_exc()  # 打印详细的错误堆栈
        return None


def process_search_results(results):
    """处理搜索结果并提取有用信息"""
    print(f"\n处理 {len(results)} 条搜索结果:")

    processed_results = []

    for i, item in enumerate(results, 1):
        # 类型检查，确保item是字典
        if not isinstance(item, dict):
            print(f"{i}. 数据格式不正确: {item} (类型: {type(item)})")
            continue

        # 提取字段信息
        title = item.get("title", "N/A")
        url = item.get("url", "N/A")
        description = (
            item.get("description", "N/A")
            if isinstance(item.get("description"), str)
            else "N/A"
        )

        # 尝试从描述或其他字段中提取阅读数和评论数
        import re

        # 尝试从描述中提取阅读和评论数
        read_count = "N/A"
        comment_count = "N/A"
        author = "N/A"
        publish_time = "N/A"

        # 查找阅读数
        if isinstance(description, str):
            read_match = re.search(r"阅读[:\s]*(\d+)", description)
            if read_match:
                read_count = read_match.group(1)

        # 查找评论数
        if isinstance(description, str):
            comment_match = re.search(r"评论[:\s]*(\d+)", description)
            if comment_match:
                comment_count = comment_match.group(1)

        # 如果描述中没有找到，尝试其他方式
        if read_count == "N/A" and "metadata" in item:
            metadata = item["metadata"]
            if isinstance(metadata, dict) and "keywords" in metadata:
                keywords = metadata["keywords"]
                if isinstance(keywords, str):
                    read_match = re.search(r"阅读[:\s]*(\d+)", keywords)
                    if read_match:
                        read_count = read_match.group(1)

        print(f"{i}. 标题: {title}")
        print(f"   作者: {author}")
        print(f"   发帖时间: {publish_time}")
        print(f"   阅读: {read_count}")
        print(f"   评论: {comment_count}")
        print(f"   链接: {url}")
        print("-" * 50)

        # 保存处理后的结果
        processed_results.append(
            {
                "title": title,
                "url": url,
                "description": description,
                "author": author,
                "publish_time": publish_time,
                "read_count": read_count,
                "comment_count": comment_count,
                "raw_data": item,
            }
        )

    return processed_results


def scrape_guba_posts():
    """抓取东方财富股吧页面并提取具体帖子信息"""
    print("\n抓取东方财富股吧页面并提取具体帖子信息...")

    try:
        headers = {
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json",
        }

        # 直接抓取股吧首页
        url = "https://guba.eastmoney.com/list,300339,1,f.html"
        data = {"url": url}

        response = requests.post(
            f"{FIRECRAWL_API_URL}/scrape", headers=headers, json=data
        )

        print(f"抓取请求状态: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("抓取请求成功")
            # print(f"响应内容: {result}")

            # 处理抓取结果
            if "data" in result:
                data_content = result["data"]

                # 提取帖子信息
                posts = []

                # 检查数据结构
                if isinstance(data_content, list):
                    page_data = data_content[0] if data_content else {}
                elif isinstance(data_content, dict):
                    page_data = data_content
                else:
                    page_data = {}

                # 从markdown或html中提取帖子信息
                content = ""
                if "markdown" in page_data:
                    content = page_data["markdown"]
                elif "html" in page_data:
                    content = page_data["html"]

                if content:
                    # 打印部分内容以便调试
                    print(f"内容长度: {len(content)} 字符")
                    # print(f"内容前500字符: {content[:500]}...")

                    # 使用正则表达式提取帖子信息
                    import re

                    # 查找帖子链接和标题的模式
                    # 匹配类似 [标题](链接) 的格式（markdown）
                    # 更宽松的匹配模式，但要确保URL是干净的
                    markdown_pattern = r'\[([^\]]+)\]\(([^)"\s]+news[^)"\s]*)'
                    markdown_matches = re.findall(markdown_pattern, content)

                    # 另一种markdown模式
                    markdown_pattern2 = r'\[([^\]]+)\]\((/news[^)"\s]*)'
                    markdown_matches2 = re.findall(markdown_pattern2, content)

                    # 匹配HTML链接模式
                    html_pattern = r'<a[^>]*href="([^"]*news[^"]*)"[^>]*>([^<]+)</a>'
                    html_matches = re.findall(html_pattern, content)

                    # 另一种HTML模式
                    html_pattern2 = r'<a[^>]*href="(/news[^"]*)"[^>]*>([^<]+)</a>'
                    html_matches2 = re.findall(html_pattern2, content)

                    print(f"从markdown找到 {len(markdown_matches)} 个链接")
                    print(f"从markdown2找到 {len(markdown_matches2)} 个链接")
                    print(f"从HTML找到 {len(html_matches)} 个链接")
                    print(f"从HTML2找到 {len(html_matches2)} 个链接")

                    # 处理markdown匹配结果
                    for match in markdown_matches[:10]:  # 取前10个
                        title, url = match
                        # 确保URL是完整的并清理URL
                        clean_url = url.split('"')[
                            0
                        ].strip()  # 移除可能的引号和额外文本
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
                                "type": "markdown_link",
                            }
                        )

                    # 处理markdown2匹配结果
                    for match in markdown_matches2[:10]:  # 取前10个
                        title, url = match
                        # 确保URL是完整的
                        full_url = "https://guba.eastmoney.com" + url

                        posts.append(
                            {
                                "title": title.strip(),
                                "url": full_url,
                                "type": "markdown_link2",
                            }
                        )

                    # 处理HTML匹配结果
                    for match in html_matches[:10]:  # 取前10个
                        url, title = match
                        # 确保URL是完整的并清理URL
                        clean_url = url.split('"')[
                            0
                        ].strip()  # 移除可能的引号和额外文本
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
                                "type": "html_link",
                            }
                        )

                    # 处理HTML2匹配结果
                    for match in html_matches2[:10]:  # 取前10个
                        url, title = match
                        # 确保URL是完整的
                        full_url = "https://guba.eastmoney.com" + url

                        posts.append(
                            {
                                "title": title.strip(),
                                "url": full_url,
                                "type": "html_link2",
                            }
                        )

                    # 去重
                    unique_posts = []
                    seen_urls = set()
                    for post in posts:
                        if post["url"] not in seen_urls:
                            unique_posts.append(post)
                            seen_urls.add(post["url"])

                    posts = unique_posts[:10]  # 最多保留10个

                    print(f"\n提取到 {len(posts)} 个帖子:")
                    for i, post in enumerate(posts, 1):
                        print(f"{i}. 标题: {post['title']}")
                        print(f"   链接: {post['url']}")
                        print(f"   类型: {post['type']}")
                        print("-" * 50)

                    # 如果找到了帖子链接，尝试抓取前几个帖子的详细内容
                    if posts:
                        print(f"\n尝试抓取前3个帖子的详细内容...")
                        detailed_posts = []
                        for i, post in enumerate(posts[:5]):  # 只抓取前3个
                            print(f"\n抓取第 {i + 1} 个帖子: {post['title']}")
                            # 清理URL，确保它是有效的
                            clean_url = post["url"].split('"')[0].strip()
                            post_data = {"url": clean_url}

                            post_response = requests.post(
                                f"{FIRECRAWL_API_URL}/scrape",
                                headers=headers,
                                json=post_data,
                            )

                            if post_response.status_code == 200:
                                post_result = post_response.json()
                                if "data" in post_result:
                                    post_content = post_result["data"]
                                    # 检查帖子是否在5天内
                                    if is_post_within_5_days(post_content):
                                        detailed_posts.append(
                                            {
                                                "title": post["title"],
                                                "url": clean_url,
                                                "content": post_content,
                                            }
                                        )
                                        print(f"  成功抓取帖子内容(5天内)")
                                    else:
                                        print(f"  帖子不在5天内，跳过")
                                else:
                                    print(f"  抓取帖子内容失败: 没有data字段")
                            else:
                                print(f"  抓取帖子失败: {post_response.status_code}")

                        # 保存抓取到的数据到文件
                        save_scraped_data(detailed_posts)
                        return detailed_posts

                    return posts
                else:
                    print("未能从页面内容中提取到帖子信息")
                    return []
            else:
                print("抓取响应中没有data字段")
                return []
        else:
            print(f"抓取请求失败: {response.text}")
            return []
    except Exception as e:
        print(f"抓取请求异常: {e}")
        import traceback

        traceback.print_exc()
        return []


def is_post_within_5_days(post_content):
    """检查帖子是否在5天内发布"""
    try:
        import re
        from datetime import datetime, timedelta

        # 从markdown内容中提取日期
        markdown_content = ""
        if isinstance(post_content, dict) and "markdown" in post_content:
            markdown_content = post_content["markdown"]
        elif isinstance(post_content, str):
            markdown_content = post_content

        if not markdown_content:
            return False

        # 查找日期模式 (例如: 2025-09-05 10:17:51)
        date_pattern = r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}"
        date_matches = re.findall(date_pattern, markdown_content)

        if not date_matches:
            return False

        # 获取最新的日期（通常是发帖日期）
        post_date_str = date_matches[0]
        post_date = datetime.strptime(post_date_str, "%Y-%m-%d %H:%M:%S")

        # 计算5天前的日期
        five_days_ago = datetime.now() - timedelta(days=5)

        # 检查帖子日期是否在5天内
        return post_date >= five_days_ago
    except Exception as e:
        print(f"检查帖子日期时出错: {e}")
        return True  # 出错时默认保留帖子


def save_scraped_data(posts):
    """保存抓取到的数据到文件"""
    import json
    from datetime import datetime

    # 创建数据目录
    import os

    if not os.path.exists("scraped_data"):
        os.makedirs("scraped_data")

    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scraped_data/guba_posts_{timestamp}.json"

    # 保存数据
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    print(f"\n数据已保存到: {filename}")

    # 打印简要统计信息
    print(f"\n抓取统计:")
    print(f"  - 总共抓取帖子数: {len(posts)}")
    for i, post in enumerate(posts, 1):
        print(f"  - 帖子 {i}: {post['title']}")


def test_firecrawl_search_guba_specific():
    """测试Firecrawl搜索东方财富股吧指定页面5天内数据"""
    print("\n测试Firecrawl搜索东方财富股吧指定页面5天内数据...")

    # 目标URL关键词 - 更具体地指向东方财富股吧
    keyword = "site:guba.eastmoney.com 300339"

    # 计算5天前的日期
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5)

    # 格式化日期为YYYY-MM-DD
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    print(f"搜索关键词: {keyword}")
    print(f"日期范围: {start_date_str} 到 {end_date_str}")

    try:
        headers = {
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json",
        }

        # 首先尝试使用site:语法搜索东方财富股吧
        print("\n1. 尝试使用site:语法搜索东方财富股吧...")
        data_site = {
            "query": keyword,
        }

        response_site = requests.post(
            f"{FIRECRAWL_API_URL}/search", headers=headers, json=data_site
        )

        print(f"site:语法搜索请求状态: {response_site.status_code}")
        if response_site.status_code == 200:
            result_site = response_site.json()
            print("site:语法搜索请求成功")

            # 检查返回的数据结构
            if not isinstance(result_site, dict):
                print("返回结果格式不正确")
                print(f"结果类型: {type(result_site)}")
                print(f"结果内容: {result_site}")
                return None

            # 检查是否有data字段
            if "data" not in result_site:
                print("返回结果中没有data字段")
                print(f"完整响应: {result_site}")
                return None

            data_content = result_site["data"]
            print(f"data字段类型: {type(data_content)}")

            # 处理不同的数据结构
            data_list = []
            if isinstance(data_content, list):
                data_list = data_content
            elif isinstance(data_content, dict):
                # 如果data是字典，检查是否有web键或其他包含实际数据的字段
                if "web" in data_content and isinstance(data_content["web"], list):
                    data_list = data_content["web"]
                elif "results" in data_content and isinstance(
                    data_content["results"], list
                ):
                    data_list = data_content["results"]
                else:
                    # 尝试将字典转换为列表
                    data_list = [data_content]
            else:
                # 其他情况，尝试包装成列表
                data_list = [data_content]

            print(f"处理后的数据列表长度: {len(data_list)}")

            # 如果site:搜索没有结果，尝试直接搜索URL
            if len(data_list) == 0:
                print("\n2. site:搜索没有结果，尝试直接搜索URL...")
                url = "https://guba.eastmoney.com/list,300339.html"
                data_url = {
                    "query": url,
                }

                response_url = requests.post(
                    f"{FIRECRAWL_API_URL}/search", headers=headers, json=data_url
                )

                print(f"URL搜索请求状态: {response_url.status_code}")
                if response_url.status_code == 200:
                    result_url = response_url.json()
                    print("URL搜索请求成功")

                    # 检查返回的数据结构
                    if "data" in result_url:
                        data_content_url = result_url["data"]

                        # 处理不同的数据结构
                        if isinstance(data_content_url, list):
                            data_list = data_content_url
                        elif isinstance(data_content_url, dict):
                            if "web" in data_content_url and isinstance(
                                data_content_url["web"], list
                            ):
                                data_list = data_content_url["web"]
                            else:
                                data_list = [data_content_url]
                        else:
                            data_list = [data_content_url]

                        print(f"URL搜索处理后的数据列表长度: {len(data_list)}")

            # 获取前5条数据（或所有数据，如果少于5条）
            top_5_results = data_list[:5] if len(data_list) >= 5 else data_list
            print(f"\n找到{len(top_5_results)}条数据:")

            if len(top_5_results) == 0:
                print("没有找到相关数据")
            else:
                for i, item in enumerate(top_5_results, 1):
                    # 确保item是字典类型
                    if not isinstance(item, dict):
                        print(f"{i}. 数据格式不正确: {item} (类型: {type(item)})")
                        continue

                    # 安全地提取字段
                    title = item.get("title", "N/A")
                    url = item.get("url", "N/A")
                    description = item.get("description", "N/A")

                    print(f"{i}. 标题: {title}")
                    print(f"   链接: {url}")
                    # 确保description是字符串类型再进行切片
                    if isinstance(description, str):
                        print(f"   描述: {description[:100]}...")
                    else:
                        print(f"   描述: {description}")
                    print("-" * 50)

            # 返回结果（如果有数据则返回前5条，否则返回空列表）
            return top_5_results if top_5_results else []
        else:
            print(f"搜索请求失败: {response_site.text}")
            return None
    except Exception as e:
        print(f"搜索请求异常: {e}")
        import traceback

        traceback.print_exc()  # 打印详细的错误堆栈
        return None


if __name__ == "__main__":
    # test_firecrawl_connection()
    # test_firecrawl_search_guba_specific()
    # test_firecrawl_search_guba()
    scrape_guba_posts()
    # test_firecrawl_scrape()
    # test_firecrawl_crawl()
    # crawl_guba_5days_filtered()
    # crawl_guba_targeted_5days()
    # crawl_guba_5days_data()
