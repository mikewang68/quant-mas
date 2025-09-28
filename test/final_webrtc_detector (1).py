#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最终版：使用Selenium WebDriver获取ident.me网站的WebRTC IPv4地址

这个脚本专门用于访问 https://www.ident.me/ 网站并获取其中的WebRTC地址。
ident.me网站会显示访问者的公网IP地址以及通过WebRTC获取的本地IP地址。
"""

import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def setup_chrome_driver(headless=True):
    """
    设置Chrome WebDriver

    Args:
        headless (bool): 是否使用无头模式

    Returns:
        webdriver.Chrome: Chrome WebDriver实例
    """
    # 配置Chrome选项
    chrome_options = Options()

    # 无头模式
    if headless:
        chrome_options.add_argument("--headless")

    # 其他有用的选项
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # 禁用自动化控制特征
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # WebRTC相关设置
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-web-security")

    # 自动下载和设置ChromeDriver
    service = Service(ChromeDriverManager().install())

    # 创建WebDriver实例
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 绕过WebDriver检测
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver

def get_webrtc_ips_from_identme(headless=True):
    """
    从ident.me网站获取WebRTC IPv4地址

    Args:
        headless (bool): 是否使用无头模式

    Returns:
        dict: 包含各种IP地址信息的字典
    """
    driver = None
    result = {
        'public_ipv4': None,
        'public_ipv6': None,
        'webrtc_ips': [],
        'all_ips': [],
        'raw_webrtc_text': None,
        'success': False,
        'error': None
    }

    try:
        print("正在初始化Chrome WebDriver...")
        driver = setup_chrome_driver(headless)

        print("正在访问 https://www.ident.me/ ...")
        driver.get("https://www.ident.me/")

        print("等待页面加载(最多15秒)...")
        # 等待主要元素加载
        start_time = time.time()
        while time.time() - start_time < 15:
            try:
                # 检查页面是否加载完成
                h1_element = driver.find_element(By.TAG_NAME, "h1")
                if h1_element and "IP addresses" in h1_element.text:
                    break
            except:
                pass
            time.sleep(0.5)

        print("等待WebRTC地址加载(最多30秒)...")
        # 等待WebRTC地址加载完成
        start_time = time.time()
        webrtc_text = ""
        while time.time() - start_time < 30:
            try:
                webrtc_element = driver.find_element(By.ID, "webrtc")
                webrtc_text = webrtc_element.text.strip()
                # 如果不再是"Loading..."，说明加载完成
                if webrtc_text and webrtc_text != "Loading...":
                    print(f"WebRTC地址已加载: {webrtc_text}")
                    result['raw_webrtc_text'] = webrtc_text
                    break
            except Exception as e:
                print(f"获取WebRTC元素时出错: {e}")
            time.sleep(1)

        # 获取页面完整内容
        page_source = driver.page_source

        # 1. 提取公网IPv4地址
        try:
            # IPv4地址通常在页面顶部显示
            ipv4_element = driver.find_element(By.ID, "v4")
            ipv4_text = ipv4_element.text.strip()
            if ipv4_text and is_valid_public_ip(ipv4_text):
                result['public_ipv4'] = ipv4_text
                print(f"公网IPv4地址: {ipv4_text}")
        except:
            # 从页面源码中查找
            ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            ipv4_matches = re.findall(ipv4_pattern, page_source)
            for ip in ipv4_matches:
                if is_valid_public_ip(ip):
                    result['public_ipv4'] = ip
                    print(f"公网IPv4地址: {ip}")
                    break

        # 2. 提取公网IPv6地址
        try:
            ipv6_element = driver.find_element(By.ID, "v6")
            ipv6_text = ipv6_element.text.strip()
            if ipv6_text and ipv6_text != "::1":
                result['public_ipv6'] = ipv6_text
                print(f"公网IPv6地址: {ipv6_text}")
        except:
            pass

        # 3. 从WebRTC文本中提取IP地址
        if webrtc_text:
            # 查找IPv4地址模式
            ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            webrtc_ips = re.findall(ipv4_pattern, webrtc_text)
            for ip in webrtc_ips:
                if is_valid_ip(ip) and ip not in result['webrtc_ips']:
                    result['webrtc_ips'].append(ip)

        # 4. 从整个页面源码中提取所有IP地址
        ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        all_ips = re.findall(ipv4_pattern, page_source)

        # 验证和过滤IP地址
        valid_ips = []
        for ip in all_ips:
            if is_valid_ip(ip):
                # 排除特殊地址
                if not ip.startswith(('127.', '0.', '255.', '224.')) and ip != '1.1.1.1':
                    valid_ips.append(ip)

        # 去重并排序
        result['all_ips'] = sorted(list(set(valid_ips)))

        # 如果我们找到了公网IPv4，确保它在WebRTC IPs中
        if result['public_ipv4'] and result['public_ipv4'] not in result['webrtc_ips']:
            result['webrtc_ips'].append(result['public_ipv4'])

        result['success'] = True
        print("成功获取IP地址信息")

    except Exception as e:
        error_msg = f"发生错误: {str(e)}"
        print(error_msg)
        result['error'] = error_msg
        import traceback
        traceback.print_exc()

    finally:
        if driver:
            print("关闭浏览器...")
            driver.quit()

    return result

def is_valid_ip(ip):
    """
    验证IP地址是否有效

    Args:
        ip (str): 要验证的IP地址

    Returns:
        bool: 如果IP地址有效返回True，否则返回False
    """
    try:
        octets = ip.split('.')
        if len(octets) != 4:
            return False
        for octet in octets:
            val = int(octet)
            if val < 0 or val > 255:
                return False
        return True
    except:
        return False

def is_valid_public_ip(ip):
    """
    验证是否为有效的公网IP地址

    Args:
        ip (str): 要验证的IP地址

    Returns:
        bool: 如果是有效的公网IP地址返回True，否则返回False
    """
    if not is_valid_ip(ip):
        return False

    # 排除私有地址范围
    if (ip.startswith('192.168.') or
        ip.startswith('10.') or
        (ip.startswith('172.') and 16 <= int(ip.split('.')[1]) <= 31) or
        ip.startswith(('127.', '0.', '255.', '224.')) or
        ip == '1.1.1.1'):
        return False

    return True

def print_results(result):
    """
    打印结果

    Args:
        result (dict): get_webrtc_ips_from_identme函数返回的结果
    """
    print("\n" + "="*60)
    print("结果详情")
    print("="*60)

    if not result['success']:
        print(f"执行失败: {result['error']}")
        return

    # 公网IPv4
    if result['public_ipv4']:
        print(f"公网IPv4地址: {result['public_ipv4']}")

    # 公网IPv6
    if result['public_ipv6']:
        print(f"公网IPv6地址: {result['public_ipv6']}")

    # WebRTC获取的IP地址
    if result['webrtc_ips']:
        print(f"\nWebRTC检测到的IP地址:")
        for ip in sorted(result['webrtc_ips']):
            ip_type = classify_ip(ip)
            print(f"  - {ip} ({ip_type})")

    # 所有检测到的IP地址
    if result['all_ips']:
        print(f"\n页面中所有检测到的IP地址:")
        for ip in sorted(result['all_ips']):
            ip_type = classify_ip(ip)
            print(f"  - {ip} ({ip_type})")

    # 原始WebRTC文本
    if result['raw_webrtc_text']:
        print(f"\n原始WebRTC文本: {result['raw_webrtc_text']}")

def classify_ip(ip):
    """
    分类IP地址类型

    Args:
        ip (str): IP地址

    Returns:
        str: IP地址类型描述
    """
    if ip.startswith('192.168.'):
        return "私有地址(192.168.x.x)"
    elif ip.startswith('10.'):
        return "私有地址(10.x.x.x)"
    elif ip.startswith('172.'):
        second_octet = int(ip.split('.')[1])
        if 16 <= second_octet <= 31:
            return "私有地址(172.16-31.x.x)"
        else:
            return "公网地址"
    elif ip.startswith(('127.', '0.', '255.', '224.')):
        return "特殊地址"
    else:
        return "公网地址"

def main():
    """
    主函数
    """
    print("=== 使用Selenium WebDriver获取ident.me网站的WebRTC IPv4地址 ===")
    print("此工具将访问 https://www.ident.me/ 网站并获取您的WebRTC IP地址")
    print("包括公网IP和可能的本地网络IP地址")

    # 先尝试可视化模式（可以看到浏览器操作）
    print("\n--- 第一次尝试：可视化模式 ---")
    result = get_webrtc_ips_from_identme(headless=False)

    # 如果失败，再尝试无头模式
    if not result['success']:
        print("\n--- 第二次尝试：无头模式 ---")
        result = get_webrtc_ips_from_identme(headless=True)

    # 打印结果
    print_results(result)

    print("\n" + "="*60)
    print("说明")
    print("="*60)
    print("1. 公网IP地址：您的互联网服务提供商(ISP)分配给您的公网IP")
    print("2. 私有IP地址：您本地网络中的IP地址(如192.168.x.x)")
    print("3. WebRTC技术可以穿透NAT发现本地网络接口的IP地址")
    print("4. 某些网络配置可能阻止WebRTC获取本地IP地址")
    print("5. 如果只显示公网IP，说明您的网络环境限制了WebRTC")

    if result['success']:
        print(f"\n✅ 成功获取到 {len(result['all_ips'])} 个IP地址")
    else:
        print(f"\n❌ 获取IP地址失败")

if __name__ == "__main__":
    main()

