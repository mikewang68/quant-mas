"""
测试东方财富股吧爬虫问题诊断脚本
重现只有前10只股票有有效数据，后续股票返回相同数据的问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.eastmoney_guba_scraper import scrape_all_guba_data
import json
import time

def test_guba_scraper_issue():
    """测试股吧爬虫问题"""

    # FireCrawl配置
    firecrawl_config = {
        "api_url": "http://localhost:3002",
        "max_retries": 3,
        "timeout": 30,
        "retry_delay": 1
    }

    # 测试股票列表（前15只股票）
    test_stocks = [
        "000001", "000002", "000004", "000005", "000006",
        "000007", "000008", "000009", "000010", "000011",
        "000012", "000014", "000016", "000017", "000018"
    ]

    results = {}

    print("=== 开始测试东方财富股吧爬虫问题 ===")
    print(f"测试股票数量: {len(test_stocks)}")

    for i, stock_code in enumerate(test_stocks, 1):
        print(f"\n--- 测试第 {i} 只股票: {stock_code} ---")

        try:
            # 爬取所有类型的数据
            all_data = scrape_all_guba_data(stock_code, firecrawl_config, limit_per_type=3)

            # 统计每种类型的数据数量
            data_counts = {}
            for data_type, data_list in all_data.items():
                data_counts[data_type] = len(data_list)

                # 打印前几条数据的标题和时间
                print(f"  {data_type}: {len(data_list)} 条数据")
                for j, item in enumerate(data_list[:2], 1):
                    title = item.get('title', 'N/A')
                    print(f"    {j}. {title}")

            results[stock_code] = {
                'data_counts': data_counts,
                'sample_data': {}
            }

            # 记录样本数据用于比较
            for data_type in ['consultations', 'hot_posts']:
                if all_data[data_type]:
                    results[stock_code]['sample_data'][data_type] = all_data[data_type][0]['title']

            # 添加请求间隔，避免过快请求
            if i < len(test_stocks):
                print(f"等待3秒...")
                time.sleep(3)

        except Exception as e:
            print(f"  错误: {e}")
            results[stock_code] = {'error': str(e)}

    print("\n=== 测试结果分析 ===")

    # 分析数据重复问题
    print("\n1. 数据重复性分析:")
    sample_titles = {}
    for stock_code, result in results.items():
        if 'sample_data' in result:
            for data_type, title in result['sample_data'].items():
                if title not in sample_titles:
                    sample_titles[title] = []
                sample_titles[title].append(stock_code)

    # 找出重复的数据
    duplicate_titles = {title: stocks for title, stocks in sample_titles.items() if len(stocks) > 1}

    if duplicate_titles:
        print("发现重复数据:")
        for title, stocks in duplicate_titles.items():
            print(f"  标题: {title[:50]}...")
            print(f"  重复股票: {stocks}")
    else:
        print("未发现重复数据")

    # 分析数据有效性
    print("\n2. 数据有效性分析:")
    valid_stocks = []
    invalid_stocks = []

    for stock_code, result in results.items():
        if 'data_counts' in result:
            total_data = sum(result['data_counts'].values())
            if total_data > 0:
                valid_stocks.append(stock_code)
            else:
                invalid_stocks.append(stock_code)

    print(f"有效数据股票: {len(valid_stocks)} 只")
    print(f"无效数据股票: {len(invalid_stocks)} 只")

    # 分析数据时间戳
    print("\n3. 数据时间戳分析:")
    april_data_stocks = []
    recent_data_stocks = []

    for stock_code, result in results.items():
        if 'sample_data' in result:
            for title in result['sample_data'].values():
                if '04-' in title or '4-' in title:
                    april_data_stocks.append(stock_code)
                    break
                else:
                    recent_data_stocks.append(stock_code)
                    break

    print(f"4月份数据股票: {len(april_data_stocks)} 只")
    print(f"近期数据股票: {len(recent_data_stocks)} 只")

    # 保存详细结果
    with open('guba_scraper_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n详细结果已保存到: guba_scraper_test_results.json")

    return results

if __name__ == "__main__":
    test_guba_scraper_issue()

