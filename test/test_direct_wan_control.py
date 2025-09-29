import requests
import re
import json
import time
from urllib3.exceptions import InsecureRequestWarning

# 禁用SSL警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class TPLinkDirectWANController:
    def __init__(self, router_ip):
        self.router_ip = router_ip
        self.base_url = f"http://{router_ip}"
        self.session = requests.Session()

        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': f'{self.base_url}/webpages/index.html',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest'
        })

    def test_direct_wan_control(self):
        """测试直接WAN控制命令"""
        print("测试直接WAN控制命令...")

        # 尝试不同的WAN控制端点和数据格式
        control_endpoints = [
            "/cgi-bin/luci/admin/wan?form=connectivity",
            "/cgi-bin/luci/;stok=/admin/wan?form=connectivity",
            "/admin/wan?form=connectivity"
        ]

        control_data_formats = [
            {'operation': 'disconnect', 'interface': 'wan2'},
            {'operation': 'connect', 'interface': 'wan2'},
            {'wan_port': 'wan2', 'action': 'disconnect'},
            {'wan_port': 'wan2', 'action': 'connect'},
            {'interface': 'wan2', 'operation': 'disconnect'},
            {'interface': 'wan2', 'operation': 'connect'}
        ]

        for endpoint in control_endpoints:
            for data in control_data_formats:
                try:
                    url = f"{self.base_url}{endpoint}"
                    print(f"\n测试端点: {url}")
                    print(f"测试数据: {data}")

                    # 尝试POST请求
                    response = self.session.post(url, data=data, timeout=10)
                    print(f"  状态码: {response.status_code}")
                    print(f"  响应内容: {response.text[:200]}")

                    # 如果是JSON响应，解析并显示
                    try:
                        json_data = response.json()
                        print(f"  JSON响应: {json.dumps(json_data, indent=2, ensure_ascii=False)[:200]}")
                    except:
                        pass

                except Exception as e:
                    print(f"  请求失败: {e}")

    def disconnect_wan2(self):
        """断开WAN2连接"""
        print("尝试断开WAN2连接...")

        # 尝试多种端点和数据格式
        endpoints = [
            "/cgi-bin/luci/admin/wan?form=connectivity",
            "/admin/wan?form=connectivity"
        ]

        disconnect_data = [
            {'operation': 'disconnect', 'interface': 'wan2'},
            {'wan_port': 'wan2', 'action': 'disconnect'},
            {'interface': 'wan2', 'operation': 'disconnect'}
        ]

        for endpoint in endpoints:
            for data in disconnect_data:
                try:
                    url = f"{self.base_url}{endpoint}"
                    print(f"断开WAN2 - 端点: {url}, 数据: {data}")

                    response = self.session.post(url, data=data, timeout=10)
                    print(f"  状态码: {response.status_code}")

                    if response.status_code in [200, 204]:
                        print("断开WAN2连接成功")
                        return True

                except Exception as e:
                    print(f"  请求失败: {e}")
                    continue

        print("所有断开WAN2连接的方式都失败")
        return False

    def connect_wan2(self):
        """连接WAN2"""
        print("尝试连接WAN2...")

        # 尝试多种端点和数据格式
        endpoints = [
            "/cgi-bin/luci/admin/wan?form=connectivity",
            "/admin/wan?form=connectivity"
        ]

        connect_data = [
            {'operation': 'connect', 'interface': 'wan2'},
            {'wan_port': 'wan2', 'action': 'connect'},
            {'interface': 'wan2', 'operation': 'connect'}
        ]

        for endpoint in endpoints:
            for data in connect_data:
                try:
                    url = f"{self.base_url}{endpoint}"
                    print(f"连接WAN2 - 端点: {url}, 数据: {data}")

                    response = self.session.post(url, data=data, timeout=10)
                    print(f"  状态码: {response.status_code}")

                    if response.status_code in [200, 204]:
                        print("连接WAN2成功")
                        return True

                except Exception as e:
                    print(f"  请求失败: {e}")
                    continue

        print("所有连接WAN2的方式都失败")
        return False

    def switch_ip(self):
        """切换IP：断开并重新连接WAN2"""
        print("开始切换IP地址...")

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

    print("TP-Link路由器直接WAN控制测试")
    print(f"路由器IP: {ROUTER_IP}")

    # 创建路由器控制器实例
    router = TPLinkDirectWANController(ROUTER_IP)

    # 测试直接WAN控制
    router.test_direct_wan_control()

    # # 执行IP切换
    # if router.switch_ip():
    # #     print("IP地址切换成功")
    # #     return True
    # # else:
    # #     print("IP地址切换失败")
    # #     return False

if __name__ == "__main__":
    main()

