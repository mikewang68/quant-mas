#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
精确IP地址检测工具

此工具专门用于检测网页上"您的iP地址是："格式的文本，并提取其中的IP地址。

根据用户反馈，页面上显示格式为：
"您的iP地址是：[223.102.68.134 ]"
"来自：中国辽宁大连沙河口 移动"

注意：此工具会专门查找这种特定格式。
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


def detect_precise_ip_format():
    """
    精确检测"您的iP地址是："格式的IP地址

    Returns:
        dict: 包含检测结果的字典
    """
    driver = None
    target_ip = "223.102.68.134"
    result = {
        'target_ip': target_ip,
        'detected_ip': None,
        'location_info': None,
        'found_exact_format': False,
        'page_full_text': None,
        'logs': [],
        'success': False,
        'error': None
    }

    try:
        print(f"🚀 启动精确IP地址检测")
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

        # 保存完整页面文本
        result['page_full_text'] = combined_text

        # 查找"您的iP地址是："格式的文本
        print("🔍 查找'您的iP地址是：'格式...")
        result['logs'].append("查找'您的iP地址是：'格式...")

        # 特别针对用户描述的格式："您的iP地址是：[223.102.68.134 ]"
        exact_pattern = r'您的iP地址是：\s*\[([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\s*\]'
        exact_match = re.search(exact_pattern, combined_text)

        if exact_match:
            detected_ip = exact_match.group(1)
            result['detected_ip'] = detected_ip
            result['found_exact_format'] = True
            print(f"✅ 找到精确格式的IP地址: {detected_ip}")
            result['logs'].append(f"找到精确格式的IP地址: {detected_ip}")

            # 查找位置信息
            location_pattern = r'来自：([^\r\n]+)'
            location_match = re.search(location_pattern, combined_text)
            if location_match:
                location_info = location_match.group(1).strip()
                result['location_info'] = location_info
                print(f"📍 位置信息: {location_info}")
                result['logs'].append(f"位置信息: {location_info}")

            # 检查是否匹配目标IP
            if detected_ip == target_ip:
                print(f"🎯 检测到的目标IP地址匹配: {target_ip}")
                result['logs'].append(f"检测到的目标IP地址匹配: {target_ip}")
            else:
                print(f"⚠️ 检测到的IP地址与目标不匹配:")
                print(f"   检测到: {detected_ip}")
                print(f"   目标:   {target_ip}")
                result['logs'].append(f"检测到的IP地址与目标不匹配: 检测到{detected_ip}, 目标{target_ip}")
        else:
            print("❌ 未找到精确格式的IP地址")
            result['logs'].append("未找到精确格式的IP地址")

            # 尝试其他可能的格式
            alternative_patterns = [
                r'您的iP地址是[：:]\s*([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})',
                r'您的IP地址是[：:]\s*([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})',
                r'本机IP[：:]\s*([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})',
                r'当前IP[：:]\s*([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})'
            ]

            for i, pattern in enumerate(alternative_patterns, 1):
                match = re.search(pattern, combined_text)
                if match:
                    detected_ip = match.group(1)
                    result['detected_ip'] = detected_ip
                    print(f"✅ 找到替代格式的IP地址 (模式{i}): {detected_ip}")
                    result['logs'].append(f"找到替代格式的IP地址 (模式{i}): {detected_ip}")
                    break

            # 如果还没找到，查找所有IP地址
            if not result['detected_ip']:
                ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
                all_ips = re.findall(ip_pattern, combined_text)
                if all_ips:
                    print(f"🔍 页面上找到的所有IP地址: {all_ips}")
                    result['logs'].append(f"页面上找到的所有IP地址: {all_ips}")

        result['success'] = True
        print("✅ 精确IP检测完成!")

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
        result (dict): detect_precise_ip_format函数返回的结果
    """
    print("\n" + "="*60)
    print("📈 精确IP地址检测结果")
    print("="*60)

    if not result['success']:
        print(f"❌ 检测失败: {result['error']}")
        return

    if result['found_exact_format']:
        print(f"\n🎯 精确格式检测结果:")
        print(f"   ✅ 找到精确格式的IP地址: {result['detected_ip']}")
        if result['location_info']:
            print(f"   📍 位置信息: {result['location_info']}")

        # 检查是否匹配目标IP
        if result['detected_ip'] == result['target_ip']:
            print(f"   🎯 与目标IP匹配: {result['target_ip']}")
        else:
            print(f"   ⚠️  与目标IP不匹配:")
            print(f"      检测到: {result['detected_ip']}")
            print(f"      目标:   {result['target_ip']}")
    elif result['detected_ip']:
        print(f"\n🔍 替代格式检测结果:")
        print(f"   ✅ 找到IP地址: {result['detected_ip']}")
        if result['location_info']:
            print(f"   📍 位置信息: {result['location_info']}")
    else:
        print(f"\n❌ 未检测到IP地址")
        print(f"   目标IP: {result['target_ip']}")


def save_results_to_file(result):
    """
    将结果保存到JSON文件

    Args:
        result (dict): 检测结果
    """
    try:
        filename = f"precise_ip_detection_result_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 结果已保存到文件: {filename}")
    except Exception as e:
        print(f"⚠️ 保存结果到文件时出错: {e}")


def main():
    """
    主函数 - 执行精确IP地址检测
    """
    print("🔍 精确IP地址检测工具")
    print("此工具专门检测网页上'您的iP地址是：'格式的文本")
    print("根据用户反馈，页面显示格式为：")
    print("  '您的iP地址是：[223.102.68.134 ]'")
    print("  '来自：中国辽宁大连沙河口 移动'")
    print()

    # 执行检测
    result = detect_precise_ip_format()

    # 打印详细结果
    print_detailed_results(result)

    # 保存结果到文件
    save_results_to_file(result)

    print("\n" + "="*60)
    print("💡 说明")
    print("="*60)
    print("1. 此工具专门查找特定格式的IP地址显示")
    print("2. 如果未找到，可能是因为:")
    print("   - 网页结构发生变化")
    print("   - 网页内容动态加载")
    print("   - 网络环境不同导致显示内容不同")

    if result['success'] and result['detected_ip']:
        if result['detected_ip'] == result['target_ip']:
            print(f"\n🎉 成功检测到目标IP地址: {result['target_ip']}")
        else:
            print(f"\n⚠️  检测到IP地址: {result['detected_ip']}")
            print(f"   但与目标IP不匹配: {result['target_ip']}")
    else:
        print(f"\n💥 未能检测到目标格式的IP地址")


if __name__ == "__main__":
    main()

