#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试脚本：用于调试右侧WAN2元素定位
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_wan2_elements():
    """测试WAN2元素定位"""
    # 设置Chrome WebDriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)

    try:
        # 登录路由器
        router_ip = "192.168.1.1"
        username = "wangdg68"
        password = "wap951020ZJL"

        login_url = f"http://{router_ip}/webpages/login.html"
        logger.info(f"正在访问登录页面: {login_url}")

        driver.get(login_url)

        # 等待登录表单加载
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "login-btn"))
        )

        # 输入用户名和密码
        username_input = driver.find_element(By.ID, "userName")
        password_input = driver.find_element(By.ID, "pcPassword")
        login_button = driver.find_element(By.ID, "login-btn")

        username_input.clear()
        username_input.send_keys(username)

        password_input.clear()
        password_input.send_keys(password)

        logger.info("正在登录...")
        login_button.click()

        # 等待登录完成
        WebDriverWait(driver, 20).until(
            EC.url_contains("index.html")
        )
        logger.info("登录成功")

        # 导航到WAN设置
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "main-menu"))
        )

        logger.info("正在导航到基本设置-WAN设置...")

        # 点击"基本设置"菜单
        basic_settings_menu = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='基本设置']"))
        )
        basic_settings_menu.click()
        time.sleep(1)

        # 点击"WAN设置"子菜单
        wan_settings_menu = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='WAN设置']"))
        )
        wan_settings_menu.click()
        time.sleep(3)

        logger.info("已进入WAN设置页面")

        # 分析页面元素
        logger.info("开始分析页面元素...")

        # 获取所有标签元素
        tab_elements = driver.find_elements(By.CSS_SELECTOR, ".tab-nav li")
        logger.info(f"找到 {len(tab_elements)} 个标签元素")

        for i, tab in enumerate(tab_elements):
            location = tab.location
            size = tab.size
            logger.info(f"标签 {i+1}: 位置 {location}, 大小 {size}")

            # 尝试获取标签文本
            try:
                text = tab.text
                logger.info(f"标签 {i+1} 文本: {text}")
            except:
                logger.info(f"标签 {i+1} 无法获取文本")

        # 获取所有按钮元素
        button_elements = driver.find_elements(By.TAG_NAME, "button")
        logger.info(f"找到 {len(button_elements)} 个按钮元素")

        disconnect_buttons = []
        connect_buttons = []

        for i, button in enumerate(button_elements):
            try:
                location = button.location
                size = button.size
                text = button.text.strip()

                if text:
                    logger.info(f"按钮 {i+1}: 文本 '{text}', 位置 {location}, 大小 {size}")

                    if "断开" in text:
                        disconnect_buttons.append((button, location, text))
                    elif "连接" in text:
                        connect_buttons.append((button, location, text))
            except:
                continue

        logger.info(f"找到 {len(disconnect_buttons)} 个断开按钮")
        logger.info(f"找到 {len(connect_buttons)} 个连接按钮")

        # 分析按钮位置，确定右侧WAN2
        if disconnect_buttons:
            logger.info("断开按钮详情:")
            for i, (btn, loc, txt) in enumerate(disconnect_buttons):
                logger.info(f"  断开按钮 {i+1}: '{txt}' 位置 {loc}")

        if connect_buttons:
            logger.info("连接按钮详情:")
            for i, (btn, loc, txt) in enumerate(connect_buttons):
                logger.info(f"  连接按钮 {i+1}: '{txt}' 位置 {loc}")

        # 根据x坐标确定右侧按钮
        if len(disconnect_buttons) >= 2:
            # 按x坐标排序
            disconnect_buttons.sort(key=lambda x: x[1]['x'], reverse=True)
            logger.info(f"右侧断开按钮: '{disconnect_buttons[0][2]}' 位置 {disconnect_buttons[0][1]}")

        if len(connect_buttons) >= 2:
            # 按x坐标排序
            connect_buttons.sort(key=lambda x: x[1]['x'], reverse=True)
            logger.info(f"右侧连接按钮: '{connect_buttons[0][2]}' 位置 {connect_buttons[0][1]}")

        input("按回车键继续...")

    except Exception as e:
        logger.error(f"测试过程中出现错误: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_wan2_elements()

