#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用示例：如何在其他程序中调用get_current_ip函数
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 方式1: 直接导入函数
from utils.get_isp_ip import get_current_ip

def check_network_environment():
    """检查当前网络环境"""
    print("检查当前网络环境...")
    ip = get_current_ip()
    if ip:
        print(f"当前公网IP地址: {ip}")
        return ip
    else:
        print("无法获取IP地址")
        return None

# 方式2: 作为模块运行
if __name__ == "__main__":
    # 直接调用函数
    current_ip = get_current_ip()
    if current_ip:
        print(f"获取到的IP地址: {current_ip}")
    else:
        print("未能获取到IP地址")

