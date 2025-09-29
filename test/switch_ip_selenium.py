import time
import sys
import argparse
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
)
import json
import os
import requests

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("switch_ip_selenium.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class RouterControllerSelenium:
    def __init__(
        self,
        config_file=None,
        router_ip=None,
        username=None,
        password=None,
        headless=True,
    ):
        """初始化路由器控制器"""
        self.config = self._load_config(config_file, router_ip, username, password)
        self.base_url = f"http://{self.config['router_ip']}"
        self.driver = None
        self.headless = headless
        logger.info(f"初始化TP-Link路由器控制器: {self.base_url}")

    def _load_config(self, config_file, router_ip, username, password):
        """加载配置"""
        config = {
            "router_ip": "192.168.1.1",
            "username": "wangdg68",
            "password": "wap951020ZJL",
        }

        # 如果提供了配置文件，从文件加载
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    file_config = json.load(f)
                    config.update(file_config)
                logger.info(f"从配置文件加载配置: {config_file}")
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}")

        # 如果提供了命令行参数，覆盖配置
        if router_ip:
            config["router_ip"] = router_ip
        if username:
            config["username"] = username
        if password:
            config["password"] = password

        return config

    def setup_driver(self):
        """设置Chrome WebDriver"""
        logger.info("设置Chrome WebDriver...")
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument("--allow-running-insecure-content")

        # 根据参数决定是否使用headless模式
        if self.headless:
            chrome_options.add_argument("--headless")

        # 设置窗口大小
        chrome_options.add_argument("--window-size=1920,1080")

        try:
            # 自动下载并设置ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(3)  # 减少隐式等待时间
            logger.info("Chrome WebDriver设置成功")
            return True
        except Exception as e:
            logger.error(f"Chrome WebDriver设置失败: {e}")
            return False

    def _safe_click(self, element):
        """安全点击元素"""
        try:
            # 滚动到元素并确保可见
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)

            # 尝试直接点击
            element.click()
            return True
        except ElementNotInteractableException:
            # 如果直接点击失败，尝试使用JavaScript
            logger.warning("直接点击失败，尝试使用JavaScript点击")
            try:
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except Exception as e:
                logger.error(f"JavaScript点击也失败: {e}")
                return False
        except Exception as e:
            logger.error(f"点击元素时出错: {e}")
            return False

    def _find_element_safely(self, selectors, timeout=3, clickable=False):
        """安全查找元素"""
        for selector_type, selector_value in selectors:
            try:
                logger.debug(f"尝试定位元素: {selector_type} = {selector_value}")
                if clickable:
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                else:
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )

                if element:
                    logger.debug("成功找到元素")
                    # 记录元素的位置信息用于调试
                    try:
                        location = element.location
                        size = element.size
                        logger.debug(f"元素位置: x={location['x']}, y={location['y']}, 宽度={size['width']}, 高度={size['height']}")
                    except Exception as e:
                        logger.debug(f"无法获取元素位置信息: {e}")
                    return element
            except TimeoutException:
                continue
            except Exception as e:
                logger.warning(f"查找元素时出错: {e}")
                continue

        return None

    def get_current_ip(self):
        """获取当前公网IP地址"""
        try:
            logger.info("获取当前公网IP地址...")
            response = requests.get("https://httpbin.org/ip", timeout=10)
            ip = response.json()["origin"]
            logger.info(f"当前公网IP地址: {ip}")
            return ip
        except Exception as e:
            logger.error(f"获取公网IP地址失败: {e}")
            return None

    def login(self):
        """登录路由器管理界面"""
        try:
            logger.info("开始登录路由器...")
            logger.info(f"路由器地址: {self.base_url}")

            # 访问登录页面
            login_url = f"{self.base_url}/webpages/login.html"
            logger.info(f"访问登录页面: {login_url}")
            self.driver.get(login_url)

            # 减少等待时间
            logger.info("等待页面加载...")
            time.sleep(2)

            # 定位用户名输入框
            logger.info("定位用户名输入框...")
            username_selectors = [
                (By.ID, "username"),
                (By.NAME, "username"),
                (By.ID, "userName"),
                (By.CSS_SELECTOR, "input[type='text']"),
            ]

            username_field = self._find_element_safely(username_selectors)
            if not username_field:
                logger.error("错误: 未找到用户名输入框")
                return False

            logger.info("成功找到用户名输入框")

            # 输入用户名
            logger.info(f"输入用户名: {self.config['username']}")
            username_field.clear()
            username_field.send_keys(self.config["username"])

            # 定位密码输入框
            logger.info("定位密码输入框...")
            password_selectors = [
                (
                    By.XPATH,
                    "//input[@type='password' or contains(@name, 'pass') or contains(@id, 'pass')]",
                ),
                (By.ID, "pcPassword"),
                (By.NAME, "password"),
                (By.ID, "password"),
            ]

            # 查找所有可能的密码字段
            password_fields = []
            for selector_type, selector_value in password_selectors:
                try:
                    elements = self.driver.find_elements(selector_type, selector_value)
                    password_fields.extend(elements)
                except:
                    continue

            password_field = None
            for field in password_fields:
                if field.is_displayed() and field.is_enabled():
                    password_field = field
                    break

            if not password_field:
                logger.error("错误: 未找到合适的密码输入框")
                return False

            logger.info("成功找到密码输入框")

            # 输入密码
            logger.info("输入密码...")
            password_field.clear()
            password_field.send_keys(self.config["password"])

            # 定位登录按钮
            logger.info("定位登录按钮...")
            login_button_selectors = [
                (By.XPATH, "//span[contains(text(), '登录')]"),
                (By.ID, "loginBtn"),
                (By.XPATH, "//input[@type='submit']"),
                (
                    By.XPATH,
                    "//button[contains(text(), '登录') or contains(text(), 'Login')]",
                ),
            ]

            login_button = self._find_element_safely(
                login_button_selectors, clickable=True
            )

            # 如果通过标准方式未找到，尝试查找包含"登录"文本的span元素
            if not login_button:
                login_spans = self.driver.find_elements(
                    By.XPATH, "//span[contains(text(), '登录')]"
                )
                for span in login_spans:
                    try:
                        button = span.find_element(
                            By.XPATH,
                            "./ancestor::div[contains(@class, 'button') or contains(@class, 'btn')]",
                        )
                        if button.is_displayed() and button.is_enabled():
                            login_button = button
                            break
                    except:
                        continue

            if not login_button:
                logger.error("错误: 未找到登录按钮")
                return False

            logger.info("成功找到登录按钮")

            # 点击登录按钮
            logger.info("点击登录按钮...")
            if not self._safe_click(login_button):
                logger.error("点击登录按钮失败")
                return False

            # 减少等待时间
            logger.info("等待页面跳转...")
            time.sleep(3)

            # 检查是否登录成功
            current_url = self.driver.current_url
            logger.info(f"登录后页面URL: {current_url}")

            if "/webpages/index.html" in current_url:
                logger.info("登录成功!")
                return True
            else:
                logger.warning("登录可能失败")
                return False

        except Exception as e:
            logger.error(f"登录过程中出错: {e}")
            import traceback

            traceback.print_exc()
            return False

    def navigate_to_wan2_settings(self):
        """导航到WAN2设置页面"""
        try:
            logger.info("导航到WAN2设置页面...")

            # 减少等待时间
            time.sleep(1)

            # 尝试多种方式定位"基本设置"菜单
            logger.info("查找基本设置菜单...")
            basic_settings_selectors = [
                (
                    By.XPATH,
                    "//a[contains(text(), '基本设置') or contains(text(), 'Basic Settings')]",
                ),
                (
                    By.XPATH,
                    "//span[contains(text(), '基本设置') or contains(text(), 'Basic Settings')]",
                ),
                (By.LINK_TEXT, "基本设置"),
                (By.LINK_TEXT, "Basic Settings"),
            ]

            basic_settings_menu = self._find_element_safely(
                basic_settings_selectors, clickable=True
            )

            if not basic_settings_menu:
                logger.error("错误: 未找到基本设置菜单")
                return False

            logger.info("成功找到基本设置菜单")

            # 点击基本设置菜单
            logger.info("点击基本设置菜单...")
            if not self._safe_click(basic_settings_menu):
                logger.error("点击基本设置菜单失败")
                return False

            time.sleep(1)

            # 尝试多种方式定位"WAN设置"菜单
            logger.info("查找WAN设置菜单...")
            wan_settings_selectors = [
                (
                    By.XPATH,
                    "//a[contains(text(), 'WAN设置') or contains(text(), 'WAN Settings')]",
                ),
                (
                    By.XPATH,
                    "//span[contains(text(), 'WAN设置') or contains(text(), 'WAN Settings')]",
                ),
                (By.LINK_TEXT, "WAN设置"),
                (By.LINK_TEXT, "WAN Settings"),
            ]

            wan_settings_menu = self._find_element_safely(
                wan_settings_selectors, clickable=True
            )

            if not wan_settings_menu:
                logger.error("错误: 未找到WAN设置菜单")
                return False

            logger.info("成功找到WAN设置菜单")

            # 点击WAN设置菜单
            logger.info("点击WAN设置菜单...")
            if not self._safe_click(wan_settings_menu):
                logger.error("点击WAN设置菜单失败")
                return False

            # 减少等待时间
            logger.info("等待WAN设置页面加载...")
            time.sleep(2)

            # 在右边的窗口里选择WAN2设置（基于位置识别右侧WAN2）
            logger.info("在右边窗口查找WAN2设置选项...")
            try:
                # 获取所有可能的WAN2元素
                wan2_elements = self.driver.find_elements(
                    By.XPATH, "//*[contains(text(), 'WAN2') or contains(@id, 'wan2') or contains(@class, 'wan2')]"
                )

                # 查找位于右侧的WAN2元素（x坐标在900-1500之间）
                right_wan2_element = None
                right_wan2_elements = []
                for element in wan2_elements:
                    if element.is_displayed():
                        # 获取元素位置
                        location = element.location
                        x = location['x']
                        # 右侧元素通常x坐标较大（根据之前的调试信息，右侧元素x坐标在900-1500之间）
                        if 900 <= x <= 1500:
                            right_wan2_elements.append((element, x))
                            logger.debug(f"找到右侧WAN2元素: 文本='{element.text}', x坐标={x}")

                # 选择x坐标最大的元素（最右侧的）
                if right_wan2_elements:
                    right_wan2_elements.sort(key=lambda x: x[1], reverse=True)
                    right_wan2_element = right_wan2_elements[0][0]
                    logger.info(f"成功找到右侧WAN2设置选项 (x坐标: {right_wan2_elements[0][1]})")

                    # 点击右侧WAN2设置选项
                    logger.info("点击右侧WAN2设置选项...")
                    if not self._safe_click(right_wan2_element):
                        logger.warning("点击右侧WAN2设置选项失败")
                        return False
                else:
                    logger.warning("未找到右侧WAN2特定设置，将继续使用默认WAN设置")

            except Exception as e:
                logger.warning(f"查找右侧WAN2设置时出错: {e}")
                # 回退到原来的查找方式
                wan2_selectors = [
                    (
                        By.XPATH,
                        "//a[contains(text(), 'WAN2') or contains(@href, 'wan2') or contains(@id, 'wan2')]",
                    ),
                    (By.XPATH, "//div[contains(@id, 'wan2') or contains(@class, 'wan2')]"),
                ]

                wan2_element = self._find_element_safely(wan2_selectors, clickable=True)

                if not wan2_element:
                    logger.warning("未找到WAN2特定设置，将继续使用默认WAN设置")
                else:
                    logger.info("成功找到WAN2设置选项")
                    # 点击WAN2设置选项
                    logger.info("点击WAN2设置选项...")
                    if not self._safe_click(wan2_element):
                        logger.warning("点击WAN2设置选项失败，将继续使用默认WAN设置")

            logger.info("成功导航到WAN设置页面")
            return True

        except Exception as e:
            logger.error(f"导航到WAN2设置时出错: {e}")
            import traceback

            traceback.print_exc()
            return False

    def disconnect_wan2(self):
        """断开WAN2连接"""
        try:
            logger.info("断开WAN2连接...")

            # 首先尝试基于位置识别右侧的断开按钮
            logger.info("查找右侧WAN2断开按钮...")
            try:
                # 获取所有可能的断开按钮元素
                disconnect_elements = self.driver.find_elements(
                    By.XPATH, "//button[contains(text(), '断开') or contains(text(), 'Disconnect')]"
                )

                # 如果没有找到，尝试查找input按钮
                if not disconnect_elements:
                    disconnect_elements = self.driver.find_elements(
                        By.XPATH, "//input[@type='button' and (contains(@value, '断开') or contains(@value, 'Disconnect'))]"
                    )

                # 查找位于右侧的断开按钮（x坐标在900-1500之间）
                right_disconnect_button = None
                right_disconnect_buttons = []
                for element in disconnect_elements:
                    if element.is_displayed():
                        # 获取元素位置
                        location = element.location
                        x = location['x']
                        # 右侧元素通常x坐标较大（根据之前的调试信息，右侧元素x坐标在900-1500之间）
                        if 900 <= x <= 1500:
                            right_disconnect_buttons.append((element, x))
                            logger.debug(f"找到右侧断开按钮: 文本='{element.text}', x坐标={x}")

                # 选择x坐标最大的元素（最右侧的）
                if right_disconnect_buttons:
                    right_disconnect_buttons.sort(key=lambda x: x[1], reverse=True)
                    right_disconnect_button = right_disconnect_buttons[0][0]
                    logger.info(f"成功找到右侧WAN2断开按钮 (x坐标: {right_disconnect_buttons[0][1]})")

                    # 点击右侧WAN2断开按钮
                    logger.info("点击右侧WAN2断开按钮...")
                    if not self._safe_click(right_disconnect_button):
                        logger.warning("点击右侧WAN2断开按钮失败")
                        return False
                else:
                    logger.warning("未找到右侧WAN2断开按钮，将使用标准方法查找")
                    # 回退到标准方法
                    raise Exception("未找到右侧按钮，需要回退")

            except Exception as e:
                logger.warning(f"基于位置查找右侧断开按钮失败: {e}")
                # 回退到原来的查找方式
                disconnect_selectors = [
                    (
                        By.XPATH,
                        "//button[contains(text(), '断开') or contains(text(), 'Disconnect')]",
                    ),
                    (
                        By.XPATH,
                        "//input[@type='button' and (contains(@value, '断开') or contains(@value, 'Disconnect'))]",
                    ),
                    (
                        By.XPATH,
                        "//*[contains(@class, 'disconnect') and (contains(text(), '断开') or contains(text(), 'Disconnect'))]",
                    ),
                    (
                        By.XPATH,
                        "//*[contains(text(), '断开') or contains(text(), 'Disconnect')]",
                    ),
                ]

                disconnect_button = self._find_element_safely(
                    disconnect_selectors, clickable=True
                )

                if not disconnect_button:
                    logger.warning("未通过标准方式找到断开按钮，尝试更通用的查找方法")
                    # 尝试更通用的查找方法
                    try:
                        # 查找所有按钮并检查文本
                        buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        for btn in buttons:
                            if btn.is_displayed() and (
                                "断开" in btn.text or "Disconnect" in btn.text
                            ):
                                disconnect_button = btn
                                logger.info("通过文本内容找到断开按钮")
                                break

                        # 如果还没找到，尝试查找input按钮
                        if not disconnect_button:
                            input_buttons = self.driver.find_elements(
                                By.XPATH, "//input[@type='button']"
                            )
                            for btn in input_buttons:
                                value = btn.get_attribute("value")
                                if btn.is_displayed() and (
                                    value and ("断开" in value or "Disconnect" in value)
                                ):
                                    disconnect_button = btn
                                    logger.info("通过input value找到断开按钮")
                                    break
                    except Exception as e:
                        logger.error(f"通用查找方法失败: {e}")

                if not disconnect_button:
                    logger.error("错误: 仍然未找到断开按钮")
                    return False

                logger.info("成功找到断开按钮")

                # 点击断开按钮
                logger.info("点击断开按钮...")
                if not self._safe_click(disconnect_button):
                    logger.error("点击断开按钮失败")
                    return False

            # 减少等待时间
            time.sleep(1)

            logger.info("WAN2已断开连接")
            return True

        except Exception as e:
            logger.error(f"断开WAN2连接时出错: {e}")
            import traceback

            traceback.print_exc()
            return False

    def connect_wan2(self):
        """连接WAN2"""
        try:
            logger.info("连接WAN2...")

            # 首先尝试基于位置识别右侧的连接按钮
            logger.info("查找右侧WAN2连接按钮...")
            try:
                # 获取所有可能的连接按钮元素
                connect_elements = self.driver.find_elements(
                    By.XPATH, "//button[contains(text(), '连接') or contains(text(), 'Connect')]"
                )

                # 如果没有找到，尝试查找input按钮
                if not connect_elements:
                    connect_elements = self.driver.find_elements(
                        By.XPATH, "//input[@type='button' and (contains(@value, '连接') or contains(@value, 'Connect'))]"
                    )

                # 查找位于右侧的连接按钮（x坐标在900-1500之间）
                right_connect_button = None
                right_connect_buttons = []
                for element in connect_elements:
                    if element.is_displayed():
                        # 获取元素位置
                        location = element.location
                        x = location['x']
                        # 右侧元素通常x坐标较大（根据之前的调试信息，右侧元素x坐标在900-1500之间）
                        if 900 <= x <= 1500:
                            right_connect_buttons.append((element, x))
                            logger.debug(f"找到右侧连接按钮: 文本='{element.text}', x坐标={x}")

                # 选择x坐标最大的元素（最右侧的）
                if right_connect_buttons:
                    right_connect_buttons.sort(key=lambda x: x[1], reverse=True)
                    right_connect_button = right_connect_buttons[0][0]
                    logger.info(f"成功找到右侧WAN2连接按钮 (x坐标: {right_connect_buttons[0][1]})")
                    # 点击右侧WAN2连接按钮
                    logger.info("点击右侧WAN2连接按钮...")
                    if not self._safe_click(right_connect_button):
                        logger.warning("点击右侧WAN2连接按钮失败")
                        return False
                else:
                    logger.warning("未找到右侧WAN2连接按钮，将使用标准方法查找")
                    # 回退到标准方法
                    raise Exception("未找到右侧按钮，需要回退")

            except Exception as e:
                logger.warning(f"基于位置查找右侧连接按钮失败: {e}")
                # 回退到原来的查找方式
                connect_selectors = [
                    (
                        By.XPATH,
                        "//button[contains(text(), '连接') or contains(text(), 'Connect')]",
                    ),
                    (
                        By.XPATH,
                        "//input[@type='button' and (contains(@value, '连接') or contains(@value, 'Connect'))]",
                    ),
                    (
                        By.XPATH,
                        "//*[contains(@class, 'connect') and (contains(text(), '连接') or contains(text(), 'Connect'))]",
                    ),
                    (
                        By.XPATH,
                        "//*[contains(text(), '连接') or contains(text(), 'Connect')]",
                    ),
                ]

                connect_button = self._find_element_safely(
                    connect_selectors, clickable=True
                )

                if not connect_button:
                    logger.warning("未通过标准方式找到连接按钮，尝试更通用的查找方法")
                    # 尝试更通用的查找方法
                    try:
                        # 查找所有按钮并检查文本
                        buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        for btn in buttons:
                            if btn.is_displayed() and (
                                "连接" in btn.text or "Connect" in btn.text
                            ):
                                connect_button = btn
                                logger.info("通过文本内容找到连接按钮")
                                break

                        # 如果还没找到，尝试查找input按钮
                        if not connect_button:
                            input_buttons = self.driver.find_elements(
                                By.XPATH, "//input[@type='button']"
                            )
                            for btn in input_buttons:
                                value = btn.get_attribute("value")
                                if btn.is_displayed() and (
                                    value and ("连接" in value or "Connect" in value)
                                ):
                                    connect_button = btn
                                    logger.info("通过input value找到连接按钮")
                                    break
                    except Exception as e:
                        logger.error(f"通用查找方法失败: {e}")

                if not connect_button:
                    logger.error("错误: 仍然未找到连接按钮")
                    return False

                logger.info("成功找到连接按钮")

                # 点击连接按钮
                logger.info("点击连接按钮...")
                if not self._safe_click(connect_button):
                    logger.error("点击连接按钮失败")
                    return False

            # 减少等待时间
            time.sleep(1)

            logger.info("WAN2已连接")
            return True

        except Exception as e:
            logger.error(f"连接WAN2时出错: {e}")
            import traceback

            traceback.print_exc()
            return False

    def switch_ip_until_different(self, max_attempts=5, wait_time=3):
        """切换IP直到获得不同的IP地址"""
        logger.info("开始获取原始IP地址...")
        original_ip = self.get_current_ip()

        if not original_ip:
            logger.warning("无法获取原始IP地址，将直接执行断开和连接操作")

        attempt = 0

        while attempt < max_attempts:
            attempt += 1
            logger.info(f"\n--- 第 {attempt} 次尝试 ---")

            # 断开WAN2连接
            logger.info("断开WAN2连接...")
            if not self.disconnect_wan2():
                logger.warning("断开WAN2连接失败")
                time.sleep(wait_time)
                continue

            # 等待
            logger.info(f"等待{wait_time}秒...")
            time.sleep(wait_time)

            # 连接WAN2
            logger.info("连接WAN2...")
            if not self.connect_wan2():
                logger.warning("连接WAN2失败")
                time.sleep(wait_time)
                continue

            # 等待一段时间让连接建立
            logger.info(f"等待连接建立({wait_time * 2}秒)...")
            time.sleep(wait_time * 2)

            # 检查IP是否改变
            if original_ip:
                logger.info("检查IP地址是否改变...")
                new_ip = self.get_current_ip()

                if new_ip and new_ip != original_ip:
                    logger.info(f"IP地址已成功改变: {original_ip} -> {new_ip}")
                    return True
                elif new_ip:
                    logger.info(f"IP地址未改变: {new_ip}")
                else:
                    logger.warning("无法获取新的IP地址")
            else:
                logger.info("WAN2连接切换完成（未验证IP地址变化）")
                return True

        logger.error(f"已达到最大尝试次数 ({max_attempts})，未能完成IP切换")
        return False

    def switch_ip(self, wait_time=3):
        """切换IP：断开并重新连接WAN2"""
        logger.info("=" * 50)
        logger.info("开始切换TP-Link路由器WAN2连接")
        logger.info("=" * 50)

        # 设置WebDriver
        if not self.setup_driver():
            logger.error("错误: WebDriver设置失败")
            return False

        try:
            # 登录路由器
            if not self.login():
                logger.error("错误: 登录失败")
                return False

            # 导航到WAN2设置
            if not self.navigate_to_wan2_settings():
                logger.error("错误: 导航到WAN2设置失败")
                return False

            # 切换IP直到获得不同的IP地址
            logger.info("\n开始切换IP地址...")
            if self.switch_ip_until_different(wait_time=wait_time):
                logger.info("IP地址切换成功")
                return True
            else:
                logger.error("IP地址切换失败")
                return False

        except Exception as e:
            logger.error(f"执行过程中出错: {e}")
            import traceback

            traceback.print_exc()
            return False
        finally:
            # 关闭浏览器
            self.close()

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            logger.info("浏览器已关闭")


def main():
    parser = argparse.ArgumentParser(description="TP-Link路由器WAN2 IP切换脚本")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--router-ip", help="路由器IP地址")
    parser.add_argument("--username", help="路由器用户名")
    parser.add_argument("--password", help="路由器密码")
    parser.add_argument("--wait-time", type=int, default=3, help="等待时间(秒)")
    parser.add_argument("--no-headless", action="store_true", help="不使用headless模式")
    parser.add_argument("--attempts", type=int, default=5, help="最大尝试次数")

    args = parser.parse_args()

    logger.info("TP-Link路由器WAN2 IP切换脚本")
    logger.info("版本: 2.0 (增强版)")

    # 创建路由器控制器实例
    router = RouterControllerSelenium(
        config_file=args.config,
        router_ip=args.router_ip,
        username=args.username,
        password=args.password,
        headless=not args.no_headless,
    )

    # 执行IP切换
    success = router.switch_ip(wait_time=args.wait_time)

    if success:
        logger.info("\n恭喜! IP切换操作成功完成。")
        return 0
    else:
        logger.error("\n抱歉，IP切换操作失败。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
