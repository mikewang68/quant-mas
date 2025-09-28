#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
专业WebRTC检测器：使用Selenium和自定义HTML页面获取真实的WebRTC IP地址

这个脚本使用Selenium WebDriver加载一个专门创建的WebRTC检测页面，
该页面使用标准的WebRTC API来发现本地和公网IP地址。
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

def setup_chrome_driver(headless=False):
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

def detect_webrtc_ips():
    """
    使用专业WebRTC检测页面获取IP地址

    Returns:
        dict: 包含检测结果的字典
    """
    driver = None
    result = {
        'local_ips': [],
        'public_ips': [],
        'logs': [],
        'success': False,
        'error': None
    }

    try:
        print("🚀 启动专业WebRTC IP地址检测")
        print("="*50)

        # 初始化WebDriver
        driver = setup_chrome_driver(headless=False)

        # 加载本地WebRTC检测页面
        current_dir = os.path.dirname(os.path.abspath(__file__))
        html_file_path = os.path.join(current_dir, "direct_webrtc_detector.html")

        if not os.path.exists(html_file_path):
            raise FileNotFoundError(f"找不到HTML文件: {html_file_path}")

        print(f"📄 加载本地检测页面: {html_file_path}")
        driver.get(f"file://{html_file_path}")

        # 等待页面加载
        print("⏳ 等待页面加载...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )

        # 点击开始检测按钮
        print("▶️ 点击开始检测按钮")
        start_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "startBtn"))
        )
        start_button.click()

        # 等待检测完成（最多30秒）
        print("🔍 正在检测IP地址，请等待...")
        time.sleep(15)  # 给足够时间执行WebRTC检测

        # 获取检测结果
        print("📊 收集检测结果...")

        # 获取本地IP地址
        try:
            local_ip_elements = driver.find_elements(By.CSS_SELECTOR, "#local-ips .ip-item")
            for element in local_ip_elements:
                ip = element.text.strip()
                if ip and is_valid_ip(ip) and ip not in result['local_ips']:
                    result['local_ips'].append(ip)
            print(f"🏠 本地IP地址: {result['local_ips']}")
        except Exception as e:
            print(f"⚠️ 获取本地IP时出错: {e}")

        # 获取公网IP地址
        try:
            public_ip_elements = driver.find_elements(By.CSS_SELECTOR, "#public-ips .ip-item")
            for element in public_ip_elements:
                ip = element.text.strip()
                if ip and is_valid_ip(ip) and ip not in result['public_ips']:
                    result['public_ips'].append(ip)
            print(f"🌐 公网IP地址: {result['public_ips']}")
        except Exception as e:
            print(f"⚠️ 获取公网IP时出错: {e}")

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
        # IPv6验证（简化）
        elif ':' in ip:
            return True
        return False
    except:
        return False

def is_private_ip(ip):
    """
    判断是否为私有IP地址

    Args:
        ip (str): IP地址

    Returns:
        bool: 如果是私有IP返回True，否则返回False
    """
    if ip.startswith('192.168.'):
        return True
    elif ip.startswith('10.'):
        return True
    elif ip.startswith('172.'):
        second_octet = int(ip.split('.')[1])
        if 16 <= second_octet <= 31:
            return True
    return False

def print_detailed_results(result):
    """
    打印详细结果

    Args:
        result (dict): detect_webrtc_ips函数返回的结果
    """
    print("\n" + "="*60)
    print("📈 检测结果详情")
    print("="*60)

    if not result['success']:
        print(f"❌ 检测失败: {result['error']}")
        return

    # 本地IP地址
    if result['local_ips']:
        print(f"\n🏠 本地IP地址 ({len(result['local_ips'])} 个):")
        for ip in sorted(result['local_ips']):
            print(f"   📱 {ip} (局域网地址)")
    else:
        print("\n🏠 本地IP地址: 未检测到")

    # 公网IP地址
    if result['public_ips']:
        print(f"\n🌐 公网IP地址 ({len(result['public_ips'])} 个):")
        for ip in sorted(result['public_ips']):
            print(f"   🌍 {ip} (互联网地址)")
    else:
        print("\n🌐 公网IP地址: 未检测到")

    # 统计信息
    print(f"\n📊 统计信息:")
    print(f"   总计IP地址: {len(result['local_ips']) + len(result['public_ips'])}")
    print(f"   本地IP地址: {len(result['local_ips'])}")
    print(f"   公网IP地址: {len(result['public_ips'])}")

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
    print("📡 专业WebRTC IP地址检测工具")
    print("此工具使用Selenium和WebRTC技术检测您的真实IP地址")
    print("包括本地网络IP和公网IP地址")

    # 执行检测
    result = detect_webrtc_ips()

    # 打印详细结果
    print_detailed_results(result)

    # 保存结果到文件
    save_results_to_file(result)

    print("\n" + "="*60)
    print("💡 说明")
    print("="*60)
    print("1. 本地IP地址：您的设备在局域网中的地址（如192.168.x.x）")
    print("2. 公网IP地址：您的互联网服务提供商分配的公网地址")
    print("3. WebRTC技术可以穿透NAT发现本地网络接口")
    print("4. 某些防火墙或网络配置可能阻止WebRTC检测")
    print("5. 如果未检测到本地IP，说明您的网络环境限制了WebRTC")

    if result['success']:
        total_ips = len(result['local_ips']) + len(result['public_ips'])
        print(f"\n🎉 成功检测到 {total_ips} 个IP地址!")
    else:
        print(f"\n💥 IP地址检测失败")

if __name__ == "__main__":
    main()

