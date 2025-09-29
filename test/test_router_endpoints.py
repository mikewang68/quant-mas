import requests
import re
import json
import time
from urllib3.exceptions import InsecureRequestWarning

# 禁用SSL警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def test_router_endpoints(router_ip, username, password):
    """测试路由器的各种端点和认证方式"""
    base_url = f"http://{router_ip}"
    session = requests.Session()

    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': f'{base_url}/webpages/login.html',
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    }
    session.headers.update(headers)

    print(f"测试路由器 {router_ip} 的各种端点和认证方式...")

    # 1. 测试登录相关端点
    print("\n1. 测试登录相关端点...")
    login_endpoints = [
        "/",
        "/login",
        "/login?operation=login-page",
        "/login?operation=login",
        "/cgi-bin/luci/",
        "/cgi-bin/luci/login",
        "/cgi-bin/luci/;stok=/login",
        "/webpages/login.html"
    ]

    for endpoint in login_endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\n测试: {url}")

            if "login-page" in endpoint or "login.html" in endpoint:
                # GET请求
                response = session.get(url, timeout=10)
            else:
                # POST请求，尝试不同的数据格式
                login_data = {
                    'method': 'login',
                    'username': username,
                    'password': password
                }
                response = session.post(url, json=login_data, timeout=10)

            print(f"  状态码: {response.status_code}")
            print(f"  响应长度: {len(response.text)}")

            # 如果是JSON响应，解析并显示
            try:
                json_data = response.json()
                print(f"  JSON响应: {json.dumps(json_data, indent=2, ensure_ascii=False)[:300]}")
            except:
                # 显示文本响应的前200个字符
                print(f"  响应预览: {response.text[:200]}")

        except Exception as e:
            print(f"  请求失败: {e}")

    # 2. 测试获取UUID（某些TP-Link路由器需要）
    print("\n2. 测试获取UUID...")
    try:
        uuid_url = f"{base_url}/login?operation=login-page"
        uuid_response = session.get(uuid_url, timeout=10)
        print(f"UUID请求状态码: {uuid_response.status_code}")

        # 查找UUID
        uuid_match = re.search(r'"uuid"\s*:\s*"([^"]+)"', uuid_response.text)
        if uuid_match:
            uuid = uuid_match.group(1)
            print(f"找到UUID: {uuid}")

            # 使用UUID尝试登录
            print("\n使用UUID尝试登录...")
            login_with_uuid_data = {
                'method': 'login',
                'params': {
                    'username': username,
                    'password': password,
                    'uuid': uuid
                }
            }

            login_uuid_response = session.post(f"{base_url}/login?operation=login", json=login_with_uuid_data, timeout=10)
            print(f"UUID登录状态码: {login_uuid_response.status_code}")
            print(f"UUID登录响应: {login_uuid_response.text[:300]}")
        else:
            print("未找到UUID")

    except Exception as e:
        print(f"获取UUID失败: {e}")

    # 3. 测试stok相关端点
    print("\n3. 测试stok相关端点...")
    # 先尝试获取stok
    stok = "12345"  # 默认stok
    stok_endpoints = [
        f"/cgi-bin/luci/;stok={stok}/admin/status",
        f"/cgi-bin/luci/;stok={stok}/admin/network",
        f"/cgi-bin/luci/;stok={stok}/admin/wan",
        f"/cgi-bin/luci/;stok={stok}/admin/wan?form=connectivity"
    ]

    for endpoint in stok_endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\n测试stok端点: {url}")
            response = session.get(url, timeout=10)
            print(f"  状态码: {response.status_code}")
            print(f"  响应长度: {len(response.text)}")

            # 尝试解析JSON
            try:
                json_data = response.json()
                print(f"  JSON响应: {json.dumps(json_data, indent=2, ensure_ascii=False)[:200]}")
            except:
                print(f"  响应预览: {response.text[:200]}")

        except Exception as e:
            print(f"  请求失败: {e}")

def main():
    ROUTER_IP = "192.168.1.1"
    USERNAME = "wangdg68"
    PASSWORD = "wap951020ZJL"

    test_router_endpoints(ROUTER_IP, USERNAME, PASSWORD)

if __name__ == "__main__":
    main()

