#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
尝试直接访问TP-Link路由器WAN设置页面
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def direct_wan_access():
    """尝试直接访问WAN设置页面"""
    # 设置Chrome WebDriver
    chrome_options = Options()
    # 不使用headless模式，以便查看页面
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(3)

    try:
        # 先登录
        login_url = "http://192.168.1.1/webpages/login.html"
        logger.info(f"正在访问登录页面: {login_url}")

        driver.get(login_url)
        time.sleep(2)

        # 使用Selenium原生方法登录
        logger.info("正在使用Selenium原生方法登录...")
        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password'].password-hidden")
        login_button = driver.find_element(By.ID, "login-btn")

        username_input.clear()
        username_input.send_keys("wangdg68")

        password_input.clear()
        password_input.send_keys("wap951020ZJL")

        login_button.click()

        # 等待登录完成
        time.sleep(8)
        logger.info("登录完成")

        # 尝试直接访问WAN设置页面
        wan_urls = [
            "http://192.168.1.1/webpages/index.html#wan",
            "http://192.168.1.1/webpages/index.html#/wan",
            "http://192.168.1.1/webpages/wan.html",
            "http://192.168.1.1/webpages/#/wan-setting"
        ]

        for wan_url in wan_urls:
            logger.info(f"尝试访问WAN设置页面: {wan_url}")
            driver.get(wan_url)
            time.sleep(5)

            # 检查页面内容
            current_url = driver.current_url
            page_title = driver.title
            logger.info(f"  当前URL: {current_url}")
            logger.info(f"  页面标题: {page_title}")

            # 检查是否有WAN相关元素
            page_source = driver.page_source
            wan_count = page_source.count("WAN")
            wan2_count = page_source.count("WAN2")
            logger.info(f"  页面源码中包含 {wan_count} 个'WAN'和 {wan2_count} 个'WAN2'")

            # 检查是否有断开/连接按钮
            disconnect_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '断开')]")
            connect_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '连接')]")
            logger.info(f"  '断开'按钮: {len(disconnect_buttons)} 个, '连接'按钮: {len(connect_buttons)} 个")

            # 保存截图
            screenshot_name = f"direct_wan_access_{wan_url.replace('http://', '').replace('/', '_').replace('#', '_')}.png"
            driver.save_screenshot(screenshot_name)
            logger.info(f"  已保存截图: {screenshot_name}")

        # 如果直接访问不成功，再尝试菜单导航
        logger.info("尝试通过菜单导航到WAN设置...")
        driver.get("http://192.168.1.1/webpages/index.html")
        time.sleep(5)

        # 点击"基本设置"菜单
        basic_settings_menu = driver.find_element(By.XPATH, "//span[text()='基本设置']")
        basic_settings_menu.click()
        logger.info("已点击'基本设置'菜单")
        time.sleep(2)

        # 点击"WAN设置"菜单
        wan_settings_menu = driver.find_element(By.XPATH, "//span[text()='WAN设置']")
        wan_settings_menu.click()
        logger.info("已点击'WAN设置'菜单")

        # 等待并检查
        for i in range(15):
            logger.info(f"等待第{i+1}秒...")

            current_url = driver.current_url
            logger.info(f"  当前URL: {current_url}")

            # 检查是否有断开/连接按钮
            disconnect_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '断开')]")
            connect_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '连接')]")
            logger.info(f"  '断开'按钮: {len(disconnect_buttons)} 个, '连接'按钮: {len(connect_buttons)} 个")

            time.sleep(1)

        # 保存最终截图
        driver.save_screenshot("direct_wan_access_final.png")
        logger.info("已保存最终截图: direct_wan_access_final.png")

    except Exception as e:
        logger.error(f"测试过程中出现错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        driver.quit()

if __name__ == "__main__":
    direct_wan_access()

