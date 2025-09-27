import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def simple_password_test():
    """简单测试密码字段交互"""
    print("开始简单测试密码字段交互...")

    # 设置Chrome WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--headless")  # 使用headless模式
    chrome_options.add_argument("--window-size=1920,1080")

    # 自动下载并设置ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(3)  # 设置隐式等待时间

    try:
        # 访问登录页面
        router_ip = "192.168.1.1"
        login_url = f"http://{router_ip}/webpages/login.html"
        print(f"访问登录页面: {login_url}")
        driver.get(login_url)

        # 等待页面加载
        print("等待页面加载...")
        time.sleep(2)

        # 查找用户名输入框
        print("\n查找用户名输入框...")
        username_field = driver.find_element(By.ID, "username")
        print(f"找到用户名输入框: {username_field.get_attribute('id')}")

        # 输入用户名
        print("输入用户名...")
        username_field.send_keys("wangdg68")

        # 查找密码输入框
        print("\n查找密码输入框...")
        # 根据之前的调试结果，有多个密码相关的字段
        # 我们需要找到可见且可交互的那个
        password_fields = driver.find_elements(By.XPATH, "//input[@type='password' or contains(@name, 'pass') or contains(@id, 'pass')]")
        print(f"找到 {len(password_fields)} 个可能的密码输入框")

        password_field = None
        for i, field in enumerate(password_fields):
            is_displayed = field.is_displayed()
            is_enabled = field.is_enabled()
            field_id = field.get_attribute("id")
            field_name = field.get_attribute("name")
            print(f"  字段 {i}: id={field_id}, name={field_name}, displayed={is_displayed}, enabled={is_enabled}")

            # 选择第一个可见且启用的密码字段
            if is_displayed and is_enabled:
                password_field = field
                print(f"  选择字段 {i} 作为密码输入框")
                break

        if password_field:
            # 输入密码
            print("输入密码...")
            password_field.send_keys("wap951020ZJL")
            print("密码输入成功")
        else:
            print("未找到合适的密码输入框")

        # 查找登录按钮
        print("\n查找登录按钮...")
        # 根据之前的调试结果，登录按钮是一个包含"登录"文本的span元素
        login_spans = driver.find_elements(By.XPATH, "//span[contains(text(), '登录')]")
        print(f"找到 {len(login_spans)} 个包含'登录'文本的元素")

        login_button = None
        for span in login_spans:
            # 尝试找到包含这个span的按钮元素
            try:
                button = span.find_element(By.XPATH, "./ancestor::div[contains(@class, 'button') or contains(@class, 'btn')]")
                if button.is_displayed() and button.is_enabled():
                    login_button = button
                    print("找到登录按钮")
                    break
            except:
                continue

        if not login_button:
            print("未找到登录按钮")

    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭浏览器
        driver.quit()
        print("浏览器已关闭")

if __name__ == "__main__":
    simple_password_test()

