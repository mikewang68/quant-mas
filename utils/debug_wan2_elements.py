import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import sys

def debug_wan2_elements():
    """调试WAN2页面元素，帮助识别WAN2特定控件"""
    print("开始调试WAN2页面元素...")
    print("注意: 此脚本需要手动导航到WAN设置页面")

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
        # 访问路由器管理界面
        router_ip = "192.168.1.1"
        base_url = f"http://{router_ip}"

        # 首先访问登录页面
        login_url = f"{base_url}/webpages/login.html"
        print(f"请先在浏览器中登录: {login_url}")
        print("登录完成后，按回车键继续...")
        input()

        # 手动导航到WAN设置页面
        print("请手动导航到WAN设置页面（基本设置 -> WAN设置）")
        print("导航完成后，按回车键开始分析元素...")
        input()

        # 等待页面加载
        print("等待页面加载...")
        time.sleep(3)

        # 打印页面标题和URL
        print(f"页面标题: {driver.title}")
        print(f"当前URL: {driver.current_url}")

        # 查找所有包含"WAN2"文本的元素
        print("\n查找包含'WAN2'文本的元素...")
        wan2_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'WAN2') or contains(@id, 'wan2') or contains(@class, 'wan2')]")
        for i, elem in enumerate(wan2_elements):
            elem_text = elem.text.strip()
            elem_tag = elem.tag_name
            elem_id = elem.get_attribute("id")
            elem_class = elem.get_attribute("class")
            is_displayed = elem.is_displayed()
            print(f"  WAN2元素 {i}: tag={elem_tag}, id={elem_id}, class={elem_class}, text='{elem_text}', displayed={is_displayed}")

        # 查找所有按钮元素
        print("\n查找页面中的所有按钮...")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        input_buttons = driver.find_elements(By.XPATH, "//input[@type='button']")
        all_buttons = buttons + input_buttons

        for i, btn in enumerate(all_buttons):
            btn_tag = btn.tag_name
            btn_type = btn.get_attribute("type")
            btn_id = btn.get_attribute("id")
            btn_class = btn.get_attribute("class")
            btn_text = btn.text or btn.get_attribute("value") or ""
            is_displayed = btn.is_displayed()
            is_enabled = btn.is_enabled()

            # 获取按钮位置
            try:
                btn_location = btn.location_once_scrolled_into_view
                location_info = f"location=({btn_location['x']}, {btn_location['y']})"
            except:
                location_info = "location=unknown"

            print(f"  按钮 {i}: tag={btn_tag}, type={btn_type}, id={btn_id}, class={btn_class}, text='{btn_text}', displayed={is_displayed}, enabled={is_enabled}, {location_info}")

        # 查找所有包含"断开"或"连接"文本的元素
        print("\n查找包含'断开'或'连接'文本的元素...")
        action_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '断开') or contains(text(), '连接') or contains(text(), 'Disconnect') or contains(text(), 'Connect')]")
        for i, elem in enumerate(action_elements):
            elem_text = elem.text.strip()
            elem_tag = elem.tag_name
            elem_id = elem.get_attribute("id")
            elem_class = elem.get_attribute("class")
            is_displayed = elem.is_displayed()
            print(f"  操作元素 {i}: tag={elem_tag}, id={elem_id}, class={elem_class}, text='{elem_text}', displayed={is_displayed}")

        # 查找所有div和span元素（可能包含按钮）
        print("\n查找页面中的div和span元素...")
        divs = driver.find_elements(By.TAG_NAME, "div")
        spans = driver.find_elements(By.TAG_NAME, "span")
        all_elements = divs + spans

        for i, elem in enumerate(all_elements[:50]):  # 只查看前50个
            elem_tag = elem.tag_name
            elem_id = elem.get_attribute("id")
            elem_class = elem.get_attribute("class")
            elem_text = elem.text.strip()

            if elem_id or elem_class or elem_text:
                # 检查是否包含WAN2或操作相关文本
                if "wan2" in elem_id.lower() or "wan2" in elem_class.lower() or "wan2" in elem_text.lower():
                    print(f"  {elem_tag} {i}: id={elem_id}, class={elem_class}, text='{elem_text[:100]}...'")

        # 打印页面源码（前2000个字符）
        print("\n页面源码预览:")
        print(driver.page_source[:2000])

        # 等待用户查看
        print("\n分析完成，按回车键退出...")
        input()

    except Exception as e:
        print(f"调试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭浏览器
        driver.quit()
        print("浏览器已关闭")

if __name__ == "__main__":
    debug_wan2_elements()

