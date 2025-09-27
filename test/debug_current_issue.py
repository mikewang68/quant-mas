#!/usr/bin/env python3
"""
Debug script to understand why the current program is not getting any information
"""

import sys
import os
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2


def debug_strategy_data_collection():
    """Debug the strategy's data collection process"""
    print("Debugging Enhanced Public Opinion Analysis Strategy V2 data collection")
    print("=" * 70)

    # Initialize strategy
    strategy = EnhancedPublicOpinionAnalysisStrategyV2()

    print(f"Strategy initialized: {strategy.name}")
    print(f"FireCrawl config: {strategy.firecrawl_config}")
    print(f"Search depth: {strategy.search_depth}")
    print(f"Data sources: {strategy.data_sources}")

    # Test with a sample stock
    stock_code = "300339"
    stock_name = "润和软件"

    print(f"\nTesting data collection for {stock_code} ({stock_name})")
    print("-" * 50)

    # Test AkShare news collection
    print("\n1. Testing AkShare news collection...")
    try:
        news_data = strategy.get_akshare_news(stock_code)
        print(f"   News items collected: {len(news_data)}")
        if news_data:
            print(f"   First news item: {news_data[0] if len(news_data) > 0 else 'None'}")
        else:
            print("   No news data collected")
    except Exception as e:
        print(f"   Error collecting news: {e}")
        import traceback
        traceback.print_exc()

    # Test industry info collection
    print("\n2. Testing industry info collection...")
    try:
        industry_info = strategy.get_stock_industry_info(stock_code)
        print(f"   Industry info: {industry_info}")
    except Exception as e:
        print(f"   Error collecting industry info: {e}")
        import traceback
        traceback.print_exc()

    # Test FireCrawl scraping
    print("\n3. Testing FireCrawl scraping...")
    try:
        guba_data = strategy.scrape_guba_data(stock_code)
        print(f"   Guba data sections: {list(guba_data.keys())}")
        for section, data in guba_data.items():
            print(f"   {section}: {len(data) if data else 0} items")
            if data and len(data) > 0:
                print(f"     Sample item: {data[0] if len(data) > 0 else 'None'}")
    except Exception as e:
        print(f"   Error scraping Guba data: {e}")
        import traceback
        traceback.print_exc()

    # Test detailed Guba data collection
    print("\n4. Testing detailed Guba data collection...")
    try:
        detailed_guba_data = strategy.get_detailed_guba_data(stock_code)
        print(f"   Detailed Guba data sections: {list(detailed_guba_data.keys())}")
        for section, data in detailed_guba_data.items():
            print(f"   {section}: {len(data) if data else 0} items")
            if data and len(data) > 0:
                print(f"     Sample item: {data[0] if len(data) > 0 else 'None'}")
    except Exception as e:
        print(f"   Error collecting detailed Guba data: {e}")
        import traceback
        traceback.print_exc()

    # Test professional site data
    print("\n5. Testing professional site data collection...")
    try:
        prof_data = strategy.get_professional_site_data(stock_code, stock_name)
        print(f"   Professional site data sections: {list(prof_data.keys())}")
        for section, data in prof_data.items():
            print(f"   {section}: {len(data) if data else 0} items")
            if data and len(data) > 0:
                print(f"     Sample item: {data[0] if len(data) > 0 else 'None'}")
    except Exception as e:
        print(f"   Error collecting professional site data: {e}")
        import traceback
        traceback.print_exc()

    # Test search stock news
    print("\n6. Testing stock news search...")
    try:
        queries = [f"{stock_name} 股票", f"{stock_code} 分析"]
        search_results = strategy.search_stock_news(queries)
        print(f"   Search results: {len(search_results)} items")
        if search_results:
            print(f"   First search result: {search_results[0] if len(search_results) > 0 else 'None'}")
    except Exception as e:
        print(f"   Error searching stock news: {e}")
        import traceback
        traceback.print_exc()

    # Test collecting all data
    print("\n7. Testing complete data collection...")
    try:
        all_data = strategy.collect_all_data(stock_code, stock_name)
        print(f"   All data sections: {list(all_data.keys())}")
        total_items = 0
        for section, data in all_data.items():
            if isinstance(data, list):
                count = len(data)
                total_items += count
                print(f"   {section}: {count} items")
            elif isinstance(data, dict):
                dict_total = sum(len(v) for v in data.values() if isinstance(v, list))
                total_items += dict_total
                print(f"   {section}: {dict_total} items (nested)")
            else:
                print(f"   {section}: {type(data)}")
        print(f"   Total items collected: {total_items}")
    except Exception as e:
        print(f"   Error collecting all data: {e}")
        import traceback
        traceback.print_exc()

    # Test LLM analysis with sample data
    print("\n8. Testing LLM analysis with sample data...")
    try:
        # Create some sample data for testing
        sample_data = {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "akshare_news": [
                {"title": "润和软件获得新合同", "content": "润和软件宣布获得重要软件开发合同", "time": "2025-09-01"},
                {"title": "润和软件股价上涨", "content": "受利好消息影响，润和软件股价上涨5%", "time": "2025-09-02"}
            ],
            "industry_info": {"industry": "软件服务", "market_cap": "中盘股"},
            "guba_data": {
                "consultations": [],
                "reports": [],
                "announcements": [],
                "hot_posts": []
            },
            "detailed_guba_data": {
                "user_focus": [{"date": "2025-09-01", "focus_index": 85.5}],
                "institutional_participation": [{"date": "2025-09-01", "participation": 42.3}],
                "historical_rating": [{"date": "2025-09-01", "rating": 68.2}],
                "daily_participation": [{"date": "2025-09-01", "daily_desire_rise": 12.5, "avg_participation_change": 2.1}]
            },
            "professional_data": [],
            "search_results": []
        }

        # Format data for LLM
        formatted_data = strategy._format_data_for_llm(sample_data)
        print(f"   Formatted data length: {len(formatted_data)} characters")
        print(f"   Formatted data preview: {formatted_data[:200]}...")

        # Test sentiment analysis (this might fail if no LLM is configured)
        print("   Attempting sentiment analysis...")
        sentiment_result = strategy.analyze_sentiment_with_llm(formatted_data)
        print(f"   Sentiment analysis result: {sentiment_result}")

    except Exception as e:
        print(f"   Error in LLM analysis: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)
    print("Debug completed")


if __name__ == "__main__":
    debug_strategy_data_collection()

