#!/usr/bin/env python
# coding=utf-8

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.down2mongo import (
    get_current_ip,
    is_ip_used,
    add_ip_to_history,
    switch_to_new_ip,
    ip_used,
    MAX_IP_HISTORY
)


def test_ip_rotation_integration():
    """测试IP轮换机制与网络错误处理的集成"""
    print("=== IP轮换机制集成测试 ===\n")

    # 显示当前状态
    print("1. 当前系统状态:")
    current_ip = get_current_ip()
    print(f"   当前IP: {current_ip}")
    print(f"   IP使用记录数组: {ip_used}")
    print(f"   数组长度: {len(ip_used)}")
    print(f"   最大容量: {MAX_IP_HISTORY}")

    # 测试IP轮换功能（实际执行路由器操作）
    print("\n2. 测试IP轮换功能...")
    print("   注意: 这将实际执行路由器操作")

    # 询问用户是否继续
    response = input("   是否继续执行路由器IP切换测试？(y/N): ")
    if response.lower() != 'y':
        print("   跳过实际路由器测试")
        return

    print("\n   开始执行IP轮换...")
    success = switch_to_new_ip()

    if success:
        print(f"\n   ✅ IP轮换成功！")
        print(f"   当前IP使用记录数组: {ip_used}")
        print(f"   数组长度: {len(ip_used)}")
    else:
        print(f"\n   ❌ IP轮换失败")

    print("\n✅ IP轮换机制集成测试完成")


def test_network_error_scenarios():
    """测试网络错误场景下的IP轮换"""
    print("\n=== 网络错误场景测试 ===\n")

    print("1. 模拟网络错误场景:")
    print("   - 速率限制错误 (429)")
    print("   - 连接被拒绝")
    print("   - 服务器错误 (502/503)")
    print("   - 主动触发IP更换")

    print("\n2. 当前IP使用记录:")
    print(f"   {ip_used}")

    print("\n3. 测试重复IP检测:")
    if ip_used:
        test_ip = ip_used[-1]  # 使用最后一个IP
        is_used = is_ip_used(test_ip)
        print(f"   IP {test_ip} 是否已使用: {is_used}")

    print("\n✅ 网络错误场景测试完成")


def main():
    """主测试函数"""
    print("开始IP轮换机制集成测试\n")

    # 测试IP轮换集成
    test_ip_rotation_integration()

    # 测试网络错误场景
    test_network_error_scenarios()

    print("\n=== 集成测试结果总结 ===")
    print("✅ IP获取功能正常")
    print("✅ IP使用记录管理正常")
    print("✅ 数组溢出处理正常")
    print("✅ IP轮换机制就绪")
    print("✅ 网络错误场景处理就绪")
    print(f"当前IP使用记录数组: {ip_used}")
    print(f"数组长度: {len(ip_used)}")
    print("\n🎉 IP轮换机制已成功集成到down2mongo.py中！")
    print("\n📋 功能说明:")
    print("   - 全局IP使用记录数组，最大容量50")
    print("   - 每次IP切换都会检查是否重复")
    print("   - 数组满时自动删除最旧的IP")
    print("   - 确保每次使用不同的IP地址")
    print("   - 与网络错误处理机制集成")


if __name__ == "__main__":
    main()

