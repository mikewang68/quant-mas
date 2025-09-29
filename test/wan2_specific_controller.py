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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
import json
import os

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wan2_control.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TPLinkWAN2SpecificController:
    def __init__(self, config_file=None, router_ip=None, username=None, password=None, headless=True):
        """初始化路由器控制器"""
        self.config = self._load_config(config_file, router_ip, username, password)
        self.base_url = f"http://{self.config['router_ip']}"
        self.driver = None
        self.headless = headless
        logger.info(f"初始化TP-Link路由器WAN2专用控制器: {self.base_url}")

    def _load_config(self, config_file, router_ip, username, password):
        """加载配置"""
        config = {
            'router_ip': '192.168.1.1',
            'username': 'admin',
            'password': 'admin'
        }

        # 如果提供了配置文件，从文件加载
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    config.update(file_config)
                logger.info(f"从配置文件加载配置: {config_file}")
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}")

        # 如果提供了命令行参数，覆盖配置
        if router_ip:
            config['router_ip'] = router_ip
        if username:
            config['username'] = username
        if password:
            config['password'] = password

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
                    return element
            except TimeoutException:
                continue
            except Exception as e:
                logger.warning(f"查找元素时出错: {e}")
                continue

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
                (By.CSS_SELECTOR, "input[type='text']")
            ]

            username_field = self._find_element_safely(username_selectors)
            if not username_field:
                logger.error("错误: 未找到用户名输入框")
                return False

            logger.info("成功找到用户名输入框")

            # 输入用户名
            logger.info(f"输入用户名: {self.config['username']}")
            username_field.clear()
            username_field.send_keys(self.config['username'])

            # 定位密码输入框
            logger.info("定位密码输入框...")
            password_selectors = [
                (By.XPATH, "//input[@type='password' or contains(@name, 'pass') or contains(@id, 'pass')]"),
                (By.ID, "pcPassword"),
                (By.NAME, "password"),
                (By.ID, "password")
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
            password_field.send_keys(self.config['password'])

            # 定位登录按钮
            logger.info("定位登录按钮...")
            login_button_selectors = [
                (By.XPATH, "//span[contains(text(), '登录')]"),
                (By.ID, "loginBtn"),
                (By.XPATH, "//input[@type='submit']"),
                (By.XPATH, "//button[contains(text(), '登录') or contains(text(), 'Login')]")
            ]

            login_button = self._find_element_safely(login_button_selectors, clickable=True)

            # 如果通过标准方式未找到，尝试查找包含"登录"文本的span元素
            if not login_button:
                login_spans = self.driver.find_elements(By.XPATH, "//span[contains(text(), '登录')]")
                for span in login_spans:
                    try:
                        button = span.find_element(By.XPATH, "./ancestor::div[contains(@class, 'button') or contains(@class, 'btn')]")
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
                (By.XPATH, "//a[contains(text(), '基本设置') or contains(text(), 'Basic Settings')]"),
                (By.XPATH, "//span[contains(text(), '基本设置') or contains(text(), 'Basic Settings')]"),
                (By.LINK_TEXT, "基本设置"),
                (By.LINK_TEXT, "Basic Settings")
            ]

            basic_settings_menu = self._find_element_safely(basic_settings_selectors, clickable=True)

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
                (By.XPATH, "//a[contains(text(), 'WAN设置') or contains(text(), 'WAN Settings')]"),
                (By.XPATH, "//span[contains(text(), 'WAN设置') or contains(text(), 'WAN Settings')]"),
                (By.LINK_TEXT, "WAN设置"),
                (By.LINK_TEXT, "WAN Settings")
            ]

            wan_settings_menu = self._find_element_safely(wan_settings_selectors, clickable=True)

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

            logger.info("成功导航到WAN设置页面")
            return True

        except Exception as e:
            logger.error(f"导航到WAN2设置时出错: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _find_wan2_specific_button(self, action_text):
        """查找WAN2特定的断开/连接按钮"""
        try:
            logger.info(f"查找WAN2特定的{action_text}按钮...")

            # 首先尝试查找包含"WAN2"文本的元素附近的按钮
            wan2_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'WAN2') or contains(@id, 'wan2') or contains(@class, 'wan2')]")
            logger.info(f"找到 {len(wan2_elements)} 个WAN2相关元素")

            # 查找所有按钮
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            input_buttons = self.driver.find_elements(By.XPATH, "//input[@type='button']")
            all_buttons.extend(input_buttons)

            logger.info(f"总共找到 {len(all_buttons)} 个按钮")

            # 查找WAN2特定的按钮
            for button in all_buttons:
                if not button.is_displayed():
                    continue

                button_text = button.text or button.get_attribute("value") or ""
                logger.debug(f"检查按钮: '{button_text}'")

                # 如果按钮文本包含操作文本（断开/连接）且在WAN2区域附近
                if action_text in button_text or action_text.lower() in button_text.lower():
                    # 检查按钮是否在WAN2区域附近
                    try:
                        # 获取按钮位置
                        button_location = button.location_once_scrolled_into_view
                        logger.debug(f"按钮位置: {button_location}")

                        # 检查附近是否有WAN2标识
                        for wan2_elem in wan2_elements:
                            if wan2_elem.is_displayed():
                                wan2_location = wan2_elem.location_once_scrolled_into_view
                                # 计算距离
                                distance = abs(button_location['y'] - wan2_location['y'])
                                if distance < 200:  # 如果在200像素范围内
                                    logger.info(f"找到WAN2特定的{action_text}按钮: '{button_text}'")
                                    return button
                    except Exception as e:
                        logger.warning(f"检查按钮位置时出错: {e}")
                        # 如果位置检查失败，仍然返回找到的按钮
                        logger.info(f"返回找到的{action_text}按钮: '{button_text}'")
                        return button

            # 如果没找到WAN2特定按钮，尝试更通用的方法
            logger.warning(f"未找到WAN2特定的{action_text}按钮，尝试通用方法")
            for button in all_buttons:
                if not button.is_displayed():
                    continue

                button_text = button.text or button.get_attribute("value") or ""
                if action_text in button_text or action_text.lower() in button_text.lower():
                    logger.info(f"找到通用的{action_text}按钮: '{button_text}'")
                    return button

            logger.error(f"未找到{action_text}按钮")
            return None

        except Exception as e:
            logger.error(f"查找WAN2特定按钮时出错: {e}")
            import traceback
            traceback.print_exc()
            return None

    def disconnect_wan2(self):
        """断开WAN2连接"""
        try:
            logger.info("断开WAN2连接...")

            # 使用专门的方法查找WAN2的断开按钮
            disconnect_button = self._find_wan2_specific_button("断开")

            if not disconnect_button:
                logger.warning("未找到WAN2特定的断开按钮，尝试查找所有断开按钮...")
                # 尝试多种方式定位"断开"按钮
                disconnect_selectors = [
                    (By.XPATH, "//button[contains(text(), '断开') or contains(text(), 'Disconnect')]"),
                    (By.XPATH, "//input[@type='button' and (contains(@value, '断开') or contains(@value, 'Disconnect'))]"),
                    (By.XPATH, "//*[contains(@class, 'disconnect') and (contains(text(), '断开') or contains(text(), 'Disconnect'))]"),
                    (By.XPATH, "//*[contains(text(), '断开') or contains(text(), 'Disconnect')]")
                ]

                disconnect_button = self._find_element_safely(disconnect_selectors, clickable=True)

                if not disconnect_button:
                    logger.warning("未通过标准方式找到断开按钮，尝试更通用的查找方法")
                    # 尝试更通用的查找方法
                    try:
                        # 查找所有按钮并检查文本
                        buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        for btn in buttons:
                            if btn.is_displayed() and ("断开" in btn.text or "Disconnect" in btn.text):
                                disconnect_button = btn
                                logger.info("通过文本内容找到断开按钮")
                                break

                        # 如果还没找到，尝试查找input按钮
                        if not disconnect_button:
                            input_buttons = self.driver.find_elements(By.XPATH, "//input[@type='button']")
                            for btn in input_buttons:
                                value = btn.get_attribute("value")
                                if btn.is_displayed() and (value and ("断开" in value or "Disconnect" in value)):
                                    disconnect_button = btn
                                    logger.info("通过input value找到断开按钮")
                                    break
                    except Exception as e:
                        logger.error(f"通用查找方法失败: {e}")

            if not disconnect_button:
                logger.error("错误: 仍然未找到断开按钮")
                # 打印页面源码帮助调试
                logger.debug("页面源码预览:")
                logger.debug(self.driver.page_source[:2000])
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

            # 使用专门的方法查找WAN2的连接按钮
            connect_button = self._find_wan2_specific_button("连接")

            if not connect_button:
                logger.warning("未找到WAN2特定的连接按钮，尝试查找所有连接按钮...")
                # 尝试多种方式定位"连接"按钮
                connect_selectors = [
                    (By.XPATH, "//button[contains(text(), '连接') or contains(text(), 'Connect')]"),
                    (By.XPATH, "//input[@type='button' and (contains(@value, '连接') or contains(@value, 'Connect'))]"),
                    (By.XPATH, "//*[contains(@class, 'connect') and (contains(text(), '连接') or contains(text(), 'Connect'))]"),
                    (By.XPATH, "//*[contains(text(), '连接') or contains(text(), 'Connect')]")
                ]

                connect_button = self._find_element_safely(connect_selectors, clickable=True)

                if not connect_button:
                    logger.warning("未通过标准方式找到连接按钮，尝试更通用的查找方法")
                    # 尝试更通用的查找方法
                    try:
                        # 查找所有按钮并检查文本
                        buttons = self.driver.find_elements(By.TAG_NAME, "button")
                        for btn in buttons:
                            if btn.is_displayed() and ("连接" in btn.text or "Connect" in btn.text):
                                connect_button = btn
                                logger.info("通过文本内容找到连接按钮")
                                break

                        # 如果还没找到，尝试查找input按钮
                        if not connect_button:
                            input_buttons = self.driver.find_elements(By.XPATH, "//input[@type='button']")
                            for btn in input_buttons:
                                value = btn.get_attribute("value")
                                if btn.is_displayed() and (value and ("连接" in value or "Connect" in value)):
                                    connect_button = btn
                                    logger.info("通过input value找到连接按钮")
                                    break
                    except Exception as e:
                        logger.error(f"通用查找方法失败: {e}")

            if not connect_button:
                logger.error("错误: 仍然未找到连接按钮")
                # 打印页面源码帮助调试
                logger.debug("页面源码预览:")
                logger.debug(self.driver.page_source[:2000])
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

    def switch_wan2_ip(self, wait_time=3):
        """切换WAN2 IP：断开并重新连接WAN2"""
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

            # 断开WAN2连接
            logger.info("\n步骤1: 断开WAN2连接...")
            if not self.disconnect_wan2():
                logger.warning("警告: 断开WAN2连接失败")
                # 继续执行下一步

            # 等待
            logger.info(f"等待{wait_time}秒...")
            time.sleep(wait_time)

            # 连接WAN2
            logger.info("\n步骤2: 连接WAN2...")
            if not self.connect_wan2():
                logger.error("错误: 连接WAN2失败")
                return False

            # 等待连接建立
            logger.info(f"等待连接建立({wait_time}秒)...")
            time.sleep(wait_time)

            logger.info("\n" + "=" * 50)
            logger.info("WAN2连接切换完成!")
            logger.info("=" * 50)
            return True

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
    parser = argparse.ArgumentParser(description="TP-Link路由器WAN2专用控制脚本")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--router-ip", help="路由器IP地址")
    parser.add_argument("--username", help="路由器用户名")
    parser.add_argument("--password", help="路由器密码")
    parser.add_argument("--wait-time", type=int, default=3, help="等待时间(秒)")
    parser.add_argument("--no-headless", action="store_true", help="不使用headless模式")

    args = parser.parse_args()

    logger.info("TP-Link路由器WAN2专用控制脚本")
    logger.info("版本: 1.0 (WAN2专用版)")

    # 创建控制器实例
    controller = TPLinkWAN2SpecificController(
        config_file=args.config,
        router_ip=args.router_ip,
        username=args.username,
        password=args.password,
        headless=not args.no_headless
    )

    # 执行WAN2 IP切换
    success = controller.switch_wan2_ip(wait_time=args.wait_time)

    if success:
        logger.info("\n恭喜! WAN2 IP切换操作成功完成。")
        return 0
    else:
        logger.error("\n抱歉，WAN2 IP切换操作失败。")
        return 1

if __name__ == "__main__":
    sys.exit(main())

