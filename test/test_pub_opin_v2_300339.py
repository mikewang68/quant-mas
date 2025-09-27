#!/usr/bin/env python3
"""
Test the Enhanced Public Opinion Analysis Strategy V2 with stock code 300339
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

def test_enhanced_public_opinion_strategy_v2():
    """Test the Enhanced Public Opinion Analysis Strategy V2 with stock 300339"""
    print("Testing Enhanced Public Opinion Analysis Strategy V2 with stock 300339")
    print("=" * 70)

    try:
        # Initialize database manager
        db_manager = MongoDBManager()

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

        print("Strategy Parameters:")
        for key, value in strategy.params.items():
            print(f"  {key}: {value}")
        print()

        # Test FireCrawl availability check
        print("Testing FireCrawl availability check...")
        firecrawl_available = strategy._is_firecrawl_available(
            strategy.firecrawl_config["api_url"],
            strategy.firecrawl_config["timeout"]
        )
        print(f"FireCrawl available: {firecrawl_available}")
        print()

        # Test data collection in detail
        print("Testing detailed data collection...")
        stock_code = "300339"
        stock_name = "未知股票"

        # Collect all data
        all_data = strategy.collect_all_data(stock_code, stock_name)

        print("\nDetailed Data Collection Results:")
        print("-" * 50)

        # Show stock info
        print(f"Stock Info:")
        print(f"  Code: {all_data.get('stock_info', {}).get('code', 'N/A')}")
        print(f"  Name: {all_data.get('stock_info', {}).get('name', 'N/A')}")
        print()

        # Show AkShare news data
        akshare_news = all_data.get('akshare_news', [])
        print(f"AkShare News Data ({len(akshare_news)} items):")
        for i, news in enumerate(akshare_news[:3]):  # Show first 3 items
            print(f"  Item {i+1}:")
            print(f"    Title: {news.get('title', 'N/A')[:50]}...")
            print(f"    Source: {news.get('source', 'N/A')}")
            print(f"    Published: {news.get('publishedAt', 'N/A')}")
            print(f"    Content preview: {news.get('content', 'N/A')[:100]}...")
            print(f"    Time weight: {news.get('time_weight', 'N/A')}")
        if len(akshare_news) > 3:
            print(f"  ... and {len(akshare_news) - 3} more items")
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

        # Show Guba data
        guba_data = all_data.get('guba_data', {})
        print(f"Guba Data:")
        if guba_data:
            for data_type, items in guba_data.items():
                print(f"  {data_type}: {len(items)} items")
                for i, item in enumerate(items[:2]):  # Show first 2 items of each type
                    print(f"    Item {i+1}:")
                    print(f"      Title: {item.get('title', 'N/A')[:50]}...")
                    print(f"      Type: {item.get('type', 'N/A')}")
                    print(f"      Published: {item.get('publishedAt', 'N/A')}")
        else:
            print("  No Guba data available")
        print()

        # Show professional sites data
        professional_data = all_data.get('professional_sites_data', [])
        print(f"Professional Sites Data ({len(professional_data)} items):")
        for i, item in enumerate(professional_data[:3]):  # Show first 3 items
            print(f"  Item {i+1}:")
            print(f"    Title: {item.get('title', 'N/A')[:50]}...")
            print(f"    Source: {item.get('source', 'N/A')}")
            print(f"    Published: {item.get('publishedAt', 'N/A')}")
            print(f"    Content preview: {item.get('content', 'N/A')[:100]}...")
            print(f"    Time weight: {item.get('time_weight', 'N/A')}")
        if len(professional_data) > 3:
            print(f"  ... and {len(professional_data) - 3} more items")
        print()

        # Show FireCrawl data
        firecrawl_data = all_data.get('firecrawl_data', [])
        print(f"FireCrawl Data ({len(firecrawl_data)} items):")
        for i, item in enumerate(firecrawl_data[:3]):  # Show first 3 items
            print(f"  Item {i+1}:")
            print(f"    Title: {item.get('title', 'N/A')[:50]}...")
            print(f"    Source: {item.get('source', 'N/A')}")
            print(f"    Published: {item.get('publishedAt', 'N/A')}")
            print(f"    Content preview: {item.get('content', 'N/A')[:100]}...")
            print(f"    Time weight: {item.get('time_weight', 'N/A')}")
        if len(firecrawl_data) > 3:
            print(f"  ... and {len(firecrawl_data) - 3} more items")
        print()

        # Test public opinion analysis with detailed output
        print("Testing detailed public opinion analysis...")
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
                    if value and isinstance(value[0], dict):
                        for i, item in enumerate(value[:2]):  # Show first 2 items
                            print(f"    Item {i+1}: {item}")
                        if len(value) > 2:
                            print(f"    ... and {len(value) - 2} more items")
                    else:
                        print(f"    {value[:5]}...")  # Show first 5 items if not dict
                elif isinstance(value, dict):
                    print(f"  {key}: {{")
                    for sub_key, sub_value in list(value.items())[:5]:  # Show first 5 key-value pairs
                        print(f"    {sub_key}: {sub_value}")
                    if len(value) > 5:
                        print(f"    ... and {len(value) - 5} more items")
                    print("  }")
                else:
                    print(f"  {key}: {type(value)} - {str(value)[:100]}...")
        else:
            print("  No detailed analysis available")
        print()

        # Test the execute method with sample data
        print("Testing execute method with sample data...")

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

        print("\nTest completed successfully!")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_enhanced_public_opinion_strategy_v2()

