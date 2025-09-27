#!/usr/bin/env python3
"""
Debug detailed data collection to show all the real data being collected
"""

import sys
import os
import pandas as pd

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2

def test_detailed_data_collection():
    """Test detailed data collection to show all real data"""
    print("Testing detailed data collection for stock 300339")
    print("=" * 60)

    # Create strategy instance with minimal parameters
    strategy_params = {
        "sentiment_threshold": 0.6,
        "news_count_threshold": 5,
        "search_depth": 10,
        "time_window_hours": 24,
        "data_sources": ["akshare", "firecrawl", "professional_sites", "guba"],
        "professional_sites": [
            "同花顺财经",
            "东方财富网",
            "雪球网",
            "新浪财经",
            "腾讯财经",
        ],
        "firecrawl_config": {
            "api_url": "http://192.168.1.2:8080",
            "timeout": 30,
            "max_retries": 3,
            "retry_delay": 1,
            "rate_limit": 10,
            "concurrent_requests": 5,
        },
        "llm_name": "gemini-2.0-flash",
    }

    strategy = EnhancedPublicOpinionAnalysisStrategyV2(params=strategy_params)

    stock_code = "300339"
    stock_name = "润和软件"  # Using actual stock name

    print(f"Collecting data for {stock_code} ({stock_name})")
    print()

    # Collect all data
    all_data = strategy.collect_all_data(stock_code, stock_name)

    print("COLLECTED DATA SUMMARY")
    print("=" * 30)

    # Show stock info
    print(f"Stock Info:")
    print(f"  Code: {all_data.get('stock_info', {}).get('code', 'N/A')}")
    print(f"  Name: {all_data.get('stock_info', {}).get('name', 'N/A')}")
    print()

    # Show AkShare news data in detail
    akshare_news = all_data.get('akshare_news', [])
    print(f"AkShare News Data ({len(akshare_news)} items):")
    for i, news in enumerate(akshare_news):
        print(f"  Item {i+1}:")
        print(f"    Title: {news.get('title', 'N/A')}")
        print(f"    Source: {news.get('source', 'N/A')}")
        print(f"    Published: {news.get('publishedAt', 'N/A')}")
        print(f"    Content: {news.get('content', 'N/A')}")
        print(f"    URL: {news.get('url', 'N/A')}")
        print(f"    Time weight: {news.get('time_weight', 'N/A')}")
        print()
    print()

    # Show industry info
    industry_info = all_data.get('industry_info', {})
    print(f"Industry Info:")
    if industry_info:
        for key, value in industry_info.items():
            print(f"  {key}: {value}")
    else:
        print("  No industry information available")
    print()

    # Show Guba data in detail
    guba_data = all_data.get('guba_data', {})
    print(f"Guba Data:")
    if guba_data:
        total_guba_items = 0
        for data_type, items in guba_data.items():
            print(f"  {data_type}: {len(items)} items")
            total_guba_items += len(items)
            for i, item in enumerate(items):
                print(f"    Item {i+1}:")
                print(f"      Title: {item.get('title', 'N/A')}")
                print(f"      Content: {item.get('content', 'N/A')}")
                print(f"      Published: {item.get('publishedAt', 'N/A')}")
                print(f"      Source: {item.get('source', 'N/A')}")
                print(f"      Type: {item.get('type', 'N/A')}")
            print()
        print(f"  Total Guba items: {total_guba_items}")
    else:
        print("  No Guba data available")
    print()

    # Show professional sites data
    professional_data = all_data.get('professional_sites_data', [])
    print(f"Professional Sites Data ({len(professional_data)} items):")
    for i, item in enumerate(professional_data):
        print(f"  Item {i+1}:")
        print(f"    Title: {item.get('title', 'N/A')}")
        print(f"    Source: {item.get('source', 'N/A')}")
        print(f"    Published: {item.get('publishedAt', 'N/A')}")
        print(f"    Content: {item.get('content', 'N/A')}")
        print(f"    Time weight: {item.get('time_weight', 'N/A')}")
        print()
    print()

    # Show FireCrawl data
    firecrawl_data = all_data.get('firecrawl_data', [])
    print(f"FireCrawl Data ({len(firecrawl_data)} items):")
    if firecrawl_data:
        for i, item in enumerate(firecrawl_data):
            print(f"  Item {i+1}:")
            print(f"    Title: {item.get('title', 'N/A')}")
            print(f"    Source: {item.get('source', 'N/A')}")
            print(f"    Published: {item.get('publishedAt', 'N/A')}")
            print(f"    Content: {item.get('content', 'N/A')}")
            print(f"    URL: {item.get('url', 'N/A')}")
            print(f"    Time weight: {item.get('time_weight', 'N/A')}")
            print()
    else:
        print("  No FireCrawl data (correctly skipped)")
    print()

    # Calculate total information items
    total_items = len(akshare_news) + len(professional_data) + len(firecrawl_data)
    # Add Guba items
    for items in guba_data.values():
        total_items += len(items)

    print(f"TOTAL INFORMATION ITEMS COLLECTED: {total_items}")
    print("Data collection test completed!")

if __name__ == "__main__":
    test_detailed_data_collection()

