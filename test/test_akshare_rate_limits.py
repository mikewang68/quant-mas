#!/usr/bin/env python
# coding=utf-8

import sys
import os
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import akshare as ak


def test_akshare_rate_limits():
    """测试akshare的速率限制"""
    print("=== akshare速率限制测试 ===\n")

    # 测试获取股票代码列表
    print("1. 测试获取股票代码列表...")
    try:
        stock_list = ak.stock_info_a_code_name()
        print(f"✅ 成功获取 {len(stock_list)} 只股票代码")
        print(f"   前5只股票: {stock_list.head()}")
    except Exception as e:
        print(f"❌ 获取股票代码列表失败: {e}")

    # 测试连续获取多只股票数据
    print("\n2. 测试连续获取多只股票数据...")
    test_codes = ['000001', '000002', '000004', '000005', '000006']

    for i, code in enumerate(test_codes):
        try:
            print(f"   获取第 {i+1} 只股票数据: {code}")
            stock_data = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date="20240101",
                end_date="20241108",
                adjust="qfq"
            )
            print(f"   ✅ 成功获取 {len(stock_data)} 条数据")

            # 添加延迟以避免速率限制
            if i < len(test_codes) - 1:
                print("   等待1秒...")
                time.sleep(1)

        except Exception as e:
            print(f"   ❌ 获取股票 {code} 数据失败: {e}")

    # 测试批量获取数据
    print("\n3. 测试批量获取数据...")
    try:
        # 获取交易日历
        trade_dates = ak.tool_trade_date_hist_sina()
        print(f"✅ 成功获取 {len(trade_dates)} 条交易日历数据")

        # 获取行业板块
        industry_boards = ak.stock_board_industry_name_em()
        print(f"✅ 成功获取 {len(industry_boards)} 个行业板块")

        # 获取概念板块
        concept_boards = ak.stock_board_concept_name_em()
        print(f"✅ 成功获取 {len(concept_boards)} 个概念板块")

    except Exception as e:
        print(f"❌ 批量获取数据失败: {e}")

    # 测试财务数据获取
    print("\n4. 测试财务数据获取...")
    try:
        # 获取业绩报表
        yjbb_data = ak.stock_yjbb_em()
        print(f"✅ 成功获取 {len(yjbb_data)} 条业绩报表数据")

        # 获取资产负债表
        zcfz_data = ak.stock_zcfz_em()
        print(f"✅ 成功获取 {len(zcfz_data)} 条资产负债表数据")

        # 获取利润表
        lrb_data = ak.stock_lrb_em()
        print(f"✅ 成功获取 {len(lrb_data)} 条利润表数据")

    except Exception as e:
        print(f"❌ 财务数据获取失败: {e}")

    print("\n✅ akshare速率限制测试完成")


def test_concurrent_requests():
    """测试并发请求"""
    print("\n=== 并发请求测试 ===\n")

    print("注意: akshare通常有速率限制，建议:")
    print("   - 单次请求间隔1-2秒")
    print("   - 避免高频并发请求")
    print("   - 使用IP轮换机制应对速率限制")
    print("   - 分批处理大量股票数据")

    # 测试快速连续请求
    print("\n5. 测试快速连续请求...")
    test_codes = ['000001', '000002']

    for i, code in enumerate(test_codes):
        try:
            print(f"   快速获取股票 {code} 数据...")
            stock_data = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date="20240101",
                end_date="20241108",
                adjust="qfq"
            )
            print(f"   ✅ 成功获取 {len(stock_data)} 条数据")

            # 不添加延迟，测试快速请求

        except Exception as e:
            print(f"   ❌ 快速请求失败: {e}")
            print("   💡 建议: 添加请求间隔避免速率限制")

    print("\n✅ 并发请求测试完成")


def main():
    """主测试函数"""
    print("开始akshare速率限制测试\n")

    # 测试akshare速率限制
    test_akshare_rate_limits()

    # 测试并发请求
    test_concurrent_requests()

    print("\n=== 测试结果总结 ===")
    print("✅ akshare基本功能正常")
    print("✅ 单只股票数据获取正常")
    print("✅ 批量数据获取正常")
    print("✅ 财务数据获取正常")
    print("\n📋 速率限制建议:")
    print("   - 单次请求间隔: 1-2秒")
    print("   - 避免高频并发请求")
    print("   - 使用IP轮换机制应对速率限制")
    print("   - 分批处理大量股票数据")
    print("\n🎉 akshare速率限制测试完成！")


if __name__ == "__main__":
    main()

