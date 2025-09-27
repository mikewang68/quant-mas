#!/usr/bin/env python3
"""
Debug script to understand FireCrawl URL logic
"""

import requests
from urllib.parse import urlparse, urljoin

def test_firecrawl_urls():
    """Test different FireCrawl URL combinations"""
    api_url = "http://192.168.1.2:8080/v1"
    timeout = 30

    print(f"Original API URL: {api_url}")

    # Extract base URL
    parsed = urlparse(api_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    print(f"Base URL: {base_url}")

    # Test base URL
    print("\n1. Testing base URL:")
    try:
        response = requests.get(base_url, timeout=timeout)
        print(f"   Status: {response.status_code}")
        print(f"   Content preview: {response.text[:100]}")
        if "SCRAPERS-JS" in response.text:
            print("   Detected SCRAPERS-JS deployment")
    except Exception as e:
        print(f"   Error: {e}")

    # Test api_url directly
    print("\n2. Testing API URL directly:")
    try:
        response = requests.get(api_url, timeout=timeout)
        print(f"   Status: {response.status_code}")
        print(f"   Content preview: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test actual scrape endpoint
    print("\n3. Testing scrape endpoint:")
    scrape_url = urljoin(base_url, "/v1/scrape")
    print(f"   Scrape URL: {scrape_url}")
    try:
        response = requests.post(scrape_url,
                               json={"url": "https://example.com"},
                               timeout=timeout)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   Scrape endpoint works!")
            print(f"   Response preview: {str(response.json())[:200]}")
        else:
            print(f"   Response: {response.text[:100]}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_firecrawl_urls()

