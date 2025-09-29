#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
特定位置IP地址检测工具

此工具使用Selenium WebDriver访问ip138.com网站获取当前网络环境的公网IP地址。
专门针对"iP地址归属地查询"下面一行进行检测。

注意：获取到的IP地址是您设备的真实公网IP地址。
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


def get_isp_ip_from_ip138():
    """
    通过ip138.com网站获取ISP分配的公网IP地址

    Returns:
        dict: 包含检测结果的字典
    """
    driver = None
    result = {
        'ip_address': None,
        'location': None,
        'target_ip': '223.102.68.134',  # 您提到的目标IP
        'all_ips': [],
        'logs': [],
        'success': False,
        'error': None
    }

    try:
        print("🚀 启动特定位置IP地址检测")
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
        time.sleep(10)

        # 获取页面源码
        page_source = driver.page_source
        print("📄 页面加载完成，分析内容...")
        result['logs'].append("页面加载完成，分析内容...")

        # 查找IP地址 - 针对性方法
        try:
            # 获取页面所有文本
            body_text = driver.find_element(By.TAG_NAME, "body").text
            page_html = driver.page_source

            # 合并文本内容以增加检测机会
            combined_text = body_text + " " + page_html
            result['logs'].append(f"合并文本长度: {len(combined_text)} 字符")

            # 查找"iP地址归属地查询"下面一行的IP地址
            print("🔍 查找'iP地址归属地查询'下面一行的IP地址...")
            result['logs'].append("查找'iP地址归属地查询'下面一行的IP地址...")

            # 将文本按行分割
            lines = combined_text.split('\n')
            result['logs'].append(f"文本总行数: {len(lines)}")

            # 查找"iP地址归属地查询"所在的行
            target_line_index = -1
            for i, line in enumerate(lines):
                if "iP地址归属地查询" in line:
                    target_line_index = i
                    print(f"✅ 找到'iP地址归属地查询'在第 {i+1} 行: {line.strip()}")
                    result['logs'].append(f"找到'iP地址归属地查询'在第 {i+1} 行: {line.strip()}")
                    break

            # 如果找到了目标行，检查下一行是否有IP地址
            if target_line_index != -1 and target_line_index + 1 < len(lines):
                next_line = lines[target_line_index + 1].strip()
                print(f"🔍 下一行内容: {next_line}")
                result['logs'].append(f"下一行内容: {next_line}")

                # 在下一行中查找IP地址
                ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
                ips = re.findall(ip_pattern, next_line)

                if ips:
                    # 验证IP地址
                    valid_ips = [ip for ip in ips if is_valid_public_ip(ip)]
                    if valid_ips:
                        result['ip_address'] = valid_ips[0]
                        result['all_ips'] = valid_ips
                        print(f"✅ 成功检测到IP地址: {result['ip_address']}")
                        result['logs'].append(f"成功检测到IP地址: {result['ip_address']}")
                    else:
                        print("⚠️ 找到IP格式但不是有效公网IP")
                        result['logs'].append(f"找到IP格式但不是有效公网IP: {ips}")
                else:
                    print("⚠️ 下一行未找到IP地址")
                    result['logs'].append("下一行未找到IP地址")

                    # 尝试在下一行附近查找IP地址
                    search_range = 3  # 在目标行的前后3行内查找
                    for i in range(max(0, target_line_index - search_range),
                                   min(len(lines), target_line_index + search_range + 1)):
                        if i != target_line_index:  # 跳过目标行本身
                            line_content = lines[i].strip()
                            ips = re.findall(ip_pattern, line_content)
                            if ips:
                                valid_ips = [ip for ip in ips if is_valid_public_ip(ip)]
                                if valid_ips:
                                    result['ip_address'] = valid_ips[0]
                                    result['all_ips'] = valid_ips
                                    print(f"✅ 在附近行找到IP地址: {result['ip_address']} (第 {i+1} 行)")
                                    result['logs'].append(f"在附近行找到IP地址: {result['ip_address']} (第 {i+1} 行)")
                                    break

            # 如果还没找到，尝试查找所有IP地址并验证
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

                    # 优先查找您提到的目标IP
                    target_ip = '223.102.68.134'
                    if target_ip in valid_ips:
                        result['ip_address'] = target_ip
                        print(f"🎯 成功检测到目标IP地址: {target_ip}")
                        result['logs'].append(f"成功检测到目标IP地址: {target_ip}")
                    else:
                        # 否则使用第一个有效的公网IP
                        result['ip_address'] = valid_ips[0]
                        print(f"✅ 成功获取到IP地址: {result['ip_address']}")
                        result['logs'].append(f"使用第一个有效IP: {result['ip_address']}")

            # 如果仍然没有找到，显示部分页面内容用于调试
            if not result['ip_address']:
                print("⚠️ 未找到有效的公网IP地址")
                result['logs'].append("未找到有效的公网IP地址")

                # 显示页面前几行用于调试
                debug_lines = lines[:50]  # 只显示前50行
                result['logs'].append(f"页面前50行内容: {debug_lines}")
                print("📄 页面前50行内容:")
                for i, line in enumerate(debug_lines[:20]):  # 只打印前20行
                    print(f"  {i+1:2d}: {line}")

        except Exception as e:
            error_msg = f"⚠️ 查找IP地址时出错: {e}"
            print(error_msg)
            result['logs'].append(error_msg)

        # 获取位置信息
        try:
            # 尝试获取位置信息
            body_text = driver.find_element(By.TAG_NAME, "body").text
            # 查找可能的位置信息
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


