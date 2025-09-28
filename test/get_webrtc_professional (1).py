#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
专业版：使用Selenium WebDriver获取WebRTC IPv4地址
通过专业的WebRTC检测页面获取真实的本地和公网IP地址
"""

import time
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def setup_chrome_driver():
    """
    设置Chrome WebDriver
    """
    # 配置Chrome选项
    chrome_options = Options()

    # 可视化模式（便于调试）
    # 如果要无头模式，取消下面这行的注释
    # chrome_options.add_argument("--headless")

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

def get_webrtc_ips_professional():
    """
    使用专业的WebRTC检测方法获取IP地址
    """
    driver = None
    try:
        print("正在初始化Chrome WebDriver...")
        driver = setup_chrome_driver()

        # 获取当前目录并加载本地HTML文件
        current_dir = os.path.dirname(os.path.abspath(__file__))
        html_file_path = os.path.join(current_dir, "webrtc_test.html")

        print(f"正在加载本地WebRTC测试页面: {html_file_path}")
        driver.get(f"file://{html_file_path}")

        print("等待页面加载和IP检测(最多20秒)...")
        time.sleep(10)  # 给页面足够时间执行WebRTC检测

        # 尝试获取检测到的IP地址
        ip_addresses = []

        try:
            # 方法1: 从页面的IP列表中获取
            ip_elements = driver.find_elements(By.CSS_SELECTOR, "#ips .ip-item")
            print(f"找到 {len(ip_elements)} 个IP元素")

            for element in ip_elements:
                text = element.text.strip()
                print(f"IP元素内容: {text}")

                # 提取IP地址
                ip_match = re.search(r'(\d{1,3}\.){3}\d{1,3}', text)
                if ip_match:
                    ip = ip_match.group()
                    if is_valid_ip(ip):
                        ip_addresses.append(ip)
                        print(f"提取到有效IP: {ip}")

        except Exception as e:
            print(f"从IP列表获取地址时出错: {e}")

        # 方法2: 从JavaScript变量中获取
        try:
            detected_ips = driver.execute_script("return detectedIPs || []")
            print(f"从JavaScript获取到的IP: {detected_ips}")

            for ip in detected_ips:
                if is_valid_ip(str(ip)):
                    ip_addresses.append(str(ip))
        except Exception as e:
            print(f"从JavaScript获取地址时出错: {e}")

        # 方法3: 从页面源码中提取
        try:
            page_source = driver.page_source
            # 查找IPv4地址模式
            ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            found_ips = re.findall(ipv4_pattern, page_source)

            for ip in found_ips:
                if is_valid_ip(ip) and ip not in ip_addresses:
                    ip_addresses.append(ip)
                    print(f"从页面源码提取到IP: {ip}")
        except Exception as e:
            print(f"从页面源码提取地址时出错: {e}")

        # 去重并验证
        unique_ips = []
        for ip in ip_addresses:
            if is_valid_ip(ip) and ip not in unique_ips:
                # 排除特殊地址
                if not ip.startswith(('127.', '0.', '255.', '224.')) and ip != '1.1.1.1':
                    unique_ips.append(ip)

        print(f"\n最终获取到的有效IP地址: {unique_ips}")
        return unique_ips

    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
        return []

    finally:
        if driver:
            print("关闭浏览器...")
            driver.quit()

def is_valid_ip(ip):
    """
    验证IP地址是否有效
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

def get_webrtc_from_identme():
    """
    从ident.me网站获取WebRTC地址（作为对比）
    """
    driver = None
    try:
        print("\n=== 从ident.me获取WebRTC地址 ===")
        driver = setup_chrome_driver()

        print("正在访问 https://www.ident.me/ ...")
        driver.get("https://www.ident.me/")

        print("等待页面加载...")
        time.sleep(5)  # 等待页面加载

        # 尝试获取所有可能包含IP的元素
        ip_addresses = []

        try:
            # 获取WebRTC元素
            webrtc_element = driver.find_element(By.ID, "webrtc")
            webrtc_text = webrtc_element.text.strip()
            print(f"WebRTC元素内容: {webrtc_text}")

            # 从文本中提取IP
            ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            ips = re.findall(ipv4_pattern, webrtc_text)
            ip_addresses.extend(ips)

        except Exception as e:
            print(f"获取WebRTC元素时出错: {e}")

        # 从整个页面源码中提取
        try:
            page_source = driver.page_source
            ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            ips = re.findall(ipv4_pattern, page_source)

            for ip in ips:
                if is_valid_ip(ip) and ip not in ip_addresses:
                    ip_addresses.append(ip)
        except Exception as e:
            print(f"从页面源码提取时出错: {e}")

        # 验证和过滤
        valid_ips = []
        for ip in ip_addresses:
            if is_valid_ip(ip):
                if not ip.startswith(('127.', '0.', '255.', '224.')) and ip != '1.1.1.1':
                    valid_ips.append(ip)

        print(f"从ident.me获取到的IP: {valid_ips}")
        return valid_ips

    except Exception as e:
        print(f"发生错误: {e}")
        return []

    finally:
        if driver:
            print("关闭浏览器...")
            driver.quit()

if __name__ == "__main__":
    print("=== 专业版：使用Selenium WebDriver获取WebRTC IPv4地址 ===\n")

    print("方法1: 使用专业WebRTC检测页面")
    ips1 = get_webrtc_ips_professional()

    print("\n" + "="*60 + "\n")

    print("方法2: 从ident.me网站获取")
    ips2 = get_webrtc_from_identme()

    # 合并所有结果
    all_ips = list(set(ips1 + ips2))

    print("\n" + "="*60 + "\n")
    print("=== 最终结果 ===")
    if all_ips:
        print("获取到的WebRTC IPv4地址:")
        for ip in sorted(all_ips):
            # 判断IP类型
            ip_type = "未知"
            if ip.startswith('192.168.'):
                ip_type = "私有地址(192.168.x.x)"
            elif ip.startswith('10.'):
                ip_type = "私有地址(10.x.x.x)"
            elif ip.startswith('172.'):
                second_octet = int(ip.split('.')[1])
                if 16 <= second_octet <= 31:
                    ip_type = "私有地址(172.16-31.x.x)"
                else:
                    ip_type = "公网地址"
            else:
                ip_type = "公网地址"

            print(f"  - {ip} ({ip_type})")
    else:
        print("未能获取到WebRTC IPv4地址")

    print("\n说明:")
    print("- WebRTC技术可以获取到本地网络接口的IP地址")
    print("- 私有地址用于局域网内部通信")
    print("- 公网地址是互联网上可访问的地址")
    print("- 某些网络环境下可能获取不到公网地址")

