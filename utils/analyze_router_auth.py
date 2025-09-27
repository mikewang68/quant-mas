import requests
import re
import json
import time
from urllib3.exceptions import InsecureRequestWarning

# 禁用SSL警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def analyze_router_login(router_ip, username, password):
    """分析路由器登录认证机制"""
    base_url = f"http://{router_ip}"
    session = requests.Session()

    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': f'{base_url}/webpages/login.html',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    }
    session.headers.update(headers)

    print(f"分析路由器 {router_ip} 的登录认证机制...")

    try:
        # 1. 访问登录页面
        print("\n1. 访问登录页面...")
        login_page = session.get(f"{base_url}/webpages/login.html", timeout=10)
        print(f"登录页面状态码: {login_page.status_code}")
        print(f"登录页面标题: {re.search(r'<title>(.*?)</title>', login_page.text).group(1) if re.search(r'<title>(.*?)</title>', login_page.text) else '无标题'}")

        # 保存登录页面内容用于分析
        with open('login_page.html', 'w', encoding='utf-8') as f:
            f.write(login_page.text)
        print("登录页面已保存到 login_page.html")

        # 2. 分析登录页面中的JavaScript文件
        print("\n2. 分析登录页面中的JavaScript文件...")
        js_files = re.findall(r'<script[^>]*src=["\']([^"\']*\.js[^"\']*)["\'][^>]*>', login_page.text)
        print(f"找到 {len(js_files)} 个JavaScript文件:")
        for js_file in js_files:
            print(f"  - {js_file}")

        # 3. 查找表单信息
        print("\n3. 查找登录表单信息...")
        form_actions = re.findall(r'<form[^>]*action=["\']([^"\']*)["\'][^>]*>', login_page.text)
        print(f"表单action: {form_actions}")

        input_fields = re.findall(r'<input[^>]*name=["\']([^"\']*)["\'][^>]*>', login_page.text)
        print(f"输入字段: {input_fields}")

        # 4. 查找可能的认证相关JavaScript代码
        print("\n4. 查找认证相关JavaScript代码...")
        auth_patterns = [
            r'login',
            r'auth',
            r'encrypt',
            r'password',
            r'stok',
            r'token'
        ]

        for pattern in auth_patterns:
            matches = re.findall(rf'({pattern}.*?)["\';\n]', login_page.text, re.IGNORECASE)
            if matches:
                print(f"  {pattern} 相关代码:")
                for match in matches[:5]:  # 只显示前5个匹配
                    print(f"    - {match}")

        # 5. 尝试模拟登录
        print("\n5. 尝试模拟登录...")

        # 查找可能的登录端点
        login_endpoints = [
            "/",
            "/login",
            "/cgi-bin/luci",
            "/cgi-bin/luci/login"
        ]

        # 尝试不同的登录数据格式
        login_data_formats = [
            {'method': 'login', 'username': username, 'password': password},
            {'username': username, 'password': password},
            {'user': username, 'pass': password},
            {'login': {'username': username, 'password': password}}
        ]

        for endpoint in login_endpoints:
            for login_data in login_data_formats:
                try:
                    print(f"\n尝试端点: {endpoint}, 数据: {login_data}")
                    response = session.post(f"{base_url}{endpoint}", data=login_data, timeout=10)
                    print(f"  状态码: {response.status_code}")
                    print(f"  响应长度: {len(response.text)}")

                    # 检查是否包含stok
                    stok_match = re.search(r'stok=([a-zA-Z0-9]+)', response.text)
                    if stok_match:
                        print(f"  找到stok: {stok_match.group(1)}")

                    # 检查是否是JSON响应
                    try:
                        json_data = response.json()
                        print(f"  JSON响应: {json.dumps(json_data, indent=2, ensure_ascii=False)[:200]}")
                    except:
                        # 检查是否包含成功或失败的关键字
                        if 'success' in response.text.lower() or 'error' in response.text.lower():
                            print(f"  响应预览: {response.text[:200]}")

                except Exception as e:
                    print(f"  请求失败: {e}")

    except Exception as e:
        print(f"分析过程中出错: {e}")
        import traceback
        traceback.print_exc()

def main():
    ROUTER_IP = "192.168.1.1"
    USERNAME = "wangdg68"
    PASSWORD = "wap951020ZJL"

    analyze_router_login(ROUTER_IP, USERNAME, PASSWORD)

if __name__ == "__main__":
    main()

