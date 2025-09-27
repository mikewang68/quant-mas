#!/usr/bin/env python3
"""
Test FireCrawl search functionality
"""

import requests
import json

def test_search_endpoints():
    """Test FireCrawl search endpoints"""
    firecrawl_url = "http://192.168.1.2:8080"

    # Test different search endpoints
    endpoints = [
        "/search",
        "/v1/search",
        "/scrape",  # This is for URL scraping, not search
    ]

    # Test search query
    search_payload = {
        "query": "半导体行业前景"
    }

    print("Testing FireCrawl search endpoints...")
    print("=" * 50)

    for endpoint in endpoints:
        url = f"{firecrawl_url}{endpoint}"
        try:
            print(f"\nTesting {endpoint}...")
            if endpoint == "/scrape":
                # For scrape endpoint, we need a URL, not a query
                payload = {"url": "https://example.com"}
            else:
                payload = search_payload

            response = requests.post(
                url,
                json=payload,
                timeout=10
            )
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  Success! Response preview: {str(response.json())[:200]}")
            else:
                print(f"  Error response: {response.text[:200]}")
        except Exception as e:
            print(f"  Exception: {e}")

def test_scrape_with_search_query():
    """Test if we can use scrape endpoint with search-like parameters"""
    firecrawl_url = "http://192.168.1.2:8080"

    # Try different payload formats for scrape endpoint
    payloads = [
        {"url": "https://www.google.com/search?q=半导体行业前景"},
        {"url": "https://www.baidu.com/s?wd=半导体行业前景"},
        {"query": "半导体行业前景"},  # This might not work
    ]

    print("\n\nTesting scrape endpoint with search-like URLs...")
    print("=" * 50)

    for i, payload in enumerate(payloads, 1):
        print(f"\nTest {i}: {payload}")
        try:
            response = requests.post(
                f"{firecrawl_url}/v1/scrape",
                json=payload,
                timeout=15
            )
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"  Success! Data keys: {list(result.keys())}")
            else:
                print(f"  Error: {response.text[:200]}")
        except Exception as e:
            print(f"  Exception: {e}")

if __name__ == "__main__":
    test_search_endpoints()
    test_scrape_with_search_query()

