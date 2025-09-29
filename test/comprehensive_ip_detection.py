#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
综合性IP地址检测工具

此工具使用多种方法尝试获取当前网络环境的公网IP地址：
1. 直接访问ip138.com并分析页面内容
2. 尝试查找iframe中的内容
3. 使用备用的IP查询网站
4. 使用API接口直接获取IP

注意：获取到的IP地址是您设备的真实公网IP地址。
"""

import time
import re
import json
import requests
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


def detect_ip_method1_ip138():
    """
    方法1: 直接访问ip138.com并分析页面内容

    Returns:
        dict: 检测结果
    """
    result = {
        'ip_address': None,
        'location': None,
        'all_ips': [],
        'logs': [],
        'method': 'ip138_direct'
    }

    driver = None
    try:
        print("🔍 方法1: 直接访问ip138.com")
        result['logs'].append("方法1: 直接访问ip138.com")

        # 初始化WebDriver
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
        time.sleep(10)

        # 获取页面源码
        page_source = driver.page_source
        print("📄 页面加载完成，分析内容...")
        result['logs'].append("页面加载完成，分析内容...")

        # 查找IP地址 - 多种方法
        try:
            # 获取页面所有文本
            body_text = driver.find_element(By.TAG_NAME, "body").text
            page_html = driver.page_source

            # 合并文本内容以增加检测机会
            combined_text = body_text + " " + page_html
            result['logs'].append(f"合并文本长度: {len(combined_text)} 字符")

            # 查找各种可能的IP显示模式
            patterns = [
                r'您的iP地址是[：:]\s*([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})',
                r'您的IP地址是[：:]\s*([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})',
                r'[Ii][Pp]地址是[：:]\s*([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})',
                r'当前IP[：:]\s*([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})',
                r'本机IP[：:]\s*([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})'
            ]

            for i, pattern in enumerate(patterns, 1):
                match = re.search(pattern, combined_text)
                if match:
                    ip_address = match.group(1)
                    print(f"✅ 找到IP地址 (模式{i}): {ip_address}")
                    result['logs'].append(f"找到IP地址 (模式{i}): {ip_address}")
                    if is_valid_public_ip(ip_address):
                        result['ip_address'] = ip_address
                        result['all_ips'].append(ip_address)
                        break

            # 如果特定模式没找到，尝试查找所有IP地址并验证
            if not result['ip_address']:
                print("🔍 尝试查找所有IP地址...")
                result['logs'].append("尝试查找所有IP地址...")

                # IP地址正则表达式
                ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
                ips = re.findall(ip_pattern, combined_text)
                result['logs'].append(f"在文本中找到所有IP: {ips}")

                # 验证和过滤IP地址
                valid_ips = []
                for ip in ips:
                    if is_valid_public_ip(ip):
                        valid_ips.append(ip)

                # 去重
                valid_ips = sorted(list(set(valid_ips)))
                result['all_ips'] = valid_ips

                if valid_ips:
                    print(f"✅ 找到有效的公网IP地址: {valid_ips}")
                    result['logs'].append(f"找到有效的公网IP地址: {valid_ips}")
                    result['ip_address'] = valid_ips[0]
                    print(f"✅ 使用第一个有效IP: {result['ip_address']}")
                    result['logs'].append(f"使用第一个有效IP: {result['ip_address']}")

        except Exception as e:
            error_msg = f"⚠️ 查找IP地址时出错: {e}"
            print(error_msg)
            result['logs'].append(error_msg)

        # 获取位置信息
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            location_patterns = [
                r'来自[:：]?\s*([^:\n\r]+?)[\s\(]*移动',
                r'来自[:：]?\s*([^:\n\r]+?)\s*移动',
                r'来自[:：]?\s*(.+?)\s*',
                r'所在地区[:：]\s*(.+?)\s',
                r'位置[:：]\s*(.+?)\s',
                r'归属地[:：]\s*(.+?)\s'
            ]

            for pattern in location_patterns:
                match = re.search(pattern, body_text)
                if match:
                    result['location'] = match.group(1).strip()
                    print(f"📍 检测到位置信息: {result['location']}")
                    result['logs'].append(f"检测到位置信息: {result['location']}")
                    break
        except Exception as e:
            error_msg = f"⚠️ 获取位置信息时出错: {e}"
            print(error_msg)
            result['logs'].append(error_msg)

    except Exception as e:
        error_msg = f"❌ 检测过程中发生错误: {str(e)}"
        print(error_msg)
        result['logs'].append(error_msg)
        import traceback
        traceback.print_exc()

    finally:
        if driver:
            print("🔚 关闭浏览器...")
            result['logs'].append("关闭浏览器...")
            driver.quit()

    return result


def detect_ip_method2_iframe():
    """
    方法2: 检查iframe内容

    Returns:
        dict: 检测结果
    """
    result = {
        'ip_address': None,
        'location': None,
        'all_ips': [],
        'logs': [],
        'method': 'ip138_iframe'
    }

    driver = None
    try:
        print("🔍 方法2: 检查iframe内容")
        result['logs'].append("方法2: 检查iframe内容")

        # 初始化WebDriver
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
        time.sleep(10)

        # 查找所有iframe
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"🔍 找到 {len(iframes)} 个iframe")
        result['logs'].append(f"找到 {len(iframes)} 个iframe")

        # 遍历所有iframe
        for i, iframe in enumerate(iframes):
            try:
                print(f"🔍 检查第 {i+1} 个iframe...")
                result['logs'].append(f"检查第 {i+1} 个iframe...")

                # 切换到iframe
                driver.switch_to.frame(iframe)

                # 获取iframe内容
                body_text = driver.find_element(By.TAG_NAME, "body").text
                page_html = driver.page_source

                # 合并文本内容
                combined_text = body_text + " " + page_html
                result['logs'].append(f"iframe {i+1} 文本长度: {len(combined_text)} 字符")

                # 查找IP地址
                ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
                ips = re.findall(ip_pattern, combined_text)
                result['logs'].append(f"在iframe {i+1} 中找到IP: {ips}")

                # 验证IP地址
                valid_ips = [ip for ip in ips if is_valid_public_ip(ip)]
                if valid_ips:
                    result['all_ips'].extend(valid_ips)
                    result['ip_address'] = valid_ips[0]
                    print(f"✅ 在iframe {i+1} 中找到IP地址: {valid_ips[0]}")
                    result['logs'].append(f"在iframe {i+1} 中找到IP地址: {valid_ips[0]}")
                    break

                # 切换回主内容
                driver.switch_to.default_content()

            except Exception as e:
                error_msg = f"⚠️ 检查iframe {i+1} 时出错: {e}"
                print(error_msg)
                result['logs'].append(error_msg)
                # 切换回主内容
                driver.switch_to.default_content()

    except Exception as e:
        error_msg = f"❌ 检测过程中发生错误: {str(e)}"
        print(error_msg)
        result['logs'].append(error_msg)
        import traceback
        traceback.print_exc()

    finally:
        if driver:
            print("🔚 关闭浏览器...")
            result['logs'].append("关闭浏览器...")
            driver.quit()

    return result


def detect_ip_method3_alternative_sites():
    """
    方法3: 使用备用的IP查询网站

    Returns:
        dict: 检测结果
    """
    result = {
        'ip_address': None,
        'location': None,
        'all_ips': [],
        'logs': [],
        'method': 'alternative_sites'
    }

    sites = [
        "https://ip.cn",
        "https://ip.tool.chinaz.com/",
        "https://www.whatismyip.com/",
        "https://ipinfo.io/"
    ]

    driver = None
    try:
        print("🔍 方法3: 使用备用的IP查询网站")
        result['logs'].append("方法3: 使用备用的IP查询网站")

        # 初始化WebDriver
        driver = setup_chrome_driver(headless=False)

        # 遍历所有备用网站
        for site in sites:
            try:
                print(f"📍 访问网站: {site}")
                result['logs'].append(f"访问网站: {site}")
                driver.get(site)

                # 等待页面加载
                print("⏳ 等待页面加载...")
                result['logs'].append("等待页面加载...")
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                # 给页面更多时间完全加载
                print("⏳ 等待JavaScript执行完成...")
                result['logs'].append("等待JavaScript执行完成...")
                time.sleep(8)

                # 获取页面内容
                body_text = driver.find_element(By.TAG_NAME, "body").text
                page_html = driver.page_source

                # 合并文本内容
                combined_text = body_text + " " + page_html
                result['logs'].append(f"网站 {site} 文本长度: {len(combined_text)} 字符")

                # 查找IP地址
                ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
                ips = re.findall(ip_pattern, combined_text)
                result['logs'].append(f"在网站 {site} 中找到IP: {ips}")

                # 验证IP地址
                valid_ips = [ip for ip in ips if is_valid_public_ip(ip)]
                if valid_ips:
                    result['all_ips'].extend(valid_ips)
                    result['ip_address'] = valid_ips[0]
                    print(f"✅ 在网站 {site} 中找到IP地址: {valid_ips[0]}")
                    result['logs'].append(f"在网站 {site} 中找到IP地址: {valid_ips[0]}")
                    break

            except Exception as e:
                error_msg = f"⚠️ 访问网站 {site} 时出错: {e}"
                print(error_msg)
                result['logs'].append(error_msg)

    except Exception as e:
        error_msg = f"❌ 检测过程中发生错误: {str(e)}"
        print(error_msg)
        result['logs'].append(error_msg)
        import traceback
        traceback.print_exc()

    finally:
        if driver:
            print("🔚 关闭浏览器...")
            result['logs'].append("关闭浏览器...")
            driver.quit()

    return result


def detect_ip_method4_api():
    """
    方法4: 使用API直接获取IP

    Returns:
        dict: 检测结果
    """
    result = {
        'ip_address': None,
        'location': None,
        'all_ips': [],
        'logs': [],
        'method': 'api_direct'
    }

    apis = [
        "https://api.ipify.org",
        "https://icanhazip.com",
        "https://ident.me",
        "https://ipecho.net/plain",
        "https://myexternalip.com/raw"
    ]

    try:
        print("🔍 方法4: 使用API直接获取IP")
        result['logs'].append("方法4: 使用API直接获取IP")

        # 遍历所有API
        for api in apis:
            try:
                print(f"📍 请求API: {api}")
                result['logs'].append(f"请求API: {api}")

                # 发送请求
                response = requests.get(api, timeout=10)
                if response.status_code == 200:
                    ip_address = response.text.strip()
                    print(f"✅ API {api} 返回IP: {ip_address}")
                    result['logs'].append(f"API {api} 返回IP: {ip_address}")

                    # 验证IP地址
                    if is_valid_public_ip(ip_address):
                        result['ip_address'] = ip_address
                        result['all_ips'].append(ip_address)
                        print(f"✅ 验证通过，使用IP: {ip_address}")
                        result['logs'].append(f"验证通过，使用IP: {ip_address}")
                        break
                    else:
                        print(f"⚠️ IP地址无效: {ip_address}")
                        result['logs'].append(f"IP地址无效: {ip_address}")
                else:
                    print(f"⚠️ API {api} 返回状态码: {response.status_code}")
                    result['logs'].append(f"API {api} 返回状态码: {response.status_code}")

            except Exception as e:
                error_msg = f"⚠️ 请求API {api} 时出错: {e}"
                print(error_msg)
                result['logs'].append(error_msg)

    except Exception as e:
        error_msg = f"❌ 检测过程中发生错误: {str(e)}"
        print(error_msg)
        result['logs'].append(error_msg)
        import traceback
        traceback.print_exc()

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
            # 排除一些常见的测试IP
            if ip.startswith('198.18.'):
                return False
            return True
        return False
    except:
        return False


def print_detailed_results(results):
    """
    打印详细结果

    Args:
        results (list): 所有检测方法的结果列表
    """
    print("\n" + "="*60)
    print("📈 综合检测结果详情")
    print("="*60)

    success_count = 0
    for result in results:
        if result['ip_address']:
            success_count += 1
            print(f"\n✅ 方法 '{result['method']}' 检测成功:")
            print(f"   🌍 IP地址: {result['ip_address']}")
            if result['location']:
                print(f"   📍 位置: {result['location']}")
        else:
            print(f"\n❌ 方法 '{result['method']}' 检测失败")

    if success_count > 0:
        print(f"\n🎉 总共 {success_count} 个方法检测成功")
    else:
        print(f"\n💥 所有方法都未能检测到IP地址")


def save_results_to_file(results):
    """
    将结果保存到JSON文件

    Args:
        results (list): 所有检测方法的结果列表
    """
    try:
        # 合并所有结果
        combined_result = {
            'timestamp': int(time.time()),
            'results': results
        }

        filename = f"comprehensive_ip_detection_result_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(combined_result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 结果已保存到文件: {filename}")
    except Exception as e:
        print(f"⚠️ 保存结果到文件时出错: {e}")


def main():
    """
    主函数 - 执行综合性IP地址检测
    """
    print("🔍 综合性IP地址检测工具")
    print("此工具使用多种方法尝试获取您的公网IP地址")
    print()

    # 执行所有检测方法
    results = []

    # 方法1: 直接访问ip138.com
    result1 = detect_ip_method1_ip138()
    results.append(result1)

    # 如果方法1失败，尝试方法2
    if not result1['ip_address']:
        result2 = detect_ip_method2_iframe()
        results.append(result2)

    # 如果前两种方法都失败，尝试方法3
    if not any(r['ip_address'] for r in results):
        result3 = detect_ip_method3_alternative_sites()
        results.append(result3)

    # 如果前三種方法都失败，尝试方法4 (API)
    if not any(r['ip_address'] for r in results):
        result4 = detect_ip_method4_api()
        results.append(result4)

    # 打印详细结果
    print_detailed_results(results)

    # 保存结果到文件
    save_results_to_file(results)

    # 显示最终结果
    print("\n" + "="*60)
    print("💡 最终结果")
    print("="*60)

    # 查找第一个成功的检测结果
    successful_result = None
    for result in results:
        if result['ip_address']:
            successful_result = result
            break

    if successful_result:
        print(f"🎉 成功检测到公网IP地址: {successful_result['ip_address']}")
        if successful_result['location']:
            print(f"📍 位置信息: {successful_result['location']}")
    else:
        print("💥 所有检测方法都失败了，未能获取到公网IP地址")

    print("\n💡 说明:")
    print("1. 这些IP地址是您设备的真实公网IP地址")
    print("2. 不同方法可能返回不同的IP地址（如使用了代理或CDN）")
    print("3. 如果所有方法都失败，请检查网络连接或防火墙设置")


if __name__ == "__main__":
    main()

