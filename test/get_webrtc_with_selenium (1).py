#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用Selenium WebDriver配合ChromeDriver获取ident.me网站的WebRTC IPv4地址
"""

import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def setup_chrome_driver():
    """
    设置Chrome WebDriver
    """
    # 配置Chrome选项
    chrome_options = Options()

    # 无头模式（可选，如果需要可视化可以注释掉）
    # chrome_options.add_argument("--headless")

    # 其他有用的选项
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # 禁用自动化控制特征
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # 自动下载和设置ChromeDriver
    service = Service(ChromeDriverManager().install())

    # 创建WebDriver实例
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 绕过WebDriver检测
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver

def get_webrtc_ips():
    """
    获取WebRTC IP地址
    """
    driver = None
    try:
        print("正在初始化Chrome WebDriver...")
        driver = setup_chrome_driver()

        print("正在访问 https://www.ident.me/ ...")
        driver.get("https://www.ident.me/")

        print("等待页面加载...")
        # 等待页面主要元素加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )

        print("等待WebRTC地址加载(最多30秒)...")
        # 等待WebRTC地址加载完成，最多等待30秒
        webrtc_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "webrtc"))
        )

        # 持续检查元素内容，直到不再是"Loading..."
        start_time = time.time()
        while time.time() - start_time < 30:  # 最多等待30秒
            webrtc_text = webrtc_element.text.strip()
            if webrtc_text and webrtc_text != "Loading...":
                print(f"WebRTC地址已加载: {webrtc_text}")
                break
            time.sleep(1)
        else:
            print("超时: WebRTC地址仍未加载完成")
            webrtc_text = webrtc_element.text

        # 获取页面完整内容用于备用分析
        page_source = driver.page_source

        # 尝试从页面源码中提取IPv4地址
        ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ipv4_addresses = re.findall(ipv4_pattern, page_source)

        # 过滤有效的IPv4地址
        valid_ips = []
        for ip in ipv4_addresses:
            try:
                octets = ip.split('.')
                if len(octets) == 4 and all(0 <= int(octet) <= 255 for octet in octets):
                    # 排除一些特殊地址
                    if not ip.startswith(('127.', '0.', '255.', '224.')) and ip != '1.1.1.1':
                        valid_ips.append(ip)
            except ValueError:
                continue

        # 去重并排序
        unique_ips = sorted(list(set(valid_ips)))

        print("\n=== 结果 ===")
        if unique_ips:
            print("找到的可能WebRTC IPv4地址:")
            for ip in unique_ips:
                print(f"  - {ip}")
        else:
            print("未找到有效的IPv4地址")

        print(f"\nWebRTC元素文本内容: {webrtc_text}")

        return unique_ips

    except Exception as e:
        print(f"发生错误: {e}")
        return []

    finally:
        if driver:
            print("\n关闭浏览器...")
            driver.quit()

def get_webrtc_ips_with_js():
    """
    使用JavaScript直接获取WebRTC地址（备用方法）
    """
    driver = None
    try:
        print("正在初始化Chrome WebDriver...")
        driver = setup_chrome_driver()

        print("正在访问测试页面...")
        # 创建一个简单的HTML页面来执行WebRTC代码
        html_content = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>WebRTC Test</title>
        </head>
        <body>
            <h1>WebRTC IP Address Detection</h1>
            <div id="ips"></div>
            <script>
                function getIPs(callback) {
                    var ips = [];
                    var pc = new RTCPeerConnection({
                        iceServers: []
                    });

                    pc.createDataChannel("");
                    pc.onicecandidate = function(e) {
                        if (!e.candidate) {
                            pc.close();
                            callback(ips);
                            return;
                        }
                        var ip = /^candidate:.+ (\S+) /gm.exec(e.candidate.candidate);
                        if (ip) {
                            ips.push(ip[1]);
                        }
                    };
                    pc.createOffer(function(sdp) {
                        pc.setLocalDescription(sdp, function() {}, function() {});
                    }, function() {});
                }

                getIPs(function(ips) {
                    document.getElementById("ips").innerHTML = ips.join("<br>");
                });
            </script>
        </body>
        </html>
        '''

        # 通过data URI加载页面
        driver.get("data:text/html;charset=utf-8," + html_content)

        print("等待WebRTC地址获取(最多10秒)...")
        time.sleep(10)  # 等待JavaScript执行

        try:
            # 尝试获取IP地址
            ips_element = driver.find_element(By.ID, "ips")
            ips_text = ips_element.text

            if ips_text:
                print(f"通过JavaScript获取的IP地址: {ips_text}")
                return ips_text.split('\n')
            else:
                print("JavaScript方法未获取到IP地址")
                return []
        except Exception as e:
            print(f"JavaScript方法出错: {e}")
            return []

    except Exception as e:
        print(f"发生错误: {e}")
        return []

    finally:
        if driver:
            print("关闭浏览器...")
            driver.quit()

if __name__ == "__main__":
    print("=== 使用Selenium WebDriver获取WebRTC IPv4地址 ===\n")

    print("方法1: 访问ident.me网站获取WebRTC地址")
    ips1 = get_webrtc_ips()

    print("\n" + "="*50 + "\n")

    print("方法2: 使用JavaScript直接获取WebRTC地址")
    ips2 = get_webrtc_ips_with_js()

    # 合并结果
    all_ips = list(set(ips1 + ips2))

    print("\n=== 最终结果 ===")
    if all_ips:
        print("获取到的WebRTC IPv4地址:")
        for ip in sorted(all_ips):
            print(f"  - {ip}")
    else:
        print("未能获取到WebRTC IPv4地址")

