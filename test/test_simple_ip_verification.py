#!/usr/bin/env python
# coding=utf-8

import time
import requests
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.enhanced_router_control import TPLinkWAN2Controller


def get_current_ip_simple():
    """使用更简单的IP查询服务获取ISP提供的IP地址"""
    try:
        # 使用更可靠的IP查询服务
        services = [
            'https://ip.cn/api/index?ip=&type=0',
            'https://www.ip138.com/',
            'https://www.ip.cn/',
            'https://ip.tool.lu/',
            'https://ip.3322.net/'
        ]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        for service in services:
            try:
                print(f"尝试从 {service} 获取IP...")
                response = requests.get(service, headers=headers, timeout=10)
                if response.status_code == 200:
                    content = response.text
                    print(f"响应内容前100字符: {content[:100]}")

                    # 尝试查找IP地址模式
                    import re
                    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
                    ips = re.findall(ip_pattern, content)

                    if ips:
                        # 返回第一个找到的IP
                        print(f"找到IP: {ips[0]}")
                        return ips[0]
                    else:
                        print("未找到IP地址模式")
            except Exception as e:
                print(f"服务 {service} 失败: {e}")
                continue

        print("所有IP查询服务都失败了")
        return "unknown"

    except Exception as e:
        print(f"获取IP地址失败: {e}")
        return "unknown"


def test_router_control_only():
    """只测试路由器控制功能，不验证IP变化"""
    print("=== 路由器控制功能测试 ===")

    # 初始化路由器控制
    print("1. 初始化路由器控制...")
    try:
        router = TPLinkWAN2Controller()
        print("路由器控制初始化成功")
    except Exception as e:
        print(f"路由器控制初始化失败: {e}")
        return False

    # 执行路由器重新连接
    print("\n2. 执行路由器重新连接...")
    try:
        success = router.switch_ip()
        if success:
            print("路由器重新连接成功")
            return True
        else:
            print("路由器重新连接失败")
            return False
    except Exception as e:
        print(f"路由器重新连接异常: {e}")
        return False


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
    print("开始简化IP验证测试...\n")

    # 测试IP查询服务
    print("=== IP查询服务测试 ===")
    current_ip = get_current_ip_simple()
    print(f"当前ISP IP: {current_ip}")

    # 测试路由器控制
    router_success = test_router_control_only()

    # 测试akshare连接性
    akshare_success = test_akshare_connectivity()

    # 总结结果
    print("\n=== 测试结果总结 ===")
    print(f"路由器控制: {'✅ 成功' if router_success else '❌ 失败'}")
    print(f"akshare连接性: {'✅ 正常' if akshare_success else '❌ 异常'}")
    print(f"当前ISP IP: {current_ip}")

    if router_success and akshare_success:
        print("\n🎉 核心功能测试通过！")
    else:
        print("\n⚠️ 部分测试失败，需要进一步调试。")


if __name__ == "__main__":
    main()

