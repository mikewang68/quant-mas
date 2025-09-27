import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def debug_password_field():
    """调试密码字段交互问题"""
    print("开始调试密码字段交互问题...")

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
    driver.implicitly_wait(3)  # 设置隐式等待时间

    try:
        # 访问登录页面
        router_ip = "192.168.1.1"
        login_url = f"http://{router_ip}/webpages/login.html"
        print(f"访问登录页面: {login_url}")
        driver.get(login_url)

        # 等待页面加载
        print("等待页面加载...")
        time.sleep(3)

        # 打印页面标题和URL
        print(f"页面标题: {driver.title}")
        print(f"当前URL: {driver.current_url}")

        # 查找用户名输入框
        print("\n查找用户名输入框...")
        try:
            username_field = driver.find_element(By.ID, "username")
            print(f"找到用户名输入框: id={username_field.get_attribute('id')}, name={username_field.get_attribute('name')}")
            print(f"  是否可见: {username_field.is_displayed()}")
            print(f"  是否启用: {username_field.is_enabled()}")

            # 尝试输入用户名
            print("尝试输入用户名...")
            username_field.clear()
            username_field.send_keys("wangdg68")
            print("用户名输入成功")
        except Exception as e:
            print(f"用户名输入框操作失败: {e}")

        # 查找密码输入框
        print("\n查找密码输入框...")
        try:
            # 根据调试结果，有多个密码相关的input元素
            password_fields = driver.find_elements(By.XPATH, "//input[@type='password' or contains(@name, 'pass') or contains(@id, 'pass')]")
            print(f"找到 {len(password_fields)} 个可能的密码输入框:")

            for i, field in enumerate(password_fields):
                field_type = field.get_attribute("type")
                field_id = field.get_attribute("id")
                field_name = field.get_attribute("name")
                field_class = field.get_attribute("class")
                is_displayed = field.is_displayed()
                is_enabled = field.is_enabled()
                print(f"  密码字段 {i}: type={field_type}, id={field_id}, name={field_name}, class={field_class}, displayed={is_displayed}, enabled={is_enabled}")

                # 尝试与每个密码字段交互
                if is_displayed and is_enabled:
                    try:
                        print(f"  尝试与密码字段 {i} 交互...")
                        field.clear()
                        field.send_keys("test123")
                        print(f"  密码字段 {i} 交互成功")
                        # 清除测试输入
                        field.clear()
                    except Exception as e:
                        print(f"  密码字段 {i} 交互失败: {e}")

        except Exception as e:
            print(f"密码输入框操作失败: {e}")

        # 查找所有input元素
        print("\n查找所有input元素...")
        inputs = driver.find_elements(By.TAG_NAME, "input")
        for i, inp in enumerate(inputs):
            inp_type = inp.get_attribute("type")
            inp_id = inp.get_attribute("id")
            inp_name = inp.get_attribute("name")
            inp_class = inp.get_attribute("class")
            inp_value = inp.get_attribute("value")
            is_displayed = inp.is_displayed()
            is_enabled = inp.is_enabled()
            print(f"  Input {i}: type={inp_type}, id={inp_id}, name={inp_name}, class={inp_class}, value='{inp_value}', displayed={is_displayed}, enabled={is_enabled}")

        # 等待用户查看
        input("\n按回车键继续...")

    except Exception as e:
        print(f"调试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭浏览器
        driver.quit()
        print("浏览器已关闭")

if __name__ == "__main__":
    debug_password_field()

