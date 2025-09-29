#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ISP IP地址获取工具

此工具用于动态获取当前网络环境的公网IP地址。
通过访问ip138.com网站并检查iframe内容来获取准确的IP地址信息。

注意：此工具可以作为模块导入，提供get_current_ip()函数供其他程序调用。
"""

import time
import re
import logging
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def setup_chrome_driver(headless=True, max_retries=3, retry_delay=1):
    """
    设置Chrome WebDriver

    Args:
        headless (bool): 是否使用无头模式
        max_retries (int): 最大重试次数
        retry_delay (int): 重试间隔（秒）

    Returns:
        webdriver.Chrome: Chrome WebDriver实例
    """
    for attempt in range(max_retries):
        try:
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

        except Exception as e:
            logger.error(f"Chrome WebDriver设置失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (2 ** attempt))  # 指数退避
                continue
            return None

    logger.error(f"经过 {max_retries} 次尝试后仍无法设置Chrome WebDriver")
    return None


def get_current_ip(max_retries=3, retry_delay=1):
    """
    获取当前网络环境的公网IP地址

    Args:
        max_retries (int): 最大重试次数
        retry_delay (int): 重试间隔（秒）

    Returns:
        str: 检测到的IP地址，如果未检测到则返回None
    """
    for attempt in range(max_retries):
        driver = None
        try:
            # 初始化WebDriver
            driver = setup_chrome_driver(headless=True)

            if not driver:
                logger.error(f"WebDriver初始化失败 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))  # 指数退避
                    continue
                return None

            # 访问主页面
            target_url = "https://www.ip138.com/"
            driver.get(target_url)

            # 等待页面加载
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # 给页面更多时间完全加载，特别是JavaScript执行
            time.sleep(8)

            # 查找所有iframe
            iframes = driver.find_elements(By.TAG_NAME, "iframe")

            # 遍历所有iframe查找IP信息
            for i, iframe in enumerate(iframes):
                try:
                    # 获取iframe的src属性
                    iframe_src = iframe.get_attribute("src")

                    # 切换到iframe
                    driver.switch_to.frame(iframe)

                    # 等待iframe内容加载
                    time.sleep(3)

                    # 获取iframe内容
                    try:
                        iframe_body = driver.find_element(By.TAG_NAME, "body")
                        iframe_text = iframe_body.text

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
                                logger.info(f"成功获取IP地址: {found_ip}")
                                return found_ip

                    except Exception as e:
                        logger.warning(f"获取iframe内容时出错: {e}")

                    # 切换回主内容
                    driver.switch_to.default_content()

                except Exception as e:
                    logger.warning(f"处理iframe时出错: {e}")
                    # 切换回主内容
                    try:
                        driver.switch_to.default_content()
                    except:
                        pass

            # 如果还没找到，直接访问iframe的URL
            try:
                iframe_url = "https://2025.ip138.com/"
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
                        logger.info(f"通过备用方法获取IP地址: {found_ip}")
                        return found_ip

            except Exception as e:
                logger.warning(f"通过备用方法获取IP时出错: {e}")

        except Exception as e:
            logger.error(f"获取IP地址时出错 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (2 ** attempt))  # 指数退避
                continue

        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    logger.warning(f"关闭WebDriver时出错: {e}")

        # 如果重试次数未用完，等待后重试
        if attempt < max_retries - 1:
            logger.info(f"等待 {retry_delay * (2 ** attempt)} 秒后重试...")
            time.sleep(retry_delay * (2 ** attempt))

    logger.error(f"经过 {max_retries} 次尝试后仍无法获取IP地址")
    return None


def main():
    """
    主函数 - 获取并显示当前IP地址
    """
    print("🔍 ISP IP地址获取工具")
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
