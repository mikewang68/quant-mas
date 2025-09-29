import requests
import time
import re
import json
import urllib.parse
import os
from urllib3.exceptions import InsecureRequestWarning

class RouterController:
    def __init__(self, router_ip, username, password):
        self.router_ip = router_ip
        self.username = username
        self.password = password
        self.base_url = f"http://{router_ip}"
        self.session = requests.Session()
        self.stok = None
        self.is_authenticated = False

        # 设置请求头，模拟浏览器访问
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': f'{self.base_url}/webpages/login.html',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest'
        })

        # 禁用SSL警告（如果使用HTTPS）
        requests.packages.urllib3.disable_warnings()

        # 文件路径用于保存最后的IP地址
        self.last_ip_file = "last_wan2_ip.txt"

    def login(self):
        """登录路由器管理界面"""
        # 如果已经认证过，直接返回
        if self.is_authenticated:
            return True

        try:
            print("开始登录路由器...")

            # 先访问登录页面以获取必要的cookies和分析页面结构
            print("访问登录页面...")
            login_page_response = self.session.get(f"{self.base_url}/webpages/login.html", timeout=10)
            print(f"登录页面响应状态码: {login_page_response.status_code}")

            # 打印登录页面的部分内容以分析结构
            content_preview = login_page_response.text[:2000] if len(login_page_response.text) > 2000 else login_page_response.text
            print(f"登录页面内容预览: {content_preview}")

            # 查找可能的隐藏字段或CSRF令牌
            csrf_token_match = re.search(r'name=["\']csrf_token["\']\s+value=["\']([^"\']+)["\']', login_page_response.text)
            if csrf_token_match:
                csrf_token = csrf_token_match.group(1)
                print(f"找到CSRF令牌: {csrf_token}")
            else:
                csrf_token = None
                print("未找到CSRF令牌")

            # 查找可能的其他隐藏字段
            hidden_fields = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*name=["\']([^"\']+)["\'][^>]*value=["\']([^"\']*)["\'][^>]*/?>', login_page_response.text)
            print(f"找到隐藏字段: {hidden_fields}")

            # 查找可能的JavaScript变量或配置
            js_vars = re.findall(r'var\s+(\w+)\s*=\s*["\']([^"\']*)["\']', login_page_response.text)
            print(f"找到JavaScript变量: {js_vars}")

            # TP-Link TL-WAR1200L路由器登录方式 - 尝试多种方法
            print("尝试TL-WAR1200L路由器登录方式...")

            # 方法1: 标准表单提交
            login_data = {
                'method': 'login',
                'username': self.username,
                'password': self.password
            }

            # 添加CSRF令牌（如果找到）
            if csrf_token:
                login_data['csrf_token'] = csrf_token

            # 添加其他隐藏字段
            for field_name, field_value in hidden_fields:
                if field_name not in login_data:  # 避免覆盖已有的字段
                    login_data[field_name] = field_value

            print(f"登录数据: {login_data}")

            # 设置特定的请求头
            self.session.headers.update({
                'Referer': f'{self.base_url}/webpages/login.html',
                'Content-Type': 'application/x-www-form-urlencoded'
            })

            # 尝试POST到登录端点
            login_response = self.session.post(
                f"{self.base_url}/",
                data=login_data,
                timeout=15,
                allow_redirects=False  # 不自动跟随重定向，以便检查响应
            )

            print(f"TL-WAR1200L登录响应状态码: {login_response.status_code}")
            print(f"TL-WAR1200L登录响应头: {dict(login_response.headers)}")

            # 检查是否有重定向
            if 'Location' in login_response.headers:
                print(f"重定向到: {login_response.headers['Location']}")

            # 打印响应内容的前2000个字符
            response_preview = login_response.text[:2000] if len(login_response.text) > 2000 else login_response.text
            print(f"TL-WAR1200L登录响应内容预览: {response_preview}")

            if login_response.status_code in [200, 302, 303]:
                response_text = login_response.text
                print(f"TL-WAR1200L登录响应内容长度: {len(response_text)}")

                # 检查是否登录成功并提取stok
                if self._extract_stok(response_text):
                    self.is_authenticated = True
                    print(f"TL-WAR1200L登录方式成功，获取到stok: {self.stok}")
                    return True

                # 如果没有stok，检查响应内容是否表示登录成功
                if '"success":true' in response_text.lower():
                    print("登录成功，但未找到stok")
                    self.is_authenticated = True
                    return True

                # 检查是否重定向到管理页面（表示登录成功）
                if 'Location' in login_response.headers and '/webpages/index.html' in login_response.headers['Location']:
                    print("登录成功，重定向到管理页面")
                    # 尝试从重定向URL中提取stok
                    if self._extract_stok(login_response.headers['Location']):
                        self.is_authenticated = True
                        print(f"从重定向URL中提取到stok: {self.stok}")
                        return True

            # 方法2: 尝试使用JSON格式的请求
            print("尝试JSON格式的登录请求...")
            json_login_data = {
                'method': 'login',
                'params': {
                    'username': self.username,
                    'password': self.password
                }
            }

            if csrf_token:
                json_login_data['params']['csrf_token'] = csrf_token

            self.session.headers.update({
                'Content-Type': 'application/json',
                'Referer': f'{self.base_url}/webpages/login.html'
            })

            json_login_response = self.session.post(
                f"{self.base_url}/",
                json=json_login_data,
                timeout=15
            )

            print(f"JSON登录响应状态码: {json_login_response.status_code}")

            if json_login_response.status_code == 200:
                response_text = json_login_response.text
                print(f"JSON登录响应内容长度: {len(response_text)}")
                response_preview = response_text[:2000] if len(response_text) > 2000 else response_text
                print(f"JSON登录响应内容预览: {response_preview}")

                # 检查是否登录成功并提取stok
                if self._extract_stok(response_text):
                    self.is_authenticated = True
                    print(f"JSON登录方式成功，获取到stok: {self.stok}")
                    return True

            # 方法3: 尝试UUID-based认证（适用于某些TP-Link路由器）
            print("尝试UUID-based认证...")
            try:
                # 访问登录页面以获取UUID
                uuid_response = self.session.get(f"{self.base_url}/login?operation=login-page", timeout=10)
                print(f"UUID请求响应状态码: {uuid_response.status_code}")

                uuid_match = re.search(r'"uuid"\s*:\s*"([^"]+)"', uuid_response.text)
                if uuid_match:
                    uuid = uuid_match.group(1)
                    print(f"找到UUID: {uuid}")

                    # 使用UUID进行认证
                    auth_data = {
                        'method': 'login',
                        'params': {
                            'username': self.username,
                            'password': self.password,
                            'uuid': uuid
                        }
                    }

                    self.session.headers.update({
                        'Content-Type': 'application/json',
                        'Referer': f'{self.base_url}/webpages/login.html'
                    })

                    auth_response = self.session.post(
                        f"{self.base_url}/login?operation=login",
                        json=auth_data,
                        timeout=15
                    )

                    print(f"UUID认证响应状态码: {auth_response.status_code}")
                    auth_response_preview = auth_response.text[:2000] if len(auth_response.text) > 2000 else auth_response.text
                    print(f"UUID认证响应内容预览: {auth_response_preview}")

                    if auth_response.status_code == 200:
                        if self._extract_stok(auth_response.text):
                            self.is_authenticated = True
                            print(f"UUID认证成功，获取到stok: {self.stok}")
                            return True
                else:
                    print("未找到UUID")
            except Exception as uuid_e:
                print(f"UUID认证过程出错: {uuid_e}")

            # 方法4: 尝试访问管理页面来检查是否已经登录
            print("检查是否已经登录...")
            index_response = self.session.get(f"{self.base_url}/webpages/index.html", timeout=10)
            print(f"管理页面响应状态码: {index_response.status_code}")

            if index_response.status_code == 200:
                index_content = index_response.text[:2000] if len(index_response.text) > 2000 else index_response.text
                print(f"管理页面内容预览: {index_content}")

                # 检查是否能从管理页面提取stok
                if self._extract_stok(index_content):
                    self.is_authenticated = True
                    print(f"已登录，从管理页面提取到stok: {self.stok}")
                    return True

            print("登录失败")
            return False

        except Exception as e:
            print(f"登录过程出错: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _extract_stok(self, response_text):
        """从响应中提取stok"""
        # 方法1: 查找 stok= 格式
        stok_match = re.search(r'[&?]stok=([a-zA-Z0-9]+)', response_text)
        if stok_match:
            self.stok = stok_match.group(1)
            print(f"提取到stok (方法1): {self.stok}")
            return True

        # 方法2: 查找 "stok": "..." 格式
        stok_match2 = re.search(r'"stok["\s]*[:\s]*"([^"]+)"', response_text)
        if stok_match2:
            self.stok = stok_match2.group(1)
            print(f"提取到stok (方法2): {self.stok}")
            return True

        # 方法3: 查找 stok: "...", 格式
        stok_match3 = re.search(r'stok["\s]*[:\s]*"([^"]+)"', response_text)
        if stok_match3:
            self.stok = stok_match3.group(1)
            print(f"提取到stok (方法3): {self.stok}")
            return True

        return False

    def get_wan2_ip(self):
        """获取WAN2口的IP地址"""
        # 先尝试登录
        if not self.login():
            print("登录失败，无法获取IP地址")
            return None

        # 构建API请求URL
        urls_to_try = []
        if self.stok:
            urls_to_try = [
                f"{self.base_url}/cgi-bin/luci/;stok={self.stok}/admin/status?form=wan",
                f"{self.base_url}/cgi-bin/luci/;stok={self.stok}/admin/network?form=wan_status",
                f"{self.base_url}/cgi-bin/luci/;stok={self.stok}/admin/status?form=all"
            ]
        else:
            # 如果没有stok，尝试直接访问
            urls_to_try = [
                f"{self.base_url}/admin/status?form=wan",
                f"{self.base_url}/admin/network?form=wan_status"
            ]

        for url in urls_to_try:
            try:
                print(f"尝试从 {url} 获取IP地址...")
                response = self.session.get(url, timeout=15)
                print(f"状态码: {response.status_code}")

                if response.status_code == 200:
                    content = response.text
                    print(f"响应内容长度: {len(content)}")

                    # 打印响应内容的前1000个字符用于调试
                    content_preview = content[:1000] if len(content) > 1000 else content
                    print(f"响应内容预览: {content_preview}")

                    # 尝试解析为JSON
                    try:
                        json_data = json.loads(content)
                        print(f"JSON数据: {json_data}")
                        ip = self._extract_ip_from_json(json_data)
                        if ip and self._is_valid_ip(ip):
                            print(f"从JSON中提取到IP: {ip}")
                            return ip
                    except Exception as json_e:
                        print(f"JSON解析失败: {json_e}")
                        pass  # 不是JSON格式，继续尝试正则表达式

                    # 尝试多种IP地址匹配模式
                    ip_patterns = [
                        r'wan2[^}]*["\']ip["\'][^}]*["\']([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)["\']',
                        r'wan2[^}]*["\']([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)["\'][^}]*ip',
                        r'"wan2"[^}]*"ip"[^}]*"([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)"',
                        r'"ip"[^}]*"([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)"[^}]*"wan2"',
                        r'wan2[^}]*ip["\s]*["\s]*([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)',
                        r'wan2[^}]*["\s]([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)',
                        r'([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)[^}]*wan2',
                        r'"ip["\s]*["\s]*([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)',
                        r'"([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)"[^}]*"interface"[^}]*"wan2"',
                        r'"interface"[^}]*"wan2"[^}]*"([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)"',
                        r'([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)'
                    ]

                    for pattern in ip_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            if self._is_valid_ip(match):
                                print(f"通过模式 '{pattern}' 找到IP: {match}")
                                return match

            except Exception as e:
                print(f"从 {url} 获取WAN2 IP失败: {e}")
                continue

        print("尝试了所有URL和模式仍未找到有效的WAN2 IP地址")
        return None

    def _extract_ip_from_json(self, json_data):
        """从JSON数据中提取IP地址"""
        # 递归搜索JSON结构
        def search_dict(d):
            if isinstance(d, dict):
                # 检查是否有wan2相关的字段
                for key, value in d.items():
                    if isinstance(value, str) and self._is_valid_ip(value):
                        # 检查键名是否与wan2或ip相关
                        if 'wan2' in key.lower() or 'ip' in key.lower():
                            return value
                    elif isinstance(value, dict):
                        result = search_dict(value)
                        if result:
                            return result
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                result = search_dict(item)
                                if result:
                                    return result
            elif isinstance(d, list):
                for item in d:
                    if isinstance(item, dict):
                        result = search_dict(item)
                        if result:
                            return result
            return None

        return search_dict(json_data)

    def _is_valid_ip(self, ip):
        """验证IP地址是否有效"""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                num = int(part)
                if num < 0 or num > 255:
                    return False
            # 排除一些常见的非公网IP
            if parts[0] == '127' or (parts[0] == '192' and parts[1] == '168') or parts[0] == '10':
                print(f"检测到本地IP地址: {ip}，继续查找...")
                return False
            if parts[0] == '172' and 16 <= int(parts[1]) <= 31:
                print(f"检测到本地IP地址: {ip}，继续查找...")
                return False
            return True
        except:
            return False

    def disconnect_wan2(self):
        """断开WAN2连接"""
        # 确保已登录
        if not self.login():
            print("登录失败，无法断开WAN2连接")
            return False

        # 构建断开连接的URL和数据
        urls_to_try = []
        if self.stok:
            urls_to_try = [
                f"{self.base_url}/cgi-bin/luci/;stok={self.stok}/admin/wan?form=connectivity"
            ]
        else:
            urls_to_try = [
                f"{self.base_url}/admin/wan?form=connectivity"
            ]

        # TP-Link路由器常用的断开连接数据格式
        data_options = [
            {'operation': 'disconnect', 'interface': 'wan2'},
            {'wan_port': 'wan2', 'action': 'disconnect'},
            {'interface': 'wan2', 'operation': 'disconnect'},
            {'operation': 'disconnect', 'port': 'wan2'}
        ]

        for url in urls_to_try:
            for data in data_options:
                try:
                    print(f"尝试断开WAN2连接: {url} with data {data}")
                    response = self.session.post(url, data=data, timeout=15)
                    print(f"断开连接状态码: {response.status_code}")
                    print(f"断开连接响应长度: {len(response.text) if response.text else 0}")

                    # 检查是否成功
                    if response.status_code in [200, 204]:
                        # 检查响应内容是否表示成功
                        response_text = response.text.lower() if response.text else ""
                        if 'success' in response_text or 'ok' in response_text or response.status_code == 204:
                            print("断开WAN2连接请求已发送")
                            return True

                except Exception as e:
                    print(f"断开WAN2连接失败: {e}")
                    continue

        return False

    def connect_wan2(self):
        """连接WAN2"""
        # 确保已登录
        if not self.login():
            print("登录失败，无法连接WAN2")
            return False

        # 构建连接的URL和数据
        urls_to_try = []
        if self.stok:
            urls_to_try = [
                f"{self.base_url}/cgi-bin/luci/;stok={self.stok}/admin/wan?form=connectivity"
            ]
        else:
            urls_to_try = [
                f"{self.base_url}/admin/wan?form=connectivity"
            ]

        # TP-Link路由器常用的连接数据格式
        data_options = [
            {'operation': 'connect', 'interface': 'wan2'},
            {'wan_port': 'wan2', 'action': 'connect'},
            {'interface': 'wan2', 'operation': 'connect'},
            {'operation': 'connect', 'port': 'wan2'}
        ]

        for url in urls_to_try:
            for data in data_options:
                try:
                    print(f"尝试连接WAN2: {url} with data {data}")
                    response = self.session.post(url, data=data, timeout=15)
                    print(f"连接状态码: {response.status_code}")
                    print(f"连接响应长度: {len(response.text) if response.text else 0}")

                    # 检查是否成功
                    if response.status_code in [200, 204]:
                        # 检查响应内容是否表示成功
                        response_text = response.text.lower() if response.text else ""
                        if 'success' in response_text or 'ok' in response_text or response.status_code == 204:
                            print("连接WAN2请求已发送")
                            return True

                except Exception as e:
                    print(f"连接WAN2失败: {e}")
                    continue

        return False

    def switch_ip_until_different(self):
        """切换IP直到获得不同的IP地址"""
        print("正在获取原始IP地址...")
        # 获取原始IP地址
        original_ip = self.get_wan2_ip()
        if not original_ip:
            print("无法获取原始IP地址，请检查路由器设置和网络连接")
            return False

        print(f"原始IP地址: {original_ip}")

        max_attempts = 5  # 最大尝试次数
        attempt = 0

        while attempt < max_attempts:
            attempt += 1
            print(f"\n--- 第 {attempt} 次尝试 ---")

            # 断开WAN2连接
            print("断开WAN2连接...")
            if not self.disconnect_wan2():
                print("断开WAN2连接失败")
                time.sleep(5)
                continue

            # 等待3秒
            print("等待3秒...")
            time.sleep(3)

            # 连接WAN2
            print("连接WAN2...")
            if not self.connect_wan2():
                print("连接WAN2失败")
                time.sleep(5)
                continue

            # 等待一段时间让连接建立
            print("等待连接建立(15秒)...")
            time.sleep(15)

            # 获取新IP地址
            print("获取新IP地址...")
            new_ip = self.get_wan2_ip()
            if not new_ip:
                print("无法获取新IP地址")
                continue

            print(f"新IP地址: {new_ip}")

            # 检查IP是否不同
            if new_ip != original_ip:
                print(f"成功获取不同IP地址: {new_ip}")
                return True
            else:
                print("IP地址相同，继续断开重连...")

        print(f"已达到最大尝试次数 ({max_attempts})，未能获取不同的IP地址")
        return False

def main():
    # 路由器配置
    ROUTER_IP = "192.168.1.1"
    USERNAME = "wangdg68"
    PASSWORD = "wap951020ZJL"
    # WAN2 PPPoE配置信息:
    # 用户名: 15998583399@net
    # 密码: 14350713

    # 创建路由器控制器实例
    router = RouterController(ROUTER_IP, USERNAME, PASSWORD)

    print("开始切换IP地址...")
    if router.switch_ip_until_different():
        print("IP地址切换成功")
    else:
        print("IP地址切换失败")

if __name__ == "__main__":
    main()

