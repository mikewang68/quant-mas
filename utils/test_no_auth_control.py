import requests
import re
import json
import time
from urllib3.exceptions import InsecureRequestWarning

# 禁用SSL警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class TPLinkNoAuthController:
    def __init__(self, router_ip):
        self.router_ip = router_ip
        self.base_url = f"http://{router_ip}"
        self.session = requests.Session()
        self.stok = None

        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': f'{self.base_url}/webpages/index.html',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest'
        })

    def get_stok(self):
        """尝试获取stok令牌"""
        print("尝试获取stok令牌...")

        try:
            # 访问主页尝试获取stok
            home_page = self.session.get(f"{self.base_url}/webpages/index.html", timeout=10)
            print(f"主页状态码: {home_page.status_code}")

            # 从URL中提取stok
            stok_match = re.search(r'stok=([a-zA-Z0-9]+)', home_page.url)
            if stok_match:
                self.stok = stok_match.group(1)
                print(f"从URL中提取到stok: {self.stok}")
                return True

            # 从页面内容中提取stok
            stok_match = re.search(r'stok["\s]*[:=]["\s]*"([^"]+)"', home_page.text)
            if stok_match:
                self.stok = stok_match.group(1)
                print(f"从页面内容中提取到stok: {self.stok}")
                return True

            print("未找到stok令牌")
            return False

        except Exception as e:
            print(f"获取stok时出错: {e}")
            return False

    def test_wan_endpoints(self):
        """测试WAN相关端点"""
        print("测试WAN相关端点...")

        # 如果没有stok，尝试使用默认值
        stok_to_use = self.stok if self.stok else "12345"

        wan_endpoints = [
            f"/cgi-bin/luci/;stok={stok_to_use}/admin/status?form=wan",
            f"/cgi-bin/luci/;stok={stok_to_use}/admin/network?form=wan_status",
            f"/cgi-bin/luci/;stok={stok_to_use}/admin/wan",
            f"/cgi-bin/luci/;stok={stok_to_use}/admin/wan?form=connectivity"
        ]

        for endpoint in wan_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                print(f"\n测试端点: {url}")

                # 先尝试GET请求
                response = self.session.get(url, timeout=10)
                print(f"  GET状态码: {response.status_code}")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"  GET响应: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}")
                    except:
                        print(f"  GET响应预览: {response.text[:200]}")

                # 如果GET失败，尝试POST请求（针对connectivity端点）
                if "connectivity" in endpoint and response.status_code != 200:
                    # 测试断开连接
                    disconnect_data = {
                        'operation': 'disconnect',
                        'interface': 'wan2'
                    }
                    post_response = self.session.post(url, json=disconnect_data, timeout=10)
                    print(f"  POST断开状态码: {post_response.status_code}")
                    print(f"  POST断开响应: {post_response.text[:200]}")

                    # 等待几秒
                    time.sleep(3)

                    # 测试连接
                    connect_data = {
                        'operation': 'connect',
                        'interface': 'wan2'
                    }
                    post_response = self.session.post(url, json=connect_data, timeout=10)
                    print(f"  POST连接状态码: {post_response.status_code}")
                    print(f"  POST连接响应: {post_response.text[:200]}")

            except Exception as e:
                print(f"  请求失败: {e}")

    def disconnect_wan2(self):
        """断开WAN2连接"""
        print("尝试断开WAN2连接...")

        # 使用默认stok尝试
        stok_to_use = self.stok if self.stok else "12345"
        url = f"{self.base_url}/cgi-bin/luci/;stok={stok_to_use}/admin/wan?form=connectivity"

        disconnect_data = {
            'operation': 'disconnect',
            'interface': 'wan2'
        }

        try:
            response = self.session.post(url, json=disconnect_data, timeout=10)
            print(f"断开WAN2响应状态码: {response.status_code}")
            print(f"断开WAN2响应内容: {response.text}")

            if response.status_code in [200, 204]:
                print("断开WAN2连接成功")
                return True
            else:
                print("断开WAN2连接失败")
                return False

        except Exception as e:
            print(f"断开WAN2连接时出错: {e}")
            return False

    def connect_wan2(self):
        """连接WAN2"""
        print("尝试连接WAN2...")

        # 使用默认stok尝试
        stok_to_use = self.stok if self.stok else "12345"
        url = f"{self.base_url}/cgi-bin/luci/;stok={stok_to_use}/admin/wan?form=connectivity"

        connect_data = {
            'operation': 'connect',
            'interface': 'wan2'
        }

        try:
            response = self.session.post(url, json=connect_data, timeout=10)
            print(f"连接WAN2响应状态码: {response.status_code}")
            print(f"连接WAN2响应内容: {response.text}")

            if response.status_code in [200, 204]:
                print("连接WAN2成功")
                return True
            else:
                print("连接WAN2失败")
                return False

        except Exception as e:
            print(f"连接WAN2时出错: {e}")
            return False

    def switch_ip(self):
        """切换IP：断开并重新连接WAN2"""
        print("开始切换IP地址...")

        # 获取stok
        self.get_stok()

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

        print("WAN2连接切换完成")
        return True

def main():
    # 路由器配置
    ROUTER_IP = "192.168.1.1"

    print("TP-Link路由器免认证控制测试")
    print(f"路由器IP: {ROUTER_IP}")

    # 创建路由器控制器实例
    router = TPLinkNoAuthController(ROUTER_IP)

    # 测试WAN端点
    router.test_wan_endpoints()

    # 执行IP切换
    # if router.switch_ip():
    #     print("IP地址切换成功")
    #     return True
    # else:
    #     print("IP地址切换失败")
    #     return False

if __name__ == "__main__":
    main()

