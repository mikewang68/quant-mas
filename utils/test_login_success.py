#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试TP-Link路由器登录是否真正成功
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_login_success():
    """测试登录是否真正成功"""
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

        # 使用JavaScript登录
        logger.info("正在使用JavaScript登录...")
        driver.execute_script("""
            document.getElementById('username').value = 'wangdg68';
            document.querySelector('input[type="password"].password-hidden').value = 'wap951020ZJL';
            var loginBtn = document.getElementById('login-btn');
            if (loginBtn) {
                loginBtn.click();
            }
        """)

        # 观察登录过程
        logger.info("观察登录过程...")
        for i in range(20):
            current_url = driver.current_url
            page_title = driver.title
            logger.info(f"第{i+1}秒 - URL: {current_url}, 标题: {page_title}")

            # 检查页面内容变化
            page_source = driver.page_source

            # 检查是否存在登录成功后的元素
            logout_elements = driver.find_elements(By.XPATH, "//span[text()='登出']")
            user_elements = driver.find_elements(By.XPATH, "//span[text()='用户']")
            status_elements = driver.find_elements(By.XPATH, "//span[text()='运行状态']")

            logger.info(f"  登出元素: {len(logout_elements)} 个")
            logger.info(f"  用户元素: {len(user_elements)} 个")
            logger.info(f"  运行状态元素: {len(status_elements)} 个")

            # 检查是否存在登录表单元素（如果仍然存在，说明登录未成功）
            username_inputs = driver.find_elements(By.ID, "username")
            password_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='password'].password-hidden")
            login_buttons = driver.find_elements(By.ID, "login-btn")

            logger.info(f"  用户名输入框: {len(username_inputs)} 个")
            logger.info(f"  密码输入框: {len(password_inputs)} 个")
            logger.info(f"  登录按钮: {len(login_buttons)} 个")

            time.sleep(1)

        # 保存截图
        driver.save_screenshot("test_login_success.png")
        logger.info("已保存登录测试截图: test_login_success.png")

    except Exception as e:
        logger.error(f"测试过程中出现错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        driver.quit()

if __name__ == "__main__":
    test_login_success()

