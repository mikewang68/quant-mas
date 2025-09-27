#!/usr/bin/env python3
"""
Debug script to understand FireCrawl search behavior
"""

import sys
import os
import requests

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2

def debug_firecrawl_search():
    """Debug FireCrawl search functionality"""
    print("Debugging FireCrawl search functionality...")

    # Initialize strategy
    strategy = EnhancedPublicOpinionAnalysisStrategyV2()

    # Get FireCrawl configuration
    api_url = strategy.firecrawl_config.get("api_url")
    timeout = strategy.firecrawl_config.get("timeout", 30)

    print(f"FireCrawl API URL: {api_url}")

    # Test search with different queries
    test_queries = [
        "科技股",
        "半导体行业前景",
        "平安银行 股票 新闻",
        "stock news"
    ]

    headers = {"Content-Type": "application/json"}

    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        try:
            # Prepare payload for individual search (v1 format)
            payload = {
                "query": query
            }

            # Send request to FireCrawl search API (using v1 endpoint)
            response = requests.post(
                f"{api_url}/search",
                headers=headers,
                json=payload,
                timeout=timeout,
            )

            print(f"  Status code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"  Full response: {result}")
                search_results = result.get("data", [])
                print(f"  Number of results: {len(search_results)}")

                # Show first few results if any
                if search_results:
                    print("  First result preview:")
                    first_result = search_results[0]
                    print(f"    Title: {first_result.get('title', 'N/A')}")
                    print(f"    URL: {first_result.get('url', 'N/A')}")
                    print(f"    Content preview: {first_result.get('content', '')[:100]}...")
                else:
                    print("  No results returned")
            else:
                print(f"  Error response: {response.text[:200]}")
        except Exception as e:
            print(f"  Exception: {e}")

if __name__ == "__main__":
    debug_firecrawl_search()

