#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug script for IP detection issues
"""

import time
import re
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
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # 禁用自动化控制特征
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # 自动下载和设置ChromeDriver
    service = Service(ChromeDriverManager().install())

    # 创建WebDriver实例
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 绕过WebDriver检测
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    return driver

def get_current_ip():
    """
    获取当前网络环境的公网IP地址

    Returns:
        str: 检测到的IP地址，如果未检测到则返回None
    """
    driver = None
    try:
        print("Initializing WebDriver...")
        # 初始化WebDriver
        driver = setup_chrome_driver(headless=True)
        print("WebDriver initialized successfully")

        # 访问主页面
        target_url = "https://www.ip138.com/"
        print(f"Visiting {target_url}...")
        driver.get(target_url)
        print("Page loaded")

        # 等待页面加载
        print("Waiting for page to load...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("Page loaded successfully")

        # 给页面更多时间完全加载，特别是JavaScript执行
        print("Waiting additional 8 seconds for JavaScript to execute...")
        time.sleep(8)

        # 查找所有iframe
        print("Finding iframes...")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Found {len(iframes)} iframes")

        # 遍历所有iframe查找IP信息
        for i, iframe in enumerate(iframes):
            try:
                print(f"Processing iframe {i}...")
                # 获取iframe的src属性
                iframe_src = iframe.get_attribute("src")
                print(f"Iframe {i} src: {iframe_src}")

                # 切换到iframe
                driver.switch_to.frame(iframe)
                print(f"Switched to iframe {i}")

                # 等待iframe内容加载
                print("Waiting 3 seconds for iframe content to load...")
                time.sleep(3)

                # 获取iframe内容
                try:
                    iframe_body = driver.find_element(By.TAG_NAME, "body")
                    iframe_text = iframe_body.text
                    print(f"Iframe {i} content: {iframe_text[:200]}...")  # 只显示前200个字符

                    # 查找IP地址模式
                    target_patterns = [
                        r"您的iP地址是[：:]\s*\[?([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\]?",
                        r"您的IP地址是[：:]\s*\[?([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\]?",
                        r"当前IP[：:]\s*\[?([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\]?",
                        r"本机IP[：:]\s*\[?([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\]?",
                    ]

                    for pattern in target_patterns:
                        match = re.search(pattern, iframe_text)
                        if match:
                            found_ip = match.group(1)
                            print(f"Found IP in iframe {i}: {found_ip}")
                            return found_ip

                except Exception as e:
                    print(f"Error getting iframe content: {e}")

                # 切换回主内容
                driver.switch_to.default_content()
                print(f"Switched back to main content from iframe {i}")

            except Exception as e:
                print(f"Error processing iframe {i}: {e}")
                # 切换回主内容
                try:
                    driver.switch_to.default_content()
                except:
                    pass

        # 如果还没找到，直接访问iframe的URL
        print("Trying direct access to iframe URL...")
        try:
            iframe_url = "https://2025.ip138.com/"
            print(f"Visiting {iframe_url}...")
            driver.get(iframe_url)

            # 等待页面加载
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # 给页面更多时间完全加载
            time.sleep(3)

            # 获取页面内容
            iframe_body = driver.find_element(By.TAG_NAME, "body")
            iframe_text = iframe_body.text
            print(f"Direct iframe page content: {iframe_text[:200]}...")  # 只显示前200个字符

            # 查找IP地址
            target_patterns = [
                r"您的iP地址是[：:]\s*\[?([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\]?",
                r"您的IP地址是[：:]\s*\[?([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\]?",
                r"当前IP[：:]\s*\[?([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\]?",
                r"本机IP[：:]\s*\[?([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\]?",
            ]

            for pattern in target_patterns:
                match = re.search(pattern, iframe_text)
                if match:
                    found_ip = match.group(1)
                    print(f"Found IP in direct iframe access: {found_ip}")
                    return found_ip

        except Exception as e:
            print(f"Error accessing iframe URL directly: {e}")

    except Exception as e:
        print(f"General error: {e}")

    finally:
        if driver:
            try:
                driver.quit()
                print("WebDriver closed")
            except:
                pass

    return None

def main():
    """
    主函数 - 获取并显示当前IP地址
    """
    print("🔍 ISP IP地址获取工具 - Debug版本")
    print("此工具用于动态获取当前网络环境的公网IP地址")
    print()

    # 获取当前IP地址
    ip_address = get_current_ip()

    if ip_address:
        print(f"✅ 成功获取到公网IP地址: {ip_address}")
    else:
        print("❌ 未能获取到公网IP地址")

if __name__ == "__main__":
    main()

