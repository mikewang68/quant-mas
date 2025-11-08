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
    """使用最方便的IP查询服务获取ISP提供的IP地址"""
    try:
        # 使用最方便的IP查询服务 - 直接返回纯文本IP
        service = 'https://ip.3322.net/'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(service, headers=headers, timeout=10)
        if response.status_code == 200:
            # 直接返回响应内容，不需要解析
            ip = response.text.strip()
            print(f"从 {service} 获取到IP: {ip}")
            return ip
        else:
            print(f"IP查询服务返回状态码: {response.status_code}")
            return "unknown"

    except Exception as e:
        print(f"获取IP地址失败: {e}")
        return "unknown"


def test_router_login_with_driver_setup():
    """测试路由器登录（包含WebDriver初始化）"""
    print("=== 路由器登录测试（包含WebDriver初始化） ===")

    # 获取初始IP
    print("1. 获取初始ISP IP地址...")
    initial_ip = get_current_ip()
    print(f"初始ISP IP: {initial_ip}")

    # 初始化路由器控制
    print("\n2. 初始化路由器控制...")
    try:
        router = TPLinkWAN2Controller()
        print("路由器控制初始化成功")
    except Exception as e:
        print(f"路由器控制初始化失败: {e}")
        return False

    # 设置WebDriver
    print("\n3. 设置WebDriver...")
    try:
        if router.setup_driver():
            print("WebDriver设置成功")
        else:
            print("WebDriver设置失败")
            return False
    except Exception as e:
        print(f"WebDriver设置异常: {e}")
        return False

    # 测试路由器登录
    print("\n4. 测试路由器登录...")
    try:
        login_success = router.login()
        if login_success:
            print("✅ 路由器登录成功")

            # 如果登录成功，测试IP切换
            print("\n5. 测试IP切换...")
            switch_success = router.switch_ip()
            if switch_success:
                print("✅ IP切换成功")

                # 等待网络稳定
                print("\n6. 等待网络稳定...")
                time.sleep(15)

                # 获取新IP
                print("\n7. 获取新ISP IP地址...")
                new_ip = get_current_ip()
                print(f"新ISP IP: {new_ip}")

                # 比较IP变化
                if new_ip != initial_ip:
                    print(f"✅ ISP IP地址已成功变更: {initial_ip} -> {new_ip}")
                    return True
                else:
                    print(f"❌ ISP IP地址未变化: {initial_ip} -> {new_ip}")
                    return False
            else:
                print("❌ IP切换失败")
                return False
        else:
            print("❌ 路由器登录失败")
            return False

    except Exception as e:
        print(f"路由器操作异常: {e}")
        return False
    finally:
        # 确保关闭浏览器
        if hasattr(router, 'driver') and router.driver:
            router.driver.quit()
            print("浏览器已关闭")


def test_akshare_connectivity():
    """测试akshare连接性"""
    print("\n=== akshare连接性测试 ===")

    try:
        import akshare as ak

        print("1. 测试akshare基本功能...")

        # 测试获取股票代码列表
        stock_list = ak.stock_info_a_code_name()
        print(f"成功获取 {len(stock_list)} 只股票代码")

        # 测试获取交易日历
        trade_dates = ak.tool_trade_date_hist_sina()
        print(f"成功获取 {len(trade_dates)} 条交易日历数据")

        print("✅ akshare连接性测试成功")
        return True

    except Exception as e:
        print(f"❌ akshare连接性测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("开始路由器登录修复测试...\n")

    # 测试路由器登录和IP变化
    router_success = test_router_login_with_driver_setup()

    # 测试akshare连接性
    akshare_success = test_akshare_connectivity()

    # 总结结果
    print("\n=== 测试结果总结 ===")
    print(f"路由器控制: {'✅ 成功' if router_success else '❌ 失败'}")
    print(f"akshare连接性: {'✅ 正常' if akshare_success else '❌ 异常'}")

    if router_success and akshare_success:
        print("\n🎉 所有测试通过！网络错误处理机制工作正常。")
    else:
        print("\n⚠️ 部分测试失败，需要进一步调试。")


if __name__ == "__main__":
    main()

