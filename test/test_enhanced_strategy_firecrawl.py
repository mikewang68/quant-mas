"""
测试enhanced_public_opinion_analysis_strategy_v2策略的FireCrawl配置问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2
from data.mongodb_manager import MongoDBManager
import pandas as pd
import json
import time

def test_enhanced_strategy_firecrawl():
    """测试增强版舆情分析策略的FireCrawl配置"""

    print("=== 开始测试EnhancedPublicOpinionAnalysisStrategyV2策略 ===")

    try:
        # 初始化数据库管理器
        db_manager = MongoDBManager()

        # 从数据库获取策略配置
        strategy_config = db_manager.get_strategy_by_name("增强型舆情分析策略V2")

        if not strategy_config:
            print("❌ 无法从数据库找到策略配置")
            return

        print(f"✅ 找到策略配置: {strategy_config.get('name', 'N/A')}")
        print(f"策略参数: {json.dumps(strategy_config.get('parameters', {}), ensure_ascii=False, indent=2)}")

        # 初始化策略
        strategy = EnhancedPublicOpinionAnalysisStrategyV2(
            name="增强型舆情分析策略V2",
            params=strategy_config.get('parameters', {}),
            db_manager=db_manager
        )

        print("✅ 策略初始化成功")

        # 测试FireCrawl配置获取
        print("\n=== 测试FireCrawl配置获取 ===")
        firecrawl_config = strategy._get_firecrawl_config()
        print(f"FireCrawl配置: {json.dumps(firecrawl_config, ensure_ascii=False, indent=2)}")

        if not firecrawl_config:
            print("❌ FireCrawl配置为空")
        else:
            print("✅ FireCrawl配置获取成功")

        # 测试几只股票的数据获取
        test_stocks = ["000001", "000002", "000004", "000005", "000006"]

        print(f"\n=== 测试股票数据获取（{len(test_stocks)}只股票） ===")

        for i, stock_code in enumerate(test_stocks, 1):
            print(f"\n--- 测试第 {i} 只股票: {stock_code} ---")

            try:
                # 创建空的股票数据（策略需要这个参数）
                stock_data = {stock_code: pd.DataFrame()}

                # 执行策略
                start_time = time.time()
                results = strategy.execute(stock_data, agent_name="test_agent", db_manager=db_manager)
                end_time = time.time()

                execution_time = end_time - start_time
                print(f"执行时间: {execution_time:.2f}秒")

                if results:
                    print(f"✅ 成功获取数据: {len(results)} 条结果")
                    for result in results:
                        print(f"  股票: {result.get('code')}, 评分: {result.get('score')}")
                        print(f"  值: {result.get('value', '')[:200]}...")
                else:
                    print("❌ 没有获取到数据")

                # 添加请求间隔
                if i < len(test_stocks):
                    print("等待5秒...")
                    time.sleep(5)

            except Exception as e:
                print(f"❌ 处理股票 {stock_code} 时出错: {e}")
                import traceback
                traceback.print_exc()

        # 测试FireCrawl API调用
        print("\n=== 测试直接FireCrawl API调用 ===")

        test_url = "https://guba.eastmoney.com/list,000001,1,f.html"
        print(f"测试URL: {test_url}")

        try:
            firecrawl_data = strategy._call_firecrawl_api(test_url, firecrawl_config)

            if firecrawl_data:
                print(f"✅ FireCrawl API调用成功，返回 {len(firecrawl_data)} 条数据")

                # 检查数据内容
                for i, item in enumerate(firecrawl_data[:2]):
                    print(f"数据项 {i+1}:")
                    if "data" in item and "markdown" in item["data"]:
                        markdown_content = item["data"]["markdown"]
                        print(f"  Markdown内容长度: {len(markdown_content)} 字符")
                        print(f"  内容预览: {markdown_content[:500]}...")
                    else:
                        print(f"  数据结构: {json.dumps(item, ensure_ascii=False, indent=2)[:500]}...")
            else:
                print("❌ FireCrawl API调用返回空数据")

        except Exception as e:
            print(f"❌ FireCrawl API调用失败: {e}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_strategy_firecrawl()

