#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版TP-Link路由器WAN2连接控制脚本
专门针对右侧WAN2接口进行控制，使用坐标定位确保准确性
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

class TPLinkRightWAN2Controller:
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
            time.sleep(3)  # 增加等待时间确保页面加载完成

            logger.info("已进入WAN设置页面")
            return True

        except TimeoutException:
            logger.error("导航到WAN设置超时")
            return False
        except Exception as e:
            logger.error(f"导航到WAN设置时出错: {str(e)}")
            return False

    def find_right_wan2_elements(self):
        """通过坐标定位找到右侧的WAN2元素"""
        try:
            logger.info("正在通过坐标定位查找右侧WAN2元素...")

            # 等待页面加载完成
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "main-frame"))
            )

            # 获取所有可能的按钮元素
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")

            # 查找具有"断开"或"连接"文本的按钮，并根据x坐标判断是否为右侧WAN2
            disconnect_buttons = []
            connect_buttons = []

            for button in all_buttons:
                try:
                    # 检查按钮是否可见且可点击
                    if button.is_displayed() and button.is_enabled():
                        text = button.text.strip()
                        location = button.location
                        size = button.size

                        # 计算按钮中心点的x坐标
                        center_x = location['x'] + size['width'] / 2

                        # 根据界面分析，右侧WAN2的按钮通常在页面右半部分
                        # 假设页面宽度为1920，右侧按钮的x坐标应该大于960
                        if center_x > 960:
                            if "断开" in text:
                                disconnect_buttons.append((button, center_x))
                                logger.info(f"找到右侧断开按钮: {text}, x坐标: {center_x}")
                            elif "连接" in text:
                                connect_buttons.append((button, center_x))
                                logger.info(f"找到右侧连接按钮: {text}, x坐标: {center_x}")
                except Exception as e:
                    continue  # 跳过无法处理的元素

            # 按x坐标排序，最右边的按钮应该是我们要找的
            if disconnect_buttons:
                disconnect_buttons.sort(key=lambda x: x[1], reverse=True)
                right_disconnect_button = disconnect_buttons[0][0]
                logger.info("已定位右侧WAN2断开按钮")
            else:
                right_disconnect_button = None
                logger.warning("未找到右侧WAN2断开按钮")

            if connect_buttons:
                connect_buttons.sort(key=lambda x: x[1], reverse=True)
                right_connect_button = connect_buttons[0][0]
                logger.info("已定位右侧WAN2连接按钮")
            else:
                right_connect_button = None
                logger.warning("未找到右侧WAN2连接按钮")

            return right_disconnect_button, right_connect_button

        except Exception as e:
            logger.error(f"查找右侧WAN2元素时出错: {str(e)}")
            return None, None

    def control_right_wan2(self):
        """控制右侧WAN2接口（断开然后连接）"""
        try:
            logger.info("开始控制右侧WAN2接口...")

            # 使用坐标定位找到右侧的WAN2按钮
            disconnect_button, connect_button = self.find_right_wan2_elements()

            if not disconnect_button and not connect_button:
                logger.error("无法找到右侧WAN2控制按钮")
                return False

            # 执行断开操作
            if disconnect_button:
                logger.info("正在断开右侧WAN2连接...")
                disconnect_button.click()
                time.sleep(3)
                logger.info("右侧WAN2已断开")
            else:
                logger.warning("未找到断开按钮，跳过断开步骤")

            # 执行连接操作
            if connect_button:
                logger.info("正在连接右侧WAN2...")
                connect_button.click()
                time.sleep(5)  # 等待连接建立
                logger.info("右侧WAN2已连接")
            else:
                logger.warning("未找到连接按钮，跳过连接步骤")

            logger.info("右侧WAN2连接控制完成")
            return True

        except Exception as e:
            logger.error(f"控制右侧WAN2时出错: {str(e)}")
            return False

    def run(self):
        """执行完整的右侧WAN2控制流程"""
        try:
            self.setup_driver()
            if self.login():
                if self.navigate_to_wan_settings():
                    return self.control_right_wan2()
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

    controller = TPLinkRightWAN2Controller(
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

