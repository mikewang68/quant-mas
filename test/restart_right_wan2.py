#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TP-Link路由器右侧WAN2重启和记录脚本
专门针对右侧WAN2接口进行重启操作，并记录操作日志
"""

import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging
import json
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TPLinkRightWAN2Controller:
    def __init__(self, router_ip="192.168.1.1", username="wangdg68", password="wap951020ZJL", headless=True, log_file="wan2_operations.log"):
        self.router_ip = router_ip
        self.username = username
        self.password = password
        self.headless = headless
        self.log_file = log_file
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

    def find_rightmost_buttons(self):
        """通过坐标算法找到最右侧的断开和连接按钮"""
        try:
            logger.info("正在通过坐标算法查找最右侧的WAN2按钮...")

            # 等待页面加载完成
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "main-frame"))
            )

            # 获取所有按钮元素
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")

            # 存储符合条件的按钮
            disconnect_buttons = []
            connect_buttons = []

            # 遍历所有按钮，筛选出包含"断开"或"连接"文本的按钮
            for button in all_buttons:
                try:
                    # 检查按钮是否可见且可点击
                    if button.is_displayed() and button.is_enabled():
                        text = button.text.strip()
                        location = button.location
                        size = button.size

                        # 计算按钮中心点的坐标
                        center_x = location['x'] + size['width'] / 2
                        center_y = location['y'] + size['height'] / 2

                        # 记录符合条件的按钮
                        if "断开" in text:
                            disconnect_buttons.append({
                                'element': button,
                                'text': text,
                                'x': center_x,
                                'y': center_y,
                                'location': location,
                                'size': size
                            })
                            logger.debug(f"发现断开按钮: '{text}' 位置({center_x}, {center_y})")
                        elif "连接" in text:
                            connect_buttons.append({
                                'element': button,
                                'text': text,
                                'x': center_x,
                                'y': center_y,
                                'location': location,
                                'size': size
                            })
                            logger.debug(f"发现连接按钮: '{text}' 位置({center_x}, {center_y})")
                except Exception as e:
                    continue  # 跳过无法处理的元素

            # 如果没有找到按钮，返回None
            if not disconnect_buttons and not connect_buttons:
                logger.warning("未找到任何WAN2控制按钮")
                return None, None

            # 根据坐标算法确定最右侧的按钮
            # 方法：选择x坐标最大的按钮（最靠右的）
            rightmost_disconnect = None
            rightmost_connect = None

            if disconnect_buttons:
                # 按x坐标排序，选择最右侧的断开按钮
                disconnect_buttons.sort(key=lambda b: b['x'], reverse=True)
                rightmost_disconnect = disconnect_buttons[0]['element']
                logger.info(f"确定最右侧断开按钮: '{disconnect_buttons[0]['text']}' x={disconnect_buttons[0]['x']}")

            if connect_buttons:
                # 按x坐标排序，选择最右侧的连接按钮
                connect_buttons.sort(key=lambda b: b['x'], reverse=True)
                rightmost_connect = connect_buttons[0]['element']
                logger.info(f"确定最右侧连接按钮: '{connect_buttons[0]['text']}' x={connect_buttons[0]['x']}")

            return rightmost_disconnect, rightmost_connect

        except Exception as e:
            logger.error(f"查找最右侧按钮时出错: {str(e)}")
            return None, None

    def control_wan2(self):
        """控制WAN2接口（断开然后连接）"""
        try:
            logger.info("开始控制右侧WAN2接口...")

            # 使用坐标算法找到最右侧的按钮
            disconnect_button, connect_button = self.find_rightmost_buttons()

            if not disconnect_button and not connect_button:
                logger.error("无法找到右侧WAN2控制按钮")
                return False

            # 记录操作时间
            operation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 执行断开操作
            if disconnect_button:
                logger.info("正在断开右侧WAN2连接...")
                # 滚动到元素位置确保可见
                self.driver.execute_script("arguments[0].scrollIntoView(true);", disconnect_button)
                time.sleep(1)
                disconnect_button.click()
                time.sleep(3)
                logger.info("右侧WAN2已断开")

                # 记录断开操作
                self.record_operation(f"[{operation_time}] 断开右侧WAN2连接")
            else:
                logger.warning("未找到断开按钮，跳过断开步骤")

            # 执行连接操作
            if connect_button:
                logger.info("正在连接右侧WAN2...")
                # 滚动到元素位置确保可见
                self.driver.execute_script("arguments[0].scrollIntoView(true);", connect_button)
                time.sleep(1)
                connect_button.click()
                time.sleep(5)  # 等待连接建立
                logger.info("右侧WAN2已连接")

                # 记录连接操作
                reconnect_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.record_operation(f"[{reconnect_time}] 连接右侧WAN2")
            else:
                logger.warning("未找到连接按钮，跳过连接步骤")

            logger.info("右侧WAN2连接控制完成")
            return True

        except Exception as e:
            logger.error(f"控制右侧WAN2时出错: {str(e)}")
            return False

    def record_operation(self, message):
        """记录操作到日志文件"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"{message}\n")
            logger.info(f"操作已记录: {message}")
        except Exception as e:
            logger.error(f"记录操作失败: {str(e)}")

    def run(self):
        """执行完整的右侧WAN2控制流程"""
        try:
            self.setup_driver()
            if self.login():
                if self.navigate_to_wan_settings():
                    return self.control_wan2()
            return False
        except Exception as e:
            logger.error(f"执行过程中出现错误: {str(e)}")
            # 记录错误
            error_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.record_operation(f"[{error_time}] 错误: {str(e)}")
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
    parser = argparse.ArgumentParser(description="TP-Link路由器右侧WAN2重启控制器")
    parser.add_argument('--router-ip', default='192.168.1.1', help='路由器IP地址')
    parser.add_argument('--username', default='wangdg68', help='登录用户名')
    parser.add_argument('--password', default='wap951020ZJL', help='登录密码')
    parser.add_argument('--no-headless', action='store_true', help='禁用无头模式（用于调试）')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--log-file', default='wan2_operations.log', help='操作日志文件路径')

    args = parser.parse_args()

    # 如果提供了配置文件，优先使用配置文件中的设置
    if args.config:
        config = load_config(args.config)
        router_ip = config.get('router_ip', args.router_ip)
        username = config.get('username', args.username)
        password = config.get('password', args.password)
        headless = config.get('headless', not args.no_headless)
        log_file = config.get('log_file', args.log_file)
    else:
        router_ip = args.router_ip
        username = args.username
        password = args.password
        headless = not args.no_headless
        log_file = args.log_file

    controller = TPLinkRightWAN2Controller(
        router_ip=router_ip,
        username=username,
        password=password,
        headless=headless,
        log_file=log_file
    )

    success = controller.run()

    if success:
        logger.info("右侧WAN2重启操作成功完成")
        print("右侧WAN2重启操作成功完成")
    else:
        logger.error("右侧WAN2重启操作失败")
        print("右侧WAN2重启操作失败")
        exit(1)

if __name__ == "__main__":
    main()

