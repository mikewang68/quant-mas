#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用Firecrawl获取ip138.com网站显示的IP地址
"""

import requests
import json
import re

def get_ip_from_ip138_with_firecrawl():
    """
    使用Firecrawl获取ip138.com网站显示的IP地址
    """
    # Firecrawl API端点
    firecrawl_url = "http://192.168.1.2:8080/v1/scrape"

    # 要抓取的网页
    target_url = "https://www.ip138.com/"

    # 请求参数
    payload = {
        "url": target_url,
        "formats": ["markdown", "html"]
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        print(f"正在向 {firecrawl_url} 发送请求...")
        print(f"目标网址: {target_url}")

        # 发送POST请求到Firecrawl
        response = requests.post(firecrawl_url, json=payload, headers=headers, timeout=30)
        print(f"响应状态码: {response.status_code}")

        if response.status_code != 200:
            print(f"错误响应内容: {response.text}")
            return None

        # 解析响应数据
        data = response.json()

        if not data.get('success', False):
            print(f"API调用失败: {data}")
            return None

        print("Firecrawl响应数据:")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        # 提取内容
        content_data = data.get('data', {})
        markdown_content = content_data.get('markdown', '')
        html_content = content_data.get('html', '')

        print("\nMarkdown内容预览:")
        print(markdown_content[:1000] + "..." if len(markdown_content) > 1000 else markdown_content)

        # 在内容中查找IPv4地址
        # ip138.com通常会在页面上直接显示访问者的IP地址
        ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ipv4_addresses = re.findall(ipv4_pattern, markdown_content + html_content)

        # 验证和过滤IP地址
        valid_ips = []
        for ip in ipv4_addresses:
            # 验证IP地址格式
            try:
                octets = ip.split('.')
                if len(octets) == 4 and all(0 <= int(octet) <= 255 for octet in octets):
                    # 排除一些特殊地址
                    if not ip.startswith(('127.', '0.', '255.', '224.')) and ip != '1.1.1.1':
                        valid_ips.append(ip)
            except ValueError:
                continue

        # 去重
        unique_ips = list(set(valid_ips))

        if unique_ips:
            print(f"\n找到的IPv4地址:")
            for ip in unique_ips:
                print(f"  - {ip}")
            return unique_ips
        else:
            print("未找到有效的IPv4地址")
            return []

    except requests.exceptions.Timeout:
        print("请求超时")
        return None
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print(f"响应内容: {response.text}")
        return None
    except Exception as e:
        print(f"其他错误: {e}")
        return None

def get_ip_from_ip138_with_firecrawl_v2():
    """
    使用Firecrawl获取ip138.com网站显示的IP地址 (增强版)
    """
    # Firecrawl API端点
    firecrawl_url = "http://192.168.1.2:8080/v1/scrape"

    # 要抓取的网页
    target_url = "https://www.ip138.com/"

    # 请求参数 - 增加等待时间
    payload = {
        "url": target_url,
        "formats": ["markdown", "html"],
        "waitFor": 3000  # 等待3秒
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        print(f"正在向 {firecrawl_url} 发送请求 (增强版)...")
        print(f"目标网址: {target_url}")

        # 发送POST请求到Firecrawl
        response = requests.post(firecrawl_url, json=payload, headers=headers, timeout=30)
        print(f"响应状态码: {response.status_code}")

        if response.status_code != 200:
            print(f"错误响应内容: {response.text}")
            return None

        # 解析响应数据
        data = response.json()

        if not data.get('success', False):
            print(f"API调用失败: {data}")
            return None

        # 提取内容
        content_data = data.get('data', {})
        markdown_content = content_data.get('markdown', '')
        html_content = content_data.get('html', '')

        # 在内容中查找IPv4地址
        ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ipv4_addresses = re.findall(ipv4_pattern, markdown_content + html_content)

        # 验证和过滤IP地址
        valid_ips = []
        for ip in ipv4_addresses:
            # 验证IP地址格式
            try:
                octets = ip.split('.')
                if len(octets) == 4 and all(0 <= int(octet) <= 255 for octet in octets):
                    # 排除一些特殊地址
                    if not ip.startswith(('127.', '0.', '255.', '224.')) and ip != '1.1.1.1':
                        valid_ips.append(ip)
            except ValueError:
                continue

        # 去重
        unique_ips = list(set(valid_ips))

        if unique_ips:
            print(f"\n找到的IPv4地址:")
            for ip in unique_ips:
                print(f"  - {ip}")
            return unique_ips
        else:
            print("未找到有效的IPv4地址")
            # 显示部分内容以便分析
            print("\n页面内容预览 (前1000字符):")
            content_preview = (markdown_content + html_content)[:1000]
            print(content_preview)
            return []

    except requests.exceptions.Timeout:
        print("请求超时")
        return None
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print(f"响应内容: {response.text}")
        return None
    except Exception as e:
        print(f"其他错误: {e}")
        return None

if __name__ == "__main__":
    print("=== 使用Firecrawl获取ip138.com网站显示的IP地址 ===\n")

    print("方法1: 基础版本")
    ips1 = get_ip_from_ip138_with_firecrawl()

    print("\n" + "="*50 + "\n")

    print("方法2: 增强版本 (带等待)")
    ips2 = get_ip_from_ip138_with_firecrawl_v2()

    # 合并结果
    all_ips = []
    if ips1:
        all_ips.extend(ips1)
    if ips2:
        all_ips.extend(ips2)
    all_ips = list(set(all_ips))  # 去重

    print("\n=== 最终结果 ===")
    if all_ips:
        print("获取到的IPv4地址:")
        for ip in sorted(all_ips):
            print(f"  - {ip}")
    else:
        print("未能获取到IP地址")

    print("\n说明:")
    print("1. ip138.com显示的是访问者的公网IP地址")
    print("2. 通过Firecrawl获取的是Firecrawl服务器的IP地址")
    print("3. 这与您本地访问该网站看到的IP地址可能不同")

