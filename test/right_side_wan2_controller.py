#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版TP-Link路由器WAN2连接控制脚本
专门针对右侧WAN2接口进行控制
"""

import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import json

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TPLinkWAN2Controller:
    def __init__(self, router_ip="192.168.1.1", username="wangdg68", password="wap951020ZJL", headless=True):
        self.router_ip = router_ip
        self.username = username
        self.password = password
        self.headless = headless
        self.driver = None

    def setup_driver(self):
        """设置Chrome WebDriver"""
        chrome_options = webdriver.ChromeOptions()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)

    def login(self):
        """登录路由器管理界面"""
        login_url = f"http://{self.router_ip}/webpages/login.html"
        logger.info(f"正在访问登录页面: {login_url}")

        self.driver.get(login_url)

        # 等待登录表单加载
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, "login-btn"))
        )

        # 输入用户名和密码
        username_input = self.driver.find_element(By.ID, "userName")
        password_input = self.driver.find_element(By.ID, "pcPassword")
        login_button = self.driver.find_element(By.ID, "login-btn")

        username_input.clear()
        username_input.send_keys(self.username)

        password_input.clear()
        password_input.send_keys(self.password)

        logger.info("正在登录...")
        login_button.click()

        # 等待登录完成
        try:
            WebDriverWait(self.driver, 20).until(
                EC.url_contains("index.html")
            )
            logger.info("登录成功")
            return True
        except TimeoutException:
            logger.error("登录超时，可能用户名或密码错误")
            return False

    def navigate_to_wan_settings(self):
        """导航到WAN设置页面"""
        try:
            # 等待主界面加载完成
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "main-menu"))
            )

            logger.info("正在导航到基本设置-WAN设置...")

            # 点击"基本设置"菜单
            basic_settings_menu = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='基本设置']"))
            )
            basic_settings_menu.click()
            time.sleep(1)

            # 点击"WAN设置"子菜单
            wan_settings_menu = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='WAN设置']"))
            )
            wan_settings_menu.click()
            time.sleep(2)

            logger.info("已进入WAN设置页面")
            return True

        except TimeoutException:
            logger.error("导航到WAN设置超时")
            return False
        except Exception as e:
            logger.error(f"导航到WAN设置时出错: {str(e)}")
            return False

    def select_right_wan2_and_control(self):
        """选择右侧WAN2并执行断开/连接操作"""
        try:
            logger.info("正在查找右侧WAN2设置...")

            # 等待WAN设置页面加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "main-frame"))
            )

            # 使用位置定位方法查找右侧的WAN2标签
            # 获取所有标签元素
            tab_elements = self.driver.find_elements(By.CSS_SELECTOR, ".tab-nav li")

            if len(tab_elements) >= 2:
                # 根据位置坐标判断右侧的WAN2标签
                # 获取第一个和第二个标签的位置
                first_tab_location = tab_elements[0].location
                second_tab_location = tab_elements[1].location

                # 判断哪个是右侧的WAN2（x坐标更大的是右侧）
                if first_tab_location['x'] > second_tab_location['x']:
                    right_wan2_tab = tab_elements[0]
                else:
                    right_wan2_tab = tab_elements[1]

                right_wan2_tab.click()
                logger.info("已选择右侧WAN2设置")
                time.sleep(1)
            else:
                logger.error("未找到足够的标签页")
                return False

            # 查找并点击断开按钮
            # 使用更精确的选择器来定位右侧的按钮
            disconnect_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), '断开')]")

            if len(disconnect_buttons) >= 2:
                # 同样使用位置判断找到右侧的断开按钮
                first_btn_location = disconnect_buttons[0].location
                second_btn_location = disconnect_buttons[1].location

                # 判断哪个是右侧的断开按钮（x坐标更大的是右侧）
                if first_btn_location['x'] > second_btn_location['x']:
                    right_disconnect_button = disconnect_buttons[0]
                else:
                    right_disconnect_button = disconnect_buttons[1]

                right_disconnect_button.click()
                logger.info("已点击右侧WAN2断开按钮")
                time.sleep(3)
            else:
                # 如果只有一个断开按钮，直接点击
                if disconnect_buttons:
                    disconnect_buttons[0].click()
                    logger.info("已点击断开按钮")
                    time.sleep(3)
                else:
                    logger.error("未找到断开按钮")
                    return False

            # 查找并点击连接按钮
            connect_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), '连接')]")

            if len(connect_buttons) >= 2:
                # 同样使用位置判断找到右侧的连接按钮
                first_btn_location = connect_buttons[0].location
                second_btn_location = connect_buttons[1].location

                # 判断哪个是右侧的连接按钮（x坐标更大的是右侧）
                if first_btn_location['x'] > second_btn_location['x']:
                    right_connect_button = connect_buttons[0]
                else:
                    right_connect_button = connect_buttons[1]

                right_connect_button.click()
                logger.info("已点击右侧WAN2连接按钮")
                time.sleep(5)
            else:
                # 如果只有一个连接按钮，直接点击
                if connect_buttons:
                    connect_buttons[0].click()
                    logger.info("已点击连接按钮")
                    time.sleep(5)
                else:
                    logger.error("未找到连接按钮")
                    return False

            logger.info("右侧WAN2连接控制完成")
            return True

        except TimeoutException:
            logger.error("操作右侧WAN2设置超时")
            return False
        except Exception as e:
            logger.error(f"操作右侧WAN2设置时出错: {str(e)}")
            return False

    def run(self):
        """执行完整的WAN2控制流程"""
        try:
            self.setup_driver()
            if self.login():
                if self.navigate_to_wan_settings():
                    return self.select_right_wan2_and_control()
            return False
        except Exception as e:
            logger.error(f"执行过程中出现错误: {str(e)}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()

def load_config(config_file):
    """从配置文件加载参数"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.warning(f"加载配置文件失败: {str(e)}")
        return {}

def main():
    parser = argparse.ArgumentParser(description="TP-Link路由器右侧WAN2连接控制器")
    parser.add_argument('--router-ip', default='192.168.1.1', help='路由器IP地址')
    parser.add_argument('--username', default='wangdg68', help='登录用户名')
    parser.add_argument('--password', default='wap951020ZJL', help='登录密码')
    parser.add_argument('--no-headless', action='store_true', help='禁用无头模式（用于调试）')
    parser.add_argument('--config', help='配置文件路径')

    args = parser.parse_args()

    # 如果提供了配置文件，优先使用配置文件中的设置
    if args.config:
        config = load_config(args.config)
        router_ip = config.get('router_ip', args.router_ip)
        username = config.get('username', args.username)
        password = config.get('password', args.password)
        headless = config.get('headless', not args.no_headless)
    else:
        router_ip = args.router_ip
        username = args.username
        password = args.password
        headless = not args.no_headless

    controller = TPLinkWAN2Controller(
        router_ip=router_ip,
        username=username,
        password=password,
        headless=headless
    )

    success = controller.run()

    if success:
        logger.info("右侧WAN2连接控制操作成功完成")
    else:
        logger.error("右侧WAN2连接控制操作失败")
        exit(1)

if __name__ == "__main__":
    main()

