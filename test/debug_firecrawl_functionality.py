#!/usr/bin/env python3
"""
Debug script to test FireCrawl functionality and diagnose why no information is being retrieved
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2


def debug_firecrawl_functionality():
    """Debug FireCrawl functionality"""
    print("Debugging FireCrawl functionality")
    print("=" * 50)

    # Initialize strategy to get FireCrawl configuration
    strategy = EnhancedPublicOpinionAnalysisStrategyV2()

    # Get FireCrawl configuration
    api_url = strategy.firecrawl_config.get("api_url")
    timeout = strategy.firecrawl_config.get("timeout", 30)
    api_key = strategy.firecrawl_config.get("api_key", "")
    max_retries = strategy.firecrawl_config.get("max_retries", 3)
    retry_delay = strategy.firecrawl_config.get("retry_delay", 1)

    print(f"FireCrawl API URL: {api_url}")
    print(f"Timeout: {timeout}")
    print(f"API Key available: {'Yes' if api_key else 'No'}")
    print(f"Max retries: {max_retries}")
    print(f"Retry delay: {retry_delay}")

    # Test FireCrawl availability using the strategy's method
    print("\n1. Testing FireCrawl availability using strategy method...")
    try:
        is_available = strategy._is_firecrawl_available(api_url, timeout)
        print(f"   FireCrawl available: {is_available}")
    except Exception as e:
        print(f"   Error checking availability: {e}")
        import traceback
        traceback.print_exc()

    # Test FireCrawl availability manually
    print("\n2. Testing FireCrawl availability manually...")
    try:
        # Test health endpoint
        health_url = f"{api_url}/health"
        print(f"   Testing health endpoint: {health_url}")
        health_response = requests.get(health_url, timeout=timeout)
        print(f"   Health check status: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"   Health check response: {health_response.json()}")
        else:
            print(f"   Health check failed: {health_response.text}")

        # Test scrape endpoint with a simple request
        scrape_url = f"{api_url}/scrape"
        print(f"   Testing scrape endpoint: {scrape_url}")

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        test_payload = {
            "url": "https://httpbin.org/html"
        }

        scrape_response = requests.post(
            scrape_url,
            headers=headers,
            json=test_payload,
            timeout=timeout
        )
        print(f"   Scrape test status: {scrape_response.status_code}")
        if scrape_response.status_code == 200:
            result = scrape_response.json()
            print(f"   Scrape test success: {result.get('success', False)}")
            if result.get('success'):
                data = result.get('data', {})
                print(f"   Scrape test title: {data.get('title', 'N/A')}")
                print(f"   Scrape test content length: {len(data.get('content', ''))}")
            else:
                print(f"   Scrape test error: {result.get('error', 'Unknown error')}")
        else:
            print(f"   Scrape test failed: {scrape_response.text}")

    except Exception as e:
        print(f"   Error in manual availability test: {e}")
        import traceback
        traceback.print_exc()

    # Test search functionality
    print("\n3. Testing FireCrawl search functionality...")
    try:
        search_url = f"{api_url}/search"
        print(f"   Testing search endpoint: {search_url}")

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        # Test with a simple query
        search_payload = {
            "query": "人工智能 股票分析"
        }

        search_response = requests.post(
            search_url,
            headers=headers,
            json=search_payload,
            timeout=timeout
        )
        print(f"   Search test status: {search_response.status_code}")
        if search_response.status_code == 200:
            result = search_response.json()
            print(f"   Search test success: {result.get('success', False)}")
            if result.get('success'):
                data = result.get('data', [])
                print(f"   Search results count: {len(data)}")
                if data:
                    print(f"   First result title: {data[0].get('title', 'N/A')}")
            else:
                print(f"   Search test error: {result.get('error', 'Unknown error')}")
        else:
            print(f"   Search test failed: {search_response.text}")

    except Exception as e:
        print(f"   Error in search test: {e}")
        import traceback
        traceback.print_exc()

    # Test the strategy's search method with specific queries
    print("\n4. Testing strategy's search method...")
    try:
        # Test with queries for stock 300339
        queries = ["润和软件 股票分析", "300339 公司新闻"]
        print(f"   Testing queries: {queries}")

        search_results = strategy.search_stock_news(queries)
        print(f"   Strategy search returned {len(search_results)} results")

        if search_results:
            print("   First result:")
            first_result = search_results[0]
            for key, value in first_result.items():
                print(f"     {key}: {value}")
        else:
            print("   No results returned from strategy search")

    except Exception as e:
        print(f"   Error in strategy search: {e}")
        import traceback
        traceback.print_exc()

    # Test scraping specific Guba URLs
    print("\n5. Testing scraping of specific Guba URLs...")
    guba_urls = [
        "https://guba.eastmoney.com/list,300339,1,f.html",
        "https://guba.eastmoney.com/list,300339.html"
    ]

    for i, url in enumerate(guba_urls, 1):
        print(f"\n   {i}. Testing URL: {url}")
        try:
            # Use the strategy's scrape method
            scraped_data = strategy.scrape_url_with_firecrawl(url)

            if scraped_data:
                print(f"     Success! Content length: {len(str(scraped_data))}")
                if 'content' in scraped_data:
                    content_length = len(scraped_data['content'])
                    print(f"     Content length: {content_length}")
                    if content_length > 0:
                        content_preview = scraped_data['content'][:200] + "..." if len(scraped_data['content']) > 200 else scraped_data['content']
                        print(f"     Content preview: {content_preview}")
                    else:
                        print("     Content is empty")
                else:
                    print("     No 'content' field in response")
                    print(f"     Response keys: {list(scraped_data.keys())}")
            else:
                print("     No data returned from scrape")

        except Exception as e:
            print(f"     Error scraping URL: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 50)
    print("FireCrawl functionality debugging completed")


if __name__ == "__main__":
    debug_firecrawl_functionality()

