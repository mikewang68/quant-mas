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
        logging.FileHandler('right_wan2_recording.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TPLinkRightWAN2Recorder:
    def __init__(self, config_file=None, router_ip=None, username=None, password=None, headless=False, record_video=False):
        """初始化路由器控制器 - 专门针对右侧WAN2，支持录屏"""
        self.config = self._load_config(config_file, router_ip, username, password)
        self.base_url = f"http://{self.config['router_ip']}"
        self.driver = None
        self.headless = headless
        self.record_video = record_video
        logger.info(f"初始化TP-Link路由器右侧WAN2录制控制器: {self.base_url}")

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
        """设置Chrome WebDriver，支持录屏"""
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

        # 启用录制功能
        if self.record_video:
            # 创建录制目录
            if not os.path.exists("recordings"):
                os.makedirs("recordings")

            # 设置录制参数
            chrome_options.add_argument("--enable-automation")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")

            # 注意：实际的屏幕录制需要额外的工具，这里只是设置浏览器选项

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

    def navigate_to_wan_settings(self):
        """导航到WAN设置页面"""
        try:
            logger.info("导航到WAN设置页面...")

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
            logger.error(f"导航到WAN设置时出错: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _find_rightmost_disconnect_button(self):
        """查找最右侧的断开按钮（用于右侧WAN2）"""
        try:
            logger.info("查找最右侧的断开按钮...")

            # 查找所有包含"断开"或"Disconnect"文本的按钮
            disconnect_buttons = []

            # 查找button元素
            button_elements = self.driver.find_elements(By.TAG_NAME, "button")
            # 查找input button元素
            input_elements = self.driver.find_elements(By.XPATH, "//input[@type='button']")

            # 合并所有按钮元素
            all_elements = button_elements + input_elements

            for element in all_elements:
                if not element.is_displayed():
                    continue

                # 获取按钮文本
                button_text = element.text or element.get_attribute("value") or ""

                # 检查是否包含断开相关的文本
                if "断开" in button_text or "Disconnect" in button_text:
                    try:
                        # 获取按钮位置
                        location = element.location_once_scrolled_into_view
                        disconnect_buttons.append({
                            'element': element,
                            'text': button_text,
                            'x': location['x'],
                            'y': location['y']
                        })
                        logger.debug(f"找到断开按钮: '{button_text}' 位置: ({location['x']}, {location['y']})")
                    except Exception as e:
                        logger.warning(f"获取按钮位置时出错: {e}")

            if not disconnect_buttons:
                logger.error("未找到任何断开按钮")
                return None

            # 按x坐标排序，选择最右侧的按钮
            disconnect_buttons.sort(key=lambda x: x['x'], reverse=True)

            # 返回最右侧的断开按钮
            rightmost_button = disconnect_buttons[0]
            logger.info(f"选择最右侧的断开按钮: '{rightmost_button['text']}' 位置: ({rightmost_button['x']}, {rightmost_button['y']})")

            return rightmost_button['element']

        except Exception as e:
            logger.error(f"查找最右侧断开按钮时出错: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _find_rightmost_connect_button(self):
        """查找最右侧的连接按钮（用于右侧WAN2）"""
        try:
            logger.info("查找最右侧的连接按钮...")

            # 查找所有包含"连接"或"Connect"文本的按钮
            connect_buttons = []

            # 查找button元素
            button_elements = self.driver.find_elements(By.TAG_NAME, "button")
            # 查找input button元素
            input_elements = self.driver.find_elements(By.XPATH, "//input[@type='button']")

            # 合并所有按钮元素
            all_elements = button_elements + input_elements

            for element in all_elements:
                if not element.is_displayed():
                    continue

                # 获取按钮文本
                button_text = element.text or element.get_attribute("value") or ""

                # 检查是否包含连接相关的文本
                if "连接" in button_text or "Connect" in button_text:
                    try:
                        # 获取按钮位置
                        location = element.location_once_scrolled_into_view
                        connect_buttons.append({
                            'element': element,
                            'text': button_text,
                            'x': location['x'],
                            'y': location['y']
                        })
                        logger.debug(f"找到连接按钮: '{button_text}' 位置: ({location['x']}, {location['y']})")
                    except Exception as e:
                        logger.warning(f"获取按钮位置时出错: {e}")

            if not connect_buttons:
                logger.error("未找到任何连接按钮")
                return None

            # 按x坐标排序，选择最右侧的按钮
            connect_buttons.sort(key=lambda x: x['x'], reverse=True)

            # 返回最右侧的连接按钮
            rightmost_button = connect_buttons[0]
            logger.info(f"选择最右侧的连接按钮: '{rightmost_button['text']}' 位置: ({rightmost_button['x']}, {rightmost_button['y']})")

            return rightmost_button['element']

        except Exception as e:
            logger.error(f"查找最右侧连接按钮时出错: {e}")
            import traceback
            traceback.print_exc()
            return None

    def disconnect_right_wan2(self):
        """断开右侧WAN2连接"""
        try:
            logger.info("断开右侧WAN2连接...")

            # 查找最右侧的断开按钮
            disconnect_button = self._find_rightmost_disconnect_button()

            if not disconnect_button:
                logger.error("错误: 未找到右侧WAN2的断开按钮")
                # 尝试备用方法：查找所有包含"断开"文本的元素
                disconnect_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '断开') or contains(text(), 'Disconnect')]")
                if disconnect_elements:
                    # 选择最右侧的元素
                    rightmost_element = None
                    max_x = -1
                    for element in disconnect_elements:
                        try:
                            if element.is_displayed():
                                location = element.location_once_scrolled_into_view
                                if location['x'] > max_x:
                                    max_x = location['x']
                                    rightmost_element = element
                        except:
                            continue

                    if rightmost_element:
                        disconnect_button = rightmost_element
                        logger.info("通过备用方法找到右侧断开按钮")

            if not disconnect_button:
                logger.error("错误: 仍然未找到右侧WAN2的断开按钮")
                return False

            logger.info("成功找到右侧WAN2的断开按钮")

            # 点击断开按钮
            logger.info("点击右侧WAN2的断开按钮...")
            if not self._safe_click(disconnect_button):
                logger.error("点击右侧WAN2的断开按钮失败")
                return False

            # 减少等待时间
            time.sleep(2)

            logger.info("右侧WAN2已断开连接")
            return True

        except Exception as e:
            logger.error(f"断开右侧WAN2连接时出错: {e}")
            import traceback
            traceback.print_exc()
            return False

    def connect_right_wan2(self):
        """连接右侧WAN2"""
        try:
            logger.info("连接右侧WAN2...")

            # 查找最右侧的连接按钮
            connect_button = self._find_rightmost_connect_button()

            if not connect_button:
                logger.error("错误: 未找到右侧WAN2的连接按钮")
                # 尝试备用方法：查找所有包含"连接"文本的元素
                connect_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '连接') or contains(text(), 'Connect')]")
                if connect_elements:
                    # 选择最右侧的元素
                    rightmost_element = None
                    max_x = -1
                    for element in connect_elements:
                        try:
                            if element.is_displayed():
                                location = element.location_once_scrolled_into_view
                                if location['x'] > max_x:
                                    max_x = location['x']
                                    rightmost_element = element
                        except:
                            continue

                    if rightmost_element:
                        connect_button = rightmost_element
                        logger.info("通过备用方法找到右侧连接按钮")

            if not connect_button:
                logger.error("错误: 仍然未找到右侧WAN2的连接按钮")
                return False

            logger.info("成功找到右侧WAN2的连接按钮")

            # 点击连接按钮
            logger.info("点击右侧WAN2的连接按钮...")
            if not self._safe_click(connect_button):
                logger.error("点击右侧WAN2的连接按钮失败")
                return False

            # 减少等待时间
            time.sleep(2)

            logger.info("右侧WAN2已连接")
            return True

        except Exception as e:
            logger.error(f"连接右侧WAN2时出错: {e}")
            import traceback
            traceback.print_exc()
            return False

    def restart_and_record_wan2(self, wait_time=3):
        """重启并录制右侧WAN2操作"""
        logger.info("=" * 50)
        logger.info("开始重启并录制TP-Link路由器右侧WAN2操作")
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

            # 导航到WAN设置
            if not self.navigate_to_wan_settings():
                logger.error("错误: 导航到WAN设置失败")
                return False

            # 断开右侧WAN2连接
            logger.info("\n步骤1: 断开右侧WAN2连接...")
            if not self.disconnect_right_wan2():
                logger.warning("警告: 断开右侧WAN2连接失败")
                # 继续执行下一步

            # 等待
            logger.info(f"等待{wait_time}秒...")
            time.sleep(wait_time)

            # 连接右侧WAN2
            logger.info("\n步骤2: 连接右侧WAN2...")
            if not self.connect_right_wan2():
                logger.error("错误: 连接右侧WAN2失败")
                return False

            # 等待连接建立
            logger.info(f"等待连接建立({wait_time}秒)...")
            time.sleep(wait_time)

            logger.info("\n" + "=" * 50)
            logger.info("右侧WAN2重启操作完成!")
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
    parser = argparse.ArgumentParser(description="TP-Link路由器右侧WAN2重启录制脚本")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--router-ip", help="路由器IP地址")
    parser.add_argument("--username", help="路由器用户名")
    parser.add_argument("--password", help="路由器密码")
    parser.add_argument("--wait-time", type=int, default=3, help="等待时间(秒)")
    parser.add_argument("--headless", action="store_true", help="使用headless模式")
    parser.add_argument("--record", action="store_true", help="启用录制功能")

    args = parser.parse_args()

    logger.info("TP-Link路由器右侧WAN2重启录制脚本")
    logger.info("版本: 1.0 (右侧WAN2重启录制版)")

    # 创建控制器实例
    controller = TPLinkRightWAN2Recorder(
        config_file=args.config,
        router_ip=args.router_ip,
        username=args.username,
        password=args.password,
        headless=args.headless,
        record_video=args.record
    )

    # 执行右侧WAN2重启
    success = controller.restart_and_record_wan2(wait_time=args.wait_time)

    if success:
        logger.info("\n恭喜! 右侧WAN2重启操作成功完成。")
        return 0
    else:
        logger.error("\n抱歉，右侧WAN2重启操作失败。")
        return 1

if __name__ == "__main__":
    sys.exit(main())

