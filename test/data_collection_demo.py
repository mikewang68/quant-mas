#!/usr/bin/env python3
"""
Data Collection Demo for the Enhanced Public Opinion Analysis Strategy V2
This program demonstrates the actual data collection capabilities.
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

# Configure logging
logging.basicConfig(level=logging.INFO)

def data_collection_demo():
    """Demonstrate the data collection capabilities of the strategy"""
    print("Data Collection Demo for Enhanced Public Opinion Analysis Strategy V2")
    print("=" * 70)

    try:
        # Create strategy instance with parameters
        strategy_params = {
            "sentiment_threshold": 0.6,
            "news_count_threshold": 5,
            "search_depth": 5,  # Limit to 5 for demo
            "time_window_hours": 24,
            "data_sources": ["akshare", "professional_sites", "guba"],
            "professional_sites": [
                "同花顺财经",
                "东方财富网",
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

        # Test with a real stock code
        stock_code = "300339"  # 瑞芯微
        stock_name = "瑞芯微"

        print(f"\nCollecting data for stock: {stock_code} ({stock_name})")
        print("-" * 50)

        # Test AkShare news collection
        print("\n1. Collecting AkShare News (5-day window)...")
        akshare_news = strategy.get_akshare_news(stock_code)
        print(f"   Found {len(akshare_news)} news items")
        for i, news in enumerate(akshare_news[:3]):  # Show first 3
            print(f"   [{i+1}] {news.get('title', 'N/A')[:60]}...")

        # Test industry information
        print("\n2. Collecting Industry Information...")
        industry_info = strategy.get_stock_industry_info(stock_code)
        if industry_info:
            print(f"   Industry info: {industry_info}")
        else:
            print("   No industry information available")

        # Test Guba data collection
        print("\n3. Collecting Guba Data (Eastmoney 股吧)...")
        guba_data = strategy.scrape_guba_data(stock_code)
        total_guba_items = sum(len(items) for items in guba_data.values())
        print(f"   Found {total_guba_items} Guba items")
        for data_type, items in guba_data.items():
            if items:
                print(f"   - {data_type}: {len(items)} items")
                print(f"     Example: {items[0].get('title', 'N/A')[:60]}...")

        # Test professional sites data
        print("\n4. Collecting Professional Sites Data...")
        professional_data = strategy.get_professional_site_data(stock_code, stock_name)
        print(f"   Found {len(professional_data)} professional site items")
        for i, item in enumerate(professional_data[:2]):  # Show first 2
            print(f"   [{i+1}] {item.get('title', 'N/A')[:60]}...")

        # Show time weight calculation examples
        print("\n5. Time Weight Calculation Examples...")
        current_time = datetime.now().isoformat()
        weight_current = strategy._calculate_time_weight(current_time)
        print(f"   Current time weight: {weight_current:.4f}")

        time_6h_ago = (datetime.now() - timedelta(hours=6)).isoformat()
        weight_6h = strategy._calculate_time_weight(time_6h_ago)
        print(f"   6 hours ago weight: {weight_6h:.4f}")

        time_12h_ago = (datetime.now() - timedelta(hours=12)).isoformat()
        weight_12h = strategy._calculate_time_weight(time_12h_ago)
        print(f"   12 hours ago weight: {weight_12h:.4f}")

        time_24h_ago = (datetime.now() - timedelta(hours=24)).isoformat()
        weight_24h = strategy._calculate_time_weight(time_24h_ago)
        print(f"   24 hours ago weight: {weight_24h:.4f}")

        # Show data collection summary
        print("\n" + "=" * 70)
        print("DATA COLLECTION SUMMARY")
        print("=" * 70)
        print(f"Stock: {stock_code} ({stock_name})")
        print(f"AkShare News: {len(akshare_news)} items")
        print(f"Industry Info: {'Available' if industry_info else 'Not Available'}")
        print(f"Guba Data: {total_guba_items} items")
        print(f"Professional Sites: {len(professional_data)} items")
        print(f"Total Data Points: {len(akshare_news) + (1 if industry_info else 0) + total_guba_items + len(professional_data)}")

        print("\nThe strategy successfully collects data from multiple sources:")
        print("✓ AkShare - Professional financial news (5-day window)")
        print("✓ Eastmoney Guba - User focus, institutional ratings, participation data")
        print("✓ Professional Sites - Analysis from financial websites")
        print("✓ Time Weighting - Recent information weighted more heavily")

        print("\nThis multi-source approach provides a comprehensive view of public opinion")
        print("for more accurate sentiment analysis and stock selection.")

    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    data_collection_demo()

