#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
等待TP-Link路由器WAN设置页面元素出现
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def wait_for_wan_elements():
    """等待WAN设置页面元素出现"""
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
        # 登录
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
        WebDriverWait(driver, 30).until(
            lambda driver: "index.html" in driver.current_url
        )
        logger.info("登录成功")

        # 导航到WAN设置
        logger.info("正在导航到WAN设置...")
        time.sleep(5)

        # 点击"基本设置"菜单
        basic_settings_menu = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='基本设置']"))
        )
        basic_settings_menu.click()
        logger.info("已点击'基本设置'菜单")
        time.sleep(2)

        # 点击"WAN设置"菜单
        wan_settings_menu = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='WAN设置']"))
        )
        wan_settings_menu.click()
        logger.info("已点击'WAN设置'菜单")

        # 等待WAN设置页面元素出现
        logger.info("等待WAN设置页面元素出现...")

        # 尝试等待不同的元素
        wait_elements = [
            (By.CLASS_NAME, "main-frame"),
            (By.CLASS_NAME, "tab-nav"),
            (By.XPATH, "//button[contains(text(), '断开')]"),
            (By.XPATH, "//button[contains(text(), '连接')]"),
            (By.XPATH, "//li[contains(text(), 'WAN2')]"),
        ]

        found_elements = []
        for by, value in wait_elements:
            try:
                logger.info(f"等待元素: {by} = {value}")
                element = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((by, value))
                )
                found_elements.append((by, value, element))
                logger.info(f"  找到元素: {by} = {value}")
            except TimeoutException:
                logger.info(f"  未找到元素: {by} = {value}")

        # 检查找到的元素
        logger.info(f"总共找到 {len(found_elements)} 个元素")

        # 如果找到了断开或连接按钮，尝试操作
        disconnect_button = None
        connect_button = None

        for by, value, element in found_elements:
            if "断开" in value:
                disconnect_button = element
            elif "连接" in value:
                connect_button = element

        if disconnect_button:
            logger.info("找到断开按钮，尝试点击...")
            disconnect_button.click()
            logger.info("已点击断开按钮")
            time.sleep(3)

            if connect_button:
                logger.info("找到连接按钮，尝试点击...")
                connect_button.click()
                logger.info("已点击连接按钮")
                time.sleep(5)
            else:
                # 尝试查找连接按钮
                try:
                    connect_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '连接')]"))
                    )
                    connect_button.click()
                    logger.info("已点击连接按钮")
                    time.sleep(5)
                except TimeoutException:
                    logger.info("未找到连接按钮")

        # 保存截图
        driver.save_screenshot("wait_for_wan_elements.png")
        logger.info("已保存截图: wait_for_wan_elements.png")

    except Exception as e:
        logger.error(f"测试过程中出现错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        driver.quit()

if __name__ == "__main__":
    wait_for_wan_elements()

