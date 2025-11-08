#!/usr/bin/env python
# coding=utf-8

"""
网络错误处理机制测试
用于验证当akshare下载失败时，网络错误处理机制是否能正确触发IP切换
"""

import sys
import os
import time
import requests

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.network_error_handler import handle_network_error, is_rate_limit_error
from utils.enhanced_router_control import TPLinkWAN2Controller

def simulate_network_error():
    """模拟网络错误"""
    print("\n🔍 模拟网络错误...")

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

def test_akshare_with_network_error():
    """测试akshare在网络错误时的行为"""
    print("\n🔍 测试akshare在网络错误时的行为...")

    import akshare as ak

    try:
        # 测试获取股票数据
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

        # 测试网络错误处理
        print(f"\n🔄 尝试处理网络错误...")
        result = handle_network_error(e, max_retries=1, retry_delay=2)
        print(f"   网络错误处理结果: {result}")

        return False

def test_router_control_integration():
    """测试路由器控制与网络错误处理的集成"""
    print("\n🔍 测试路由器控制与网络错误处理的集成...")

    try:
        # 创建路由器控制器
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
        print("\n🔄 开始登录测试...")
        if controller.login():
            print("✅ 登录成功")
        else:
            print("❌ 登录失败")
            controller.close()
            return False

        # 测试IP切换
        print("\n🔄 开始IP切换测试...")
        if controller.switch_ip():
            print("✅ IP切换成功")
        else:
            print("❌ IP切换失败")
            controller.close()
            return False

        # 关闭浏览器
        controller.close()
        print("✅ 浏览器已关闭")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_down2mongo_integration():
    """测试down2mongo与网络错误处理的集成"""
    print("\n🔍 测试down2mongo与网络错误处理的集成...")

    try:
        # 导入down2mongo模块
        from utils.down2mongo import conn_mongo, write_k_daily

        # 连接数据库
        db = conn_mongo()
        print("✅ 数据库连接成功")

        # 测试下载单只股票数据
        test_code = "000001"  # 平安银行
        print(f"\n🔄 测试下载股票数据: {test_code}")

        success = write_k_daily(db, test_code)
        if success:
            print("✅ 股票数据下载成功")
        else:
            print("❌ 股票数据下载失败")

        return success

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("网络错误处理机制测试工具")
    print("=" * 60)

    # 测试1: 模拟网络错误
    simulate_network_error()

    # 测试2: akshare网络错误测试
    akshare_success = test_akshare_with_network_error()

    # 测试3: 路由器控制集成测试
    router_success = test_router_control_integration()

    # 测试4: down2mongo集成测试
    down2mongo_success = test_down2mongo_integration()

    print("\n💡 测试结果总结:")
    print(f"   - 网络错误分类: ✅ 完成")
    print(f"   - akshare连接: {'✅' if akshare_success else '❌'}")
    print(f"   - 路由器控制: {'✅' if router_success else '❌'}")
    print(f"   - down2mongo集成: {'✅' if down2mongo_success else '❌'}")

    print("\n📋 问题诊断:")
    if not akshare_success:
        print("   - akshare连接失败时，网络错误处理机制应该自动触发IP切换")
    if not router_success:
        print("   - 路由器控制程序需要进一步优化")
    if not down2mongo_success:
        print("   - down2mongo需要更好的网络错误处理集成")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()

