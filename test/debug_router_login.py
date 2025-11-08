#!/usr/bin/env python
# coding=utf-8

import time
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.enhanced_router_control import TPLinkWAN2Controller


def debug_router_login():
    """调试路由器登录过程"""
    print("=== 路由器登录调试 ===")

    # 初始化路由器控制
    print("1. 初始化路由器控制...")
    try:
        router = TPLinkWAN2Controller()
        print("路由器控制初始化成功")
    except Exception as e:
        print(f"路由器控制初始化失败: {e}")
        return False

    # 设置WebDriver
    print("\n2. 设置WebDriver...")
    try:
        if router.setup_driver():
            print("WebDriver设置成功")
        else:
            print("WebDriver设置失败")
            return False
    except Exception as e:
        print(f"WebDriver设置异常: {e}")
        return False

    # 访问登录页面
    print("\n3. 访问登录页面...")
    try:
        login_url = f"{router.base_url}/webpages/login.html"
        print(f"访问: {login_url}")
        router.driver.get(login_url)

        # 等待页面加载
        time.sleep(3)

        # 打印页面信息
        print(f"当前URL: {router.driver.current_url}")
        print(f"页面标题: {router.driver.title}")

        # 打印页面源代码前1000字符用于调试
        page_source = router.driver.page_source
        print(f"页面源代码长度: {len(page_source)}")
        print(f"页面源代码前1000字符:\n{page_source[:1000]}")

        # 查找所有输入框
        print("\n4. 查找所有输入框...")
        from selenium.webdriver.common.by import By
        inputs = router.driver.find_elements(By.TAG_NAME, "input")
        print(f"找到 {len(inputs)} 个输入框:")
        for i, input_elem in enumerate(inputs):
            input_type = input_elem.get_attribute("type")
            input_id = input_elem.get_attribute("id")
            input_name = input_elem.get_attribute("name")
            input_class = input_elem.get_attribute("class")
            print(f"  输入框 {i}: type={input_type}, id={input_id}, name={input_name}, class={input_class}")

        # 查找所有按钮
        print("\n5. 查找所有按钮...")
        buttons = router.driver.find_elements(By.TAG_NAME, "button")
        print(f"找到 {len(buttons)} 个按钮:")
        for i, button in enumerate(buttons):
            button_text = button.text
            button_id = button.get_attribute("id")
            button_class = button.get_attribute("class")
            print(f"  按钮 {i}: text='{button_text}', id={button_id}, class={button_class}")

        # 查找所有span元素（可能包含登录文本）
        print("\n6. 查找所有span元素...")
        spans = router.driver.find_elements(By.TAG_NAME, "span")
        login_spans = []
        for span in spans:
            if "登录" in span.text:
                login_spans.append(span)
                print(f"  找到登录span: text='{span.text}', id={span.get_attribute('id')}")

        print(f"\n总共找到 {len(login_spans)} 个包含'登录'的span元素")

        return True

    except Exception as e:
        print(f"调试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 确保关闭浏览器
        if hasattr(router, 'driver') and router.driver:
            router.driver.quit()
            print("\n浏览器已关闭")


def main():
    """主调试函数"""
    print("开始路由器登录调试...\n")

    success = debug_router_login()

    if success:
        print("\n✅ 调试完成，请检查输出信息")
    else:
        print("\n❌ 调试失败")


if __name__ == "__main__":
    main()

