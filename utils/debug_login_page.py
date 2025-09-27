#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试脚本：分析TP-Link路由器登录页面元素结构
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

def debug_login_page():
    """调试登录页面元素结构"""
    # 设置Chrome WebDriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)

    try:
        # 访问登录页面
        router_ip = "192.168.1.1"
        login_url = f"http://{router_ip}/webpages/login.html"
        logger.info(f"正在访问登录页面: {login_url}")

        driver.get(login_url)

        # 等待页面加载
        time.sleep(5)

        # 打印页面标题和URL
        logger.info(f"页面标题: {driver.title}")
        logger.info(f"当前URL: {driver.current_url}")

        # 尝试获取页面源码
        logger.info("页面源码预览:")
        source = driver.page_source
        logger.info(f"源码长度: {len(source)} 字符")

        # 打印部分源码用于分析
        logger.info("页面源码片段:")
        logger.info(source[:2000])

        # 查找可能的输入元素
        logger.info("查找页面中的输入元素...")

        # 查找所有input元素
        input_elements = driver.find_elements(By.TAG_NAME, "input")
        logger.info(f"找到 {len(input_elements)} 个input元素")

        for i, element in enumerate(input_elements):
            try:
                element_id = element.get_attribute("id")
                element_name = element.get_attribute("name")
                element_type = element.get_attribute("type")
                element_class = element.get_attribute("class")
                element_placeholder = element.get_attribute("placeholder")

                logger.info(f"Input {i+1}: ID='{element_id}', Name='{element_name}', Type='{element_type}', Class='{element_class}', Placeholder='{element_placeholder}'")
            except Exception as e:
                logger.error(f"获取Input {i+1} 属性时出错: {str(e)}")

        # 查找所有button元素
        logger.info("查找页面中的按钮元素...")
        button_elements = driver.find_elements(By.TAG_NAME, "button")
        logger.info(f"找到 {len(button_elements)} 个button元素")

        for i, element in enumerate(button_elements):
            try:
                element_id = element.get_attribute("id")
                element_text = element.text
                element_class = element.get_attribute("class")
                element_type = element.get_attribute("type")

                logger.info(f"Button {i+1}: ID='{element_id}', Text='{element_text}', Class='{element_class}', Type='{element_type}'")
            except Exception as e:
                logger.error(f"获取Button {i+1} 属性时出错: {str(e)}")

        # 尝试通过不同方式查找登录相关元素
        logger.info("尝试不同方式查找登录元素...")

        # 尝试常见的用户名输入框定位方式
        possible_username_selectors = [
            (By.ID, "userName"),
            (By.ID, "username"),
            (By.NAME, "username"),
            (By.NAME, "userName"),
            (By.CSS_SELECTOR, "input[type='text']"),
            (By.CSS_SELECTOR, "input[placeholder*='用户名']"),
            (By.CSS_SELECTOR, "input[placeholder*='user']"),
        ]

        found_username = False
        for by, selector in possible_username_selectors:
            try:
                element = driver.find_element(by, selector)
                logger.info(f"✓ 找到用户名输入框: By.{by.name}('{selector}')")
                element_id = element.get_attribute("id")
                element_name = element.get_attribute("name")
                logger.info(f"  详细信息: ID='{element_id}', Name='{element_name}'")
                found_username = True
                break
            except:
                logger.info(f"✗ 未找到: By.{by.name}('{selector}')")

        if not found_username:
            logger.warning("未能找到用户名输入框，尝试查找所有input元素...")
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            for i, inp in enumerate(all_inputs):
                try:
                    inp_id = inp.get_attribute("id")
                    inp_name = inp.get_attribute("name")
                    inp_type = inp.get_attribute("type")
                    inp_placeholder = inp.get_attribute("placeholder")
                    logger.info(f"  Input {i}: ID='{inp_id}', Name='{inp_name}', Type='{inp_type}', Placeholder='{inp_placeholder}'")
                except:
                    pass

        # 尝试常见的密码输入框定位方式
        possible_password_selectors = [
            (By.ID, "pcPassword"),
            (By.ID, "password"),
            (By.NAME, "password"),
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.CSS_SELECTOR, "input[placeholder*='密码']"),
            (By.CSS_SELECTOR, "input[placeholder*='password']"),
        ]

        found_password = False
        for by, selector in possible_password_selectors:
            try:
                element = driver.find_element(by, selector)
                logger.info(f"✓ 找到密码输入框: By.{by.name}('{selector}')")
                element_id = element.get_attribute("id")
                element_name = element.get_attribute("name")
                logger.info(f"  详细信息: ID='{element_id}', Name='{element_name}'")
                found_password = True
                break
            except:
                logger.info(f"✗ 未找到: By.{by.name}('{selector}')")

        if not found_password:
            logger.warning("未能找到密码输入框")

        # 尝试常见的登录按钮定位方式
        possible_login_selectors = [
            (By.ID, "login-btn"),
            (By.ID, "login"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//button[contains(text(), '登录')]"),
            (By.XPATH, "//button[contains(text(), 'Login')]"),
            (By.XPATH, "//input[@type='submit']"),
        ]

        found_login = False
        for by, selector in possible_login_selectors:
            try:
                element = driver.find_element(by, selector)
                logger.info(f"✓ 找到登录按钮: By.{by.name}('{selector}')")
                element_id = element.get_attribute("id")
                element_text = element.text
                logger.info(f"  详细信息: ID='{element_id}', Text='{element_text}'")
                found_login = True
                break
            except:
                logger.info(f"✗ 未找到: By.{by.name}('{selector}')")

        if not found_login:
            logger.warning("未能找到登录按钮，尝试查找所有button元素...")
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            for i, btn in enumerate(all_buttons):
                try:
                    btn_id = btn.get_attribute("id")
                    btn_text = btn.text
                    btn_class = btn.get_attribute("class")
                    logger.info(f"  Button {i}: ID='{btn_id}', Text='{btn_text}', Class='{btn_class}'")
                except:
                    pass

        input("按回车键结束调试...")

    except Exception as e:
        logger.error(f"调试过程中出现错误: {str(e)}")
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_login_page()

