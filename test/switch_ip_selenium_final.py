import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException

class RouterControllerSelenium:
    def __init__(self, router_ip, username, password):
        self.router_ip = router_ip
        self.username = username
        self.password = password
        self.base_url = f"http://{router_ip}"
        self.driver = None

    def setup_driver(self):
        """设置Chrome WebDriver"""
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

        # 自动下载并设置ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)  # 设置隐式等待时间

    def login(self):
        """登录路由器管理界面"""
        try:
            print("开始登录路由器...")

            # 访问登录页面
            login_url = f"{self.base_url}/webpages/login.html"
            print(f"访问登录页面: {login_url}")
            self.driver.get(login_url)

            # 等待页面加载
            print("等待页面加载...")
            time.sleep(5)

            # 打印当前页面信息用于调试
            print(f"当前页面URL: {self.driver.current_url}")
            print(f"页面标题: {self.driver.title}")

            # 尝试多种可能的用户名输入框定位方式
            print("查找用户名输入框...")
            username_field = None
            username_selectors = [
                (By.ID, "userName"),
                (By.NAME, "username"),
                (By.ID, "username"),
                (By.CSS_SELECTOR, "input[type='text']"),
                (By.XPATH, "//input[@type='text' and not(@id='pcPassword')]")
            ]

            for selector_type, selector_value in username_selectors:
                try:
                    print(f"尝试定位用户名输入框: {selector_type} = {selector_value}")
                    username_field = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if username_field:
                        print("找到用户名输入框")
                        # 滚动到元素并确保可见
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", username_field)
                        time.sleep(1)
                        break
                except TimeoutException:
                    continue

            if not username_field:
                print("未找到用户名输入框")
                # 检查是否有iframe
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                print(f"发现 {len(iframes)} 个iframe")
                for i, iframe in enumerate(iframes):
                    print(f"  iframe {i}: {iframe.get_attribute('src')}")
                return False

            # 尝试清除并输入用户名
            try:
                print(f"输入用户名: {self.username}")
                username_field.clear()
                username_field.send_keys(self.username)
            except ElementNotInteractableException:
                # 如果直接输入失败，尝试使用JavaScript
                print("直接输入失败，尝试使用JavaScript输入用户名")
                self.driver.execute_script("arguments[0].value = arguments[1];", username_field, self.username)

            # 尝试多种可能的密码输入框定位方式
            print("查找密码输入框...")
            password_field = None
            password_selectors = [
                (By.ID, "pcPassword"),
                (By.NAME, "password"),
                (By.ID, "password"),
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.XPATH, "//input[@type='password']")
            ]

            for selector_type, selector_value in password_selectors:
                try:
                    print(f"尝试定位密码输入框: {selector_type} = {selector_value}")
                    password_field = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if password_field:
                        print("找到密码输入框")
                        # 滚动到元素并确保可见
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", password_field)
                        time.sleep(1)
                        break
                except TimeoutException:
                    continue

            if not password_field:
                print("未找到密码输入框")
                return False

            # 尝试清除并输入密码
            try:
                print("输入密码...")
                password_field.clear()
                password_field.send_keys(self.password)
            except ElementNotInteractableException:
                # 如果直接输入失败，尝试使用JavaScript
                print("直接输入失败，尝试使用JavaScript输入密码")
                self.driver.execute_script("arguments[0].value = arguments[1];", password_field, self.password)

            # 尝试多种可能的登录按钮定位方式
            print("查找登录按钮...")
            login_button = None
            login_button_selectors = [
                (By.ID, "loginBtn"),
                (By.XPATH, "//input[@type='submit']"),
                (By.XPATH, "//button[contains(text(), '登录') or contains(text(), 'Login')]"),
                (By.CSS_SELECTOR, "input[type='submit']"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.XPATH, "//a[contains(@onclick, 'login') or contains(@href, 'login')]"),
                (By.XPATH, "//*[contains(text(), '登录') or contains(text(), 'Login')]")
            ]

            for selector_type, selector_value in login_button_selectors:
                try:
                    print(f"尝试定位登录按钮: {selector_type} = {selector_value}")
                    login_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if login_button:
                        print("找到登录按钮")
                        # 滚动到元素并确保可见
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
                        time.sleep(1)
                        break
                except TimeoutException:
                    continue

            if not login_button:
                print("未找到登录按钮")
                return False

            # 尝试点击登录按钮
            try:
                print("点击登录按钮...")
                login_button.click()
            except ElementNotInteractableException:
                # 如果直接点击失败，尝试使用JavaScript
                print("直接点击失败，尝试使用JavaScript点击登录按钮")
                self.driver.execute_script("arguments[0].click();", login_button)

            # 等待页面跳转，最多等待15秒
            print("等待页面跳转...")
            time.sleep(8)

            # 检查是否登录成功
            current_url = self.driver.current_url
            page_title = self.driver.title
            print(f"登录后页面URL: {current_url}")
            print(f"登录后页面标题: {page_title}")

            # 检查是否成功进入管理界面
            if "/webpages/index.html" in current_url or "管理" in page_title or "admin" in page_title.lower():
                print("登录成功!")
                return True
            else:
                print("登录可能失败，未跳转到管理页面")
                # 检查是否有错误信息
                try:
                    error_elements = self.driver.find_elements(By.CLASS_NAME, "error")
                    for error_element in error_elements:
                        if error_element.is_displayed():
                            print(f"错误信息: {error_element.text}")
                except NoSuchElementException:
                    pass

                # 检查是否仍在登录页面
                if "login" in current_url.lower():
                    print("仍在登录页面，可能登录失败")
                else:
                    print("页面已跳转，但不是管理页面")

                return False

        except Exception as e:
            print(f"登录过程中出错: {e}")
            import traceback
            traceback.print_exc()
            return False

    def navigate_to_wan2_settings(self):
        """导航到WAN2设置页面"""
        try:
            print("导航到WAN2设置...")

            # 等待页面加载完成
            time.sleep(5)

            # 尝试多种可能的"基本设置"菜单定位方式
            print("查找基本设置菜单...")
            basic_settings_menu = None
            basic_settings_selectors = [
                (By.XPATH, "//a[contains(text(), '基本设置') or contains(text(), 'Basic Settings')]"),
                (By.XPATH, "//span[contains(text(), '基本设置') or contains(text(), 'Basic Settings')]"),
                (By.XPATH, "//*[contains(@class, 'menu') or contains(@class, 'nav')]//*[contains(text(), '基本设置') or contains(text(), 'Basic Settings')]"),
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
                        print("找到基本设置菜单")
                        # 滚动到元素并确保可见
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", basic_settings_menu)
                        time.sleep(1)
                        break
                except TimeoutException:
                    continue

            if not basic_settings_menu:
                print("未找到基本设置菜单，尝试打印页面结构...")
                # 获取页面中所有可见的链接用于调试
                links = self.driver.find_elements(By.TAG_NAME, "a")
                print("页面中的链接:")
                for link in links:
                    if link.is_displayed():
                        print(f"  - {link.text} ({link.get_attribute('href')})")
                return False

            # 尝试点击基本设置菜单
            try:
                print("点击基本设置菜单...")
                basic_settings_menu.click()
            except ElementNotInteractableException:
                # 如果直接点击失败，尝试使用JavaScript
                print("直接点击失败，尝试使用JavaScript点击基本设置菜单")
                self.driver.execute_script("arguments[0].click();", basic_settings_menu)

            time.sleep(3)

            # 尝试多种可能的"WAN设置"菜单定位方式
            print("查找WAN设置菜单...")
            wan_settings_menu = None
            wan_settings_selectors = [
                (By.XPATH, "//a[contains(text(), 'WAN设置') or contains(text(), 'WAN Settings')]"),
                (By.XPATH, "//span[contains(text(), 'WAN设置') or contains(text(), 'WAN Settings')]"),
                (By.XPATH, "//*[contains(text(), 'WAN设置') or contains(text(), 'WAN Settings')]"),
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
                        print("找到WAN设置菜单")
                        # 滚动到元素并确保可见
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", wan_settings_menu)
                        time.sleep(1)
                        break
                except TimeoutException:
                    continue

            if not wan_settings_menu:
                print("未找到WAN设置菜单")
                return False

            # 尝试点击WAN设置菜单
            try:
                print("点击WAN设置菜单...")
                wan_settings_menu.click()
            except ElementNotInteractableException:
                # 如果直接点击失败，尝试使用JavaScript
                print("直接点击失败，尝试使用JavaScript点击WAN设置菜单")
                self.driver.execute_script("arguments[0].click();", wan_settings_menu)

            time.sleep(5)  # 等待WAN设置页面加载

            # 检查是否成功导航到WAN设置页面
            print("检查页面是否包含WAN2设置...")
            page_source = self.driver.page_source.lower()
            if "wan2" in page_source or "WAN2" in self.driver.page_source:
                print("成功导航到WAN2设置页面")
                return True
            else:
                print("可能未成功导航到WAN2设置页面")
                # 打印页面中所有按钮用于调试
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                print("页面中的按钮:")
                for button in buttons:
                    if button.is_displayed():
                        print(f"  - {button.text}")
                return False

        except Exception as e:
            print(f"导航到WAN2设置时出错: {e}")
            import traceback
            traceback.print_exc()
            return False

    def disconnect_wan2(self):
        """断开WAN2连接"""
        try:
            print("断开WAN2连接...")

            # 查找"断开"按钮，尝试多种定位方式
            disconnect_button = None
            disconnect_selectors = [
                (By.XPATH, "//button[contains(text(), '断开') or contains(text(), 'Disconnect')]"),
                (By.XPATH, "//*[contains(@onclick, 'disconnect') and (contains(text(), '断开') or contains(text(), 'Disconnect'))]"),
                (By.XPATH, "//input[@type='button' and (contains(@value, '断开') or contains(@value, 'Disconnect'))]"),
                (By.XPATH, "//*[contains(@class, 'disconnect') and (contains(text(), '断开') or contains(text(), 'Disconnect'))]"),
                (By.XPATH, "//a[contains(text(), '断开') or contains(text(), 'Disconnect')]")
            ]

            for selector_type, selector_value in disconnect_selectors:
                try:
                    print(f"尝试定位断开按钮: {selector_type} = {selector_value}")
                    disconnect_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if disconnect_button:
                        print("找到断开按钮")
                        # 滚动到元素并确保可见
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", disconnect_button)
                        time.sleep(1)
                        break
                except TimeoutException:
                    continue

            if not disconnect_button:
                print("未找到断开按钮，尝试打印页面中所有可见按钮...")
                # 获取页面中所有可见按钮用于调试
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                inputs = self.driver.find_elements(By.XPATH, "//input[@type='button']")
                links = self.driver.find_elements(By.TAG_NAME, "a")

                print("页面中的可见按钮:")
                for button in buttons:
                    if button.is_displayed():
                        print(f"  - {button.text}")

                print("页面中的可见输入按钮:")
                for input_btn in inputs:
                    if input_btn.is_displayed():
                        print(f"  - {input_btn.get_attribute('value')}")

                print("页面中的可见链接:")
                for link in links:
                    if link.is_displayed():
                        print(f"  - {link.text}")

                return False

            # 尝试点击断开按钮
            try:
                print("点击断开按钮...")
                disconnect_button.click()
            except ElementNotInteractableException:
                # 如果直接点击失败，尝试使用JavaScript
                print("直接点击失败，尝试使用JavaScript点击断开按钮")
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

            # 查找"连接"按钮，尝试多种定位方式
            connect_button = None
            connect_selectors = [
                (By.XPATH, "//button[contains(text(), '连接') or contains(text(), 'Connect')]"),
                (By.XPATH, "//*[contains(@onclick, 'connect') and (contains(text(), '连接') or contains(text(), 'Connect'))]"),
                (By.XPATH, "//input[@type='button' and (contains(@value, '连接') or contains(@value, 'Connect'))]"),
                (By.XPATH, "//*[contains(@class, 'connect') and (contains(text(), '连接') or contains(text(), 'Connect'))]"),
                (By.XPATH, "//a[contains(text(), '连接') or contains(text(), 'Connect')]")
            ]

            for selector_type, selector_value in connect_selectors:
                try:
                    print(f"尝试定位连接按钮: {selector_type} = {selector_value}")
                    connect_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if connect_button:
                        print("找到连接按钮")
                        # 滚动到元素并确保可见
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", connect_button)
                        time.sleep(1)
                        break
                except TimeoutException:
                    continue

            if not connect_button:
                print("未找到连接按钮")
                return False

            # 尝试点击连接按钮
            try:
                print("点击连接按钮...")
                connect_button.click()
            except ElementNotInteractableException:
                # 如果直接点击失败，尝试使用JavaScript
                print("直接点击失败，尝试使用JavaScript点击连接按钮")
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
        print("开始切换IP地址...")

        # 断开WAN2连接
        print("断开WAN2连接...")
        if not self.disconnect_wan2():
            print("断开WAN2连接失败")
            return False

        # 等待3秒
        print("等待3秒...")
        time.sleep(3)

        # 连接WAN2
        print("连接WAN2...")
        if not self.connect_wan2():
            print("连接WAN2失败")
            return False

        # 等待一段时间让连接建立
        print("等待连接建立(15秒)...")
        time.sleep(15)

        print("WAN2连接切换完成")
        return True

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("浏览器已关闭")

def main():
    # 路由器配置 - 直接使用用户提供的信息
    ROUTER_IP = "192.168.1.1"
    USERNAME = "wangdg68"
    PASSWORD = "wap951020ZJL"

    # WAN2 PPPoE配置信息:
    # 用户名: 15998583399@net
    # 密码: 14350713

    print("路由器控制脚本启动")
    print(f"路由器IP: {ROUTER_IP}")
    print(f"用户名: {USERNAME}")

    # 创建路由器控制器实例
    router = RouterControllerSelenium(ROUTER_IP, USERNAME, PASSWORD)

    try:
        # 设置WebDriver
        print("设置浏览器驱动...")
        router.setup_driver()

        # 登录路由器
        print("尝试登录路由器...")
        if not router.login():
            print("登录失败，退出程序")
            return False

        # 导航到WAN2设置
        print("导航到WAN2设置页面...")
        if not router.navigate_to_wan2_settings():
            print("导航到WAN2设置失败，退出程序")
            return False

        # 切换IP
        print("执行IP切换...")
        if router.switch_ip():
            print("IP切换成功")
            return True
        else:
            print("IP切换失败")
            return False

    except Exception as e:
        print(f"程序执行过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 关闭浏览器
        router.close()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

