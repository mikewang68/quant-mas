import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

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
        # 如果需要无头模式（不显示浏览器窗口），取消下面这行的注释
        # chrome_options.add_argument("--headless")

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
            time.sleep(3)

            # 尝试多种可能的用户名输入框定位方式
            print("输入用户名...")
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
                    username_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    if username_field:
                        break
                except TimeoutException:
                    continue

            if not username_field:
                print("未找到用户名输入框")
                return False

            username_field.clear()
            username_field.send_keys(self.username)

            # 尝试多种可能的密码输入框定位方式
            print("输入密码...")
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
                    password_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    if password_field:
                        break
                except TimeoutException:
                    continue

            if not password_field:
                print("未找到密码输入框")
                return False

            password_field.clear()
            password_field.send_keys(self.password)

            # 尝试多种可能的登录按钮定位方式
            print("点击登录按钮...")
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
                    login_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if login_button:
                        break
                except TimeoutException:
                    continue

            if not login_button:
                print("未找到登录按钮")
                return False

            login_button.click()

            # 等待页面跳转，最多等待10秒
            print("等待页面跳转...")
            time.sleep(5)

            # 检查是否登录成功（检查当前URL是否为管理页面）
            current_url = self.driver.current_url
            print(f"当前页面URL: {current_url}")

            # 检查页面标题或内容是否包含管理界面的特征
            page_title = self.driver.title
            page_source = self.driver.page_source[:500]  # 获取前500个字符用于检查

            print(f"页面标题: {page_title}")
            print(f"页面内容预览: {page_source}")

            if "/webpages/index.html" in current_url or "管理" in page_title or "admin" in page_title.lower():
                print("登录成功!")
                return True
            else:
                print("登录可能失败，请检查用户名和密码")
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
            time.sleep(3)

            # 尝试多种可能的"基本设置"菜单定位方式
            print("点击基本设置...")
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
                    basic_settings_menu = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if basic_settings_menu:
                        break
                except TimeoutException:
                    continue

            if not basic_settings_menu:
                print("未找到基本设置菜单")
                # 打印页面源码帮助调试
                print("页面源码预览:")
                print(self.driver.page_source[:2000])
                return False

            basic_settings_menu.click()
            time.sleep(2)

            # 尝试多种可能的"WAN设置"菜单定位方式
            print("点击WAN设置...")
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
                    wan_settings_menu = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if wan_settings_menu:
                        break
                except TimeoutException:
                    continue

            if not wan_settings_menu:
                print("未找到WAN设置菜单")
                return False

            wan_settings_menu.click()
            time.sleep(2)

            # 确保WAN2设置部分可见
            print("查找WAN2设置...")
            wan2_section = None
            wan2_selectors = [
                (By.XPATH, "//div[contains(@class, 'wan2') or contains(text(), 'WAN2')]"),
                (By.XPATH, "//*[contains(text(), 'WAN2')]"),
                (By.ID, "wan2"),
                (By.CLASS_NAME, "wan2")
            ]

            for selector_type, selector_value in wan2_selectors:
                try:
                    wan2_section = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    if wan2_section:
                        break
                except TimeoutException:
                    continue

            if not wan2_section:
                print("未找到WAN2设置部分")
                return False

            # 滚动到WAN2设置部分
            self.driver.execute_script("arguments[0].scrollIntoView();", wan2_section)
            time.sleep(1)

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

            # 查找"断开"按钮并点击，尝试多种定位方式
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
                    disconnect_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if disconnect_button:
                        break
                except TimeoutException:
                    continue

            if not disconnect_button:
                print("未找到断开按钮")
                # 打印页面源码帮助调试
                print("WAN设置页面源码预览:")
                print(self.driver.page_source[:2000])
                return False

            disconnect_button.click()

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

            # 查找"连接"按钮并点击，尝试多种定位方式
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
                    connect_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if connect_button:
                        break
                except TimeoutException:
                    continue

            if not connect_button:
                print("未找到连接按钮")
                return False

            connect_button.click()

            # 等待操作完成
            time.sleep(3)

            print("WAN2已连接")
            return True

        except Exception as e:
            print(f"连接WAN2时出错: {e}")
            import traceback
            traceback.print_exc()
            return False

    def switch_ip_until_different(self):
        """切换IP直到获得不同的IP地址"""
        print("正在获取原始IP地址...")
        # 这里需要实现获取IP地址的逻辑
        # 由于我们是在浏览器中操作，可能需要通过其他方式获取IP地址
        # 暂时跳过IP地址检查，直接执行断开和连接操作

        print("原始IP地址检查功能待实现...")

        max_attempts = 5  # 最大尝试次数
        attempt = 0

        while attempt < max_attempts:
            attempt += 1
            print(f"\n--- 第 {attempt} 次尝试 ---")

            # 断开WAN2连接
            print("断开WAN2连接...")
            if not self.disconnect_wan2():
                print("断开WAN2连接失败")
                time.sleep(5)
                continue

            # 等待3秒
            print("等待3秒...")
            time.sleep(3)

            # 连接WAN2
            print("连接WAN2...")
            if not self.connect_wan2():
                print("连接WAN2失败")
                time.sleep(5)
                continue

            # 等待一段时间让连接建立
            print("等待连接建立(15秒)...")
            time.sleep(15)

            print("WAN2连接切换完成")
            return True

        print(f"已达到最大尝试次数 ({max_attempts})，未能完成IP切换")
        return False

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()

def main():
    # 路由器配置
    ROUTER_IP = "192.168.1.1"
    USERNAME = "wangdg68"
    PASSWORD = "wap951020ZJL"
    # WAN2 PPPoE配置信息:
    # 用户名: 15998583399@net
    # 密码: 14350713

    # 创建路由器控制器实例
    router = RouterControllerSelenium(ROUTER_IP, USERNAME, PASSWORD)

    try:
        # 设置WebDriver
        router.setup_driver()

        # 登录路由器
        if not router.login():
            print("登录失败，退出程序")
            return

        # 导航到WAN2设置
        if not router.navigate_to_wan2_settings():
            print("导航到WAN2设置失败，退出程序")
            return

        print("开始切换IP地址...")
        if router.switch_ip_until_different():
            print("IP地址切换成功")
        else:
            print("IP地址切换失败")

    except Exception as e:
        print(f"程序执行过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭浏览器
        router.close()

if __name__ == "__main__":
    main()

