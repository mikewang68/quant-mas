import requests
import re
import json
import time
from urllib3.exceptions import InsecureRequestWarning

# 禁用SSL警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def analyze_encrypt_js(router_ip):
    """分析路由器的加密JavaScript文件"""
    base_url = f"http://{router_ip}"
    session = requests.Session()

    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': f'{base_url}/webpages/login.html'
    }
    session.headers.update(headers)

    print(f"分析路由器 {router_ip} 的加密JavaScript文件...")

    try:
        # 1. 下载encrypt.js文件
        print("\n1. 下载encrypt.js文件...")
        encrypt_js_url = f"{base_url}/js/libs/encrypt.js"
        encrypt_js_response = session.get(encrypt_js_url, timeout=10)
        print(f"encrypt.js状态码: {encrypt_js_response.status_code}")
        print(f"encrypt.js内容长度: {len(encrypt_js_response.text)}")

        # 保存encrypt.js文件
        with open('encrypt.js', 'w', encoding='utf-8') as f:
            f.write(encrypt_js_response.text)
        print("encrypt.js已保存到 encrypt.js")

        # 2. 分析加密函数
        print("\n2. 分析加密函数...")
        encrypt_content = encrypt_js_response.text

        # 查找加密相关的函数定义
        encrypt_functions = re.findall(r'function\s+(\w*encrypt\w*)\s*\([^)]*\)', encrypt_content, re.IGNORECASE)
        print(f"找到加密函数: {encrypt_functions}")

        # 查找RSA相关代码
        rsa_patterns = [
            r'RSA',
            r'rsa',
            r'encrypt',
            r'decrypt',
            r'key',
            r'modulus',
            r'exponent'
        ]

        print("查找加密相关代码:")
        for pattern in rsa_patterns:
            matches = re.findall(rf'({pattern}.*?)[;{{\n]', encrypt_content, re.IGNORECASE)
            if matches:
                print(f"  {pattern} 相关代码:")
                for match in matches[:3]:  # 只显示前3个匹配
                    print(f"    - {match}")

        # 3. 下载su.full.min.js文件
        print("\n3. 下载su.full.min.js文件...")
        su_js_url = f"{base_url}/js/su/su.full.min.js"
        su_js_response = session.get(su_js_url, timeout=10)
        print(f"su.full.min.js状态码: {su_js_response.status_code}")
        print(f"su.full.min.js内容长度: {len(su_js_response.text)}")

        # 保存su.full.min.js文件
        with open('su.full.min.js', 'w', encoding='utf-8') as f:
            f.write(su_js_response.text)
        print("su.full.min.js已保存到 su.full.min.js")

        # 4. 分析su.full.min.js中的登录相关代码
        print("\n4. 分析su.full.min.js中的登录相关代码...")
        su_content = su_js_response.text

        # 查找登录相关的函数和代码
        login_patterns = [
            r'login',
            r'auth',
            r'proxy',
            r'stok',
            r'token'
        ]

        print("查找登录相关代码:")
        for pattern in login_patterns:
            matches = re.findall(rf'({pattern}.*?)[;{{\n]', su_content, re.IGNORECASE)
            if matches:
                print(f"  {pattern} 相关代码:")
                for match in matches[:3]:  # 只显示前3个匹配
                    print(f"    - {match}")

        # 5. 查找$.su.Proxy相关代码
        print("\n5. 查找$.su.Proxy相关代码...")
        proxy_matches = re.findall(r'(\$.su\.Proxy.*?)[;{{\n]', su_content)
        if proxy_matches:
            print("找到$.su.Proxy相关代码:")
            for match in proxy_matches[:5]:
                print(f"  - {match}")

        # 6. 查找可能的API调用格式
        print("\n6. 查找可能的API调用格式...")
        api_call_patterns = [
            r'\.ajax\(',
            r'\.post\(',
            r'\.get\(',
            r'url\s*:',
            r'method\s*:',
            r'data\s*:'
        ]

        for pattern in api_call_patterns:
            matches = re.findall(rf'({pattern}.*?)[;{{\n]', su_content)
            if matches:
                print(f"  {pattern} 相关代码:")
                for match in matches[:3]:
                    print(f"    - {match}")

    except Exception as e:
        print(f"分析过程中出错: {e}")
        import traceback
        traceback.print_exc()

def main():
    ROUTER_IP = "192.168.1.1"
    analyze_encrypt_js(ROUTER_IP)

if __name__ == "__main__":
    main()

