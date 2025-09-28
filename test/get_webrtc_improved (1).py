#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
改进版本：使用Selenium WebDriver获取真实的WebRTC IPv4地址
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

    # 允许WebRTC
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")

    # 自动下载和设置ChromeDriver
    service = Service(ChromeDriverManager().install())

    # 创建WebDriver实例
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 绕过WebDriver检测
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver

def get_webrtc_ips_direct():
    """
    使用JavaScript直接获取WebRTC地址
    """
    driver = None
    try:
        print("正在初始化Chrome WebDriver...")
        driver = setup_chrome_driver()

        print("正在创建WebRTC测试页面...")
        # 创建一个专门用于WebRTC检测的页面
        html_content = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>WebRTC IP Detection</title>
        </head>
        <body>
            <h1>WebRTC IP Address Detection</h1>
            <div id="local-ips">
                <h2>Local IPs:</h2>
                <ul id="ip-list"></ul>
            </div>
            <div id="status">Detecting IPs...</div>
            <script>
                var ips = [];

                function addIP(ip) {
                    if (ips.indexOf(ip) === -1) {
                        ips.push(ip);
                        var li = document.createElement("li");
                        li.textContent = ip;
                        document.getElementById("ip-list").appendChild(li);
                        console.log("Found IP: " + ip);
                    }
                }

                function getIPs() {
                    // Compatibility for different browsers
                    var RTCPeerConnection = window.RTCPeerConnection ||
                        window.webkitRTCPeerConnection ||
                        window.mozRTCPeerConnection;

                    if (!RTCPeerConnection) {
                        document.getElementById("status").textContent = "WebRTC not supported";
                        return;
                    }

                    var rtc = new RTCPeerConnection({iceServers:[]});

                    rtc.createDataChannel("");

                    rtc.onicecandidate = function (ice) {
                        if (!ice || !ice.candidate || !ice.candidate.candidate) return;

                        var myIP = /([0-9]{1,3}(\\.[0-9]{1,3}){3})/.exec(ice.candidate.candidate)[1];
                        if (myIP) {
                            addIP(myIP);
                        }

                        document.getElementById("status").textContent = "Found " + ips.length + " IP(s)";
                    };

                    rtc.createOffer(
                        function (offerDesc) {
                            rtc.setLocalDescription(offerDesc, function () {}, function () {});
                        },
                        function (e) {
                            console.warn("Offer failed: ", e);
                            document.getElementById("status").textContent = "Error: " + e;
                        }
                    );
                }

                // Start detection
                getIPs();
            </script>
        </body>
        </html>
        '''

        # 通过data URI加载页面
        driver.get("data:text/html;charset=utf-8," + html_content)

        print("等待WebRTC地址获取(最多15秒)...")
        time.sleep(15)  # 等待JavaScript执行

        # 尝试获取IP地址列表
        ip_addresses = []
        try:
            # 获取所有li元素中的IP地址
            ip_elements = driver.find_elements(By.CSS_SELECTOR, "#ip-list li")
            for element in ip_elements:
                ip_text = element.text.strip()
                if ip_text:
                    # 验证是否为有效的IPv4地址
                    ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
                    if re.match(ipv4_pattern, ip_text):
                        ip_addresses.append(ip_text)

            print(f"通过JavaScript获取的IP地址: {ip_addresses}")
        except Exception as e:
            print(f"获取IP地址时出错: {e}")

        # 也尝试从控制台日志获取信息
        try:
            logs = driver.get_log('browser')
            for log in logs:
                if 'Found IP' in log['message']:
                    print(f"浏览器日志: {log['message']}")
        except:
            pass

        return ip_addresses

    except Exception as e:
        print(f"发生错误: {e}")
        return []

    finally:
        if driver:
            print("关闭浏览器...")
            driver.quit()

def get_webrtc_ips_from_identme():
    """
    从ident.me网站获取WebRTC地址
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
        # 等待WebRTC地址加载完成
        webrtc_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "webrtc"))
        )

        # 持续检查元素内容，直到不再是"Loading..."
        start_time = time.time()
        webrtc_text = ""
        while time.time() - start_time < 30:  # 最多等待30秒
            webrtc_text = webrtc_element.text.strip()
            if webrtc_text and webrtc_text != "Loading...":
                print(f"WebRTC地址已加载: {webrtc_text}")
                break
            time.sleep(1)

        # 尝试从页面中提取IPv4地址
        page_source = driver.page_source

        # 查找IPv4地址模式
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
                        # 检查是否为合理的私有地址或公网地址
                        if (ip.startswith(('192.168.', '10.', '172.16.', '172.17.', '172.18.', '172.19.',
                                          '172.20.', '172.21.', '172.22.', '172.23.', '172.24.', '172.25.',
                                          '172.26.', '172.27.', '172.28.', '172.29.', '172.30.', '172.31.')) or
                            not ip.startswith(('192.168.', '10.', '172.'))):
                            valid_ips.append(ip)
            except ValueError:
                continue

        # 去重
        unique_ips = list(set(valid_ips))

        print(f"\n从页面源码提取的IPv4地址: {unique_ips}")
        print(f"WebRTC元素直接文本: '{webrtc_text}'")

        return unique_ips

    except Exception as e:
        print(f"发生错误: {e}")
        return []

    finally:
        if driver:
            print("关闭浏览器...")
            driver.quit()

if __name__ == "__main__":
    print("=== 改进版：使用Selenium WebDriver获取WebRTC IPv4地址 ===\n")

    print("方法1: 使用JavaScript直接获取WebRTC地址")
    ips1 = get_webrtc_ips_direct()

    print("\n" + "="*50 + "\n")

    print("方法2: 从ident.me网站获取WebRTC地址")
    ips2 = get_webrtc_ips_from_identme()

    # 合并结果
    all_ips = list(set(ips1 + ips2))

    print("\n=== 最终结果 ===")
    if all_ips:
        print("获取到的WebRTC IPv4地址:")
        for ip in sorted(all_ips):
            print(f"  - {ip}")
    else:
        print("未能获取到WebRTC IPv4地址")

    print("\n说明:")
    print("- 私有地址范围 (可能的本地IP):")
    print("  * 192.168.x.x")
    print("  * 10.x.x.x")
    print("  * 172.16.x.x - 172.31.x.x")
    print("- 其他为公网IP地址")

