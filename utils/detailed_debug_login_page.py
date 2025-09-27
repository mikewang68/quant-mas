#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
详细调试TP-Link路由器登录页面结构的脚本
用于分析登录页面的实际元素结构
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def detailed_debug_login_page():
    """详细调试登录页面结构"""
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

        # 等待页面加载
        time.sleep(5)

        # 打印页面标题
        logger.info(f"页面标题: {driver.title}")

        # 打印当前URL
        logger.info(f"当前URL: {driver.current_url}")

        # 打印页面源码（前5000字符）
        page_source = driver.page_source
        logger.info(f"页面源码（前5000字符）: {page_source[:5000]}")

        # 详细查找所有输入框
        logger.info("详细查找页面中的所有输入框...")
        input_fields = driver.find_elements(By.TAG_NAME, "input")
        for i, field in enumerate(input_fields):
            field_type = field.get_attribute("type")
            field_id = field.get_attribute("id")
            field_name = field.get_attribute("name")
            field_class = field.get_attribute("class")
            field_placeholder = field.get_attribute("placeholder")
            field_value = field.get_attribute("value")
            is_displayed = field.is_displayed()
            is_enabled = field.is_enabled()

            logger.info(f"  输入框 {i+1}:")
            logger.info(f"    type={field_type}")
            logger.info(f"    id={field_id}")
            logger.info(f"    name={field_name}")
            logger.info(f"    class={field_class}")
            logger.info(f"    placeholder={field_placeholder}")
            logger.info(f"    value={field_value}")
            logger.info(f"    displayed={is_displayed}")
            logger.info(f"    enabled={is_enabled}")

        # 详细查找所有按钮
        logger.info("\n详细查找页面中的所有按钮...")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for i, button in enumerate(buttons):
            button_type = button.get_attribute("type")
            button_id = button.get_attribute("id")
            button_text = button.text
            button_value = button.get_attribute("value")
            button_class = button.get_attribute("class")
            is_displayed = button.is_displayed()
            is_enabled = button.is_enabled()

            logger.info(f"  按钮 {i+1}:")
            logger.info(f"    type={button_type}")
            logger.info(f"    id={button_id}")
            logger.info(f"    text='{button_text}'")
            logger.info(f"    value={button_value}")
            logger.info(f"    class={button_class}")
            logger.info(f"    displayed={is_displayed}")
            logger.info(f"    enabled={is_enabled}")

        # 查找所有具有特定类名的元素
        logger.info("\n查找具有特定类名的元素...")
        class_elements = driver.find_elements(By.XPATH, "//*[@class]")
        for i, element in enumerate(class_elements[:20]):  # 限制前20个
            element_tag = element.tag_name
            element_id = element.get_attribute("id")
            element_class = element.get_attribute("class")
            element_text = element.text
            logger.info(f"  元素 {i+1}: tag={element_tag}, id={element_id}, class={element_class}, text='{element_text}'")

        # 尝试通过XPath查找可能的登录表单元素
        logger.info("\n尝试通过XPath查找登录表单元素...")

        # 查找所有表单
        forms = driver.find_elements(By.TAG_NAME, "form")
        logger.info(f"找到 {len(forms)} 个表单")
        for i, form in enumerate(forms):
            form_id = form.get_attribute("id")
            form_class = form.get_attribute("class")
            form_action = form.get_attribute("action")
            logger.info(f"  表单 {i+1}: id={form_id}, class={form_class}, action={form_action}")

        # 尝试查找包含"用户名"或"密码"文本的元素
        logger.info("\n查找包含'用户名'或'密码'文本的元素...")
        text_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '用户名') or contains(text(), '密码') or contains(text(), 'user') or contains(text(), 'password')]")
        for i, element in enumerate(text_elements):
            element_tag = element.tag_name
            element_id = element.get_attribute("id")
            element_class = element.get_attribute("class")
            element_text = element.text
            logger.info(f"  文本元素 {i+1}: tag={element_tag}, id={element_id}, class={element_class}, text='{element_text}'")

        # 尝试截图保存页面
        try:
            driver.save_screenshot("detailed_login_page_screenshot.png")
            logger.info("已保存详细登录页面截图: detailed_login_page_screenshot.png")
        except Exception as e:
            logger.error(f"保存截图时出错: {str(e)}")

    except Exception as e:
        logger.error(f"调试过程中出现错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        driver.quit()

if __name__ == "__main__":
    detailed_debug_login_page()

