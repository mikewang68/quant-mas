#!/usr/bin/env python3
"""
Comprehensive test for FireCrawl integration
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2

def test_firecrawl_comprehensive():
    """Comprehensive test for FireCrawl integration"""
    print("Comprehensive FireCrawl Integration Test")
    print("=" * 50)

    # Initialize strategy
    strategy = EnhancedPublicOpinionAnalysisStrategyV2()

    # Check configuration
    print(f"FireCrawl config: {strategy.firecrawl_config}")

    # Check if FireCrawl is available
    api_url = strategy.firecrawl_config.get("api_url")
    timeout = strategy.firecrawl_config.get("timeout", 30)

    is_available = strategy._is_firecrawl_available(api_url, timeout)
    print(f"FireCrawl available: {is_available}")

    if not is_available:
        print("ERROR: FireCrawl should be available but is reported as unavailable!")
        return False

    # Test different types of queries
    test_queries = [
        "科技股",           # Tech stocks (Chinese)
        "semiconductor",    # Semiconductor (English)
        "stock market",     # Stock market (English)
        "股市",             # Stock market (Chinese)
        "investment",       # Investment (English)
    ]

    print(f"\nTesting {len(test_queries)} different queries...")

    total_results = 0
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing query: '{query}'")
        try:
            firecrawl_data = strategy.search_stock_news([query])
            count = len(firecrawl_data)
            total_results += count
            print(f"   Results: {count}")

            if count > 0:
                # Show first result details
                first_result = firecrawl_data[0]
                print(f"   First result title: {first_result.get('title', 'N/A')[:50]}...")
                print(f"   First result URL: {first_result.get('url', 'N/A')}")
        except Exception as e:
            print(f"   Error: {e}")

    print(f"\nTotal results across all queries: {total_results}")

    # Test with multiple queries at once
    print(f"\nTesting multiple queries at once...")
    try:
        combined_data = strategy.search_stock_news(test_queries)
        print(f"Combined results: {len(combined_data)}")
        if combined_data:
            print("Sample combined results:")
            for i, item in enumerate(combined_data[:3]):
                print(f"  {i+1}. {item.get('title', 'N/A')[:60]}...")
    except Exception as e:
        print(f"Error with combined queries: {e}")

    return True

def main():
    """Main test function"""
    success = test_firecrawl_comprehensive()

    print("\n" + "=" * 50)
    if success:
        print("SUCCESS: FireCrawl integration test completed!")
    else:
        print("FAILURE: FireCrawl integration test failed!")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())

