#!/usr/bin/env python3
"""
Debug script to fix the issue where the current program is not getting any information
"""

import sys
import os
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2


def debug_and_fix_data_collection():
    """Debug and fix the strategy's data collection process"""
    print("Debugging and fixing Enhanced Public Opinion Analysis Strategy V2 data collection")
    print("=" * 80)

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
    print("-" * 60)

    # Test AkShare news collection
    print("\n1. Testing AkShare news collection...")
    try:
        news_data = strategy.get_akshare_news(stock_code)
        print(f"   News items collected: {len(news_data)}")
        if news_data:
            # Check if news data has actual content
            valid_news_count = sum(1 for item in news_data if item.get('title') or item.get('content'))
            print(f"   Valid news items: {valid_news_count}")
            if valid_news_count > 0:
                first_valid_news = next((item for item in news_data if item.get('title') or item.get('content')), None)
                if first_valid_news:
                    print(f"   First valid news item: {first_valid_news}")
            else:
                print("   All news items are empty - this is the issue!")
                # Let's check what's actually in AkShare
                import akshare as ak
                print("   Checking raw AkShare data...")
                try:
                    raw_news = ak.stock_news_em(symbol=stock_code, pageSize=5)
                    print(f"   Raw AkShare news shape: {raw_news.shape}")
                    print(f"   Raw AkShare news columns: {list(raw_news.columns)}")
                    if len(raw_news) > 0:
                        print("   First raw news item:")
                        for col in raw_news.columns:
                            print(f"     {col}: {raw_news.iloc[0][col]}")
                except Exception as e:
                    print(f"   Error getting raw AkShare data: {e}")
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
        total_items = 0
        for section, data in guba_data.items():
            count = len(data) if data else 0
            total_items += count
            print(f"   {section}: {count} items")
            if data and len(data) > 0:
                print(f"     Sample item: {data[0] if len(data) > 0 else 'None'}")
        print(f"   Total Guba items: {total_items}")
    except Exception as e:
        print(f"   Error scraping Guba data: {e}")
        import traceback
        traceback.print_exc()

    # Test detailed Guba data collection
    print("\n4. Testing detailed Guba data collection...")
    try:
        detailed_guba_data = strategy.get_detailed_guba_data(stock_code)
        print(f"   Detailed Guba data sections: {list(detailed_guba_data.keys())}")
        total_items = 0
        for section, data in detailed_guba_data.items():
            count = len(data) if data else 0
            total_items += count
            print(f"   {section}: {count} items")
            if data and len(data) > 0:
                print(f"     Sample item: {data[0] if len(data) > 0 else 'None'}")
        print(f"   Total detailed Guba items: {total_items}")
    except Exception as e:
        print(f"   Error collecting detailed Guba data: {e}")
        import traceback
        traceback.print_exc()

    # Test professional site data (fix the issue with return type)
    print("\n5. Testing professional site data collection...")
    try:
        prof_data = strategy.get_professional_site_data(stock_code, stock_name)
        print(f"   Professional site data type: {type(prof_data)}")
        if isinstance(prof_data, list):
            print(f"   Professional site data items: {len(prof_data)}")
            if prof_data:
                print(f"   First item: {prof_data[0] if len(prof_data) > 0 else 'None'}")
        elif isinstance(prof_data, dict):
            print(f"   Professional site data sections: {list(prof_data.keys())}")
            for section, data in prof_data.items():
                print(f"   {section}: {len(data) if data else 0} items")
                if data and len(data) > 0:
                    print(f"     Sample item: {data[0] if len(data) > 0 else 'None'}")
        else:
            print(f"   Professional site data: {prof_data}")
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
        else:
            print("   No search results - checking FireCrawl availability...")
            # Check if FireCrawl is actually working
            api_url = strategy.firecrawl_config.get("api_url")
            timeout = strategy.firecrawl_config.get("timeout", 30)
            is_available = strategy._is_firecrawl_available(api_url, timeout)
            print(f"   FireCrawl available: {is_available}")
    except Exception as e:
        print(f"   Error searching stock news: {e}")
        import traceback
        traceback.print_exc()

    # Test collecting all data with proper structure
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
                # Check if it's the stock_info dict
                if section == "stock_info":
                    print(f"   {section}: {data}")
                    continue
                dict_total = sum(len(v) for v in data.values() if isinstance(v, list))
                total_items += dict_total
                print(f"   {section}: {dict_total} items (nested)")
            else:
                print(f"   {section}: {type(data)} - {data}")
        print(f"   Total items collected: {total_items}")

        # Test data formatting for LLM
        print("\n8. Testing data formatting for LLM...")
        try:
            formatted_data = strategy._format_data_for_llm(all_data)
            print(f"   Formatted data length: {len(formatted_data)} characters")
            if len(formatted_data) > 200:
                print(f"   Formatted data preview: {formatted_data[:200]}...")
            else:
                print(f"   Formatted data: {formatted_data}")

            # Check if formatting was successful
            if "数据格式化失败" in formatted_data:
                print("   ERROR: Data formatting failed!")
            elif len(formatted_data) < 50:
                print("   WARNING: Formatted data seems too short!")
        except Exception as e:
            print(f"   Error formatting data: {e}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"   Error collecting all data: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("Debug and fix analysis completed")


if __name__ == "__main__":
    debug_and_fix_data_collection()

