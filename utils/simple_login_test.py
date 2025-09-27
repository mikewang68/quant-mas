import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def test_login_page():
    """测试登录页面元素定位"""
    print("开始测试登录页面元素定位...")

    # 设置Chrome WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--allow-running-insecure-content")
    # 不使用headless模式，以便查看页面
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")

    # 自动下载并设置ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(5)  # 设置隐式等待时间

    try:
        # 访问登录页面
        router_ip = "192.168.1.1"
        login_url = f"http://{router_ip}/webpages/login.html"
        print(f"访问登录页面: {login_url}")
        driver.get(login_url)

        # 等待页面加载
        print("等待页面加载...")
        time.sleep(5)

        # 打印页面标题和URL
        print(f"页面标题: {driver.title}")
        print(f"当前URL: {driver.current_url}")

        # 尝试查找用户名输入框
        print("\n尝试查找用户名输入框...")
        try:
            username_field = driver.find_element(By.ID, "userName")
            print(f"找到用户名输入框: {username_field.tag_name}, id={username_field.get_attribute('id')}")
        except Exception as e:
            print(f"未找到ID为'userName'的元素: {e}")

        # 尝试通过其他方式查找用户名输入框
        try:
            username_fields = driver.find_elements(By.TAG_NAME, "input")
            print(f"找到 {len(username_fields)} 个输入框:")
            for i, field in enumerate(username_fields):
                field_type = field.get_attribute("type")
                field_id = field.get_attribute("id")
                field_name = field.get_attribute("name")
                print(f"  {i}: type={field_type}, id={field_id}, name={field_name}")
        except Exception as e:
            print(f"查找输入框时出错: {e}")

        # 尝试查找登录按钮
        print("\n尝试查找登录按钮...")
        try:
            login_button = driver.find_element(By.ID, "loginBtn")
            print(f"找到登录按钮: {login_button.tag_name}, id={login_button.get_attribute('id')}")
        except Exception as e:
            print(f"未找到ID为'loginBtn'的元素: {e}")

        # 尝试通过其他方式查找登录按钮
        try:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            print(f"找到 {len(buttons)} 个按钮:")
            for i, button in enumerate(buttons):
                button_id = button.get_attribute("id")
                button_text = button.text
                button_type = button.get_attribute("type")
                print(f"  {i}: id={button_id}, text='{button_text}', type={button_type}")
        except Exception as e:
            print(f"查找按钮时出错: {e}")

        # 等待用户查看
        input("按回车键继续...")

    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭浏览器
        driver.quit()
        print("浏览器已关闭")

if __name__ == "__main__":
    test_login_page()

