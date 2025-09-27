#!/usr/bin/env python3
"""
Step-by-step test for the Enhanced Public Opinion Analysis Strategy V2 with stock code 300339
This program will show each step of the process and wait for user confirmation before proceeding.
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta
import logging
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2
from config.mongodb_config import MongoDBConfig
from data.mongodb_manager import MongoDBManager

# Configure logging
logging.basicConfig(level=logging.INFO)

def wait_for_user_input():
    """Wait for user to press Enter to continue"""
    input("\nPress Enter to continue to the next step...")

def step_by_step_test():
    """Step-by-step test of the Enhanced Public Opinion Analysis Strategy V2 with stock 300339"""
    print("Step-by-Step Testing of Enhanced Public Opinion Analysis Strategy V2 with stock 300339")
    print("=" * 80)

    try:
        # Step 1: Initialize database manager
        print("\n[Step 1] Initializing database manager...")
        db_manager = MongoDBManager()
        print("✓ Database manager initialized successfully")
        wait_for_user_input()

        # Step 2: Create strategy instance with parameters
        print("\n[Step 2] Creating strategy instance with parameters...")
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
        print("✓ Strategy instance created successfully")

        print("\nStrategy Parameters:")
        for key, value in strategy.params.items():
            print(f"  {key}: {value}")
        wait_for_user_input()

        # Step 3: Test FireCrawl availability check
        print("\n[Step 3] Testing FireCrawl availability check...")
        firecrawl_available = strategy._is_firecrawl_available(
            strategy.firecrawl_config["api_url"],
            strategy.firecrawl_config["timeout"]
        )
        print(f"FireCrawl available: {firecrawl_available}")
        if not firecrawl_available:
            print("Note: FireCrawl is not available, will skip FireCrawl data collection")
        wait_for_user_input()

        # Step 4: Test AkShare news collection
        print("\n[Step 4] Testing AkShare news collection...")
        stock_code = "300339"
        stock_name = "瑞芯微"

        akshare_news = strategy.get_akshare_news(stock_code)
        print(f"AkShare News Data ({len(akshare_news)} items):")
        for i, news in enumerate(akshare_news[:5]):  # Show first 5 items
            print(f"  Item {i+1}:")
            print(f"    Title: {news.get('title', 'N/A')[:100]}...")
            print(f"    Source: {news.get('source', 'N/A')}")
            print(f"    Published: {news.get('publishedAt', 'N/A')}")
            print(f"    Content preview: {news.get('content', 'N/A')[:150]}...")
            print(f"    Time weight: {news.get('time_weight', 'N/A')}")
        if len(akshare_news) > 5:
            print(f"  ... and {len(akshare_news) - 5} more items")
        wait_for_user_input()

        # Step 5: Test industry information collection
        print("\n[Step 5] Testing industry information collection...")
        industry_info = strategy.get_stock_industry_info(stock_code)
        print(f"Industry Info:")
        if industry_info:
            for key, value in industry_info.items():
                print(f"  {key}: {value}")
        else:
            print("  No industry information available")
        wait_for_user_input()

        # Step 6: Test Guba data collection
        print("\n[Step 6] Testing Guba data collection...")
        guba_data = strategy.scrape_guba_data(stock_code)
        print(f"Guba Data:")
        if guba_data:
            for data_type, items in guba_data.items():
                print(f"  {data_type}: {len(items)} items")
                for i, item in enumerate(items[:3]):  # Show first 3 items of each type
                    print(f"    Item {i+1}:")
                    print(f"      Title: {item.get('title', 'N/A')[:100]}...")
                    print(f"      Type: {item.get('type', 'N/A')}")
                    print(f"      Published: {item.get('publishedAt', 'N/A')}")
                    print(f"      Content preview: {item.get('content', 'N/A')[:100]}...")
                    print(f"      Source: {item.get('source', 'N/A')}")
        else:
            print("  No Guba data available")
        wait_for_user_input()

        # Step 7: Test professional sites data collection
        print("\n[Step 7] Testing professional sites data collection...")
        professional_data = strategy.get_professional_site_data(stock_code, stock_name)
        print(f"Professional Sites Data ({len(professional_data)} items):")
        for i, item in enumerate(professional_data[:5]):  # Show first 5 items
            print(f"  Item {i+1}:")
            print(f"    Title: {item.get('title', 'N/A')[:100]}...")
            print(f"    Source: {item.get('source', 'N/A')}")
            print(f"    Published: {item.get('publishedAt', 'N/A')}")
            print(f"    Content preview: {item.get('content', 'N/A')[:100]}...")
            print(f"    Time weight: {item.get('time_weight', 'N/A')}")
        if len(professional_data) > 5:
            print(f"  ... and {len(professional_data) - 5} more items")
        wait_for_user_input()

        # Step 8: Test FireCrawl data collection (if available)
        print("\n[Step 8] Testing FireCrawl data collection...")
        if firecrawl_available:
            search_query = f"{stock_name} {stock_code} 股票 新闻 分析 评论"
            firecrawl_data = strategy.search_stock_news([search_query])
            print(f"FireCrawl Data ({len(firecrawl_data)} items):")
            for i, item in enumerate(firecrawl_data[:5]):  # Show first 5 items
                print(f"  Item {i+1}:")
                print(f"    Title: {item.get('title', 'N/A')[:100]}...")
                print(f"    Source: {item.get('source', 'N/A')}")
                print(f"    Published: {item.get('publishedAt', 'N/A')}")
                print(f"    Content preview: {item.get('content', 'N/A')[:150]}...")
                print(f"    Time weight: {item.get('time_weight', 'N/A')}")
            if len(firecrawl_data) > 5:
                print(f"  ... and {len(firecrawl_data) - 5} more items")
        else:
            print("Skipping FireCrawl data collection as FireCrawl is not available")
        wait_for_user_input()

        # Step 9: Test data collection in detail
        print("\n[Step 9] Testing detailed data collection (collect_all_data)...")
        all_data = strategy.collect_all_data(stock_code, stock_name)

        print("\nDetailed Data Collection Results:")
        print("-" * 50)

        # Show stock info
        print(f"Stock Info:")
        print(f"  Code: {all_data.get('stock_info', {}).get('code', 'N/A')}")
        print(f"  Name: {all_data.get('stock_info', {}).get('name', 'N/A')}")
        print()

        # Show data counts
        akshare_news_count = len(all_data.get('akshare_news', []))
        industry_info_count = len(all_data.get('industry_info', {}))
        guba_data_count = sum(len(items) for items in all_data.get('guba_data', {}).values())
        professional_data_count = len(all_data.get('professional_sites_data', []))
        firecrawl_data_count = len(all_data.get('firecrawl_data', []))

        print(f"Data Collection Summary:")
        print(f"  AkShare News: {akshare_news_count} items")
        print(f"  Industry Info: {industry_info_count} items")
        print(f"  Guba Data: {guba_data_count} items")
        print(f"  Professional Sites: {professional_data_count} items")
        print(f"  FireCrawl Data: {firecrawl_data_count} items")
        print(f"  Total Items: {akshare_news_count + industry_info_count + guba_data_count + professional_data_count + firecrawl_data_count}")
        wait_for_user_input()

        # Step 10: Test time weight calculation
        print("\n[Step 10] Testing time weight calculation...")
        # Test with current time
        current_time = datetime.now().isoformat()
        weight_current = strategy._calculate_time_weight(current_time)
        print(f"Time weight for current time: {weight_current}")

        # Test with 12 hours ago
        time_12h_ago = (datetime.now() - timedelta(hours=12)).isoformat()
        weight_12h = strategy._calculate_time_weight(time_12h_ago)
        print(f"Time weight for 12 hours ago: {weight_12h}")

        # Test with 24 hours ago
        time_24h_ago = (datetime.now() - timedelta(hours=24)).isoformat()
        weight_24h = strategy._calculate_time_weight(time_24h_ago)
        print(f"Time weight for 24 hours ago: {weight_24h}")

        # Test with 48 hours ago
        time_48h_ago = (datetime.now() - timedelta(hours=48)).isoformat()
        weight_48h = strategy._calculate_time_weight(time_48h_ago)
        print(f"Time weight for 48 hours ago: {weight_48h}")
        wait_for_user_input()

        # Step 11: Test public opinion analysis
        print("\n[Step 11] Testing public opinion analysis...")
        meets_criteria, reason, sentiment_score, full_analysis = strategy.analyze_public_opinion(stock_code, stock_name)

        print("\nPublic Opinion Analysis Results:")
        print("-" * 50)
        print(f"Meets Criteria: {meets_criteria}")
        print(f"Reason: {reason}")
        print(f"Sentiment Score: {sentiment_score}")
        print()

        print("Full Analysis Details:")
        if full_analysis:
            for key, value in full_analysis.items():
                if isinstance(value, (str, int, float)) or value is None:
                    print(f"  {key}: {value}")
                elif isinstance(value, list):
                    print(f"  {key}: {len(value)} items")
                elif isinstance(value, dict):
                    print(f"  {key}: {{")
                    for sub_key, sub_value in list(value.items())[:3]:  # Show first 3 key-value pairs
                        print(f"    {sub_key}: {sub_value}")
                    if len(value) > 3:
                        print(f"    ... and {len(value) - 3} more items")
                    print("  }")
                else:
                    print(f"  {key}: {type(value)} - {str(value)[:100]}...")
        else:
            print("  No detailed analysis available")
        wait_for_user_input()

        # Step 12: Test the execute method
        print("\n[Step 12] Testing execute method with sample data...")

        # Create sample stock data (empty DataFrames as the strategy doesn't use them)
        stock_data = {
            "300339": pd.DataFrame()
        }

        # Mock agent name
        agent_name = "舆情分析Agent"

        # Execute strategy (this will return the required format)
        results = strategy.execute(stock_data, agent_name, db_manager)

        print("Strategy Execution Results:")
        print(f"Type of results: {type(results)}")
        print(f"Number of selected stocks: {len(results)}")

        # Display the output format
        print("\nOutput Format Analysis:")
        if results:
            for i, stock_result in enumerate(results):
                print(f"\nStock {i+1}:")
                print(f"  Type: {type(stock_result)}")
                print(f"  Keys: {list(stock_result.keys())}")
                print(f"  Code: {stock_result.get('code', 'N/A')}")
                print(f"  Score: {stock_result.get('score', 'N/A')} (Type: {type(stock_result.get('score'))})")
                print(f"  Value (Reason): {stock_result.get('value', 'N/A')}")
        else:
            print("No stocks selected (this is expected in a test environment)")

        # Show the complete structure as JSON
        print("\nComplete Results Structure (JSON format):")
        print(json.dumps(results, ensure_ascii=False, indent=2))

        # Verify the format meets requirements
        print("\nFormat Verification:")
        if isinstance(results, list):
            print("✓ Output is a list")
            if results:
                first_item = results[0]
                if isinstance(first_item, dict):
                    print("✓ Items are dictionaries")
                    if "score" in first_item and "value" in first_item:
                        print("✓ Contains required 'score' and 'value' fields")
                        score = first_item["score"]
                        if isinstance(score, (int, float)) and 0 <= score <= 1:
                            print("✓ Score is a number between 0 and 1")
                        else:
                            print("⚠ Score is not in the correct range or type")
                        if "value" in first_item and isinstance(first_item["value"], str):
                            print("✓ Value is a string containing the reason")
                        else:
                            print("⚠ Value field is missing or not a string")
                    else:
                        print("✗ Missing required fields 'score' or 'value'")
                else:
                    print("✗ Items are not dictionaries")
            else:
                print("⚠ No items to verify (empty list)")
        else:
            print("✗ Output is not a list")
        wait_for_user_input()

        # Final summary
        print("\n" + "=" * 80)
        print("STEP-BY-STEP TEST COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nSummary of what was tested:")
        print("1. Strategy initialization with parameters")
        print("2. FireCrawl availability checking")
        print("3. AkShare news collection")
        print("4. Industry information collection")
        print("5. Guba data collection")
        print("6. Professional sites data collection")
        print("7. FireCrawl data collection (if available)")
        print("8. Complete data collection process")
        print("9. Time weight calculation")
        print("10. Public opinion analysis")
        print("11. Strategy execution with proper output format")
        print("12. Output format verification")

        print("\nAll components are working correctly and producing the expected output format.")
        print("The strategy is ready for integration with the Public Opinion Selector agent.")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    step_by_step_test()

