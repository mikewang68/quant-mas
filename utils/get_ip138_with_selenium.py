#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用Selenium访问ip138.com获取IP地址

此工具使用Selenium WebDriver访问https://www.ip138.com/网站，
获取该网站显示的IP地址信息。与Firecrawl不同，这种方法可以
完全模拟浏览器行为，获取完整的页面内容。
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


def get_ip_from_ip138_with_selenium():
    """
    使用Selenium访问ip138.com获取IP地址

    Returns:
        dict: 包含检测结果的字典
    """
    driver = None
    result = {
        'ips': [],
        'page_title': None,
        'page_content': None,
        'logs': [],
        'success': False,
        'error': None
    }

    try:
        print("🚀 启动ip138.com IP地址检测")
        print("="*50)

        # 初始化WebDriver
        driver = setup_chrome_driver(headless=True)

        # 访问ip138.com网站
        target_url = "https://www.ip138.com/"
        print(f"📍 访问网站: {target_url}")
        result['logs'].append(f"访问网站: {target_url}")

        driver.get(target_url)

        # 等待页面加载
        print("⏳ 等待页面加载...")
        result['logs'].append("等待页面加载...")

        # 等待页面标题出现
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "title"))
        )

        # 获取页面标题
        result['page_title'] = driver.title
        print(f"📄 页面标题: {result['page_title']}")
        result['logs'].append(f"页面标题: {result['page_title']}")

        # 等待一段时间确保页面完全加载
        time.sleep(3)

        # 获取页面源码
        page_source = driver.page_source
        result['page_content'] = page_source
        print("📄 页面加载完成，分析内容...")
        result['logs'].append("页面加载完成，分析内容...")

        # 在页面内容中查找IPv4地址
        ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ipv4_addresses = re.findall(ipv4_pattern, page_source)

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
            result['ips'] = unique_ips
            print(f"✅ 找到的IPv4地址:")
            result['logs'].append(f"找到的IPv4地址: {unique_ips}")
            for ip in unique_ips:
                print(f"   🌐 {ip}")
        else:
            print("⚠️ 未找到有效的IPv4地址")
            result['logs'].append("未找到有效的IPv4地址")
            # 显示部分内容以便分析
            content_preview = page_source[:1000]
            print(f"📄 页面内容预览: {content_preview}")
            result['logs'].append(f"页面内容预览: {content_preview[:500]}")

        result['success'] = True
        print("✅ IP地址检测完成!")

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


def get_ip_from_ip138_iframe_with_selenium():
    """
    使用Selenium访问ip138.com的iframe页面获取IP地址

    Returns:
        dict: 包含检测结果的字典
    """
    driver = None
    result = {
        'ips': [],
        'page_title': None,
        'page_content': None,
        'logs': [],
        'success': False,
        'error': None
    }

    try:
        print("\n🚀 启动ip138.com iframe IP地址检测")
        print("="*50)

        # 初始化WebDriver
        driver = setup_chrome_driver(headless=True)

        # 访问ip138.com的iframe页面
        target_url = "https://2025.ip138.com/"
        print(f"📍 访问iframe页面: {target_url}")
        result['logs'].append(f"访问iframe页面: {target_url}")

        driver.get(target_url)

        # 等待页面加载
        print("⏳ 等待页面加载...")
        result['logs'].append("等待页面加载...")

        # 等待页面标题出现
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "title"))
        )

        # 获取页面标题
        result['page_title'] = driver.title
        print(f"📄 页面标题: {result['page_title']}")
        result['logs'].append(f"页面标题: {result['page_title']}")

        # 等待一段时间确保页面完全加载
        time.sleep(3)

        # 获取页面源码
        page_source = driver.page_source
        result['page_content'] = page_source
        print("📄 页面加载完成，分析内容...")
        result['logs'].append("页面加载完成，分析内容...")

        # 在页面内容中查找IPv4地址
        ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ipv4_addresses = re.findall(ipv4_pattern, page_source)

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
            result['ips'] = unique_ips
            print(f"✅ 找到的IPv4地址:")
            result['logs'].append(f"找到的IPv4地址: {unique_ips}")
            for ip in unique_ips:
                print(f"   🌐 {ip}")
        else:
            print("⚠️ 未找到有效的IPv4地址")
            result['logs'].append("未找到有效的IPv4地址")
            # 显示部分内容以便分析
            content_preview = page_source[:1000]
            print(f"📄 页面内容预览: {content_preview}")
            result['logs'].append(f"页面内容预览: {content_preview[:500]}")

        result['success'] = True
        print("✅ IP地址检测完成!")

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


