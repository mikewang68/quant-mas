#!/usr/bin/env python
# coding=utf-8

"""
修复后的IP地址切换测试
用于验证修复后的路由器控制程序是否能成功更改IP地址
"""

import requests
import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.enhanced_router_control import TPLinkWAN2Controller

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

def test_fixed_ip_switching():
    """测试修复后的IP切换功能"""
    print("\n🔍 测试修复后的IP切换功能...")

    # 获取切换前的IP
    original_ip = get_current_ip()
    if not original_ip:
        print("❌ 无法获取当前IP地址，无法进行测试")
        return False

    print(f"\n切换前IP: {original_ip}")

    try:
        # 创建路由器控制器
        controller = TPLinkWAN2Controller(
            router_ip="192.168.1.1",
            username="wangdg68",
            password="wap951020ZJL",
            headless=False  # 使用非headless模式以便观察
        )

        print("✅ 路由器控制器初始化成功")

        # 测试WebDriver设置
        if controller.setup_driver():
            print("✅ WebDriver设置成功")
        else:
            print("❌ WebDriver设置失败")
            return False

        # 测试登录
        print("\n🔄 开始登录测试...")
        if controller.login():
            print("✅ 登录成功")
        else:
            print("❌ 登录失败")
            controller.close()
            return False

        # 第一次IP切换
        print("\n🔄 第一次IP切换...")
        if controller.switch_ip():
            print("✅ 第一次IP切换成功")
        else:
            print("❌ 第一次IP切换失败")
            controller.close()
            return False

        # 等待一段时间让网络重新连接
        print("\n⏳ 等待15秒让网络重新稳定...")
        time.sleep(15)

        # 获取第一次切换后的IP
        first_new_ip = get_current_ip()

        if first_new_ip:
            print(f"\n第一次切换后IP: {first_new_ip}")

            if first_new_ip != original_ip:
                print("✅ 第一次IP地址已成功更改!")
                print(f"   原IP: {original_ip}")
                print(f"   新IP: {first_new_ip}")
            else:
                print("❌ 第一次IP地址未更改")
                print(f"   原IP: {original_ip}")
                print(f"   新IP: {first_new_ip}")

        # 第二次IP切换（测试会话保持）
        print("\n🔄 第二次IP切换（测试会话保持）...")
        if controller.switch_ip():
            print("✅ 第二次IP切换成功")
        else:
            print("❌ 第二次IP切换失败")
            controller.close()
            return False

        # 等待一段时间让网络重新连接
        print("\n⏳ 等待15秒让网络重新稳定...")
        time.sleep(15)

        # 获取第二次切换后的IP
        second_new_ip = get_current_ip()

        if second_new_ip:
            print(f"\n第二次切换后IP: {second_new_ip}")

            if second_new_ip != first_new_ip:
                print("✅ 第二次IP地址已成功更改!")
                print(f"   第一次IP: {first_new_ip}")
                print(f"   第二次IP: {second_new_ip}")
            else:
                print("❌ 第二次IP地址未更改")
                print(f"   第一次IP: {first_new_ip}")
                print(f"   第二次IP: {second_new_ip}")

        # 关闭浏览器
        controller.close()
        print("✅ 浏览器已关闭")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_akshare_after_ip_switch():
    """测试IP切换后akshare是否能正常工作"""
    print("\n🔍 测试IP切换后akshare连接性...")

    import akshare as ak

    try:
        # 测试获取股票数据
        test_code = "000001"  # 平安银行
        stock_data = ak.stock_zh_a_hist(symbol=test_code, period="daily", adjust="qfq")
        print(f"✅ akshare股票数据: 获取成功 ({len(stock_data)} 条记录)")
        return True
    except Exception as e:
        print(f"❌ akshare连接失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("修复后的IP地址切换测试工具")
    print("=" * 60)

    # 测试1: 获取当前IP
    current_ip = get_current_ip()
    if not current_ip:
        print("❌ 无法获取当前IP地址，测试终止")
        return

    print(f"\n当前公网IP: {current_ip}")

    # 测试2: 修复后的IP切换
    ip_switched = test_fixed_ip_switching()

    # 测试3: IP切换后akshare连接性
    if ip_switched:
        akshare_works = test_akshare_after_ip_switch()

        print("\n💡 测试结果总结:")
        print(f"   - IP切换成功: {'✅' if ip_switched else '❌'}")
        print(f"   - akshare工作正常: {'✅' if akshare_works else '❌'}")
    else:
        print("\n⚠️  IP切换失败，无法测试akshare连接性")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()

