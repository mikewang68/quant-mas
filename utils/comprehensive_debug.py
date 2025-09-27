import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def comprehensive_debug():
    """全面调试路由器页面元素"""
    print("开始全面调试路由器页面元素...")

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

        # 打印页面源码（前1000个字符）
        print("\n页面源码预览:")
        print(driver.page_source[:1000])

        # 查找所有input元素
        print("\n查找页面中的所有input元素...")
        inputs = driver.find_elements(By.TAG_NAME, "input")
        for i, inp in enumerate(inputs):
            inp_type = inp.get_attribute("type")
            inp_id = inp.get_attribute("id")
            inp_name = inp.get_attribute("name")
            inp_class = inp.get_attribute("class")
            inp_value = inp.get_attribute("value")
            is_displayed = inp.is_displayed()
            print(f"  Input {i}: type={inp_type}, id={inp_id}, name={inp_name}, class={inp_class}, value='{inp_value}', displayed={is_displayed}")

        # 查找所有按钮元素
        print("\n查找页面中的所有button元素...")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for i, btn in enumerate(buttons):
            btn_type = btn.get_attribute("type")
            btn_id = btn.get_attribute("id")
            btn_name = btn.get_attribute("name")
            btn_class = btn.get_attribute("class")
            btn_text = btn.text
            is_displayed = btn.is_displayed()
            print(f"  Button {i}: type={btn_type}, id={btn_id}, name={btn_name}, class={btn_class}, text='{btn_text}', displayed={is_displayed}")

        # 查找所有div元素（可能包含按钮）
        print("\n查找页面中的所有div元素...")
        divs = driver.find_elements(By.TAG_NAME, "div")
        for i, div in enumerate(divs[:20]):  # 只查看前20个
            div_id = div.get_attribute("id")
            div_class = div.get_attribute("class")
            div_text = div.text.strip()
            if div_id or div_class or div_text:
                print(f"  Div {i}: id={div_id}, class={div_class}, text='{div_text[:50]}...'")

        # 查找所有span元素
        print("\n查找页面中的所有span元素...")
        spans = driver.find_elements(By.TAG_NAME, "span")
        for i, span in enumerate(spans[:20]):  # 只查看前20个
            span_id = span.get_attribute("id")
            span_class = span.get_attribute("class")
            span_text = span.text.strip()
            if span_id or span_class or span_text:
                print(f"  Span {i}: id={span_id}, class={span_class}, text='{span_text[:50]}...'")

        # 尝试通过XPath查找可能的元素
        print("\n尝试通过XPath查找元素...")

        # 查找可能的用户名输入框
        possible_username_xpaths = [
            "//input[@type='text']",
            "//input[contains(@id, 'user')]",
            "//input[contains(@name, 'user')]",
            "//input[contains(@class, 'user')]",
            "//input[@id='username']",
            "//input[@name='username']"
        ]

        for xpath in possible_username_xpaths:
            try:
                elements = driver.find_elements(By.XPATH, xpath)
                if elements:
                    print(f"XPath '{xpath}' 找到 {len(elements)} 个元素")
                    for elem in elements:
                        elem_id = elem.get_attribute("id")
                        elem_name = elem.get_attribute("name")
                        print(f"  - id={elem_id}, name={elem_name}")
            except Exception as e:
                print(f"XPath '{xpath}' 查询失败: {e}")

        # 查找可能的密码输入框
        possible_password_xpaths = [
            "//input[@type='password']",
            "//input[contains(@id, 'pass')]",
            "//input[contains(@name, 'pass')]",
            "//input[contains(@class, 'pass')]",
            "//input[@id='password']",
            "//input[@name='password']"
        ]

        for xpath in possible_password_xpaths:
            try:
                elements = driver.find_elements(By.XPATH, xpath)
                if elements:
                    print(f"XPath '{xpath}' 找到 {len(elements)} 个元素")
                    for elem in elements:
                        elem_id = elem.get_attribute("id")
                        elem_name = elem.get_attribute("name")
                        print(f"  - id={elem_id}, name={elem_name}")
            except Exception as e:
                print(f"XPath '{xpath}' 查询失败: {e}")

        # 查找可能的登录按钮
        possible_button_xpaths = [
            "//input[@type='submit']",
            "//input[@type='button']",
            "//button",
            "//input[contains(@value, '登录')]",
            "//input[contains(@value, 'Login')]",
            "//button[contains(text(), '登录')]",
            "//button[contains(text(), 'Login')]",
            "//*[contains(text(), '登录')]",
            "//*[contains(text(), 'Login')]"
        ]

        for xpath in possible_button_xpaths:
            try:
                elements = driver.find_elements(By.XPATH, xpath)
                if elements:
                    print(f"XPath '{xpath}' 找到 {len(elements)} 个元素")
                    for elem in elements:
                        elem_tag = elem.tag_name
                        elem_id = elem.get_attribute("id")
                        elem_name = elem.get_attribute("name")
                        elem_value = elem.get_attribute("value")
                        elem_text = elem.text
                        print(f"  - tag={elem_tag}, id={elem_id}, name={elem_name}, value='{elem_value}', text='{elem_text}'")
            except Exception as e:
                print(f"XPath '{xpath}' 查询失败: {e}")

    except Exception as e:
        print(f"调试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭浏览器
        driver.quit()
        print("浏览器已关闭")

if __name__ == "__main__":
    comprehensive_debug()

