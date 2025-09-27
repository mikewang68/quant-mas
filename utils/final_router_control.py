import requests
import re
import json
import time
from urllib3.exceptions import InsecureRequestWarning

# 禁用SSL警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class TPLinkRouterController:
    def __init__(self, router_ip, username, password):
        self.router_ip = router_ip
        self.username = username
        self.password = password
        self.base_url = f"http://{router_ip}"
        self.session = requests.Session()
        self.stok = None

        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': f'{self.base_url}/webpages/login.html',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest'
        })

    def _extract_stok(self, response_text):
        """从响应中提取stok"""
        stok_match = re.search(r'stok=([a-zA-Z0-9]+)', response_text)
        if stok_match:
            self.stok = stok_match.group(1)
            print(f"提取到stok: {self.stok}")
            return True
        return False

    def login(self):
        """登录路由器"""
        print("开始登录路由器...")

        try:
            # 1. 访问登录页面以获取初始信息
            print("访问登录页面...")
            login_page = self.session.get(f"{self.base_url}/webpages/login.html", timeout=10)
            print(f"登录页面状态码: {login_page.status_code}")

            # 尝试从登录页面提取stok
            self._extract_stok(login_page.text)

            # 2. 尝试通过/cgi-bin/luci/login端点登录
            print("尝试通过/cgi-bin/luci/login登录...")
            login_data = {
                'method': 'login',
                'params': {
                    'username': self.username,
                    'password': self.password
                }
            }

            login_response = self.session.post(
                f"{self.base_url}/cgi-bin/luci/login",
                json=login_data,
                timeout=15
            )

            print(f"登录响应状态码: {login_response.status_code}")
            print(f"登录响应内容: {login_response.text}")

            # 检查是否登录成功
            if login_response.status_code == 200:
                try:
                    response_json = login_response.json()
                    if 'result' in response_json and response_json['result'] == 'success':
                        print("登录成功!")
                        # 尝试提取stok
                        if 'stok' in response_json:
                            self.stok = response_json['stok']
                            print(f"获取到stok: {self.stok}")
                        return True
                    elif 'error_code' in response_json:
                        print(f"登录失败，错误代码: {response_json['error_code']}")
                except:
                    # 如果不是JSON响应，检查是否包含stok
                    if self._extract_stok(login_response.text):
                        print("登录成功!")
                        return True

            # 3. 如果上述方法失败，尝试其他登录方式
            print("尝试其他登录方式...")
            alternative_login_data = [
                {'method': 'login', 'username': self.username, 'password': self.password},
                {'username': self.username, 'password': self.password},
                {'user': self.username, 'pass': self.password}
            ]

            for data in alternative_login_data:
                try:
                    alt_response = self.session.post(
                        f"{self.base_url}/",
                        json=data,
                        timeout=10
                    )
                    print(f"替代登录方式响应: {alt_response.status_code}")
                    if self._extract_stok(alt_response.text):
                        print("通过替代方式登录成功!")
                        return True
                except Exception as e:
                    print(f"替代登录方式失败: {e}")
                    continue

            print("所有登录方式都失败")
            return False

        except Exception as e:
            print(f"登录过程中出错: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_wan_status(self):
        """获取WAN口状态"""
        if not self.stok:
            print("未登录，无法获取WAN状态")
            return None

        try:
            print("获取WAN口状态...")
            url = f"{self.base_url}/cgi-bin/luci/;stok={self.stok}/admin/status?form=wan"
            response = self.session.get(url, timeout=10)
            print(f"WAN状态响应状态码: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"WAN状态数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    return data
                except:
                    print(f"WAN状态响应内容: {response.text[:500]}")
                    return response.text
            else:
                print(f"获取WAN状态失败: {response.status_code}")
                return None

        except Exception as e:
            print(f"获取WAN状态时出错: {e}")
            return None

    def disconnect_wan2(self):
        """断开WAN2连接"""
        if not self.stok:
            print("未登录，无法断开WAN2连接")
            return False

        try:
            print("断开WAN2连接...")
            url = f"{self.base_url}/cgi-bin/luci/;stok={self.stok}/admin/wan?form=connectivity"

            # 尝试多种数据格式
            disconnect_data_options = [
                {'operation': 'disconnect', 'interface': 'wan2'},
                {'wan_port': 'wan2', 'action': 'disconnect'},
                {'interface': 'wan2', 'operation': 'disconnect'},
                {'operation': 'disconnect', 'port': 'wan2'}
            ]

            for data in disconnect_data_options:
                try:
                    print(f"尝试断开WAN2连接，数据: {data}")
                    response = self.session.post(url, json=data, timeout=10)
                    print(f"断开连接响应状态码: {response.status_code}")
                    print(f"断开连接响应内容: {response.text}")

                    if response.status_code in [200, 204]:
                        print("断开WAN2连接请求已发送")
                        return True
                except Exception as e:
                    print(f"断开WAN2连接失败: {e}")
                    continue

            print("所有断开WAN2连接的方式都失败")
            return False

        except Exception as e:
            print(f"断开WAN2连接时出错: {e}")
            return False

    def connect_wan2(self):
        """连接WAN2"""
        if not self.stok:
            print("未登录，无法连接WAN2")
            return False

        try:
            print("连接WAN2...")
            url = f"{self.base_url}/cgi-bin/luci/;stok={self.stok}/admin/wan?form=connectivity"

            # 尝试多种数据格式
            connect_data_options = [
                {'operation': 'connect', 'interface': 'wan2'},
                {'wan_port': 'wan2', 'action': 'connect'},
                {'interface': 'wan2', 'operation': 'connect'},
                {'operation': 'connect', 'port': 'wan2'}
            ]

            for data in connect_data_options:
                try:
                    print(f"尝试连接WAN2，数据: {data}")
                    response = self.session.post(url, json=data, timeout=10)
                    print(f"连接响应状态码: {response.status_code}")
                    print(f"连接响应内容: {response.text}")

                    if response.status_code in [200, 204]:
                        print("连接WAN2请求已发送")
                        return True
                except Exception as e:
                    print(f"连接WAN2失败: {e}")
                    continue

            print("所有连接WAN2的方式都失败")
            return False

        except Exception as e:
            print(f"连接WAN2时出错: {e}")
            return False

    def switch_ip(self):
        """切换IP：断开并重新连接WAN2"""
        print("开始切换IP地址...")

        # 登录路由器
        if not self.login():
            print("登录失败，无法切换IP")
            return False

        # 获取当前WAN状态
        self.get_wan_status()

        # 断开WAN2连接
        print("断开WAN2连接...")
        if not self.disconnect_wan2():
            print("断开WAN2连接失败")
            return False

        # 等待3秒
        print("等待3秒...")
        time.sleep(3)

        # 连接WAN2
        print("连接WAN2...")
        if not self.connect_wan2():
            print("连接WAN2失败")
            return False

        # 等待一段时间让连接建立
        print("等待连接建立(15秒)...")
        time.sleep(15)

        # 再次获取WAN状态
        self.get_wan_status()

        print("WAN2连接切换完成")
        return True

def main():
    # 路由器配置
    ROUTER_IP = "192.168.1.1"
    USERNAME = "wangdg68"
    PASSWORD = "wap951020ZJL"
    # WAN2 PPPoE配置信息:
    # 用户名: 15998583399@net
    # 密码: 14350713

    print("TP-Link路由器控制脚本")
    print(f"路由器IP: {ROUTER_IP}")
    print(f"用户名: {USERNAME}")

    # 创建路由器控制器实例
    router = TPLinkRouterController(ROUTER_IP, USERNAME, PASSWORD)

    # 执行IP切换
    if router.switch_ip():
        print("IP地址切换成功")
        return True
    else:
        print("IP地址切换失败")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

