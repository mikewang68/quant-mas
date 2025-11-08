#!/usr/bin/env python
# coding=utf-8

"""
网络连接性诊断脚本
用于诊断为什么程序无法下载股票数据，但手动操作路由器后可以下载的问题
"""

import time
import requests
import akshare as ak
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.network_error_handler import handle_network_error, is_rate_limit_error
from utils.enhanced_router_control import TPLinkWAN2Controller

def test_internet_connectivity():
    """测试互联网连接性"""
    print("\n🔍 测试互联网连接性...")

    test_urls = [
        "https://www.baidu.com",
        "https://www.google.com",
        "https://www.qq.com"
    ]

    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ {url}: 连接成功 (状态码: {response.status_code})")
        except Exception as e:
            print(f"❌ {url}: 连接失败 - {str(e)}")

def test_akshare_connectivity():
    """测试akshare连接性"""
    print("\n🔍 测试akshare连接性...")

    try:
        # 测试获取股票代码列表
        stock_list = ak.stock_info_a_code_name()
        print(f"✅ akshare股票代码列表: 获取成功 ({len(stock_list)} 只股票)")

        # 测试获取单只股票数据
        test_code = "000001"  # 平安银行
        stock_data = ak.stock_zh_a_hist(symbol=test_code, period="daily", adjust="qfq")
        print(f"✅ akshare股票数据: 获取成功 ({len(stock_data)} 条记录)")

        return True
    except Exception as e:
        print(f"❌ akshare连接失败: {str(e)}")

        # 分析错误类型
        error_str = str(e)
        print(f"   错误类型分析:")
        print(f"   - 是否为速率限制错误: {is_rate_limit_error(error_str)}")
        print(f"   - 错误详情: {error_str}")

        return False

def test_router_control():
    """测试路由器控制功能"""
    print("\n🔍 测试路由器控制功能...")

    try:
        controller = TPLinkWAN2Controller(
            router_ip="192.168.1.1",
            username="wangdg68",
            password="wap951020ZJL",
            headless=False  # 使用非headless模式以便观察
        )

        print("✅ 路由器控制器初始化成功")

        # 测试WebDriver设置
        if controller.setup_driver():
            print("✅ WebDriver设置成功")
        else:
            print("❌ WebDriver设置失败")
            return False

        # 测试登录
        if controller.login():
            print("✅ 路由器登录成功")
        else:
            print("❌ 路由器登录失败")
            return False

        controller.close()
        return True

    except Exception as e:
        print(f"❌ 路由器控制测试失败: {str(e)}")
        return False

def test_network_error_handler():
    """测试网络错误处理功能"""
    print("\n🔍 测试网络错误处理功能...")

    # 模拟各种网络错误
    test_errors = [
        "Connection aborted by remote host",
        "Could not reach host. Are you offline?",
        "429 Too Many Requests",
        "主动触发IP更换",
        "Unknown error type"
    ]

    for error_msg in test_errors:
        print(f"\n测试错误: {error_msg}")

        # 测试错误分类
        from utils.network_error_handler import NetworkErrorClassifier
        classification = NetworkErrorClassifier.classify_error(error_msg)
        print(f"   分类: {classification['type']}")
        print(f"   严重性: {classification['severity']}")
        print(f"   需要切换IP: {classification['should_switch_ip']}")

        # 测试错误处理
        class MockError(Exception):
            def __init__(self, message):
                self.message = message
            def __str__(self):
                return self.message

        mock_error = MockError(error_msg)
        result = handle_network_error(mock_error, max_retries=1, retry_delay=1)
        print(f"   处理结果: {result}")

def main():
    """主函数"""
    print("=" * 60)
    print("网络连接性诊断工具")
    print("=" * 60)

    # 测试1: 互联网连接性
    test_internet_connectivity()

    # 测试2: akshare连接性
    akshare_success = test_akshare_connectivity()

    # 如果akshare连接失败，进行进一步诊断
    if not akshare_success:
        print("\n⚠️  akshare连接失败，进行进一步诊断...")

        # 测试3: 路由器控制功能
        router_success = test_router_control()

        # 测试4: 网络错误处理功能
        test_network_error_handler()

        print("\n💡 建议:")
        print("1. 检查路由器是否正常工作")
        print("2. 检查网络连接是否稳定")
        print("3. 尝试手动在路由器Web页面断开并重新连接WAN2")
        print("4. 检查防火墙或代理设置")
    else:
        print("\n✅ 所有测试通过，网络连接正常")

    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)

if __name__ == "__main__":
    main()

