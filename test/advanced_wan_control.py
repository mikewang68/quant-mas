import requests
import re
import json
import time
from urllib3.exceptions import InsecureRequestWarning

# 禁用SSL警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class TPLinkAdvancedWANController:
    def __init__(self, router_ip):
        self.router_ip = router_ip
        self.base_url = f"http://{router_ip}"
        self.session = requests.Session()

        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': f'{self.base_url}/webpages/index.html',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest'
        })

    def test_all_wan_endpoints(self):
        """测试所有可能的WAN端点"""
        print("测试所有可能的WAN端点...")

        # 构造可能的端点列表
        endpoints = [
            # 标准LuCI端点
            "/cgi-bin/luci/admin/status",
            "/cgi-bin/luci/admin/network",
            "/cgi-bin/luci/admin/wan",
            "/cgi-bin/luci/admin/network/wan",
            "/cgi-bin/luci/admin/status/wan",

            # 带表单参数的端点
            "/cgi-bin/luci/admin/status?form=wan",
            "/cgi-bin/luci/admin/network?form=wan",
            "/cgi-bin/luci/admin/wan?form=status",
            "/cgi-bin/luci/admin/wan?form=connectivity",
            "/cgi-bin/luci/admin/wan?form=info",

            # 带stok的端点
            "/cgi-bin/luci/;stok=/admin/status",
            "/cgi-bin/luci/;stok=/admin/network",
            "/cgi-bin/luci/;stok=/admin/wan",

            # 其他可能的端点
            "/admin/status",
            "/admin/network",
            "/admin/wan",
            "/api/wan",
            "/api/network"
        ]

        for endpoint in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                print(f"\n测试端点: {url}")

                # 尝试GET请求
                response = self.session.get(url, timeout=5)
                print(f"  GET状态码: {response.status_code}")

                if response.status_code == 200:
                    # 尝试解析JSON
                    try:
                        data = response.json()
                        print(f"  JSON响应: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}")
                    except:
                        # 显示文本响应的前200个字符
                        print(f"  响应预览: {response.text[:200]}")

            except Exception as e:
                print(f"  请求失败: {e}")

    def test_wan_control_with_different_formats(self):
        """测试不同格式的WAN控制命令"""
        print("测试不同格式的WAN控制命令...")

        # 测试端点
        control_endpoint = "/cgi-bin/luci/admin/wan?form=connectivity"

        # 不同的数据格式
        data_formats = [
            # JSON格式
            {
                "operation": "disconnect",
                "interface": "wan2"
            },
            {
                "operation": "connect",
                "interface": "wan2"
            },
            # 嵌套格式
            {
                "method": "disconnect",
                "params": {
                    "interface": "wan2"
                }
            },
            {
                "method": "connect",
                "params": {
                    "interface": "wan2"
                }
            },
            # 数组格式
            {
                "operations": [
                    {
                        "operation": "disconnect",
                        "interface": "wan2"
                    }
                ]
            }
        ]

        # 不同的内容类型
        content_types = [
            'application/json',
            'application/x-www-form-urlencoded',
            'text/plain'
        ]

        for data in data_formats:
            for content_type in content_types:
                try:
                    url = f"{self.base_url}{control_endpoint}"
                    print(f"\n测试数据: {data}")
                    print(f"内容类型: {content_type}")

                    # 设置内容类型
                    self.session.headers['Content-Type'] = content_type

                    if content_type == 'application/json':
                        response = self.session.post(url, json=data, timeout=10)
                    else:
                        # 对于表单格式，需要转换数据
                        if isinstance(data, dict):
                            form_data = {}
                            for k, v in data.items():
                                if isinstance(v, (str, int, float)):
                                    form_data[k] = str(v)
                                else:
                                    form_data[k] = json.dumps(v)
                            response = self.session.post(url, data=form_data, timeout=10)
                        else:
                            response = self.session.post(url, data=str(data), timeout=10)

                    print(f"  状态码: {response.status_code}")
                    print(f"  响应内容: {response.text[:200]}")

                except Exception as e:
                    print(f"  请求失败: {e}")

    def try_wan_control_sequence(self):
        """尝试WAN控制序列"""
        print("尝试WAN控制序列...")

        # 步骤1: 获取当前WAN状态
        print("\n步骤1: 获取当前WAN状态")
        status_endpoints = [
            "/cgi-bin/luci/admin/status?form=wan",
            "/cgi-bin/luci/admin/network?form=wan"
        ]

        for endpoint in status_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = self.session.get(url, timeout=10)
                print(f"  状态端点: {url}")
                print(f"  状态码: {response.status_code}")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"  状态数据: {json.dumps(data, indent=2, ensure_ascii=False)[:300]}")
                    except:
                        print(f"  状态响应: {response.text[:200]}")
            except Exception as e:
                print(f"  获取状态失败: {e}")

        # 步骤2: 尝试断开WAN2
        print("\n步骤2: 尝试断开WAN2")
        disconnect_commands = [
            {
                "url": "/cgi-bin/luci/admin/wan?form=connectivity",
                "data": {"operation": "disconnect", "interface": "wan2"}
            },
            {
                "url": "/cgi-bin/luci/admin/wan?form=connectivity",
                "data": {"wan_port": "wan2", "action": "disconnect"}
            }
        ]

        for cmd in disconnect_commands:
            try:
                url = f"{self.base_url}{cmd['url']}"
                data = cmd['data']
                print(f"  断开命令: {url}, 数据: {data}")

                response = self.session.post(url, json=data, timeout=10)
                print(f"  断开状态码: {response.status_code}")
                print(f"  断开响应: {response.text[:200]}")
            except Exception as e:
                print(f"  断开失败: {e}")

        # 步骤3: 等待
        print("\n步骤3: 等待5秒...")
        time.sleep(5)

        # 步骤4: 尝试连接WAN2
        print("\n步骤4: 尝试连接WAN2")
        connect_commands = [
            {
                "url": "/cgi-bin/luci/admin/wan?form=connectivity",
                "data": {"operation": "connect", "interface": "wan2"}
            },
            {
                "url": "/cgi-bin/luci/admin/wan?form=connectivity",
                "data": {"wan_port": "wan2", "action": "connect"}
            }
        ]

        for cmd in connect_commands:
            try:
                url = f"{self.base_url}{cmd['url']}"
                data = cmd['data']
                print(f"  连接命令: {url}, 数据: {data}")

                response = self.session.post(url, json=data, timeout=10)
                print(f"  连接状态码: {response.status_code}")
                print(f"  连接响应: {response.text[:200]}")
            except Exception as e:
                print(f"  连接失败: {e}")

    def comprehensive_test(self):
        """综合测试"""
        print("开始综合测试...")

        # 1. 测试所有端点
        self.test_all_wan_endpoints()

        # 2. 测试不同格式的控制命令
        self.test_wan_control_with_different_formats()

        # 3. 尝试控制序列
        self.try_wan_control_sequence()

def main():
    # 路由器配置
    ROUTER_IP = "192.168.1.1"

    print("TP-Link路由器高级WAN控制测试")
    print(f"路由器IP: {ROUTER_IP}")

    # 创建路由器控制器实例
    router = TPLinkAdvancedWANController(ROUTER_IP)

    # 执行综合测试
    router.comprehensive_test()

if __name__ == "__main__":
    main()

