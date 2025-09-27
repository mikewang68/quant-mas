import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def simple_debug():
    """简单调试路由器页面元素"""
    print("开始简单调试路由器页面元素...")

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

        # 打印页面标题和URL
        print(f"页面标题: {driver.title}")
        print(f"当前URL: {driver.current_url}")

        # 查找用户名输入框
        print("\n查找用户名输入框...")
        try:
            username_field = driver.find_element(By.ID, "userName")
            print(f"找到用户名输入框: id={username_field.get_attribute('id')}, name={username_field.get_attribute('name')}")
        except:
            print("未找到ID为'userName'的元素")

        # 查找密码输入框
        print("\n查找密码输入框...")
        try:
            password_field = driver.find_element(By.ID, "pcPassword")
            print(f"找到密码输入框: id={password_field.get_attribute('id')}, name={password_field.get_attribute('name')}")
        except:
            print("未找到ID为'pcPassword'的元素")

        # 查找所有按钮
        print("\n查找页面中的所有按钮...")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for i, button in enumerate(buttons):
            button_id = button.get_attribute("id")
            button_text = button.text
            print(f"  按钮 {i}: id={button_id}, text='{button_text}'")

        # 查找所有input类型的按钮
        print("\n查找页面中的所有input按钮...")
        input_buttons = driver.find_elements(By.XPATH, "//input")
        for i, button in enumerate(input_buttons):
            button_type = button.get_attribute("type")
            button_id = button.get_attribute("id")
            button_value = button.get_attribute("value")
            if button_type in ["button", "submit"]:
                print(f"  Input按钮 {i}: type={button_type}, id={button_id}, value='{button_value}'")

        # 查找登录按钮的可能ID
        print("\n尝试查找登录按钮...")
        possible_login_ids = ["loginBtn", "login", "submit", "btnLogin"]
        for btn_id in possible_login_ids:
            try:
                login_btn = driver.find_element(By.ID, btn_id)
                print(f"找到登录按钮: id={btn_id}")
            except:
                print(f"未找到ID为'{btn_id}'的按钮")

    except Exception as e:
        print(f"调试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭浏览器
        driver.quit()
        print("浏览器已关闭")

if __name__ == "__main__":
    simple_debug()

