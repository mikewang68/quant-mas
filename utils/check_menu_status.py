#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查TP-Link路由器菜单状态
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_menu_status():
    """检查菜单状态"""
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

        # 检查所有菜单项
        logger.info("检查所有菜单项...")

        # 查找所有span元素
        span_elements = driver.find_elements(By.TAG_NAME, "span")
        logger.info(f"找到 {len(span_elements)} 个span元素")

        menu_items = []
        for i, span in enumerate(span_elements):
            text = span.text.strip()
            if text:
                # 获取元素的属性
                element_id = span.get_attribute('id')
                element_class = span.get_attribute('class')
                is_displayed = span.is_displayed()
                is_enabled = span.is_enabled()

                logger.info(f"  Span {i+1}: text='{text}', id={element_id}, class={element_class}, displayed={is_displayed}, enabled={is_enabled}")

                # 收集菜单项
                if text in ["基本设置", "WAN设置"]:
                    menu_items.append({
                        'text': text,
                        'element': span,
                        'id': element_id,
                        'class': element_class,
                        'displayed': is_displayed,
                        'enabled': is_enabled
                    })

        # 详细检查目标菜单项
        logger.info("详细检查目标菜单项...")
        for item in menu_items:
            logger.info(f"菜单项 '{item['text']}':")
            logger.info(f"  ID: {item['id']}")
            logger.info(f"  Class: {item['class']}")
            logger.info(f"  Displayed: {item['displayed']}")
            logger.info(f"  Enabled: {item['enabled']}")

            # 检查父元素
            try:
                parent = item['element'].find_element(By.XPATH, "./..")
                parent_tag = parent.tag_name
                parent_id = parent.get_attribute('id')
                parent_class = parent.get_attribute('class')
                parent_displayed = parent.is_displayed()
                parent_enabled = parent.is_enabled()

                logger.info(f"  父元素: tag={parent_tag}, id={parent_id}, class={parent_class}, displayed={parent_displayed}, enabled={parent_enabled}")
            except Exception as e:
                logger.error(f"  检查父元素时出错: {str(e)}")

        # 点击"基本设置"菜单
        logger.info("点击'基本设置'菜单...")
        basic_settings_menu = None
        for item in menu_items:
            if item['text'] == "基本设置":
                basic_settings_menu = item['element']
                break

        if basic_settings_menu:
            try:
                basic_settings_menu.click()
                logger.info("已点击'基本设置'菜单")
            except Exception as e:
                logger.error(f"点击'基本设置'菜单时出错: {str(e)}")
                # 尝试JavaScript点击
                try:
                    driver.execute_script("arguments[0].click();", basic_settings_menu)
                    logger.info("已使用JavaScript点击'基本设置'菜单")
                except Exception as e2:
                    logger.error(f"使用JavaScript点击'基本设置'菜单时出错: {str(e2)}")
        else:
            logger.error("未找到'基本设置'菜单")

        # 等待子菜单出现
        logger.info("等待子菜单出现...")
        time.sleep(3)

        # 再次检查所有菜单项，特别是"WAN设置"
        logger.info("再次检查所有菜单项...")
        span_elements_after = driver.find_elements(By.TAG_NAME, "span")
        logger.info(f"找到 {len(span_elements_after)} 个span元素")

        wan_settings_found = False
        for i, span in enumerate(span_elements_after):
            text = span.text.strip()
            if text:
                element_id = span.get_attribute('id')
                element_class = span.get_attribute('class')
                is_displayed = span.is_displayed()
                is_enabled = span.is_enabled()

                logger.info(f"  Span {i+1}: text='{text}', id={element_id}, class={element_class}, displayed={is_displayed}, enabled={is_enabled}")

                if text == "WAN设置":
                    wan_settings_found = True
                    logger.info(f"  >>> 找到'WAN设置'菜单项 <<<")

                    # 尝试点击
                    try:
                        span.click()
                        logger.info("  >>> 已点击'WAN设置'菜单 <<<")
                    except Exception as e:
                        logger.error(f"  >>> 点击'WAN设置'菜单时出错: {str(e)} <<<")
                        # 尝试JavaScript点击
                        try:
                            driver.execute_script("arguments[0].click();", span)
                            logger.info("  >>> 已使用JavaScript点击'WAN设置'菜单 <<<")
                        except Exception as e2:
                            logger.error(f"  >>> 使用JavaScript点击'WAN设置'菜单时出错: {str(e2)} <<<")

        if not wan_settings_found:
            logger.error("未找到'WAN设置'菜单项")

        # 保存截图
        driver.save_screenshot("check_menu_status.png")
        logger.info("已保存菜单状态检查截图: check_menu_status.png")

        # 等待观察
        time.sleep(10)

    except Exception as e:
        logger.error(f"检查过程中出现错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        driver.quit()

if __name__ == "__main__":
    check_menu_status()

