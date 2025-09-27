#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用Selenium原生方法提交TP-Link路由器登录表单
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def selenium_form_submit():
    """使用Selenium原生方法提交登录表单"""
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
        # 访问登录页面
        login_url = "http://192.168.1.1/webpages/login.html"
        logger.info(f"正在访问登录页面: {login_url}")

        driver.get(login_url)

        # 等待页面加载
        time.sleep(2)

        # 使用Selenium方法填充表单
        logger.info("正在使用Selenium方法填充表单...")
        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password'].password-hidden")
        login_button = driver.find_element(By.ID, "login-btn")

        username_input.clear()
        username_input.send_keys("wangdg68")

        password_input.clear()
        password_input.send_keys("wap951020ZJL")

        logger.info("正在点击登录按钮...")
        login_button.click()

        # 观察提交结果
        logger.info("观察提交结果...")
        for i in range(20):
            current_url = driver.current_url
            page_title = driver.title
            logger.info(f"第{i+1}秒 - URL: {current_url}, 标题: {page_title}")

            time.sleep(1)

        # 保存截图
        driver.save_screenshot("selenium_form_submit.png")
        logger.info("已保存Selenium表单提交截图: selenium_form_submit.png")

    except Exception as e:
        logger.error(f"测试过程中出现错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        driver.quit()

if __name__ == "__main__":
    selenium_form_submit()

