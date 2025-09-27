#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
专门测试登录功能的脚本
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

def test_login():
    """测试登录功能"""
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

        # 等待页面加载
        time.sleep(3)

        # 尝试不同的方式定位密码输入框
        logger.info("尝试定位密码输入框...")

        # 方法1: 通过class定位隐藏的密码框
        try:
            password_input = driver.find_element(By.CSS_SELECTOR, ".password-hidden")
            logger.info("✓ 成功找到password-hidden输入框")
        except Exception as e:
            logger.error(f"✗ 无法找到password-hidden输入框: {str(e)}")
            password_input = None

        # 方法2: 通过type=password定位
        if not password_input:
            try:
                password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                logger.info("✓ 成功找到type='password'输入框")
            except Exception as e:
                logger.error(f"✗ 无法找到type='password'输入框: {str(e)}")
                password_input = None

        # 方法3: 通过ID定位
        if not password_input:
            try:
                password_input = driver.find_element(By.ID, "password")
                logger.info("✓ 成功找到ID='password'输入框")
            except Exception as e:
                logger.error(f"✗ 无法找到ID='password'输入框: {str(e)}")
                password_input = None

        # 方法4: 查找所有input元素，找到password类型的
        if not password_input:
            try:
                all_inputs = driver.find_elements(By.TAG_NAME, "input")
                for inp in all_inputs:
                    inp_type = inp.get_attribute("type") or ""
                    if "password" in inp_type.lower():
                        password_input = inp
                        logger.info("✓ 通过遍历找到password类型输入框")
                        break
            except Exception as e:
                logger.error(f"✗ 遍历查找password输入框失败: {str(e)}")

        # 定位用户名输入框
        logger.info("定位用户名输入框...")
        try:
            username_input = driver.find_element(By.ID, "username")
            logger.info("✓ 成功找到用户名输入框")
        except Exception as e:
            logger.error(f"✗ 无法找到用户名输入框: {str(e)}")
            username_input = None

        # 定位登录按钮
        logger.info("定位登录按钮...")
        try:
            login_button = driver.find_element(By.ID, "login-btn")
            logger.info("✓ 成功找到登录按钮")
        except Exception as e:
            logger.error(f"✗ 无法找到登录按钮: {str(e)}")
            login_button = None

        # 如果所有元素都找到了，尝试登录
        if username_input and password_input and login_button:
            logger.info("开始登录测试...")

            # 输入用户名
            try:
                username_input.clear()
                username_input.send_keys("wangdg68")
                logger.info("已输入用户名")
            except Exception as e:
                logger.error(f"输入用户名失败: {str(e)}")
                return

            # 输入密码
            try:
                password_input.clear()
                password_input.send_keys("wap951020ZJL")
                logger.info("已输入密码")
            except Exception as e:
                logger.error(f"输入密码失败: {str(e)}")
                return

            # 点击登录按钮
            try:
                logger.info("点击登录按钮...")
                login_button.click()

                # 等待登录结果
                logger.info("等待登录结果...")
                WebDriverWait(driver, 10).until(
                    EC.url_contains("index.html")
                )
                logger.info("✓ 登录成功!")
                logger.info(f"当前URL: {driver.current_url}")

            except TimeoutException:
                logger.error("✗ 登录超时，可能用户名或密码错误")
                # 检查是否有错误提示
                try:
                    error_elements = driver.find_elements(By.CLASS_NAME, "error")
                    for error in error_elements:
                        logger.info(f"错误提示: {error.text}")
                except:
                    pass
            except Exception as e:
                logger.error(f"✗ 登录过程出错: {str(e)}")
        else:
            logger.error("无法找到必要的登录元素")

        input("按回车键结束...")

    except Exception as e:
        logger.error(f"测试过程中出现错误: {str(e)}")
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_login()

