#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
目标IP地址检测工具

此工具专门用于检测您指定的目标IP地址223.102.68.134是否在网页上显示。

注意：此工具会详细分析网页内容以查找特定的IP地址。
"""

import time
import re
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

    # 无头模式 - 默认使用有头模式以更好地模拟浏览器
    if headless:
        chrome_options.add_argument("--headless")

    # 其他有用的选项
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

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


def detect_target_ip():
    """
    检测目标IP地址223.102.68.134是否在网页上显示

    Returns:
        dict: 包含检测结果的字典
    """
    driver = None
    target_ip = "223.102.68.134"
    result = {
        'target_ip': target_ip,
        'found_on_page': False,
        'found_location': None,
        'page_content': None,
        'logs': [],
        'success': False,
        'error': None
    }

    try:
        print(f"🚀 启动目标IP地址检测: {target_ip}")
        print("="*50)

        # 初始化WebDriver - 使用有头模式以更好地模拟浏览器
        driver = setup_chrome_driver(headless=False)

        # 访问ip138.com网站
        target_url = "https://www.ip138.com/"
        print(f"📍 访问网站: {target_url}")
        result['logs'].append(f"访问网站: {target_url}")
        driver.get(target_url)

        # 等待页面加载
        print("⏳ 等待页面加载...")
        result['logs'].append("等待页面加载...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # 给页面更多时间完全加载，特别是JavaScript执行
        print("⏳ 等待JavaScript执行完成...")
        result['logs'].append("等待JavaScript执行完成...")
        time.sleep(15)

        # 获取页面源码
        page_source = driver.page_source
        body_text = driver.find_element(By.TAG_NAME, "body").text
        print("📄 页面加载完成，分析内容...")
        result['logs'].append("页面加载完成，分析内容...")

        # 合并所有文本内容
        combined_text = body_text + " " + page_source
        result['logs'].append(f"合并文本长度: {len(combined_text)} 字符")

        # 保存部分页面内容用于分析
        result['page_content'] = combined_text[:5000]  # 保存前5000字符

        # 检查目标IP是否在页面上
        if target_ip in combined_text:
            result['found_on_page'] = True
            print(f"✅ 在页面上找到目标IP地址: {target_ip}")
            result['logs'].append(f"在页面上找到目标IP地址: {target_ip}")

            # 查找目标IP在页面上的具体位置
            lines = combined_text.split('\n')
            for i, line in enumerate(lines):
                if target_ip in line:
                    result['found_location'] = f"第 {i+1} 行: {line.strip()}"
                    print(f"📍 目标IP位置: {result['found_location']}")
                    result['logs'].append(f"目标IP位置: {result['found_location']}")
                    break
        else:
            print(f"❌ 页面上未找到目标IP地址: {target_ip}")
            result['logs'].append(f"页面上未找到目标IP地址: {target_ip}")

            # 显示页面上找到的所有IP地址（用于调试）
            ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            all_ips = re.findall(ip_pattern, combined_text)
            if all_ips:
                print(f"🔍 页面上找到的其他IP地址: {all_ips}")
                result['logs'].append(f"页面上找到的其他IP地址: {all_ips}")

        result['success'] = True
        print("✅ 目标IP检测完成!")

    except Exception as e:
        error_msg = f"❌ 检测过程中发生错误: {str(e)}"
        print(error_msg)
        result['error'] = error_msg
        result['logs'].append(error_msg)
        import traceback
        traceback.print_exc()

    finally:
        if driver:
            print("🔚 关闭浏览器...")
            result['logs'].append("关闭浏览器...")
            driver.quit()

    return result


def print_detailed_results(result):
    """
    打印详细结果

    Args:
        result (dict): detect_target_ip函数返回的结果
    """
    print("\n" + "="*60)
    print("📈 目标IP地址检测结果")
    print("="*60)

    if not result['success']:
        print(f"❌ 检测失败: {result['error']}")
        return

    target_ip = result['target_ip']
    if result['found_on_page']:
        print(f"\n🎯 目标IP地址 {target_ip} 检测结果:")
        print(f"   ✅ 在页面上找到目标IP地址: {target_ip}")
        if result['found_location']:
            print(f"   📍 位置: {result['found_location']}")
    else:
        print(f"\n❌ 目标IP地址 {target_ip} 检测结果:")
        print(f"   ❌ 页面上未找到目标IP地址: {target_ip}")
        print(f"   💡 说明: 页面可能显示了其他IP地址，但不是您指定的目标IP")


def save_results_to_file(result):
    """
    将结果保存到JSON文件

    Args:
        result (dict): 检测结果
    """
    try:
        filename = f"target_ip_detection_result_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 结果已保存到文件: {filename}")
    except Exception as e:
        print(f"⚠️ 保存结果到文件时出错: {e}")


def main():
    """
    主函数 - 执行目标IP地址检测
    """
    print("🔍 目标IP地址检测工具")
    print("此工具专门检测您指定的目标IP地址是否在ip138.com网站上显示")
    print()

    # 执行检测
    result = detect_target_ip()

    # 打印详细结果
    print_detailed_results(result)

    # 保存结果到文件
    save_results_to_file(result)

    print("\n" + "="*60)
    print("💡 说明")
    print("="*60)
    print("1. 此工具检测您指定的目标IP地址是否在网页上显示")
    print("2. 如果未找到，可能是因为:")
    print("   - 网络环境已变化")
    print("   - 网站显示内容已更新")
    print("   - 您当前的网络环境不显示该IP地址")

    if result['success'] and result['found_on_page']:
        print(f"\n🎉 成功在页面上找到目标IP地址: {result['target_ip']}")
    else:
        print(f"\n💥 页面上未找到目标IP地址: {result['target_ip']}")
        print("   说明: 这可能意味着您当前的网络环境不显示该IP地址")


if __name__ == "__main__":
    main()

