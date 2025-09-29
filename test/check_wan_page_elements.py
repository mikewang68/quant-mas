#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查TP-Link路由器WAN设置页面元素
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_wan_page_elements():
    """检查WAN设置页面元素"""
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

        # 等待并检查页面元素
        logger.info("检查WAN设置页面元素...")
        time.sleep(5)

        for i in range(20):
            logger.info(f"第{i+1}秒:")

            # 检查当前URL
            current_url = driver.current_url
            logger.info(f"  当前URL: {current_url}")

            # 检查页面标题
            page_title = driver.title
            logger.info(f"  页面标题: {page_title}")

            # 检查各种可能的元素
            main_frame_elements = driver.find_elements(By.CLASS_NAME, "main-frame")
            logger.info(f"  'main-frame'元素: {len(main_frame_elements)} 个")

            tab_nav_elements = driver.find_elements(By.CLASS_NAME, "tab-nav")
            logger.info(f"  'tab-nav'元素: {len(tab_nav_elements)} 个")

            # 检查是否包含WAN相关文本
            page_source = driver.page_source
            wan_count = page_source.count("WAN")
            wan2_count = page_source.count("WAN2")
            logger.info(f"  页面源码中包含 {wan_count} 个'WAN'和 {wan2_count} 个'WAN2'")

            # 检查是否有特定的WAN设置元素
            wan_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'WAN') or contains(text(), ' wan')]")
            logger.info(f"  包含'WAN'文本的元素: {len(wan_elements)} 个")

            # 检查是否有表单元素
            form_elements = driver.find_elements(By.TAG_NAME, "form")
            logger.info(f"  表单元素: {len(form_elements)} 个")

            # 检查是否有按钮元素
            button_elements = driver.find_elements(By.TAG_NAME, "button")
            logger.info(f"  按钮元素: {len(button_elements)} 个")

            # 检查是否有断开/连接按钮
            disconnect_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '断开')]")
            connect_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '连接')]")
            logger.info(f"  '断开'按钮: {len(disconnect_buttons)} 个, '连接'按钮: {len(connect_buttons)} 个")

            time.sleep(1)

        # 保存截图
        driver.save_screenshot("check_wan_page_elements.png")
        logger.info("已保存WAN页面元素检查截图: check_wan_page_elements.png")

    except Exception as e:
        logger.error(f"检查过程中出现错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        driver.quit()

if __name__ == "__main__":
    check_wan_page_elements()

