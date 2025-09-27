#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试TP-Link路由器WAN设置导航过程
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_wan_navigation():
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
        WebDriverWait(driver, 30).until(
            lambda driver: "index.html" in driver.current_url
        )
        logger.info("登录成功")

        # 等待主界面加载完成
        logger.info("等待主界面加载...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "main-menu"))
        )
        logger.info("主界面加载完成")

        # 查找所有菜单项
        logger.info("查找所有菜单项...")
        menu_items = driver.find_elements(By.XPATH, "//span[@class='menu-text']")
        for i, item in enumerate(menu_items):
            logger.info(f"菜单项 {i+1}: '{item.text}'")

        # 查找"基本设置"菜单
        logger.info("查找'基本设置'菜单...")
        try:
            basic_settings_menus = driver.find_elements(By.XPATH, "//span[text()='基本设置']")
            logger.info(f"找到 {len(basic_settings_menus)} 个'基本设置'菜单项")
            for i, menu in enumerate(basic_settings_menus):
                parent = menu.find_element(By.XPATH, "./..")
                logger.info(f"  菜单 {i+1}: tag={parent.tag_name}, id={parent.get_attribute('id')}, class={parent.get_attribute('class')}")
        except Exception as e:
            logger.error(f"查找'基本设置'菜单时出错: {str(e)}")

        # 查找所有包含"基本设置"文本的元素
        logger.info("查找所有包含'基本设置'文本的元素...")
        basic_settings_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '基本设置')]")
        for i, element in enumerate(basic_settings_elements):
            logger.info(f"  元素 {i+1}: tag={element.tag_name}, text='{element.text}', id={element.get_attribute('id')}, class={element.get_attribute('class')}")

        # 尝试点击第一个"基本设置"菜单
        if basic_settings_elements:
            logger.info("尝试点击第一个'基本设置'菜单...")
            try:
                basic_settings_elements[0].click()
                logger.info("已点击'基本设置'菜单")
                time.sleep(2)

                # 查找"WAN设置"子菜单
                logger.info("查找'WAN设置'子菜单...")
                wan_settings_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'WAN设置')]")
                for i, element in enumerate(wan_settings_elements):
                    logger.info(f"  WAN设置元素 {i+1}: tag={element.tag_name}, text='{element.text}', id={element.get_attribute('id')}, class={element.get_attribute('class')}")

                # 尝试点击第一个"WAN设置"菜单
                if wan_settings_elements:
                    logger.info("尝试点击第一个'WAN设置'菜单...")
                    wan_settings_elements[0].click()
                    logger.info("已点击'WAN设置'菜单")
                    time.sleep(3)

                    # 检查是否进入WAN设置页面
                    logger.info("检查是否进入WAN设置页面...")
                    main_frame = driver.find_elements(By.CLASS_NAME, "main-frame")
                    if main_frame:
                        logger.info("成功进入WAN设置页面")
                    else:
                        logger.info("未检测到WAN设置页面特征")

            except Exception as e:
                logger.error(f"点击菜单时出错: {str(e)}")

        # 保存截图
        driver.save_screenshot("wan_navigation_debug.png")
        logger.info("已保存WAN导航调试截图: wan_navigation_debug.png")

        # 等待观察
        time.sleep(10)

    except Exception as e:
        logger.error(f"调试过程中出现错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_wan_navigation()

