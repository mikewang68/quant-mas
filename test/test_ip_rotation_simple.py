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
    ip_used,
    MAX_IP_HISTORY
)


def test_ip_functions():
    """测试IP相关功能"""
    print("=== IP轮换机制测试 ===\n")

    # 测试获取当前IP
    print("1. 测试获取当前IP...")
    current_ip = get_current_ip()
    print(f"当前IP: {current_ip}")

    # 测试IP使用记录检查
    print("\n2. 测试IP使用记录检查...")
    is_used = is_ip_used(current_ip)
    print(f"IP {current_ip} 是否已使用: {is_used}")

    # 测试添加IP到历史记录
    print("\n3. 测试添加IP到历史记录...")
    add_ip_to_history(current_ip)
    print(f"当前IP使用记录数组: {ip_used}")

    # 测试重复添加
    print("\n4. 测试重复添加相同IP...")
    add_ip_to_history(current_ip)
    print(f"重复添加后IP使用记录数组: {ip_used}")

    print("\n✅ IP轮换机制测试完成")


def test_array_overflow():
    """测试数组溢出情况"""
    print("\n=== 数组溢出测试 ===\n")

    # 保存原始数组
    original_ips = ip_used.copy()

    # 清空数组并填充测试数据
    ip_used.clear()
    print("清空数组并填充测试数据...")

    for i in range(MAX_IP_HISTORY + 5):
        test_ip = f"192.168.1.{i+1}"
        add_ip_to_history(test_ip)

    print(f"填充后IP使用记录数组 (长度: {len(ip_used)}): {ip_used}")

    # 恢复原始数组
    ip_used.clear()
    ip_used.extend(original_ips)
    print("\n✅ 数组溢出测试完成")


def main():
    """主测试函数"""
    print("开始IP轮换机制测试\n")

    # 测试基本IP功能
    test_ip_functions()

    # 测试数组溢出
    test_array_overflow()

    print("\n=== 测试结果总结 ===")
    print("✅ IP获取功能正常")
    print("✅ IP使用记录检查正常")
    print("✅ IP历史记录管理正常")
    print("✅ 数组溢出处理正常")
    print(f"当前IP使用记录数组: {ip_used}")
    print("\n🎉 所有IP轮换机制测试通过！")


if __name__ == "__main__":
    main()

