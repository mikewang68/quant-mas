import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def debug_router_elements():
    """调试路由器页面元素"""
    print("开始调试路由器页面元素...")

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
        time.sleep(3)

        # 打印页面标题和URL
        print(f"页面标题: {driver.title}")
        print(f"当前URL: {driver.current_url}")

        # 查找所有输入框
        print("\n查找页面中的所有输入框...")
        input_fields = driver.find_elements(By.TAG_NAME, "input")
        for i, field in enumerate(input_fields):
            field_type = field.get_attribute("type")
            field_id = field.get_attribute("id")
            field_name = field.get_attribute("name")
            field_class = field.get_attribute("class")
            field_value = field.get_attribute("value")
            is_displayed = field.is_displayed()
            print(f"  输入框 {i}: type={field_type}, id={field_id}, name={field_name}, class={field_class}, value={field_value}, displayed={is_displayed}")

        # 查找所有按钮
        print("\n查找页面中的所有按钮...")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for i, button in enumerate(buttons):
            button_type = button.get_attribute("type")
            button_id = button.get_attribute("id")
            button_text = button.text
            button_value = button.get_attribute("value")
            button_class = button.get_attribute("class")
            is_displayed = button.is_displayed()
            print(f"  按钮 {i}: type={button_type}, id={button_id}, text='{button_text}', value={button_value}, class={button_class}, displayed={is_displayed}")

        # 查找所有input类型的按钮
        print("\n查找页面中的所有input按钮...")
        input_buttons = driver.find_elements(By.XPATH, "//input[@type='button' or @type='submit']")
        for i, button in enumerate(input_buttons):
            button_type = button.get_attribute("type")
            button_id = button.get_attribute("id")
            button_value = button.get_attribute("value")
            button_class = button.get_attribute("class")
            is_displayed = button.is_displayed()
            print(f"  Input按钮 {i}: type={button_type}, id={button_id}, value='{button_value}', class={button_class}, displayed={is_displayed}")

        # 查找所有链接
        print("\n查找页面中的所有链接...")
        links = driver.find_elements(By.TAG_NAME, "a")
        for i, link in enumerate(links):
            link_href = link.get_attribute("href")
            link_text = link.text
            link_id = link.get_attribute("id")
            link_class = link.get_attribute("class")
            is_displayed = link.is_displayed()
            print(f"  链接 {i}: href={link_href}, text='{link_text}', id={link_id}, class={link_class}, displayed={is_displayed}")

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
    debug_router_elements()

