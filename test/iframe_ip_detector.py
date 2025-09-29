#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
iframe IP地址检测工具

此工具专门用于检测ip138.com网站中iframe内显示的IP地址信息。
根据分析，IP地址信息实际显示在 //2025.ip138.com/ 这个iframe中。

注意：此工具会专门检查iframe内容以获取准确的IP地址信息。
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


def detect_ip_in_iframe():
    """
    检测iframe中的IP地址信息

    Returns:
        dict: 包含检测结果的字典
    """
    driver = None
    target_ip = "223.102.68.134"
    result = {
        'target_ip': target_ip,
        'found_ip': None,
        'found_location': None,
        'iframe_content': None,
        'logs': [],
        'success': False,
        'error': None
    }

    try:
        print("🚀 启动iframe IP地址检测")
        print("="*50)

        # 初始化WebDriver - 使用有头模式以更好地模拟浏览器
        driver = setup_chrome_driver(headless=False)

        # 直接访问主页面
        target_url = "https://www.ip138.com/"
        print(f"📍 访问主页面: {target_url}")
        result['logs'].append(f"访问主页面: {target_url}")
        driver.get(target_url)

        # 等待页面加载
        print("⏳ 等待主页面加载...")
        result['logs'].append("等待主页面加载...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # 给页面更多时间完全加载，特别是JavaScript执行
        print("⏳ 等待JavaScript执行完成...")
        result['logs'].append("等待JavaScript执行完成...")
        time.sleep(10)

        # 查找iframe
        print("🔍 查找iframe...")
        result['logs'].append("查找iframe...")

        # 查找所有iframe
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"🔍 找到 {len(iframes)} 个iframe")
        result['logs'].append(f"找到 {len(iframes)} 个iframe")

        # 遍历所有iframe查找IP信息
        for i, iframe in enumerate(iframes):
            try:
                print(f"🔍 检查第 {i+1} 个iframe...")
                result['logs'].append(f"检查第 {i+1} 个iframe...")

                # 获取iframe的src属性
                iframe_src = iframe.get_attribute("src")
                print(f"   iframe src: {iframe_src}")
                result['logs'].append(f"iframe {i+1} src: {iframe_src}")

                # 切换到iframe
                driver.switch_to.frame(iframe)

                # 等待iframe内容加载
                time.sleep(5)

                # 获取iframe内容
                try:
                    iframe_body = driver.find_element(By.TAG_NAME, "body")
                    iframe_text = iframe_body.text
                    print(f"   iframe文本长度: {len(iframe_text)} 字符")
                    result['logs'].append(f"iframe {i+1} 文本长度: {len(iframe_text)} 字符")

                    # 保存iframe内容用于分析
                    if not result['iframe_content']:
                        result['iframe_content'] = iframe_text[:2000]  # 保存前2000字符

                    # 查找"您的iP地址是："模式
                    target_patterns = [
                        r'您的iP地址是[：:]\s*\[?([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\]?',
                        r'您的IP地址是[：:]\s*\[?([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\]?',
                        r'当前IP[：:]\s*\[?([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\]?',
                        r'本机IP[：:]\s*\[?([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\]?'
                    ]

                    found_ip = None
                    for pattern in target_patterns:
                        match = re.search(pattern, iframe_text)
                        if match:
                            found_ip = match.group(1)
                            result['found_ip'] = found_ip
                            result['found_location'] = f"iframe {i+1}, 匹配模式: {pattern}"
                            print(f"✅ 在iframe {i+1} 中找到IP地址: {found_ip}")
                            result['logs'].append(f"在iframe {i+1} 中找到IP地址: {found_ip}")
                            break

                    # 如果找到了目标格式，检查是否匹配目标IP
                    if found_ip:
                        if found_ip == target_ip:
                            print(f"🎯 找到目标IP地址: {target_ip}")
                            result['logs'].append(f"找到目标IP地址: {target_ip}")
                        else:
                            print(f"ℹ️ 找到IP地址 {found_ip}，但不是目标IP {target_ip}")
                            result['logs'].append(f"找到IP地址 {found_ip}，但不是目标IP {target_ip}")

                        # 找到IP后退出循环
                        break

                except Exception as e:
                    error_msg = f"⚠️ 获取iframe {i+1} 内容时出错: {e}"
                    print(error_msg)
                    result['logs'].append(error_msg)

                # 切换回主内容
                driver.switch_to.default_content()

            except Exception as e:
                error_msg = f"⚠️ 检查iframe {i+1} 时出错: {e}"
                print(error_msg)
                result['logs'].append(error_msg)
                # 切换回主内容
                try:
                    driver.switch_to.default_content()
                except:
                    pass

        # 如果还没找到，直接访问iframe的URL
        if not result['found_ip']:
            print("🔍 尝试直接访问iframe URL...")
            result['logs'].append("尝试直接访问iframe URL...")

            try:
                iframe_url = "https://2025.ip138.com/"
                print(f"📍 访问iframe URL: {iframe_url}")
                result['logs'].append(f"访问iframe URL: {iframe_url}")
                driver.get(iframe_url)

                # 等待页面加载
                print("⏳ 等待iframe页面加载...")
                result['logs'].append("等待iframe页面加载...")
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                # 给页面更多时间完全加载
                time.sleep(5)

                # 获取页面内容
                iframe_body = driver.find_element(By.TAG_NAME, "body")
                iframe_text = iframe_body.text
                print(f"   iframe页面文本长度: {len(iframe_text)} 字符")
                result['logs'].append(f"iframe页面文本长度: {len(iframe_text)} 字符")

                # 保存内容用于分析
                result['iframe_content'] = iframe_text[:2000]

                # 查找IP地址
                target_patterns = [
                    r'您的iP地址是[：:]\s*\[?([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\]?',
                    r'您的IP地址是[：:]\s*\[?([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\]?',
                    r'当前IP[：:]\s*\[?([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\]?',
                    r'本机IP[：:]\s*\[?([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\]?'
                ]

                for pattern in target_patterns:
                    match = re.search(pattern, iframe_text)
                    if match:
                        found_ip = match.group(1)
                        result['found_ip'] = found_ip
                        result['found_location'] = f"直接访问iframe URL, 匹配模式: {pattern}"
                        print(f"✅ 在iframe URL中找到IP地址: {found_ip}")
                        result['logs'].append(f"在iframe URL中找到IP地址: {found_ip}")

                        # 检查是否匹配目标IP
                        if found_ip == target_ip:
                            print(f"🎯 找到目标IP地址: {target_ip}")
                            result['logs'].append(f"找到目标IP地址: {target_ip}")
                        else:
                            print(f"ℹ️ 找到IP地址 {found_ip}，但不是目标IP {target_ip}")
                            result['logs'].append(f"找到IP地址 {found_ip}，但不是目标IP {target_ip}")
                        break

            except Exception as e:
                error_msg = f"⚠️ 访问iframe URL时出错: {e}"
                print(error_msg)
                result['logs'].append(error_msg)

        result['success'] = True
        print("✅ iframe IP检测完成!")

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
        result (dict): detect_ip_in_iframe函数返回的结果
    """
    print("\n" + "="*60)
    print("📈 iframe IP地址检测结果")
    print("="*60)

    if not result['success']:
        print(f"❌ 检测失败: {result['error']}")
        return

    target_ip = result['target_ip']
    if result['found_ip']:
        print(f"\n🎯 检测到的IP地址: {result['found_ip']}")
        print(f"   📍 位置: {result['found_location']}")

        if result['found_ip'] == target_ip:
            print(f"   ✅ 匹配目标IP地址: {target_ip}")
        else:
            print(f"   ℹ️  不匹配目标IP地址: {target_ip}")
    else:
        print(f"\n❌ 未检测到任何IP地址")
        print(f"   目标IP地址: {target_ip}")


def save_results_to_file(result):
    """
    将结果保存到JSON文件

    Args:
        result (dict): 检测结果
    """
    try:
        filename = f"iframe_ip_detection_result_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 结果已保存到文件: {filename}")
    except Exception as e:
        print(f"⚠️ 保存结果到文件时出错: {e}")


def main():
    """
    主函数 - 执行iframe IP地址检测
    """
    print("🔍 iframe IP地址检测工具")
    print("此工具专门检测ip138.com网站中iframe内显示的IP地址信息")
    print()

    # 执行检测
    result = detect_ip_in_iframe()

    # 打印详细结果
    print_detailed_results(result)

    # 保存结果到文件
    save_results_to_file(result)

    print("\n" + "="*60)
    print("💡 说明")
    print("="*60)
    print("1. 此工具检测iframe中显示的IP地址信息")
    print("2. IP地址信息实际显示在 //2025.ip138.com/ 这个iframe中")
    print("3. 如果未找到，可能是因为:")
    print("   - 网络环境已变化")
    print("   - iframe内容已更新")

    if result['success'] and result['found_ip']:
        if result['found_ip'] == result['target_ip']:
            print(f"\n🎉 成功找到目标IP地址: {result['target_ip']}")
        else:
            print(f"\n✅ 找到IP地址: {result['found_ip']} (但不是目标IP {result['target_ip']})")
    else:
        print(f"\n💥 未找到任何IP地址")


if __name__ == "__main__":
    main()

