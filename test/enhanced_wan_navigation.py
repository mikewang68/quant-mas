#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版调试TP-Link路由器WAN设置导航过程
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def enhanced_wan_navigation():
    """增强版调试WAN设置导航过程"""
    # 设置Chrome WebDriver
    chrome_options = Options()
    # 不使用headless模式，以便查看页面
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(3)

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
        time.sleep(8)  # 给更多时间确保登录完成
        logger.info("登录完成，当前URL: " + driver.current_url)

        # 等待主界面加载
        logger.info("等待主界面加载...")
        time.sleep(3)

        # 点击"基本设置"菜单
        logger.info("点击'基本设置'菜单...")
        basic_settings_menu = driver.find_element(By.XPATH, "//span[text()='基本设置']")
        basic_settings_menu.click()
        logger.info("已点击'基本设置'菜单")
        time.sleep(2)

        # 点击"WAN设置"菜单
        logger.info("点击'WAN设置'菜单...")
        wan_settings_menu = driver.find_element(By.XPATH, "//span[text()='WAN设置']")
        wan_settings_menu.click()
        logger.info("已点击'WAN设置'菜单")

        # 等待更长时间并检查页面变化
        logger.info("开始监控页面变化（等待30秒）...")
        for i in range(30):
            logger.info(f"第{i+1}秒:")

            # 检查当前URL
            current_url = driver.current_url
            logger.info(f"  当前URL: {current_url}")

            # 检查页面标题
            page_title = driver.title
            logger.info(f"  页面标题: {page_title}")

            # 检查是否存在特定元素
            main_frame_elements = driver.find_elements(By.CLASS_NAME, "main-frame")
            logger.info(f"  找到 {len(main_frame_elements)} 个 'main-frame' 元素")

            # 检查是否有tab-nav元素
            tab_nav_elements = driver.find_elements(By.CLASS_NAME, "tab-nav")
            logger.info(f"  找到 {len(tab_nav_elements)} 个 'tab-nav' 元素")

            # 检查是否有WAN相关元素
            wan_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'WAN2') or contains(text(), 'wan2')]")
            logger.info(f"  找到 {len(wan_elements)} 个包含'WAN2'的元素")

            # 检查是否有断开/连接按钮
            disconnect_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '断开')]")
            connect_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '连接')]")
            logger.info(f"  找到 {len(disconnect_buttons)} 个'断开'按钮, {len(connect_buttons)} 个'连接'按钮")

            # 检查页面源码中是否包含WAN相关文本
            page_source = driver.page_source
            wan_count = page_source.count("WAN")
            wan2_count = page_source.count("WAN2")
            logger.info(f"  页面源码中包含 {wan_count} 个'WAN'和 {wan2_count} 个'WAN2'")

            time.sleep(1)

        # 保存截图
        driver.save_screenshot("enhanced_wan_navigation.png")
        logger.info("已保存增强版WAN导航截图: enhanced_wan_navigation.png")

    except Exception as e:
        logger.error(f"调试过程中出现错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        driver.quit()

if __name__ == "__main__":
    enhanced_wan_navigation()

