#!/usr/bin/env python
# coding=utf-8

"""
快速IP检查测试
快速验证当前IP地址和路由器控制程序状态
"""

import requests
import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_current_ip():
    """获取当前公网IP地址"""
    print("\n🔍 获取当前公网IP地址...")

    ip_services = [
        "https://api.ipify.org",
        "https://api.myip.com",
        "https://httpbin.org/ip"
    ]

    current_ip = None

    for service in ip_services:
        try:
            response = requests.get(service, timeout=10)
            if response.status_code == 200:
                if service == "https://httpbin.org/ip":
                    data = response.json()
                    current_ip = data.get("origin", None)
                else:
                    current_ip = response.text.strip()

                if current_ip:
                    print(f"✅ {service}: {current_ip}")
                    return current_ip
        except Exception as e:
            print(f"❌ {service}: 获取失败 - {str(e)}")

    return None

def test_manual_ip_change():
    """测试手动IP切换后的IP变化"""
    print("\n🔍 测试手动IP切换后的IP变化...")

    # 获取切换前的IP
    original_ip = get_current_ip()
    if not original_ip:
        print("❌ 无法获取当前IP地址，无法进行测试")
        return False

    print(f"\n当前IP: {original_ip}")

    print("\n💡 请手动执行以下操作:")
    print("   1. 打开浏览器访问 http://192.168.1.1")
    print("   2. 登录路由器管理界面")
    print("   3. 导航到 WAN2 设置页面")
    print("   4. 点击断开按钮断开WAN2连接")
    print("   5. 等待几秒后点击连接按钮重新连接WAN2")
    print("   6. 等待网络重新连接")

    input("\n按回车键继续，当您完成手动IP切换后...")

    # 等待一段时间让网络重新连接
    print("\n⏳ 等待15秒让网络重新稳定...")
    time.sleep(15)

    # 获取切换后的IP
    new_ip = get_current_ip()

    if new_ip:
        print(f"\n切换后IP: {new_ip}")

        if new_ip != original_ip:
            print("✅ IP地址已成功更改!")
            print(f"   原IP: {original_ip}")
            print(f"   新IP: {new_ip}")
            return True
        else:
            print("❌ IP地址未更改")
            print(f"   原IP: {original_ip}")
            print(f"   新IP: {new_ip}")
            return False
    else:
        print("❌ 无法获取切换后的IP地址")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("快速IP检查测试")
    print("=" * 60)

    # 测试1: 获取当前IP
    current_ip = get_current_ip()
    if not current_ip:
        print("❌ 无法获取当前IP地址，测试终止")
        return

    print(f"\n当前公网IP: {current_ip}")

    # 测试2: 手动IP切换测试
    print("\n🔄 开始手动IP切换测试...")
    ip_changed = test_manual_ip_change()

    print("\n" + "=" * 60)
    print("📊 IP地址变化验证结果:")
    print("=" * 60)
    print(f"   - IP地址是否改变: {'✅ 是' if ip_changed else '❌ 否'}")

    if not ip_changed:
        print("\n💡 诊断信息:")
        print("   - 如果手动切换IP地址都没有改变，说明问题不在程序")
        print("   - 可能的原因:")
        print("     1. 网络服务商限制了IP切换")
        print("     2. 路由器配置问题")
        print("     3. 需要更长的等待时间")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()

