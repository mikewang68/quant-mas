#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试TP-Link路由器登录按钮位置的脚本
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

def debug_login_button():
    """调试登录按钮位置"""
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

        # 查找所有按钮元素并详细分析
        logger.info("详细查找页面中的所有按钮...")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for i, button in enumerate(buttons):
            button_type = button.get_attribute("type")
            button_id = button.get_attribute("id")
            button_text = button.text
            button_value = button.get_attribute("value")
            button_class = button.get_attribute("class")
            button_name = button.get_attribute("name")
            is_displayed = button.is_displayed()
            is_enabled = button.is_enabled()

            logger.info(f"  按钮 {i+1}:")
            logger.info(f"    type={button_type}")
            logger.info(f"    id={button_id}")
            logger.info(f"    name={button_name}")
            logger.info(f"    text='{button_text}'")
            logger.info(f"    value={button_value}")
            logger.info(f"    class={button_class}")
            logger.info(f"    displayed={is_displayed}")
            logger.info(f"    enabled={is_enabled}")

            # 点击事件处理程序
            try:
                onclick = button.get_attribute("onclick")
                if onclick:
                    logger.info(f"    onclick={onclick}")
            except:
                pass

        # 查找所有input元素中type为submit或button的
        logger.info("\n查找所有input元素中type为submit或button的...")
        input_buttons = driver.find_elements(By.XPATH, "//input[@type='submit' or @type='button']")
        for i, input_btn in enumerate(input_buttons):
            input_type = input_btn.get_attribute("type")
            input_id = input_btn.get_attribute("id")
            input_text = input_btn.get_attribute("value")
            input_class = input_btn.get_attribute("class")
            input_name = input_btn.get_attribute("name")
            is_displayed = input_btn.is_displayed()
            is_enabled = input_btn.is_enabled()

            logger.info(f"  Input按钮 {i+1}:")
            logger.info(f"    type={input_type}")
            logger.info(f"    id={input_id}")
            logger.info(f"    name={input_name}")
            logger.info(f"    value='{input_text}'")
            logger.info(f"    class={input_class}")
            logger.info(f"    displayed={is_displayed}")
            logger.info(f"    enabled={is_enabled}")

        # 通过文本内容查找登录按钮
        logger.info("\n通过文本内容查找登录按钮...")
        login_texts = ["登录", "Login", "login", "LOGIN", "登 录"]
        for text in login_texts:
            try:
                elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
                if elements:
                    logger.info(f"  找到包含'{text}'文本的元素:")
                    for i, element in enumerate(elements):
                        element_tag = element.tag_name
                        element_id = element.get_attribute("id")
                        element_class = element.get_attribute("class")
                        is_displayed = element.is_displayed()
                        is_enabled = element.is_enabled()
                        logger.info(f"    元素 {i+1}: tag={element_tag}, id={element_id}, class={element_class}, displayed={is_displayed}, enabled={is_enabled}")
            except Exception as e:
                logger.error(f"  查找包含'{text}'文本的元素时出错: {str(e)}")

        # 查找所有具有特定类名的元素，可能包含登录按钮
        logger.info("\n查找可能的登录按钮相关元素...")
        possible_classes = ["login", "btn", "button", "submit"]
        for cls in possible_classes:
            try:
                elements = driver.find_elements(By.XPATH, f"//*[contains(@class, '{cls}')]")
                if elements:
                    logger.info(f"  找到包含'{cls}'类名的元素:")
                    for i, element in enumerate(elements[:10]):  # 限制前10个
                        element_tag = element.tag_name
                        element_id = element.get_attribute("id")
                        element_class = element.get_attribute("class")
                        element_text = element.text
                        is_displayed = element.is_displayed()
                        is_enabled = element.is_enabled()
                        logger.info(f"    元素 {i+1}: tag={element_tag}, id={element_id}, class={element_class}, text='{element_text}', displayed={is_displayed}, enabled={is_enabled}")
            except Exception as e:
                logger.error(f"  查找包含'{cls}'类名的元素时出错: {str(e)}")

        # 尝试截图保存页面
        try:
            driver.save_screenshot("login_button_debug_screenshot.png")
            logger.info("已保存登录按钮调试截图: login_button_debug_screenshot.png")
        except Exception as e:
            logger.error(f"保存截图时出错: {str(e)}")

    except Exception as e:
        logger.error(f"调试过程中出现错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_login_button()