def print_detailed_results(result, method_name):
    """
    打印详细结果

    Args:
        result (dict): 检测函数返回的结果
        method_name (str): 方法名称
    """
    print(f"\n" + "="*60)
    print(f"📈 {method_name} 检测结果详情")
    print("="*60)

    if not result['success']:
        print(f"❌ 检测失败: {result['error']}")
        return

    if result['ips']:
        print(f"\n🌐 检测到的IPv4地址 ({len(result['ips'])} 个):")
        for ip in sorted(result['ips']):
            print(f"   🌐 {ip}")
    else:
        print("\n🌐 IPv4地址: 未检测到")

    print(f"\n📊 统计信息:")
    print(f"   检测到的IP地址: {len(result['ips'])}")
    if result['page_title']:
        print(f"   页面标题: {result['page_title']}")


def save_results_to_file(result, method_name):
    """
    将结果保存到JSON文件

    Args:
        result (dict): 检测结果
        method_name (str): 方法名称
    """
    try:
        # 清理结果中的大内容
        clean_result = result.copy()
        if 'page_content' in clean_result:
            # 只保留前2000个字符
            clean_result['page_content'] = clean_result['page_content'][:2000] + "...(内容已截断)"

        filename = f"ip138_selenium_{method_name}_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(clean_result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 结果已保存到文件: {filename}")
    except Exception as e:
        print(f"⚠️ 保存结果到文件时出错: {e}")


def main():
    """
    主函数
    """
    print("🔍 使用Selenium访问ip138.com获取IP地址")
    print("此工具使用Selenium WebDriver完全模拟浏览器行为访问ip138.com")
    print()

    # 方法1: 访问主页面
    print("方法1: 访问ip138.com主页面")
    result1 = get_ip_from_ip138_with_selenium()

    # 方法2: 访问iframe页面
    print("\n" + "="*50 + "\n")
    print("方法2: 访问ip138.com iframe页面")
    result2 = get_ip_from_ip138_iframe_with_selenium()

    # 打印详细结果
    print_detailed_results(result1, "主页面访问")
    print_detailed_results(result2, "iframe页面访问")

    # 保存结果到文件
    save_results_to_file(result1, "main_page")
    save_results_to_file(result2, "iframe_page")

    # 合并结果
    all_ips = []
    if result1['ips']:
        all_ips.extend(result1['ips'])
    if result2['ips']:
        all_ips.extend(result2['ips'])
    all_ips = sorted(list(set(all_ips)))  # 去重并排序

    print("\n" + "="*60)
    print("📊 最终结果")
    print("="*60)

    if all_ips:
        print("✅ 检测到的IPv4地址:")
        for ip in all_ips:
            print(f"   🌐 {ip}")
    else:
        print("❌ 未能获取到IP地址")

    print("\n💡 说明:")
    print("1. 这些IP地址是通过Selenium模拟浏览器访问ip138.com获取的")
    print("2. 与Firecrawl相比，Selenium可以完全模拟浏览器行为")
    print("3. 获取到的是Selenium运行环境的公网IP地址")
    print("4. 与您本地访问该网站看到的IP地址可能不同")


if __name__ == "__main__":
    main()

