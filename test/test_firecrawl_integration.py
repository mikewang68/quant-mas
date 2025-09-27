#!/usr/bin/env python3
"""
Test script to verify FireCrawl integration is working in the strategy
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2

def test_firecrawl_integration():
    """Test that FireCrawl integration works properly"""
    print("Testing FireCrawl integration in EnhancedPublicOpinionAnalysisStrategyV2...")

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

    # Test actual data collection
    print("\nTesting FireCrawl data collection...")
    try:
        # Collect data for a sample query using the search_stock_news method
        queries = ["半导体行业前景", "科技股投资策略"]
        firecrawl_data = strategy.search_stock_news(queries)

        print(f"Collected {len(firecrawl_data)} FireCrawl results")
        if firecrawl_data:
            print("Sample FireCrawl data:")
            for i, data in enumerate(firecrawl_data[:2]):  # Show first 2 results
                print(f"  {i+1}. URL: {data.get('url', 'N/A')}")
                print(f"     Title: {data.get('title', 'N/A')[:50]}...")
                print(f"     Content preview: {data.get('content', 'N/A')[:100]}...")
        else:
            print("No FireCrawl data collected (this might be expected if queries don't return results)")

        return True
    except Exception as e:
        print(f"Error during FireCrawl data collection: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("FireCrawl Integration Test")
    print("=" * 40)

    success = test_firecrawl_integration()

    print("\n" + "=" * 40)
    if success:
        print("SUCCESS: FireCrawl integration is working properly!")
    else:
        print("FAILURE: FireCrawl integration has issues!")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())

