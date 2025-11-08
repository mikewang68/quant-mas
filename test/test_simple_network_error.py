#!/usr/bin/env python
# coding=utf-8

"""
简单网络错误处理测试
用于快速验证网络错误处理机制的核心功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.network_error_handler import handle_network_error, is_rate_limit_error

def test_network_error_detection():
    """测试网络错误检测"""
    print("\n🔍 测试网络错误检测...")

    # 测试各种错误类型
    test_errors = [
        "Connection aborted by remote host",
        "Could not reach host. Are you offline?",
        "429 Too Many Requests",
        "主动触发IP更换",
        "Unknown error type"
    ]

    for error_msg in test_errors:
        print(f"\n测试错误: {error_msg}")

        # 测试错误分类
        from utils.network_error_handler import NetworkErrorClassifier
        classification = NetworkErrorClassifier.classify_error(error_msg)
        print(f"   分类: {classification['type']}")
        print(f"   严重性: {classification['severity']}")
        print(f"   需要切换IP: {classification['should_switch_ip']}")

        # 测试错误处理
        class MockError(Exception):
            def __init__(self, message):
                self.message = message
            def __str__(self):
                return self.message

        mock_error = MockError(error_msg)
        result = handle_network_error(mock_error, max_retries=1, retry_delay=1)
        print(f"   处理结果: {result}")

def test_akshare_connectivity():
    """测试akshare连接性"""
    print("\n🔍 测试akshare连接性...")

    import akshare as ak

    try:
        # 测试获取股票数据
        test_code = "000001"  # 平安银行
        stock_data = ak.stock_zh_a_hist(symbol=test_code, period="daily", adjust="qfq")
        print(f"✅ akshare股票数据: 获取成功 ({len(stock_data)} 条记录)")
        return True
    except Exception as e:
        print(f"❌ akshare连接失败: {str(e)}")

        # 分析错误类型
        error_str = str(e)
        print(f"   错误类型分析:")
        print(f"   - 是否为速率限制错误: {is_rate_limit_error(error_str)}")
        print(f"   - 错误详情: {error_str}")

        return False

def main():
    """主函数"""
    print("=" * 60)
    print("简单网络错误处理测试")
    print("=" * 60)

    # 测试1: 网络错误检测
    test_network_error_detection()

    # 测试2: akshare连接性
    akshare_success = test_akshare_connectivity()

    print("\n💡 测试结果总结:")
    print(f"   - 网络错误检测: ✅ 完成")
    print(f"   - akshare连接: {'✅' if akshare_success else '❌'}")

    if not akshare_success:
        print("\n📋 问题诊断:")
        print("   - 当akshare连接失败时，网络错误处理机制应该自动触发IP切换")
        print("   - 请检查down2mongo.py中的网络错误处理逻辑")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()

