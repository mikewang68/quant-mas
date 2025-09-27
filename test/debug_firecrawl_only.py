#!/usr/bin/env python3
"""
Debug script to test FireCrawl functionality exclusively for information retrieval
"""

import sys
import os
import requests
import json
from datetime import datetime, timedelta
from urllib.parse import urljoin

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2


def debug_firecrawl_exclusive():
    """Debug FireCrawl functionality exclusively"""
    print("Debugging FireCrawl functionality exclusively")
    print("=" * 55)

    # Initialize strategy to get FireCrawl configuration
    strategy = EnhancedPublicOpinionAnalysisStrategyV2()

    # Get FireCrawl configuration
    api_url = strategy.firecrawl_config.get("api_url")
    timeout = strategy.firecrawl_config.get("timeout", 30)
    api_key = strategy.firecrawl_config.get("api_key", "")

    print(f"FireCrawl API URL: {api_url}")
    print(f"Timeout: {timeout}")
    print(f"API Key available: {'Yes' if api_key else 'No'}")

    # Test FireCrawl availability
    print("\n1. Testing FireCrawl availability...")
    try:
        is_available = strategy._is_firecrawl_available(api_url, timeout)
        print(f"   FireCrawl available: {is_available}")
    except Exception as e:
        print(f"   Error checking availability: {e}")

    # Test scraping specific Guba URLs directly with FireCrawl
    print("\n2. Testing direct FireCrawl scraping of Guba URLs...")
    guba_urls = [
        "https://guba.eastmoney.com/list,300339,1,f.html",  # Consultation section
        "https://guba.eastmoney.com/list,300339,2,f.html",  # Research reports section
        "https://guba.eastmoney.com/list,300339,3,f.html",  # Announcements section
        "https://guba.eastmoney.com/list,300339,99.html",   # Hot posts section
        "https://guba.eastmoney.com/list,300339.html"       # Main page
    ]

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    all_scraped_data = {}

    for i, url in enumerate(guba_urls, 1):
        print(f"\n   {i}. Scraping URL: {url}")
        try:
            # Prepare payload for scrape endpoint
            payload = {
                "url": url
            }

            # Send request to FireCrawl scrape API
            scrape_url = urljoin(api_url + "/", "scrape")
            response = requests.post(
                scrape_url,
                headers=headers,
                json=payload,
                timeout=timeout,
            )

            print(f"     Status code: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                success = result.get('success', False)
                print(f"     Success: {success}")

                if success:
                    data = result.get('data', {})
                    content = data.get('content', '')
                    title = data.get('title', 'N/A')
                    links = data.get('links', [])

                    print(f"     Title: {title}")
                    print(f"     Content length: {len(content)} characters")
                    print(f"     Links found: {len(links)}")

                    # Show content preview if available
                    if content:
                        content_preview = content[:300] + "..." if len(content) > 300 else content
                        print(f"     Content preview: {content_preview}")

                    all_scraped_data[url] = {
                        "status": "success",
                        "title": title,
                        "content_length": len(content),
                        "links_count": len(links),
                        "content": content[:1000]  # Store first 1000 chars
                    }
                else:
                    error_msg = result.get('error', 'Unknown error')
                    print(f"     Error: {error_msg}")
                    all_scraped_data[url] = {
                        "status": "failed",
                        "error": error_msg
                    }
            else:
                error_text = response.text[:300] + "..." if len(response.text) > 300 else response.text
                print(f"     Error response: {error_text}")
                all_scraped_data[url] = {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {error_text}"
                }

        except Exception as e:
            print(f"     Exception: {e}")
            all_scraped_data[url] = {
                "status": "exception",
                "error": str(e)
            }

    # Test FireCrawl search with specific queries
    print("\n3. Testing FireCrawl search with stock-specific queries...")
    search_queries = [
        "润和软件 股票分析",
        "300339 公司新闻",
        "润和软件 投资者关系",
        "300339 财务数据"
    ]

    search_results = {}

    for i, query in enumerate(search_queries, 1):
        print(f"\n   {i}. Searching for: '{query}'")
        try:
            # Prepare payload for search endpoint
            payload = {
                "query": query
            }

            # Send request to FireCrawl search API
            search_url = urljoin(api_url + "/", "search")
            response = requests.post(
                search_url,
                headers=headers,
                json=payload,
                timeout=timeout,
            )

            print(f"     Status code: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                success = result.get('success', False)
                print(f"     Success: {success}")

                if success:
                    data = result.get('data', [])
                    print(f"     Results count: {len(data)}")

                    if data:
                        # Show first few results
                        for j, item in enumerate(data[:3]):
                            title = item.get('title', 'N/A')
                            url = item.get('url', 'N/A')
                            print(f"       {j+1}. Title: {title}")
                            print(f"          URL: {url}")

                    search_results[query] = {
                        "status": "success",
                        "results_count": len(data),
                        "results": data[:5]  # Store first 5 results
                    }
                else:
                    error_msg = result.get('error', 'Unknown error')
                    print(f"     Error: {error_msg}")
                    search_results[query] = {
                        "status": "failed",
                        "error": error_msg
                    }
            else:
                error_text = response.text[:300] + "..." if len(response.text) > 300 else response.text
                print(f"     Error response: {error_text}")
                search_results[query] = {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {error_text}"
                }

        except Exception as e:
            print(f"     Exception: {e}")
            search_results[query] = {
                "status": "exception",
                "error": str(e)
            }

    # Summary
    print("\n" + "=" * 55)
    print("SUMMARY")
    print("=" * 55)

    print("\nScraping Results:")
    successful_scrapes = sum(1 for r in all_scraped_data.values() if r["status"] == "success")
    print(f"  Successful scrapes: {successful_scrapes}/{len(guba_urls)}")

    for url, result in all_scraped_data.items():
        short_url = url.replace("https://guba.eastmoney.com/", "")
        print(f"  {short_url}: {result['status'].upper()}")
        if result["status"] == "success":
            print(f"    Content length: {result['content_length']} characters")
            print(f"    Links: {result['links_count']}")
        else:
            print(f"    Error: {result['error']}")

    print("\nSearch Results:")
    successful_searches = sum(1 for r in search_results.values() if r["status"] == "success")
    print(f"  Successful searches: {successful_searches}/{len(search_queries)}")

    for query, result in search_results.items():
        print(f"  '{query}': {result['status'].upper()}")
        if result["status"] == "success":
            print(f"    Results: {result['results_count']}")
        else:
            print(f"    Error: {result['error']}")

    # Save detailed results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"firecrawl_exclusive_debug_results_{timestamp}.json"

    output_data = {
        "test_timestamp": timestamp,
        "firecrawl_config": {
            "api_url": api_url,
            "timeout": timeout,
            "api_key_available": bool(api_key)
        },
        "scraping_results": all_scraped_data,
        "search_results": search_results
    }

    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"\nDetailed results saved to: {results_file}")
    except Exception as e:
        print(f"\nFailed to save results: {e}")

    print("\n" + "=" * 55)
    print("FireCrawl exclusive debugging completed")


if __name__ == "__main__":
    debug_firecrawl_exclusive()

