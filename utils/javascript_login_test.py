#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用JavaScript方式测试TP-Link路由器登录功能
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

def javascript_login_test():
    """使用JavaScript方式测试登录"""
    # 设置Chrome WebDriver
    chrome_options = Options()
    # 不使用headless模式，以便查看页面
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)

    try:
        login_url = "http://192.168.1.1/webpages/login.html"
        logger.info(f"正在访问登录页面: {login_url}")

        driver.get(login_url)

        # 等待登录表单加载
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "login-form"))
        )

        # 输入用户名和密码
        # 用户名输入框：ID为 "username"
        username_input = driver.find_element(By.ID, "username")
        logger.info(f"找到用户名输入框: {username_input.tag_name}, ID: {username_input.get_attribute('id')}")

        # 密码输入框：通过class定位可见的密码输入框
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password'].password-hidden")
        logger.info(f"找到密码输入框(通过CSS选择器): {password_input.tag_name}, type: {password_input.get_attribute('type')}, class: {password_input.get_attribute('class')}")

        # 登录按钮：ID为 "login-btn"
        login_button = driver.find_element(By.ID, "login-btn")
        logger.info(f"找到登录按钮: {login_button.tag_name}, ID: {login_button.get_attribute('id')}, 文本: '{login_button.text}'")

        # 清除并输入用户名
        username_input.clear()
        username_input.send_keys("wangdg68")
        logger.info("已输入用户名")

        # 清除并输入密码
        password_input.clear()
        password_input.send_keys("wap951020ZJL")
        logger.info("已输入密码")

        # 尝试使用JavaScript点击登录按钮
        logger.info("正在使用JavaScript点击登录按钮...")
        driver.execute_script("arguments[0].click();", login_button)

        # 等待一段时间观察变化
        logger.info("等待5秒钟观察页面变化...")
        time.sleep(5)

        # 检查URL是否发生变化
        current_url = driver.current_url
        logger.info(f"当前URL: {current_url}")

        # 检查页面标题是否发生变化
        page_title = driver.title
        logger.info(f"当前页面标题: {page_title}")

        # 保存截图
        driver.save_screenshot("javascript_login_test.png")
        logger.info("已保存JavaScript登录测试截图: javascript_login_test.png")

        # 继续等待更长时间看是否能登录成功
        logger.info("继续等待20秒钟看是否能登录成功...")
        time.sleep(20)

        # 再次检查URL和标题
        final_url = driver.current_url
        final_title = driver.title
        logger.info(f"最终URL: {final_url}")
        logger.info(f"最终页面标题: {final_title}")

        # 尝试直接提交表单
        logger.info("尝试直接提交表单...")
        driver.execute_script("document.querySelector('.login-form').submit();")

        # 再次等待观察
        logger.info("等待5秒钟观察表单提交结果...")
        time.sleep(5)

        # 检查结果
        submit_url = driver.current_url
        submit_title = driver.title
        logger.info(f"表单提交后URL: {submit_url}")
        logger.info(f"表单提交后标题: {submit_title}")

        # 保存最终截图
        driver.save_screenshot("form_submit_test.png")
        logger.info("已保存表单提交测试截图: form_submit_test.png")

    except Exception as e:
        logger.error(f"登录测试过程中出现错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        driver.quit()

if __name__ == "__main__":
    javascript_login_test()

