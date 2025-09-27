#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
详细分析TP-Link路由器登录过程的脚本
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

def detailed_login_analysis():
    """详细分析登录过程"""
    # 设置Chrome WebDriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 访问登录页面
        router_ip = "192.168.1.1"
        login_url = f"http://{router_ip}/webpages/login.html"
        logger.info(f"正在访问登录页面: {login_url}")

        driver.get(login_url)

        # 步骤1: 等待页面基本加载
        logger.info("步骤1: 等待页面基本加载...")
        time.sleep(3)

        logger.info(f"当前URL: {driver.current_url}")
        logger.info(f"页面标题: '{driver.title}'")

        # 步骤2: 检查页面源码
        logger.info("步骤2: 分析页面源码...")
        page_source = driver.page_source
        logger.info(f"页面源码长度: {len(page_source)} 字符")

        # 检查是否包含登录相关关键词
        login_keywords = ['login', '用户名', '密码', 'password', 'username', 'user']
        for keyword in login_keywords:
            if keyword in page_source.lower():
                logger.info(f"✓ 页面包含关键词: '{keyword}'")
            else:
                logger.info(f"✗ 页面不包含关键词: '{keyword}'")

        # 步骤3: 尝试查找所有元素
        logger.info("步骤3: 查找页面元素...")

        # 查找所有input元素
        try:
            input_elements = driver.find_elements(By.TAG_NAME, "input")
            logger.info(f"找到 {len(input_elements)} 个input元素")

            for i, element in enumerate(input_elements):
                try:
                    element_id = element.get_attribute("id") or "无ID"
                    element_name = element.get_attribute("name") or "无name"
                    element_type = element.get_attribute("type") or "无type"
                    element_class = element.get_attribute("class") or "无class"
                    element_placeholder = element.get_attribute("placeholder") or "无placeholder"

                    logger.info(f"  Input {i+1}: ID='{element_id}', Name='{element_name}', Type='{element_type}', Class='{element_class}', Placeholder='{element_placeholder}'")
                except Exception as e:
                    logger.error(f"  获取Input {i+1} 属性时出错: {str(e)}")
        except Exception as e:
            logger.error(f"查找input元素时出错: {str(e)}")

        # 查找所有button元素
        try:
            button_elements = driver.find_elements(By.TAG_NAME, "button")
            logger.info(f"找到 {len(button_elements)} 个button元素")

            for i, element in enumerate(button_elements):
                try:
                    element_id = element.get_attribute("id") or "无ID"
                    element_text = element.text or "无文本"
                    element_class = element.get_attribute("class") or "无class"
                    element_type = element.get_attribute("type") or "无type"

                    logger.info(f"  Button {i+1}: ID='{element_id}', Text='{element_text}', Class='{element_class}', Type='{element_type}'")
                except Exception as e:
                    logger.error(f"  获取Button {i+1} 属性时出错: {str(e)}")
        except Exception as e:
            logger.error(f"查找button元素时出错: {str(e)}")

        # 查找所有form元素
        try:
            form_elements = driver.find_elements(By.TAG_NAME, "form")
            logger.info(f"找到 {len(form_elements)} 个form元素")
        except Exception as e:
            logger.error(f"查找form元素时出错: {str(e)}")

        # 步骤4: 尝试不同的元素定位方法
        logger.info("步骤4: 尝试不同的元素定位方法...")

        # 尝试多种用户名输入框定位方式
        username_selectors = [
            ("ID", By.ID, "username"),
            ("NAME", By.NAME, "username"),
            ("ID", By.ID, "userName"),
            ("NAME", By.NAME, "userName"),
            ("CSS", By.CSS_SELECTOR, "input[type='text']"),
            ("CSS", By.CSS_SELECTOR, "input[placeholder*='用户名']"),
            ("CSS", By.CSS_SELECTOR, "input[placeholder*='user']"),
            ("CSS", By.CSS_SELECTOR, "input"),
        ]

        logger.info("尝试定位用户名输入框:")
        for i, (method, by, selector) in enumerate(username_selectors):
            try:
                element = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((by, selector))
                )
                logger.info(f"  ✓ 方式 {i+1}: {method}('{selector}') - 成功找到")
                element_id = element.get_attribute("id") or "无ID"
                element_name = element.get_attribute("name") or "无name"
                logger.info(f"    详细信息: ID='{element_id}', Name='{element_name}'")
                break
            except TimeoutException:
                logger.info(f"  ✗ 方式 {i+1}: {method}('{selector}') - 超时未找到")
            except Exception as e:
                logger.info(f"  ✗ 方式 {i+1}: {method}('{selector}') - 出错: {str(e)}")

        # 尝试多种密码输入框定位方式
        password_selectors = [
            ("ID", By.ID, "password"),
            ("NAME", By.NAME, "password"),
            ("ID", By.ID, "pcPassword"),
            ("CSS", By.CSS_SELECTOR, "input[type='password']"),
            ("CSS", By.CSS_SELECTOR, "input[placeholder*='密码']"),
            ("CSS", By.CSS_SELECTOR, "input[placeholder*='password']"),
        ]

        logger.info("尝试定位密码输入框:")
        for i, (method, by, selector) in enumerate(password_selectors):
            try:
                element = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((by, selector))
                )
                logger.info(f"  ✓ 方式 {i+1}: {method}('{selector}') - 成功找到")
                element_id = element.get_attribute("id") or "无ID"
                element_name = element.get_attribute("name") or "无name"
                logger.info(f"    详细信息: ID='{element_id}', Name='{element_name}'")
                break
            except TimeoutException:
                logger.info(f"  ✗ 方式 {i+1}: {method}('{selector}') - 超时未找到")
            except Exception as e:
                logger.info(f"  ✗ 方式 {i+1}: {method}('{selector}') - 出错: {str(e)}")

        # 尝试多种登录按钮定位方式
        login_button_selectors = [
            ("ID", By.ID, "login-btn"),
            ("ID", By.ID, "login"),
            ("CSS", By.CSS_SELECTOR, "button[type='submit']"),
            ("XPATH", By.XPATH, "//button[contains(text(), '登录')]"),
            ("XPATH", By.XPATH, "//button[contains(text(), 'Login')]"),
            ("CSS", By.CSS_SELECTOR, "button"),
            ("XPATH", By.XPATH, "//input[@type='submit']"),
        ]

        logger.info("尝试定位登录按钮:")
        for i, (method, by, selector) in enumerate(login_button_selectors):
            try:
                element = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((by, selector))
                )
                logger.info(f"  ✓ 方式 {i+1}: {method}('{selector}') - 成功找到")
                element_id = element.get_attribute("id") or "无ID"
                element_text = element.text or "无文本"
                logger.info(f"    详细信息: ID='{element_id}', Text='{element_text}'")
                break
            except TimeoutException:
                logger.info(f"  ✗ 方式 {i+1}: {method}('{selector}') - 超时未找到")
            except Exception as e:
                logger.info(f"  ✗ 方式 {i+1}: {method}('{selector}') - 出错: {str(e)}")

        # 步骤5: 尝试手动分析页面结构
        logger.info("步骤5: 手动分析页面结构...")
        logger.info("页面源码前2000字符:")
        logger.info("=" * 50)
        logger.info(page_source[:2000])
        logger.info("=" * 50)

        input("\n按回车键结束分析...")

    except Exception as e:
        logger.error(f"分析过程中出现错误: {str(e)}")
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
    finally:
        driver.quit()

if __name__ == "__main__":
    detailed_login_analysis()

