#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试脚本：演示如何从其他程序中调用get_isp_ip.py中的get_current_ip函数
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入我们修改后的函数
from utils.get_isp_ip import get_current_ip

def main():
    """
    主函数 - 测试IP地址获取功能
    """
    print("🔍 测试从其他程序调用IP地址获取功能")
    print("="*50)

    # 调用函数获取当前IP地址
    ip_address = get_current_ip()

    if ip_address:
        print(f"✅ 成功获取到公网IP地址: {ip_address}")
        print(f"   类型: {type(ip_address)}")
        print(f"   长度: {len(ip_address)} 字符")
    else:
        print("❌ 未能获取到公网IP地址")

    print("\n💡 说明:")
    print("1. 此脚本演示了如何从其他Python程序中导入和使用get_current_ip函数")
    print("2. 函数返回字符串类型的IP地址，如果获取失败则返回None")
    print("3. 该函数会自动处理浏览器驱动和页面解析的复杂性")

if __name__ == "__main__":
    main()

