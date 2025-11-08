#!/usr/bin/env python
# coding=utf-8

import time
import requests
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.enhanced_router_control import TPLinkWAN2Controller


def get_current_ip():
    """使用最可靠的IP查询服务获取ISP提供的IP地址"""
    try:
        # 使用最可靠的IP查询服务
        service = 'https://ip.3322.net/'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(service, headers=headers, timeout=10)
        if response.status_code == 200:
            ip = response.text.strip()
            print(f"从 {service} 获取到IP: {ip}")
            return ip
        else:
            print(f"IP查询服务返回状态码: {response.status_code}")
            return "unknown"

    except Exception as e:
        print(f"获取IP地址失败: {e}")
        return "unknown"


def test_router_login_issue():
    """测试路由器登录问题"""
    print("=== 路由器登录问题诊断 ===")

    # 初始化路由器控制
    print("1. 初始化路由器控制...")
    try:
        router = TPLinkWAN2Controller()
        print("路由器控制初始化成功")
    except Exception as e:
        print(f"路由器控制初始化失败: {e}")
        return False

    # 测试登录
    print("\n2. 测试登录功能...")
    try:
        # 直接调用登录方法
        success = router.login()
        if success:
            print("登录成功")
            return True
        else:
            print("登录失败")
            return False
    except Exception as e:
        print(f"登录异常: {e}")
        return False


def test_ip_change_manual():
    """手动测试IP变化：先获取IP，手动操作路由器，再获取IP"""
    print("=== 手动IP变化验证测试 ===")

    # 获取初始IP
    print("1. 获取初始ISP IP地址...")
    initial_ip = get_current_ip()
    print(f"初始ISP IP: {initial_ip}")

    if initial_ip == "unknown":
        print("警告: 无法获取初始ISP IP地址")
        return False

    print("\n2. 请手动操作路由器断开并重新连接WAN2...")
    print("   等待您手动操作完成...")
    input("   按回车键继续...")

    # 等待网络稳定
    print("\n3. 等待网络稳定...")
    time.sleep(15)

    # 获取新IP
    print("\n4. 获取新ISP IP地址...")
    new_ip = get_current_ip()
    print(f"新ISP IP: {new_ip}")

    # 比较IP变化
    print("\n5. 比较ISP IP变化...")
    if new_ip == "unknown":
        print("警告: 无法获取新ISP IP地址")
        return False
    elif new_ip != initial_ip:
        print(f"✅ ISP IP地址已成功变更: {initial_ip} -> {new_ip}")
        return True
    else:
        print(f"❌ ISP IP地址未变化: {initial_ip} -> {new_ip}")
        return False


def main():
    """主测试函数"""
    print("开始IP地址变化验证测试...\n")

    # 测试IP查询服务
    print("=== IP查询服务测试 ===")
    current_ip = get_current_ip()
    print(f"当前ISP IP: {current_ip}")

    # 测试路由器登录问题
    print("\n=== 路由器登录问题诊断 ===")
    login_success = test_router_login_issue()

    # 手动IP变化测试
    print("\n=== 手动IP变化验证 ===")
    print("这个测试需要您手动操作路由器断开并重新连接WAN2接口")
    print("是否要运行手动测试？(y/n)")

    choice = input().strip().lower()
    if choice == 'y':
        ip_changed = test_ip_change_manual()
        print(f"\n手动IP变化测试: {'✅ 成功' if ip_changed else '❌ 失败'}")
    else:
        print("跳过手动测试")

    # 总结结果
    print("\n=== 测试结果总结 ===")
    print(f"当前ISP IP: {current_ip}")
    print(f"路由器登录: {'✅ 成功' if login_success else '❌ 失败'}")

    if not login_success:
        print("\n⚠️ 路由器登录失败，需要检查：")
        print("  1. 路由器IP地址是否正确")
        print("  2. 用户名和密码是否正确")
        print("  3. 路由器管理界面是否可访问")


if __name__ == "__main__":
    main()

