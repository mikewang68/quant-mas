#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试TP-Link路由器登录功能
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

def test_login():
    """测试登录功能"""
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
        # 根据调试结果，密码输入框是type=password且有password-hidden类
        try:
            password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password'].password-hidden")
            logger.info(f"找到密码输入框(通过CSS选择器): {password_input.tag_name}, type: {password_input.get_attribute('type')}, class: {password_input.get_attribute('class')}")
        except:
            # 如果找不到，尝试其他方式
            password_inputs = driver.find_elements(By.XPATH, "//input[@type='password']")
            if password_inputs:
                password_input = password_inputs[0]
                logger.info(f"找到密码输入框(通过XPath): {password_input.tag_name}, type: {password_input.get_attribute('type')}")
            else:
                # 最后尝试通过name属性
                password_input = driver.find_element(By.NAME, "password")
                logger.info(f"找到密码输入框(通过name): {password_input.tag_name}, name: {password_input.get_attribute('name')}")

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

        # 点击登录按钮
        logger.info("正在点击登录按钮...")
        login_button.click()

        # 等待登录完成，增加超时时间
        logger.info("等待登录完成...")
        WebDriverWait(driver, 30).until(
            EC.url_contains("index.html")
        )
        logger.info("登录成功!")

        # 保存成功登录的截图
        driver.save_screenshot("successful_login.png")
        logger.info("已保存成功登录截图: successful_login.png")

        # 等待几秒钟查看结果
        time.sleep(5)

    except TimeoutException as e:
        logger.error(f"登录超时: {str(e)}")
        # 保存失败截图
        driver.save_screenshot("failed_login.png")
        logger.info("已保存失败登录截图: failed_login.png")
    except Exception as e:
        logger.error(f"登录过程中出现错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        # 保存失败截图
        driver.save_screenshot("error_login.png")
        logger.info("已保存错误登录截图: error_login.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_login()

