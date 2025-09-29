#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试脚本：验证初始IP获取逻辑
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入IP获取函数
try:
    from utils.get_isp_ip import get_current_ip
    IP_DETECTION_AVAILABLE = True
    print("✅ IP检测模块可用")
except ImportError:
    IP_DETECTION_AVAILABLE = False
    print("❌ IP检测模块不可用")

def test_initial_ip_logic():
    """测试初始IP获取逻辑"""
    print("🔍 测试初始IP获取逻辑")
    print("="*50)

    if not IP_DETECTION_AVAILABLE:
        print("❌ IP检测模块不可用，无法进行测试")
        return

    # 模拟used_ip列表初始化
    used_ip = []
    print(f"📋 初始used_ip列表: {used_ip}")

    # 模拟在开始数据收集前获取初始IP
    print("\n🔄 在开始数据收集前获取初始IP...")
    initial_ip = get_current_ip()

    if initial_ip:
        print(f"📍 获取到初始IP: {initial_ip}")

        # 将初始IP添加到used_ip列表
        used_ip.append(initial_ip)
        print(f"➕ 已将初始IP {initial_ip} 添加到used_ip列表")
        print(f"📋 更新后的used_ip列表: {used_ip}")

        # 模拟后续IP检查逻辑
        print("\n🔄 模拟后续IP检查...")
        current_ip = initial_ip  # 模拟当前IP

        if current_ip in used_ip:
            print(f"⚠️  当前IP {current_ip} 已在used_ip列表中")
            print("   需要切换IP以获取新IP地址")
        else:
            print(f"✅ 当前IP {current_ip} 不在used_ip列表中")
    else:
        print("❌ 无法获取初始IP地址")

    print("\n✅ 初始IP获取逻辑测试完成")

if __name__ == "__main__":
    test_initial_ip_logic()

