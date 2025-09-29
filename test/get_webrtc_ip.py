#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WebRTC IP地址检测工具

此工具使用Selenium WebDriver配合ChromeDriver实现获取 https://www.ident.me/ 网站中
Browser data的WebRTC IPv4地址。与Firecrawl等服务器端抓取工具不同，此方法能够执行
浏览器端JavaScript代码，从而获取真实的客户端IP地址。

注意：获取到的IP地址是您设备的真实公网IP地址，可能会暴露您的网络信息。
"""

import time
import re
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")

    # 禁用自动化控制特征
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # 自动下载和设置ChromeDriver
    service = Service(ChromeDriverManager().install())

    # 创建WebDriver实例
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 绕过WebDriver检测
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver


def get_webrtc_ips_from_ident_me():
    """
    通过ident.me网站获取WebRTC IP地址

    Returns:
        dict: 包含检测结果的字典
    """
    driver = None
    result = {
        'webrtc_ips': [],
        'http_ip': None,
        'logs': [],
        'success': False,
        'error': None
    }

    try:
        print("🚀 启动WebRTC IP地址检测")
        print("="*50)

        # 初始化WebDriver
        driver = setup_chrome_driver(headless=True)

        # 访问ident.me网站
        target_url = "https://www.ident.me/"
        print(f"📍 访问网站: {target_url}")
        driver.get(target_url)

        # 等待页面加载
        print("⏳ 等待页面加载...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )

        # 等待WebRTC地址加载完成（可能需要一些时间）
        print("🔍 等待WebRTC地址加载...")
        time.sleep(5)  # 给WebRTC一些时间来获取地址

        # 获取页面源码
        page_source = driver.page_source
        print("📄 页面加载完成，分析内容...")

        # 提取HTTP IP地址（页面标题中的IP）
        try:
            title_element = driver.find_element(By.TAG_NAME, "h1")
            title_text = title_element.text
            ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            http_ips = re.findall(ip_pattern, title_text)
            if http_ips:
                result['http_ip'] = http_ips[0]
                print(f"🌐 HTTP IP地址: {result['http_ip']}")
        except Exception as e:
            print(f"⚠️ 获取HTTP IP时出错: {e}")

        # 提取WebRTC地址
        try:
            # 查找包含WebRTC地址的元素
            webrtc_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'WebRTC') or contains(text(), 'webrtc')]")

            for element in webrtc_elements:
                # 获取父元素或相邻元素中的IP地址
                parent = element.find_element(By.XPATH, "..")
                text_content = parent.text

                # 在文本内容中查找IP地址
                ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
                ips = re.findall(ip_pattern, text_content)

                for ip in ips:
                    # 验证IP地址格式并排除特殊地址
                    try:
                        octets = ip.split('.')
                        if len(octets) == 4 and all(0 <= int(octet) <= 255 for octet in octets):
                            if not ip.startswith(('127.', '0.', '255.', '224.')) and ip != '1.1.1.1':
                                if ip not in result['webrtc_ips']:
                                    result['webrtc_ips'].append(ip)
                    except ValueError:
                        continue

        except Exception as e:
            print(f"⚠️ 查找WebRTC IP时出错: {e}")

        # 如果通过元素查找没有找到，尝试直接解析页面源码
        if not result['webrtc_ips']:
            print("🔄 尝试从页面源码直接提取IP...")
            ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            all_ips = re.findall(ip_pattern, page_source)

            for ip in all_ips:
                # 验证IP地址格式并排除特殊地址
                try:
                    octets = ip.split('.')
                    if len(octets) == 4 and all(0 <= int(octet) <= 255 for octet in octets):
                        if not ip.startswith(('127.', '0.', '255.', '224.')) and ip != '1.1.1.1':
                            # 排除HTTP IP（如果已找到）
                            if result['http_ip'] and ip != result['http_ip']:
                                if ip not in result['webrtc_ips']:
                                    result['webrtc_ips'].append(ip)
                            elif not result['http_ip']:
                                if ip not in result['webrtc_ips']:
                                    result['webrtc_ips'].append(ip)
                except ValueError:
                    continue

        # 去重并排序
        result['webrtc_ips'] = sorted(list(set(result['webrtc_ips'])))

        if result['webrtc_ips']:
            print(f"✅ 成功获取到WebRTC IP地址:")
            for ip in result['webrtc_ips']:
                print(f"   🌐 {ip}")
        else:
            print("⚠️ 未找到WebRTC IP地址")
            # 显示部分内容以便分析
            content_preview = page_source[:1000]
            print(f"📄 页面内容预览: {content_preview}")

        result['success'] = True
        print("✅ IP地址检测完成!")

    except Exception as e:
        error_msg = f"❌ 检测过程中发生错误: {str(e)}"
        print(error_msg)
        result['error'] = error_msg
        import traceback
        traceback.print_exc()

    finally:
        if driver:
            print("🔚 关闭浏览器...")
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
        # IPv4验证
        if '.' in ip:
            octets = ip.split('.')
            if len(octets) != 4:
                return False
            for octet in octets:
                val = int(octet)
                if val < 0 or val > 255:
                    return False
            return True
        return False
    except:
        return False


def print_detailed_results(result):
    """
    打印详细结果

    Args:
        result (dict): get_webrtc_ips_from_ident_me函数返回的结果
    """
    print("\n" + "="*60)
    print("📈 检测结果详情")
    print("="*60)

    if not result['success']:
        print(f"❌ 检测失败: {result['error']}")
        return

    # HTTP IP地址
    if result['http_ip']:
        print(f"\n🌐 HTTP IP地址:")
        print(f"   🌍 {result['http_ip']} (通过HTTP请求获取)")
    else:
        print(f"\n🌐 HTTP IP地址: 未检测到")

    # WebRTC IP地址
    if result['webrtc_ips']:
        print(f"\n📡 WebRTC IP地址 ({len(result['webrtc_ips'])} 个):")
        for ip in sorted(result['webrtc_ips']):
            print(f"   🌐 {ip} (真实客户端IP)")
    else:
        print("\n📡 WebRTC IP地址: 未检测到")

    # 统计信息
    print(f"\n📊 统计信息:")
    print(f"   总计IP地址: {len(result['webrtc_ips']) + (1 if result['http_ip'] else 0)}")
    print(f"   HTTP IP地址: {1 if result['http_ip'] else 0}")
    print(f"   WebRTC IP地址: {len(result['webrtc_ips'])}")


def save_results_to_file(result):
    """
    将结果保存到JSON文件

    Args:
        result (dict): 检测结果
    """
    try:
        filename = f"webrtc_detection_result_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 结果已保存到文件: {filename}")
    except Exception as e:
        print(f"⚠️ 保存结果到文件时出错: {e}")


def main():
    """
    主函数
    """
    print("📡 WebRTC IP地址检测工具")
    print("此工具使用Selenium和WebRTC技术检测您的真实IP地址")
    print("包括通过WebRTC获取的真实客户端IP地址")
    print()

    # 执行检测
    result = get_webrtc_ips_from_ident_me()

    # 打印详细结果
    print_detailed_results(result)

    # 保存结果到文件
    save_results_to_file(result)

    print("\n" + "="*60)
    print("💡 说明")
    print("="*60)
    print("1. HTTP IP地址：通过HTTP请求获取的服务器端看到的IP地址")
    print("2. WebRTC IP地址：通过浏览器WebRTC技术获取的真实客户端IP地址")
    print("3. WebRTC技术可以穿透NAT发现您的真实公网IP地址")
    print("4. 某些防火墙或网络配置可能阻止WebRTC检测")
    print("5. 如果WebRTC IP与HTTP IP不同，说明您可能使用了代理或VPN")

    if result['success']:
        total_ips = len(result['webrtc_ips']) + (1 if result['http_ip'] else 0)
        print(f"\n🎉 成功检测到 {total_ips} 个IP地址!")
    else:
        print(f"\n💥 IP地址检测失败")


if __name__ == "__main__":
    main()

