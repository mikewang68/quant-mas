#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用JavaScript直接触发TP-Link路由器登录
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def javascript_login():
    """使用JavaScript直接登录"""
    # 设置Chrome WebDriver
    chrome_options = Options()
    # 不使用headless模式，以便查看页面
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(5)

    try:
        login_url = "http://192.168.1.1/webpages/login.html"
        logger.info(f"正在访问登录页面: {login_url}")

        driver.get(login_url)

        # 等待页面加载
        time.sleep(3)

        # 输入用户名和密码
        logger.info("正在输入用户名和密码...")
        driver.execute_script("document.getElementById('username').value = 'wangdg68';")
        driver.execute_script("document.querySelector('input[type=\"password\"].password-hidden').value = 'wap951020ZJL';")

        # 尝试直接调用登录函数
        logger.info("尝试直接调用登录函数...")
        # 根据页面源码分析，可能有登录函数
        driver.execute_script("""
            var username = 'wangdg68';
            var password = 'wap951020ZJL';
            // 尝试调用可能存在的登录函数
            if (typeof doLogin === 'function') {
                doLogin(username, password);
            } else if (typeof login === 'function') {
                login(username, password);
            } else {
                // 如果没有专门的登录函数，尝试提交表单
                var form = document.querySelector('.login-form');
                if (form) {
                    form.submit();
                }
            }
        """)

        # 观察结果
        logger.info("观察登录结果...")
        for i in range(30):
            current_url = driver.current_url
            page_title = driver.title
            logger.info(f"第{i+1}秒 - URL: {current_url}, 标题: {page_title}")

            # 检查是否登录成功
            if "index.html" in current_url:
                logger.info("检测到登录成功!")
                break

            time.sleep(1)

        # 保存截图
        driver.save_screenshot("javascript_direct_login.png")
        logger.info("已保存JavaScript直接登录截图: javascript_direct_login.png")

    except Exception as e:
        logger.error(f"JavaScript登录时出现错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        driver.quit()

if __name__ == "__main__":
    javascript_login()

