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
        self.password = "wap951020ZJL"
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
            self.driver.implicitly_wait(10)  # 设置隐式等待时间
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

            # 等待页面加载
            print("等待页面加载...")
            time.sleep(5)

            # 尝试多种方式定位用户名输入框
            username_field = None
            username_selectors = [
                (By.ID, "userName"),
                (By.NAME, "username"),
                (By.CSS_SELECTOR, "input[type='text']"),
                (By.XPATH, "//input[@type='text' and not(@id='pcPassword')]")
            ]

            for selector_type, selector_value in username_selectors:
                try:
                    print(f"尝试定位用户名输入框: {selector_type} = {selector_value}")
                    username_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    if username_field and username_field.is_displayed():
                        print("成功找到用户名输入框")
                        break
                except TimeoutException:
                    continue

            if not username_field:
                print("错误: 未找到用户名输入框")
                return False

            # 输入用户名
            print(f"输入用户名: {self.username}")
            username_field.clear()
            username_field.send_keys(self.username)

            # 尝试多种方式定位密码输入框
            password_field = None
            password_selectors = [
                (By.ID, "pcPassword"),
                (By.NAME, "password"),
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.XPATH, "//input[@type='password']")
            ]

            for selector_type, selector_value in password_selectors:
                try:
                    print(f"尝试定位密码输入框: {selector_type} = {selector_value}")
                    password_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    if password_field and password_field.is_displayed():
                        print("成功找到密码输入框")
                        break
                except TimeoutException:
                    continue

            if not password_field:
                print("错误: 未找到密码输入框")
                return False

            # 输入密码
            print("输入密码...")
            password_field.clear()
            password_field.send_keys(self.password)

            # 尝试多种方式定位登录按钮
            login_button = None
            login_button_selectors = [
                (By.ID, "loginBtn"),
                (By.XPATH, "//input[@type='submit']"),
                (By.XPATH, "//button[contains(text(), '登录') or contains(text(), 'Login')]"),
                (By.CSS_SELECTOR, "input[type='submit']"),
                (By.CSS_SELECTOR, "button[type='submit']")
            ]

            for selector_type, selector_value in login_button_selectors:
                try:
                    print(f"尝试定位登录按钮: {selector_type} = {selector_value}")
                    login_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if login_button:
                        print("成功找到登录按钮")
                        break
                except TimeoutException:
                    continue

            if not login_button:
                print("错误: 未找到登录按钮")
                return False

            # 点击登录按钮
            print("点击登录按钮...")
            # 滚动到元素并确保可见
            self.driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
            time.sleep(1)

            try:
                login_button.click()
            except ElementNotInteractableException:
                # 如果直接点击失败，尝试使用JavaScript
                print("直接点击失败，尝试使用JavaScript点击")
                self.driver.execute_script("arguments[0].click();", login_button)

            # 等待页面跳转
            print("等待页面跳转...")
            time.sleep(8)

            # 检查是否登录成功
            current_url = self.driver.current_url
            print(f"登录后页面URL: {current_url}")

            if "/webpages/index.html" in current_url:
                print("登录成功!")
                return True
            else:
                print("登录可能失败")
                # 打印页面标题和部分内容用于调试
                print(f"页面标题: {self.driver.title}")
                print(f"页面内容预览: {self.driver.page_source[:500]}")
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

            # 等待页面加载完成
            time.sleep(3)

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
                    basic_settings_menu = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if basic_settings_menu:
                        print("成功找到基本设置菜单")
                        break
                except TimeoutException:
                    continue

            if not basic_settings_menu:
                print("错误: 未找到基本设置菜单")
                # 打印页面中所有链接用于调试
                links = self.driver.find_elements(By.TAG_NAME, "a")
                print("页面中的链接:")
                for link in links[:10]:  # 只打印前10个
                    if link.is_displayed():
                        print(f"  - {link.text} ({link.get_attribute('href')})")
                return False

            # 点击基本设置菜单
            print("点击基本设置菜单...")
            # 滚动到元素并确保可见
            self.driver.execute_script("arguments[0].scrollIntoView(true);", basic_settings_menu)
            time.sleep(1)

            try:
                basic_settings_menu.click()
            except ElementNotInteractableException:
                # 如果直接点击失败，尝试使用JavaScript
                print("直接点击失败，尝试使用JavaScript点击")
                self.driver.execute_script("arguments[0].click();", basic_settings_menu)

            time.sleep(2)

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
                    wan_settings_menu = WebDriverWait(self.driver, 10).until(
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
            time.sleep(1)

            try:
                wan_settings_menu.click()
            except ElementNotInteractableException:
                # 如果直接点击失败，尝试使用JavaScript
                print("直接点击失败，尝试使用JavaScript点击")
                self.driver.execute_script("arguments[0].click();", wan_settings_menu)

            # 等待WAN设置页面加载
            print("等待WAN设置页面加载...")
            time.sleep(5)

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
                    disconnect_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if disconnect_button and disconnect_button.is_displayed():
                        print("成功找到断开按钮")
                        break
                except TimeoutException:
                    continue

            if not disconnect_button:
                print("错误: 未找到断开按钮")
                # 打印页面中所有按钮用于调试
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                inputs = self.driver.find_elements(By.XPATH, "//input[@type='button']")

                print("页面中的按钮:")
                for button in buttons:
                    if button.is_displayed():
                        print(f"  - {button.text}")

                print("页面中的输入按钮:")
                for input_btn in inputs:
                    if input_btn.is_displayed():
                        print(f"  - {input_btn.get_attribute('value')}")
                return False

            # 点击断开按钮
            print("点击断开按钮...")
            # 滚动到元素并确保可见
            self.driver.execute_script("arguments[0].scrollIntoView(true);", disconnect_button)
            time.sleep(1)

            try:
                disconnect_button.click()
            except ElementNotInteractableException:
                # 如果直接点击失败，尝试使用JavaScript
                print("直接点击失败，尝试使用JavaScript点击")
                self.driver.execute_script("arguments[0].click();", disconnect_button)

            # 等待操作完成
            time.sleep(3)

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
                    connect_button = WebDriverWait(self.driver, 10).until(
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
            time.sleep(1)

            try:
                connect_button.click()
            except ElementNotInteractableException:
                # 如果直接点击失败，尝试使用JavaScript
                print("直接点击失败，尝试使用JavaScript点击")
                self.driver.execute_script("arguments[0].click();", connect_button)

            # 等待操作完成
            time.sleep(3)

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

            # 等待几秒
            print("等待3秒...")
            time.sleep(3)

            # 连接WAN2
            print("\n步骤2: 连接WAN2...")
            if not self.connect_wan2():
                print("错误: 连接WAN2失败")
                return False

            # 等待一段时间让连接建立
            print("等待连接建立(15秒)...")
            time.sleep(15)

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
    print("版本: 1.0")
    print("注意: 请确保路由器管理界面可以正常访问")

    # 创建控制器实例
    controller = TPLinkWAN2Controller()

    # 执行IP切换
    success = controller.switch_ip()

    if success:
        print("\n恭喜! IP切换操作成功完成。")
        return 0
    else:
        print("\n抱歉，IP切换操作失败。请检查以下几点：")
        print("1. 路由器是否可以正常访问 (192.168.1.1)")
        print("2. 用户名和密码是否正确")
        print("3. 是否可以手动登录路由器并操作WAN2设置")
        print("4. 网络连接是否正常")
        return 1

if __name__ == "__main__":
    sys.exit(main())

