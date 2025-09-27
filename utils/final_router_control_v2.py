import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
import sys

class TPLinkWAN2Controller:
    def __init__(self):
        # 路由器配置信息（硬编码）
        self.router_ip = "192.168.1.1"
        self.username = "wangdg68"
        self.password = "wap951020ZJL"  # 已更正的密码
        self.base_url = f"http://{self.router_ip}"
        self.driver = None

    def setup_driver(self):
        """设置Chrome WebDriver"""
        print("设置Chrome WebDriver...")
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument("--allow-running-insecure-content")
        # 隐藏浏览器窗口，静默执行
        chrome_options.add_argument("--headless")
        # 设置窗口大小
        chrome_options.add_argument("--window-size=1920,1080")

        try:
            # 自动下载并设置ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(3)  # 减少隐式等待时间
            print("Chrome WebDriver设置成功")
            return True
        except Exception as e:
            print(f"Chrome WebDriver设置失败: {e}")
            return False

    def login(self):
        """登录路由器管理界面"""
        try:
            print("开始登录路由器...")
            print(f"路由器地址: {self.base_url}")

            # 访问登录页面
            login_url = f"{self.base_url}/webpages/login.html"
            print(f"访问登录页面: {login_url}")
            self.driver.get(login_url)

            # 减少等待时间
            print("等待页面加载...")
            time.sleep(2)

            # 定位用户名输入框（根据调试结果）
            print("定位用户名输入框...")
            try:
                username_field = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                if username_field and username_field.is_displayed():
                    print("成功找到用户名输入框")
                else:
                    # 如果通过ID找不到，尝试通过name属性
                    username_field = self.driver.find_element(By.NAME, "username")
                    print("通过name属性找到用户名输入框")
            except:
                # 最后尝试通过XPath
                username_field = self.driver.find_element(By.XPATH, "//input[contains(@name, 'user')]")
                print("通过XPath找到用户名输入框")

            # 输入用户名
            print(f"输入用户名: {self.username}")
            username_field.clear()
            username_field.send_keys(self.username)

            # 定位密码输入框（根据调试结果）
            print("定位密码输入框...")
            try:
                password_field = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, "password"))
                )
                if password_field and password_field.is_displayed():
                    print("成功找到密码输入框")
                else:
                    # 如果通过ID找不到，尝试通过name属性
                    password_field = self.driver.find_element(By.NAME, "password")
                    print("通过name属性找到密码输入框")
            except:
                # 最后尝试通过XPath
                password_field = self.driver.find_element(By.XPATH, "//input[contains(@name, 'pass')]")
                print("通过XPath找到密码输入框")

            # 输入密码
            print("输入密码...")
            password_field.clear()
            password_field.send_keys(self.password)

            # 定位登录按钮（根据调试结果）
            print("定位登录按钮...")
            # 根据调试结果，登录按钮是一个包含"登录"文本的span元素
            # 我们需要找到包含这个span的按钮或div元素
            try:
                # 尝试找到包含"登录"文本的span，然后找到其父元素
                login_span = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, "//span[contains(text(), '登录')]"))
                )
                print("找到登录按钮文本")

                # 找到父按钮元素
                login_button = login_span.find_element(By.XPATH, "./ancestor::div[contains(@class, 'button') or contains(@class, 'btn') or @type='button']")
                print("找到登录按钮")
            except:
                # 如果上述方法失败，尝试直接查找包含"登录"文本的按钮
                try:
                    login_button = self.driver.find_element(By.XPATH, "//div[contains(text(), '登录') and @type='button']")
                    print("通过div找到登录按钮")
                except:
                    # 最后尝试查找所有按钮并选择合适的
                    buttons = self.driver.find_elements(By.TAG_NAME, "div")
                    login_button = None
                    for btn in buttons:
                        if "button" in btn.get_attribute("class") and "登录" in btn.text:
                            login_button = btn
                            print("通过遍历找到登录按钮")
                            break

            if not login_button:
                print("错误: 未找到登录按钮")
                return False

            # 点击登录按钮
            print("点击登录按钮...")
            # 滚动到元素并确保可见
            self.driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
            time.sleep(0.5)

            try:
                login_button.click()
            except ElementNotInteractableException:
                # 如果直接点击失败，尝试使用JavaScript
                print("直接点击失败，尝试使用JavaScript点击")
                self.driver.execute_script("arguments[0].click();", login_button)

            # 减少等待时间
            print("等待页面跳转...")
            time.sleep(3)

            # 检查是否登录成功
            current_url = self.driver.current_url
            print(f"登录后页面URL: {current_url}")

            if "/webpages/index.html" in current_url:
                print("登录成功!")
                return True
            else:
                print("登录可能失败")
                # 检查是否有错误信息
                try:
                    error_elements = self.driver.find_elements(By.CLASS_NAME, "text-failed")
                    for error_element in error_elements:
                        if error_element.is_displayed() and error_element.text:
                            print(f"登录错误信息: {error_element.text}")
                            return False
                except:
                    pass
                return False

        except Exception as e:
            print(f"登录过程中出错: {e}")
            import traceback
            traceback.print_exc()
            return False

    def navigate_to_wan2_settings(self):
        """导航到WAN2设置页面"""
        try:
            print("导航到WAN2设置页面...")

            # 减少等待时间
            time.sleep(1)

            # 尝试多种方式定位"基本设置"菜单
            print("查找基本设置菜单...")
            basic_settings_menu = None
            basic_settings_selectors = [
                (By.XPATH, "//a[contains(text(), '基本设置') or contains(text(), 'Basic Settings')]"),
                (By.XPATH, "//span[contains(text(), '基本设置') or contains(text(), 'Basic Settings')]"),
                (By.LINK_TEXT, "基本设置"),
                (By.LINK_TEXT, "Basic Settings")
            ]

            for selector_type, selector_value in basic_settings_selectors:
                try:
                    print(f"尝试定位基本设置菜单: {selector_type} = {selector_value}")
                    basic_settings_menu = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if basic_settings_menu:
                        print("成功找到基本设置菜单")
                        break
                except TimeoutException:
                    continue

            if not basic_settings_menu:
                print("错误: 未找到基本设置菜单")
                return False

            # 点击基本设置菜单
            print("点击基本设置菜单...")
            # 滚动到元素并确保可见
            self.driver.execute_script("arguments[0].scrollIntoView(true);", basic_settings_menu)
            time.sleep(0.5)

            try:
                basic_settings_menu.click()
            except ElementNotInteractableException:
                # 如果直接点击失败，尝试使用JavaScript
                print("直接点击失败，尝试使用JavaScript点击")
                self.driver.execute_script("arguments[0].click();", basic_settings_menu)

            time.sleep(1)

            # 尝试多种方式定位"WAN设置"菜单
            print("查找WAN设置菜单...")
            wan_settings_menu = None
            wan_settings_selectors = [
                (By.XPATH, "//a[contains(text(), 'WAN设置') or contains(text(), 'WAN Settings')]"),
                (By.XPATH, "//span[contains(text(), 'WAN设置') or contains(text(), 'WAN Settings')]"),
                (By.LINK_TEXT, "WAN设置"),
                (By.LINK_TEXT, "WAN Settings")
            ]

            for selector_type, selector_value in wan_settings_selectors:
                try:
                    print(f"尝试定位WAN设置菜单: {selector_type} = {selector_value}")
                    wan_settings_menu = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if wan_settings_menu:
                        print("成功找到WAN设置菜单")
                        break
                except TimeoutException:
                    continue

            if not wan_settings_menu:
                print("错误: 未找到WAN设置菜单")
                return False

            # 点击WAN设置菜单
            print("点击WAN设置菜单...")
            # 滚动到元素并确保可见
            self.driver.execute_script("arguments[0].scrollIntoView(true);", wan_settings_menu)
            time.sleep(0.5)

            try:
                wan_settings_menu.click()
            except ElementNotInteractableException:
                # 如果直接点击失败，尝试使用JavaScript
                print("直接点击失败，尝试使用JavaScript点击")
                self.driver.execute_script("arguments[0].click();", wan_settings_menu)

            # 减少等待时间
            print("等待WAN设置页面加载...")
            time.sleep(2)

            print("成功导航到WAN设置页面")
            return True

        except Exception as e:
            print(f"导航到WAN2设置时出错: {e}")
            import traceback
            traceback.print_exc()
            return False

    def disconnect_wan2(self):
        """断开WAN2连接"""
        try:
            print("断开WAN2连接...")

            # 尝试多种方式定位"断开"按钮
            disconnect_button = None
            disconnect_selectors = [
                (By.XPATH, "//button[contains(text(), '断开') or contains(text(), 'Disconnect')]"),
                (By.XPATH, "//input[@type='button' and (contains(@value, '断开') or contains(@value, 'Disconnect'))]"),
                (By.XPATH, "//*[contains(@class, 'disconnect') and (contains(text(), '断开') or contains(text(), 'Disconnect'))]"),
                (By.XPATH, "//*[contains(text(), '断开') or contains(text(), 'Disconnect')]")
            ]

            for selector_type, selector_value in disconnect_selectors:
                try:
                    print(f"尝试定位断开按钮: {selector_type} = {selector_value}")
                    disconnect_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if disconnect_button and disconnect_button.is_displayed():
                        print("成功找到断开按钮")
                        break
                except TimeoutException:
                    continue

            if not disconnect_button:
                print("错误: 未找到断开按钮")
                return False

            # 点击断开按钮
            print("点击断开按钮...")
            # 滚动到元素并确保可见
            self.driver.execute_script("arguments[0].scrollIntoView(true);", disconnect_button)
            time.sleep(0.5)

            try:
                disconnect_button.click()
            except ElementNotInteractableException:
                # 如果直接点击失败，尝试使用JavaScript
                print("直接点击失败，尝试使用JavaScript点击")
                self.driver.execute_script("arguments[0].click();", disconnect_button)

            # 减少等待时间
            time.sleep(1)

            print("WAN2已断开连接")
            return True

        except Exception as e:
            print(f"断开WAN2连接时出错: {e}")
            import traceback
            traceback.print_exc()
            return False

    def connect_wan2(self):
        """连接WAN2"""
        try:
            print("连接WAN2...")

            # 尝试多种方式定位"连接"按钮
            connect_button = None
            connect_selectors = [
                (By.XPATH, "//button[contains(text(), '连接') or contains(text(), 'Connect')]"),
                (By.XPATH, "//input[@type='button' and (contains(@value, '连接') or contains(@value, 'Connect'))]"),
                (By.XPATH, "//*[contains(@class, 'connect') and (contains(text(), '连接') or contains(text(), 'Connect'))]"),
                (By.XPATH, "//*[contains(text(), '连接') or contains(text(), 'Connect')]")
            ]

            for selector_type, selector_value in connect_selectors:
                try:
                    print(f"尝试定位连接按钮: {selector_type} = {selector_value}")
                    connect_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if connect_button and connect_button.is_displayed():
                        print("成功找到连接按钮")
                        break
                except TimeoutException:
                    continue

            if not connect_button:
                print("错误: 未找到连接按钮")
                return False

            # 点击连接按钮
            print("点击连接按钮...")
            # 滚动到元素并确保可见
            self.driver.execute_script("arguments[0].scrollIntoView(true);", connect_button)
            time.sleep(0.5)

            try:
                connect_button.click()
            except ElementNotInteractableException:
                # 如果直接点击失败，尝试使用JavaScript
                print("直接点击失败，尝试使用JavaScript点击")
                self.driver.execute_script("arguments[0].click();", connect_button)

            # 减少等待时间
            time.sleep(1)

            print("WAN2已连接")
            return True

        except Exception as e:
            print(f"连接WAN2时出错: {e}")
            import traceback
            traceback.print_exc()
            return False

    def switch_ip(self):
        """切换IP：断开并重新连接WAN2"""
        print("=" * 50)
        print("开始切换TP-Link路由器WAN2连接")
        print("=" * 50)

        # 设置WebDriver
        if not self.setup_driver():
            print("错误: WebDriver设置失败")
            return False

        try:
            # 登录路由器
            if not self.login():
                print("错误: 登录失败")
                return False

            # 导航到WAN2设置
            if not self.navigate_to_wan2_settings():
                print("错误: 导航到WAN2设置失败")
                return False

            # 断开WAN2连接
            print("\n步骤1: 断开WAN2连接...")
            if not self.disconnect_wan2():
                print("警告: 断开WAN2连接失败")
                # 继续执行下一步

            # 减少等待时间
            print("等待1秒...")
            time.sleep(1)

            # 连接WAN2
            print("\n步骤2: 连接WAN2...")
            if not self.connect_wan2():
                print("错误: 连接WAN2失败")
                return False

            # 减少等待时间
            print("等待连接建立(5秒)...")
            time.sleep(5)

            print("\n" + "=" * 50)
            print("WAN2连接切换完成!")
            print("=" * 50)
            return True

        except Exception as e:
            print(f"执行过程中出错: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # 关闭浏览器
            if self.driver:
                self.driver.quit()
                print("浏览器已关闭")

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("浏览器已关闭")

def main():
    print("TP-Link路由器WAN2自动控制脚本")
    print("版本: 2.0 (基于调试结果优化)")
    print("注意: 已使用正确的密码并优化等待时间")

    # 创建控制器实例
    controller = TPLinkWAN2Controller()

    # 执行IP切换
    success = controller.switch_ip()

    if success:
        print("\n恭喜! IP切换操作成功完成。")
        return 0
    else:
        print("\n抱歉，IP切换操作失败。")
        return 1

if __name__ == "__main__":
    sys.exit(main())

