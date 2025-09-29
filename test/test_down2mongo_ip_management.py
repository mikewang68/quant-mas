#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试脚本：验证down2mongo.py中的IP管理功能
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

# 模拟路由器控制函数
def mock_switch_ip(router_ip="192.168.1.1", username="test", password="test"):
    """模拟IP切换函数"""
    print(f"🔄 模拟切换IP: {router_ip} (用户: {username})")
    return True

def test_ip_management():
    """测试IP管理功能"""
    print("🔍 测试down2mongo.py中的IP管理功能")
    print("="*50)

    if not IP_DETECTION_AVAILABLE:
        print("❌ IP检测模块不可用，无法进行测试")
        return

    # 模拟used_ip列表
    used_ip = []

    # 获取当前IP
    current_ip = get_current_ip()
    print(f"📍 当前IP地址: {current_ip}")

    if current_ip:
        # 检查IP是否在已使用列表中
        if current_ip in used_ip:
            print(f"⚠️  IP {current_ip} 已在使用列表中")

            # 模拟IP切换循环
            attempts = 0
            max_attempts = 3
            while current_ip in used_ip and attempts < max_attempts:
                print(f"🔄 尝试切换IP (第{attempts+1}次)...")
                success = mock_switch_ip()
                if success:
                    time.sleep(2)  # 等待IP切换完成
                    new_ip = get_current_ip()
                    print(f"📍 新IP地址: {new_ip}")
                    if new_ip and new_ip != current_ip:
                        current_ip = new_ip
                        break
                attempts += 1
        else:
            print(f"✅ IP {current_ip} 不在使用列表中")

        # 将IP添加到已使用列表
        if current_ip and current_ip not in used_ip:
            used_ip.append(current_ip)
            print(f"➕ 已将 {current_ip} 添加到使用列表")
            print(f"📋 当前已使用IP列表: {used_ip}")

        # 模拟再次处理
        print("\n🔄 模拟再次处理...")
        if current_ip in used_ip:
            print(f"⚠️  IP {current_ip} 已在使用列表中，需要切换")
        else:
            print(f"✅ IP {current_ip} 可以使用")

    else:
        print("❌ 无法获取当前IP地址")

if __name__ == "__main__":
    import time
    test_ip_management()

