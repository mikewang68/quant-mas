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

            # 输入用户名
            print("输入用户名...")
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "userName"))
            )
            username_field.clear()
            username_field.send_keys(self.username)

            # 输入密码
            print("输入密码...")
            password_field = self.driver.find_element(By.ID, "pcPassword")
            password_field.clear()
            password_field.send_keys(self.password)

            # 点击登录按钮
            print("点击登录按钮...")
            login_button = self.driver.find_element(By.ID, "loginBtn")
            login_button.click()

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

            # 点击"基本设置"菜单
            print("点击基本设置菜单...")
            basic_settings_menu = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '基本设置') or contains(text(), 'Basic Settings')]"))
            )
            basic_settings_menu.click()
            time.sleep(2)

            # 点击"WAN设置"子菜单
            print("点击WAN设置菜单...")
            wan_settings_menu = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'WAN设置') or contains(text(), 'WAN Settings')]"))
            )
            wan_settings_menu.click()
            time.sleep(5)  # 等待WAN设置页面加载

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

            # 根据截图，查找"断开"按钮
            # 通常是一个具有特定类名或文本的按钮
            disconnect_button = None

            # 尝试多种定位方式
            disconnect_selectors = [
                (By.XPATH, "//button[contains(text(), '断开') or contains(text(), 'Disconnect')]"),
                (By.XPATH, "//input[@type='button' and contains(@value, '断开') or contains(@value, 'Disconnect')]"),
                (By.XPATH, "//*[contains(@class, 'disconnect') and (contains(text(), '断开') or contains(text(), 'Disconnect'))]")
            ]

            for selector_type, selector_value in disconnect_selectors:
                try:
                    print(f"尝试定位断开按钮: {selector_type} = {selector_value}")
                    disconnect_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if disconnect_button:
                        print("找到断开按钮")
                        break
                except TimeoutException:
                    continue

            if not disconnect_button:
                print("未找到断开按钮，尝试查找页面中所有按钮...")
                # 获取页面中所有可见按钮用于调试
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

                # 如果还是找不到，尝试更通用的定位方式
                try:
                    # 查找可能包含"断开"文本的元素
                    disconnect_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '断开') or contains(text(), 'Disconnect')]")
                    for element in disconnect_elements:
                        if element.is_displayed():
                            print(f"找到可能的断开元素: {element.text}")
                            disconnect_button = element
                            break
                except:
                    pass

            if not disconnect_button:
                print("仍然未找到断开按钮，无法执行断开操作")
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

            # 查找"连接"按钮
            connect_button = None

            # 尝试多种定位方式
            connect_selectors = [
                (By.XPATH, "//button[contains(text(), '连接') or contains(text(), 'Connect')]"),
                (By.XPATH, "//input[@type='button' and contains(@value, '连接') or contains(@value, 'Connect')]"),
                (By.XPATH, "//*[contains(@class, 'connect') and (contains(text(), '连接') or contains(text(), 'Connect'))]")
            ]

            for selector_type, selector_value in connect_selectors:
                try:
                    print(f"尝试定位连接按钮: {selector_type} = {selector_value}")
                    connect_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    if connect_button:
                        print("找到连接按钮")
                        break
                except TimeoutException:
                    continue

            if not connect_button:
                print("未找到连接按钮，尝试查找页面中所有按钮...")
                # 获取页面中所有可见按钮用于调试
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

                # 如果还是找不到，尝试更通用的定位方式
                try:
                    # 查找可能包含"连接"文本的元素
                    connect_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '连接') or contains(text(), 'Connect')]")
                    for element in connect_elements:
                        if element.is_displayed():
                            print(f"找到可能的连接元素: {element.text}")
                            connect_button = element
                            break
                except:
                    pass

            if not connect_button:
                print("仍然未找到连接按钮，无法执行连接操作")
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
        print("开始切换IP地址...")

        # 登录路由器
        if not self.login():
            print("登录失败，无法切换IP")
            return False

        # 导航到WAN2设置
        if not self.navigate_to_wan2_settings():
            print("导航到WAN2设置失败，退出程序")
            return False

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
    # 路由器配置
    ROUTER_IP = "192.168.1.1"
    USERNAME = "wangdg68"
    PASSWORD = "wap951020ZJL"

    print("TP-Link路由器WAN2控制脚本")
    print(f"路由器IP: {ROUTER_IP}")
    print(f"用户名: {USERNAME}")

    # 创建路由器控制器实例
    router = RouterControllerSelenium(ROUTER_IP, USERNAME, PASSWORD)

    try:
        # 设置WebDriver
        print("设置浏览器驱动...")
        router.setup_driver()

        # 执行IP切换
        if router.switch_ip():
            print("IP地址切换成功")
            return True
        else:
            print("IP地址切换失败")
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

