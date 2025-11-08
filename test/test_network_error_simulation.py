#!/usr/bin/env python
# coding=utf-8

"""
模拟网络错误测试脚本
用于测试当网络出现问题时，程序是否能正确检测和处理错误
"""

import time
import requests
import akshare as ak
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.down2mongo import write_k_daily, conn_mongo

def test_akshare_with_forced_error():
    """测试akshare在强制网络错误下的行为"""
    print("\n🔍 测试akshare在强制网络错误下的行为...")

    db = conn_mongo()

    # 测试一个已知的股票代码
    test_code = "000001"  # 平安银行

    try:
        print(f"尝试下载股票 {test_code} 的数据...")

        # 调用write_k_daily函数
        success = write_k_daily(db, test_code)

        if success:
            print(f"✅ 股票 {test_code} 数据下载成功")
        else:
            print(f"❌ 股票 {test_code} 数据下载失败")

    except Exception as e:
        print(f"❌ 下载过程中出现异常: {str(e)}")

def test_network_error_simulation():
    """模拟网络错误场景"""
    print("\n🔍 模拟网络错误场景...")

    # 模拟各种网络错误
    error_scenarios = [
        "Connection aborted by remote host",
        "Could not reach host. Are you offline?",
        "429 Too Many Requests",
        "主动触发IP更换",
    ]

    for error_msg in error_scenarios:
        print(f"\n模拟错误: {error_msg}")

        # 测试错误分类
        from utils.network_error_handler import NetworkErrorClassifier
        classification = NetworkErrorClassifier.classify_error(error_msg)
        print(f"   分类: {classification['type']}")
        print(f"   严重性: {classification['severity']}")
        print(f"   需要切换IP: {classification['should_switch_ip']}")

def test_router_control_in_error_scenario():
    """在错误场景下测试路由器控制"""
    print("\n🔍 在错误场景下测试路由器控制...")

    try:
        from utils.enhanced_router_control import TPLinkWAN2Controller

        controller = TPLinkWAN2Controller(
            router_ip="192.168.1.1",
            username="wangdg68",
            password="wap951020ZJL",
            headless=False  # 使用非headless模式以便观察
        )

        print("✅ 路由器控制器初始化成功")

        # 测试IP切换功能
        print("\n测试IP切换功能...")
        success = controller.switch_ip(wait_time=3)

        if success:
            print("✅ IP切换成功")
        else:
            print("❌ IP切换失败")

    except Exception as e:
        print(f"❌ 路由器控制测试失败: {str(e)}")

def main():
    """主函数"""
    print("=" * 60)
    print("模拟网络错误测试工具")
    print("=" * 60)

    # 测试1: 正常情况下的akshare下载
    test_akshare_with_forced_error()

    # 测试2: 模拟网络错误场景
    test_network_error_simulation()

    # 测试3: 在错误场景下测试路由器控制
    test_router_control_in_error_scenario()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()

