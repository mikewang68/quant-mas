#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
专业WebRTC IP地址检测工具

此工具使用Selenium WebDriver加载自定义的WebRTC检测页面，
通过标准WebRTC API获取真实的客户端公网IP地址。
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


def detect_webrtc_ips_professional():
    """
    使用专业WebRTC检测页面获取IP地址

    Returns:
        dict: 包含检测结果的字典
    """
    driver = None
    result = {
        'webrtc_ips': [],
        'logs': [],
        'success': False,
        'error': None
    }

    try:
        print("🚀 启动专业WebRTC IP地址检测")
        print("="*50)

        # 初始化WebDriver
        driver = setup_chrome_driver(headless=True)

        # 加载本地WebRTC检测页面
        current_dir = os.path.dirname(os.path.abspath(__file__))
        html_file_path = os.path.join(current_dir, "webrtc_detector.html")

        print(f"📄 加载本地检测页面: {html_file_path}")
        driver.get(f"file://{html_file_path}")

        # 等待页面加载和检测完成
        print("⏳ 等待检测完成...")
        time.sleep(10)  # 给足够时间执行WebRTC检测

        # 获取检测结果
        print("📊 收集检测结果...")

        # 获取WebRTC IP地址
        try:
            ip_elements = driver.find_elements(By.CSS_SELECTOR, "#webrtc-ips .ip-item")
            for element in ip_elements:
                ip = element.text.strip()
                if ip and is_valid_public_ip(ip) and ip not in result['webrtc_ips']:
                    result['webrtc_ips'].append(ip)
            print(f"🌐 WebRTC IP地址: {result['webrtc_ips']}")
        except Exception as e:
            print(f"⚠️ 获取WebRTC IP时出错: {e}")

        # 获取日志信息
        try:
            log_elements = driver.find_elements(By.CSS_SELECTOR, "#logs div")
            for element in log_elements:
                log_text = element.text.strip()
                if log_text:
                    result['logs'].append(log_text)
        except Exception as e:
            print(f"⚠️ 获取日志时出错: {e}")

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


def is_valid_public_ip(ip):
    """
    验证是否为有效的公网IP地址

    Args:
        ip (str): 要验证的IP地址

    Returns:
        bool: 如果是有效的公网IP返回True，否则返回False
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
            # 排除私有IP和特殊IP
            if ip.startswith(('127.', '0.', '255.', '224.')):
                return False
            if ip.startswith('192.168.'):
                return False
            if ip.startswith('10.'):
                return False
            if ip.startswith('172.'):
                second_octet = int(ip.split('.')[1])
                if 16 <= second_octet <= 31:
                    return False
            if ip == '1.1.1.1':
                return False
            return True
        return False
    except:
        return False


def print_detailed_results(result):
    """
    打印详细结果

    Args:
        result (dict): detect_webrtc_ips_professional函数返回的结果
    """
    print("\n" + "="*60)
    print("📈 检测结果详情")
    print("="*60)

    if not result['success']:
        print(f"❌ 检测失败: {result['error']}")
        return

    # WebRTC IP地址
    if result['webrtc_ips']:
        print(f"\n🌐 WebRTC检测到的公网IP地址 ({len(result['webrtc_ips'])} 个):")
        for ip in sorted(result['webrtc_ips']):
            print(f"   🌐 {ip} (真实客户端公网IP)")
    else:
        print("\n🌐 WebRTC检测到的公网IP地址: 未检测到")

    # 统计信息
    print(f"\n📊 统计信息:")
    print(f"   WebRTC公网IP地址: {len(result['webrtc_ips'])}")

    # 显示部分日志（最后10条）
    if result['logs']:
        print(f"\n📋 最近日志 (最后10条):")
        for log in result['logs'][-10:]:
            print(f"   {log}")


def save_results_to_file(result):
    """
    将结果保存到JSON文件

    Args:
        result (dict): 检测结果
    """
    try:
        filename = f"webrtc_professional_result_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 结果已保存到文件: {filename}")
    except Exception as e:
        print(f"⚠️ 保存结果到文件时出错: {e}")


def main():
    """
    主函数
    """
    print("📡 专业WebRTC IP地址检测工具")
    print("此工具使用Selenium和WebRTC技术检测您的真实公网IP地址")
    print()

    # 执行检测
    result = detect_webrtc_ips_professional()

    # 打印详细结果
    print_detailed_results(result)

    # 保存结果到文件
    save_results_to_file(result)

    print("\n" + "="*60)
    print("💡 说明")
    print("="*60)
    print("1. WebRTC IP地址：通过浏览器WebRTC技术获取的真实客户端公网IP地址")
    print("2. 与HTTP请求不同，WebRTC可以直接发现您的真实公网IP")
    print("3. 某些网络环境（如企业防火墙）可能阻止WebRTC检测")
    print("4. 如果未检测到IP，可能是因为网络限制或STUN服务器不可达")

    if result['success'] and result['webrtc_ips']:
        print(f"\n🎉 成功检测到 {len(result['webrtc_ips'])} 个公网IP地址!")
        # 显示您提到的目标IP地址
        target_ip = "223.102.68.134"
        if target_ip in result['webrtc_ips']:
            print(f"✅ 找到目标IP地址: {target_ip}")
        else:
            print(f"ℹ️  未找到目标IP地址 {target_ip}，但检测到其他公网IP地址")
    else:
        print(f"\n💥 IP地址检测失败或未检测到公网IP地址")


if __name__ == "__main__":
    main()

