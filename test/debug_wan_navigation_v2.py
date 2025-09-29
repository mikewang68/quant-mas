#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试TP-Link路由器WAN设置导航过程（版本2）
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_wan_navigation_v2():
    """调试WAN设置导航过程"""
    # 设置Chrome WebDriver
    chrome_options = Options()
    # 不使用headless模式，以便查看页面
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(5)

    try:
        # 先登录
        login_url = "http://192.168.1.1/webpages/login.html"
        logger.info(f"正在访问登录页面: {login_url}")

        driver.get(login_url)

        # 等待页面加载
        time.sleep(2)

        # 使用JavaScript登录
        logger.info("正在使用JavaScript登录...")
        driver.execute_script("""
            document.getElementById('username').value = 'wangdg68';
            document.querySelector('input[type="password"].password-hidden').value = 'wap951020ZJL';
            var loginBtn = document.getElementById('login-btn');
            if (loginBtn) {
                loginBtn.click();
            }
        """)

        # 等待登录完成
        time.sleep(10)  # 给更多时间确保登录完成
        logger.info("登录完成，当前URL: " + driver.current_url)

        # 检查页面源码
        page_source = driver.page_source[:2000]
        logger.info("页面源码预览(前2000字符): " + page_source)

        # 查找菜单相关元素
        logger.info("查找菜单相关元素...")

        # 查找所有span元素
        span_elements = driver.find_elements(By.TAG_NAME, "span")
        logger.info(f"找到 {len(span_elements)} 个span元素")
        for i, span in enumerate(span_elements[:20]):  # 只显示前20个
            text = span.text.strip()
            if text:
                logger.info(f"  Span {i+1}: '{text}'")

        # 查找所有包含特定文本的元素
        menu_texts = ["基本设置", "Basic Settings", "WAN设置", "WAN Setting"]
        for text in menu_texts:
            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
            logger.info(f"找到 {len(elements)} 个包含'{text}'的元素")
            for i, element in enumerate(elements):
                tag = element.tag_name
                element_text = element.text.strip()
                element_id = element.get_attribute('id')
                element_class = element.get_attribute('class')
                logger.info(f"  元素 {i+1}: tag={tag}, text='{element_text}', id={element_id}, class={element_class}")

        # 尝试不同的菜单定位方式
        logger.info("尝试不同的菜单定位方式...")

        # 方式1: 通过XPath定位
        menu_candidates = [
            "//span[text()='基本设置']",
            "//span[contains(text(), '基本设置')]",
            "//*[text()='基本设置']",
            "//*[contains(@class, 'menu') and contains(text(), '基本设置')]"
        ]

        for i, xpath in enumerate(menu_candidates):
            try:
                elements = driver.find_elements(By.XPATH, xpath)
                logger.info(f"XPath '{xpath}' 找到 {len(elements)} 个元素")
                if elements:
                    for j, element in enumerate(elements):
                        logger.info(f"  元素 {j+1}: text='{element.text}', tag={element.tag_name}")
            except Exception as e:
                logger.error(f"XPath '{xpath}' 查询出错: {str(e)}")

        # 保存截图
        driver.save_screenshot("wan_navigation_debug_v2.png")
        logger.info("已保存WAN导航调试截图: wan_navigation_debug_v2.png")

        # 等待观察
        time.sleep(10)

    except Exception as e:
        logger.error(f"调试过程中出现错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_wan_navigation_v2()

