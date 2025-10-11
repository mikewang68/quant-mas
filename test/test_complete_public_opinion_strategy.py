"""
测试完整的增强型舆情分析策略V2
"""
import sys
import os
sys.path.append('.')

# Mock the dependencies to avoid import issues
import unittest.mock as mock

# Mock the database and other dependencies
with mock.patch('pymongo.MongoClient'), \
     mock.patch('strategies.enhanced_public_opinion_analysis_strategy_v2.AkshareClient'), \
     mock.patch('strategies.enhanced_public_opinion_analysis_strategy_v2.FireCrawlClient'):

    try:
        from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2

        print("=== 测试增强型舆情分析策略V2 ===")

        # Test strategy initialization
        strategy = EnhancedPublicOpinionAnalysisStrategyV2()
        print("✅ 策略初始化成功")

        # Test method availability
        methods_to_check = [
            '_get_professional_sites_data',
            'generate_signals',
            'calculate_position_size',
            '_collect_public_opinion_data',
            '_analyze_with_llm',
            '_get_akshare_data',
            '_get_eastmoney_guba_data',
            '_get_qian_gu_qian_ping_data',
            '_get_firecrawl_data'
        ]

        print("\n=== 检查方法实现 ===")
        all_methods_exist = True
        for method_name in methods_to_check:
            if hasattr(strategy, method_name):
                print(f"✅ 方法 {method_name} 存在")
            else:
                print(f"❌ 方法 {method_name} 不存在")
                all_methods_exist = False

        if all_methods_exist:
            print("\n✅ 所有必需方法都已实现")
        else:
            print("\n❌ 部分方法缺失")

        # Test professional sites data method
        print("\n=== 测试专业网站数据方法 ===")
        try:
            professional_data = strategy._get_professional_sites_data("000001", "平安银行")
            print(f"✅ 专业网站数据方法执行成功")
            print(f"   返回数据条数: {len(professional_data)}")
            if professional_data:
                print(f"   第一条数据标题: {professional_data[0].get('title', 'N/A')}")
        except Exception as e:
            print(f"❌ 专业网站数据方法执行失败: {e}")

        # Test calculate_position_size method
        print("\n=== 测试仓位计算方法 ===")
        try:
            position = strategy.calculate_position_size("BUY", 100000, 10.0)
            print(f"✅ 仓位计算方法执行成功")
            print(f"   建议仓位: {position} 股")
        except Exception as e:
            print(f"❌ 仓位计算方法执行失败: {e}")

        # Test generate_signals method
        print("\n=== 测试信号生成方法 ===")
        try:
            import pandas as pd
            test_data = pd.DataFrame({
                'close': [10.0, 10.5, 11.0],
                'volume': [1000000, 1200000, 1500000]
            })
            signals = strategy.generate_signals(test_data)
            print(f"✅ 信号生成方法执行成功")
            print(f"   返回信号数量: {len(signals)}")
        except Exception as e:
            print(f"❌ 信号生成方法执行失败: {e}")

        print("\n=== 测试完成 ===")

    except Exception as e:
        print(f"❌ 导入策略失败: {e}")
        import traceback
        traceback.print_exc()

