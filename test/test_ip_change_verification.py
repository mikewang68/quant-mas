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
    """获取当前ISP提供的公网IP地址"""
    try:
        # 使用百度IP查询服务获取ISP提供的IP地址
        service = 'https://qifu.baidu.com/?activeKey=SEARCH_IP&trace=apistore_ip_aladdin&activeId=SEARCH_IP_ADDRESS'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(service, headers=headers, timeout=10)
        if response.status_code == 200:
            # 解析返回的HTML或JSON来获取IP地址
            # 这里需要根据实际返回格式来解析
            # 暂时使用简单的文本搜索
            content = response.text

            # 尝试查找IP地址模式
            import re
            ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            ips = re.findall(ip_pattern, content)

            if ips:
                # 返回第一个找到的IP
                return ips[0]
            else:
                print("警告: 无法从响应中解析IP地址")
                return "unknown"
        else:
            print(f"IP查询服务返回状态码: {response.status_code}")
            return "unknown"

    except Exception as e:
        print(f"获取IP地址失败: {e}")
        return "unknown"


def test_ip_change_with_router_control():
    """测试路由器控制后的ISP IP地址变化"""
    print("=== ISP IP地址变化验证测试 ===")

    # 获取初始IP
    print("1. 获取初始ISP IP地址...")
    initial_ip = get_current_ip()
    print(f"初始ISP IP: {initial_ip}")

    if initial_ip == "unknown":
        print("警告: 无法获取初始ISP IP地址，可能网络连接有问题")
        return False

    # 初始化路由器控制
    print("\n2. 初始化路由器控制...")
    try:
        router = TPLinkWAN2Controller()
        print("路由器控制初始化成功")
    except Exception as e:
        print(f"路由器控制初始化失败: {e}")
        return False

    # 执行路由器重新连接
    print("\n3. 执行路由器重新连接...")
    try:
        success = router.switch_ip()
        if success:
            print("路由器重新连接成功")
        else:
            print("路由器重新连接失败")
            return False
    except Exception as e:
        print(f"路由器重新连接异常: {e}")
        return False

    # 等待网络稳定
    print("\n4. 等待网络稳定...")
    time.sleep(15)  # 等待15秒让网络稳定

    # 获取新IP
    print("\n5. 获取新ISP IP地址...")
    new_ip = get_current_ip()
    print(f"新ISP IP: {new_ip}")

    # 比较IP变化
    print("\n6. 比较ISP IP变化...")
    if new_ip == "unknown":
        print("警告: 无法获取新ISP IP地址")
        return False
    elif new_ip != initial_ip:
        print(f"✅ ISP IP地址已成功变更: {initial_ip} -> {new_ip}")
        return True
    else:
        print(f"❌ ISP IP地址未变化: {initial_ip} -> {new_ip}")
        return False


def test_akshare_with_new_ip():
    """测试新IP是否启用成功的akshare下载"""
    print("\n=== akshare下载测试 ===")

    try:
        import akshare as ak

        print("1. 测试akshare基本功能...")

        # 测试获取股票代码列表
        stock_list = ak.stock_info_a_code_name()
        print(f"成功获取 {len(stock_list)} 只股票代码")

        # 测试获取交易日历
        trade_dates = ak.tool_trade_date_hist_sina()
        print(f"成功获取 {len(trade_dates)} 条交易日历数据")

        # 测试获取单只股票数据
        if len(stock_list) > 0:
            test_code = stock_list.iloc[0]['code']
            stock_data = ak.stock_zh_a_hist(symbol=test_code, period="daily", adjust="qfq")
            print(f"成功获取股票 {test_code} 的 {len(stock_data)} 条K线数据")

        print("✅ akshare下载测试成功")
        return True

    except Exception as e:
        print(f"❌ akshare下载测试失败: {e}")
        return False


def analyze_timeout_issues():
    """分析IP验证测试超时原因"""
    print("\n=== 超时问题分析 ===")

    # 测试网络连接超时
    print("1. 测试网络连接超时...")
    timeout_services = [
        'https://qifu.baidu.com/?activeKey=SEARCH_IP&trace=apistore_ip_aladdin&activeId=SEARCH_IP_ADDRESS'
    ]

    for service in timeout_services:
        try:
            start_time = time.time()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(service, headers=headers, timeout=5)
            end_time = time.time()
            response_time = end_time - start_time
            print(f"  {service}: {response.status_code} (响应时间: {response_time:.2f}s)")
        except requests.exceptions.Timeout:
            print(f"  {service}: 超时")
        except Exception as e:
            print(f"  {service}: 错误 - {e}")

    # 测试路由器连接超时
    print("\n2. 测试路由器连接超时...")
    try:
        router = TPLinkWAN2Controller()
        print("  路由器控制初始化成功")
    except Exception as e:
        print(f"  路由器控制初始化失败: {e}")


def main():
    """主测试函数"""
    print("开始ISP IP地址变化验证测试...\n")

    # 分析超时问题
    analyze_timeout_issues()

    # 测试IP变化
    ip_changed = test_ip_change_with_router_control()

    # 测试akshare功能
    akshare_working = test_akshare_with_new_ip()

    # 总结结果
    print("\n=== 测试结果总结 ===")
    print(f"ISP IP地址变化: {'✅ 成功' if ip_changed else '❌ 失败'}")
    print(f"akshare功能: {'✅ 正常' if akshare_working else '❌ 异常'}")

    if ip_changed and akshare_working:
        print("\n🎉 所有测试通过！网络错误处理机制工作正常。")
    else:
        print("\n⚠️ 部分测试失败，需要进一步调试。")


if __name__ == "__main__":
    main()

