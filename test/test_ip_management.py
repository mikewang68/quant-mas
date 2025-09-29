#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试脚本：验证IP管理功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入IP获取函数
from utils.get_isp_ip import get_current_ip

def test_ip_management():
    """测试IP管理功能"""
    print("🔍 测试IP管理功能")
    print("="*50)

    # 模拟used_ip列表
    used_ip = []

    # 获取当前IP
    current_ip = get_current_ip()
    print(f"当前IP地址: {current_ip}")

    if current_ip:
        # 检查IP是否在已使用列表中
        if current_ip in used_ip:
            print(f"⚠️  IP {current_ip} 已在使用列表中")
        else:
            print(f"✅ IP {current_ip} 不在使用列表中")
            # 添加到已使用列表
            used_ip.append(current_ip)
            print(f"➕ 已将 {current_ip} 添加到使用列表")

    print(f"📋 当前已使用IP列表: {used_ip}")

    # 模拟再次获取IP
    print("\n🔄 模拟再次获取IP...")
    new_ip = get_current_ip()
    print(f"新获取的IP地址: {new_ip}")

    if new_ip:
        if new_ip in used_ip:
            print(f"⚠️  IP {new_ip} 已在使用列表中，需要切换IP")
        else:
            print(f"✅ IP {new_ip} 不在使用列表中，可以使用")
            used_ip.append(new_ip)
            print(f"➕ 已将 {new_ip} 添加到使用列表")

    print(f"📋 最终已使用IP列表: {used_ip}")

if __name__ == "__main__":
    test_ip_management()

