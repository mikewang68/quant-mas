import requests
import json
import time
import re
from urllib3.exceptions import InsecureRequestWarning

# 禁用SSL警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def test_router_api(router_ip):
    """测试路由器API接口"""
    base_url = f"http://{router_ip}"
    session = requests.Session()

    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    }
    session.headers.update(headers)

    print(f"测试路由器 {router_ip} 的API接口...")

    # 1. 测试登录接口
    print("\n1. 测试登录接口...")
    try:
        # 尝试访问登录页面
        login_page = session.get(f"{base_url}/webpages/login.html", timeout=10)
        print(f"登录页面状态码: {login_page.status_code}")

        # 尝试查找stok参数
        stok_match = re.search(r'stok=([a-zA-Z0-9]+)', login_page.text)
        if stok_match:
            stok = stok_match.group(1)
            print(f"找到stok参数: {stok}")
        else:
            print("未找到stok参数")

    except Exception as e:
        print(f"访问登录页面失败: {e}")

    # 2. 测试API端点
    api_endpoints = [
        "/cgi-bin/luci/",
        "/cgi-bin/luci/admin/status",
        "/cgi-bin/luci/admin/network",
        "/cgi-bin/luci/api",
        "/api",
        "/api/v1",
        "/api/v2"
    ]

    print("\n2. 测试API端点...")
    for endpoint in api_endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = session.get(url, timeout=5)
            print(f"{endpoint}: {response.status_code}")
            if response.status_code == 200 and len(response.text) > 0:
                print(f"  内容预览: {response.text[:200]}")
        except Exception as e:
            print(f"{endpoint}: 访问失败 - {e}")

    # 3. 尝试使用默认stok测试
    print("\n3. 测试默认stok...")
    default_stok = "12345"
    test_urls = [
        f"{base_url}/cgi-bin/luci/;stok={default_stok}/admin/status",
        f"{base_url}/cgi-bin/luci/;stok={default_stok}/admin/network",
        f"{base_url}/cgi-bin/luci/;stok={default_stok}/admin/wan"
    ]

    for url in test_urls:
        try:
            response = session.get(url, timeout=5)
            print(f"{url}: {response.status_code}")
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    print(f"  JSON响应: {json.dumps(json_data, indent=2, ensure_ascii=False)[:200]}")
                except:
                    print(f"  响应内容: {response.text[:200]}")
        except Exception as e:
            print(f"{url}: 访问失败 - {e}")

def main():
    ROUTER_IP = "192.168.1.1"
    test_router_api(ROUTER_IP)

if __name__ == "__main__":
    main()