def print_detailed_results(result):
    """
    打印详细结果

    Args:
        result (dict): get_isp_ip_from_ip138函数返回的结果
    """
    print("\n" + "="*60)
    print("📈 检测结果详情")
    print("="*60)

    if not result['success']:
        print(f"❌ 检测失败: {result['error']}")
        return

    # IP地址
    if result['ip_address']:
        print(f"\n🌐 检测到的公网IP地址:")
        print(f"   🌍 {result['ip_address']}")
    else:
        print(f"\n🌐 公网IP地址: 未检测到")

    # 所有找到的IP地址
    if result['all_ips']:
        print(f"\n📋 所有检测到的公网IP地址:")
        for ip in result['all_ips']:
            marker = " 🎯" if ip == result.get('target_ip') else ""
            print(f"   🌐 {ip}{marker}")

    # 位置信息
    if result['location']:
        print(f"\n📍 位置信息:")
        print(f"   📍 {result['location']}")
    else:
        print(f"\n📍 位置信息: 未检测到")

    # 特别检查目标IP
    target_ip = result.get('target_ip', '223.102.68.134')
    if result['ip_address'] == target_ip:
        print(f"\n✅ 成功检测到目标IP地址: {target_ip}")
    elif target_ip in result['all_ips']:
        print(f"\n✅ 目标IP地址 {target_ip} 已找到，但未被选为主要IP")
    else:
        print(f"\n❌ 未检测到目标IP地址: {target_ip}")
        print("   可能原因:")
        print("   1. 网络环境已变化")
        print("   2. 网站显示内容已更新")
        print("   3. 检测时机问题")


def save_results_to_file(result):
    """
    将结果保存到JSON文件

    Args:
        result (dict): 检测结果
    """
    try:
        filename = f"specific_location_ip_result_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 结果已保存到文件: {filename}")
    except Exception as e:
        print(f"⚠️ 保存结果到文件时出错: {e}")


def main():
    """
    主函数 - 执行ISP IP地址检测
    """
    print("🔍 特定位置IP地址检测工具")
    print("此工具专门检测ip138.com网站中'iP地址归属地查询'下面一行的IP地址")
    print()

    # 执行检测
    result = get_isp_ip_from_ip138()

    # 打印详细结果
    print_detailed_results(result)

    # 保存结果到文件
    save_results_to_file(result)

    print("\n" + "="*60)
    print("💡 说明")
    print("="*60)
    print("1. 这些IP地址是您设备的真实公网IP地址")
    print("2. 与Firecrawl等服务器端工具不同，这是真实的客户端IP")
    print("3. 位置信息基于IP地址的地理位置数据库")
    print("4. 如果未检测到目标IP，请检查网络环境是否已变化")

    if result['success'] and result['ip_address']:
        print(f"\n🎉 成功检测到公网IP地址: {result['ip_address']}")
        target_ip = result.get('target_ip', '223.102.68.134')
        if result['ip_address'] == target_ip:
            print(f"🎯 并且成功匹配到目标IP地址: {target_ip}")
    else:
        print(f"\n💥 IP地址检测失败")


if __name__ == "__main__":
    main()

