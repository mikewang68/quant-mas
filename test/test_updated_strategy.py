#!/usr/bin/env python3
"""
Test script for the updated Enhanced Public Opinion Analysis Strategy V2
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2

def test_strategy_scraping():
    """Test the updated strategy with actual Guba URL scraping"""
    print("Testing Enhanced Public Opinion Analysis Strategy V2 with FireCrawl integration")
    print("=" * 80)

    # Initialize strategy
    strategy = EnhancedPublicOpinionAnalysisStrategyV2()

    # Test with a sample stock code
    stock_code = "300339"
    stock_name = "润和软件"

    print(f"Testing with stock: {stock_code} ({stock_name})")

    # Test Guba data scraping
    print("\n1. Testing Guba data scraping...")
    try:
        guba_data = strategy.scrape_guba_data(stock_code)
        print(f"   Guba data scraping result: {type(guba_data)}")
        print(f"   Keys in guba_data: {list(guba_data.keys()) if isinstance(guba_data, dict) else 'Not a dict'}")

        # Check specific sections
        if isinstance(guba_data, dict):
            for key, value in guba_data.items():
                print(f"   {key}: {len(value) if isinstance(value, list) else value} items")
                if isinstance(value, list) and len(value) > 0:
                    print(f"     Sample item: {value[0] if len(value) > 0 else 'None'}")
    except Exception as e:
        print(f"   Error in Guba data scraping: {e}")

    # Test individual page scraping
    print("\n2. Testing individual page scraping...")
    test_urls = [
        f"https://guba.eastmoney.com/list,{stock_code},1,f.html",
        f"https://guba.eastmoney.com/list,{stock_code},2,f.html",
        f"https://guba.eastmoney.com/list,{stock_code}.html"
    ]

    for i, url in enumerate(test_urls, 1):
        print(f"\n   Testing URL {i}: {url}")
        try:
            items = strategy._scrape_guba_page(url, f"test_type_{i}")
            print(f"     Scraped {len(items)} items")
            if items:
                print(f"     First item: {items[0] if len(items) > 0 else 'None'}")
        except Exception as e:
            print(f"     Error scraping {url}: {e}")

    # Test full data collection
    print("\n3. Testing full data collection...")
    try:
        all_data = strategy.collect_all_data(stock_code, stock_name)
        print(f"   Full data collection result: {type(all_data)}")
        if isinstance(all_data, dict):
            print(f"   Keys in all_data: {list(all_data.keys())}")
    except Exception as e:
        print(f"   Error in full data collection: {e}")

    print("\n" + "=" * 80)
    print("Test completed!")

if __name__ == "__main__":
    test_strategy_scraping()

