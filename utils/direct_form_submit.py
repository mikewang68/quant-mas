#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
尝试直接提交TP-Link路由器登录表单
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def direct_form_submit():
    """尝试直接提交登录表单"""
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

        # 直接使用JavaScript设置表单值并提交
        logger.info("正在直接设置表单值并提交...")
        driver.execute_script("""
            // 设置用户名和密码
            document.getElementById('username').value = 'wangdg68';
            document.querySelector('input[type="password"].password-hidden').value = 'wap951020ZJL';

            // 查找登录表单并提交
            var loginForm = document.querySelector('.login-form');
            if (loginForm) {
                loginForm.submit();
            } else {
                console.log('未找到登录表单');
            }
        """)

        # 观察提交结果
        logger.info("观察提交结果...")
        for i in range(20):
            current_url = driver.current_url
            page_title = driver.title
            logger.info(f"第{i+1}秒 - URL: {current_url}, 标题: {page_title}")

            time.sleep(1)

        # 保存截图
        driver.save_screenshot("direct_form_submit.png")
        logger.info("已保存直接表单提交截图: direct_form_submit.png")

    except Exception as e:
        logger.error(f"测试过程中出现错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        driver.quit()

if __name__ == "__main__":
    direct_form_submit()

