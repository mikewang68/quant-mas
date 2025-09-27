#!/usr/bin/env python3
"""
Test FireCrawl v1 search API with different payload formats
"""

import requests
import json

def test_v1_search_formats():
    """Test different payload formats for v1 search API"""
    firecrawl_url = "http://192.168.1.2:8080/v1"

    # Different payload formats to test
    payloads = [
        # Simple query only
        {"query": "半导体行业前景"},

        # Query with limit
        {"query": "半导体行业前景", "limit": 5},

        # Query with page options (might be v2 format)
        {
            "query": "半导体行业前景",
            "pageOptions": {
                "onlyMainContent": True,
                "fetchPageContent": True,
                "includeHtml": False,
            },
            "searchOptions": {"limit": 5},
        },

        # Minimal v1 format
        {
            "query": "半导体行业前景",
            "maxResults": 5,
        }
    ]

    print("Testing FireCrawl v1 search API formats...")
    print("=" * 50)

    for i, payload in enumerate(payloads, 1):
        print(f"\nTest {i}: {payload}")
        try:
            response = requests.post(
                f"{firecrawl_url}/search",
                json=payload,
                timeout=15
            )
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"  Success! Data keys: {list(result.keys())}")
                if "data" in result:
                    print(f"  Data count: {len(result['data'])}")
                    if result["data"]:
                        print(f"  Sample item keys: {list(result['data'][0].keys())}")
            else:
                print(f"  Error: {response.text[:300]}")
        except Exception as e:
            print(f"  Exception: {e}")

if __name__ == "__main__":
    test_v1_search_formats()

