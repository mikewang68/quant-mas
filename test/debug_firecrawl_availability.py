#!/usr/bin/env python3
"""
Debug FireCrawl availability and test different endpoints
"""

import sys
import os
import requests

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_firecrawl_endpoints():
    """Test various FireCrawl endpoints to see what's available"""
    firecrawl_url = "http://192.168.1.2:8080"
    print(f"Testing FireCrawl at {firecrawl_url}")

    # Test base URL
    try:
        response = requests.get(firecrawl_url, timeout=10)
        print(f"Base URL status: {response.status_code}")
        if response.status_code == 200:
            print(f"Base URL response: {response.text[:100]}...")
            if "SCRAPERS-JS" in response.text:
                print("Detected SCRAPERS-JS deployment - this is a custom FireCrawl deployment")
    except Exception as e:
        print(f"Error accessing base URL: {e}")

    # Test if it's a standard FireCrawl deployment
    standard_endpoints = [
        "/v0/scrape",
        "/v1/scrape",
        "/scrape",
        "/v0/crawl",
        "/v1/crawl",
        "/crawl"
    ]

    available_endpoints = []
    for endpoint in standard_endpoints:
        try:
            url = f"{firecrawl_url}{endpoint}"
            response = requests.get(url, timeout=5)
            print(f"  {endpoint}: {response.status_code}")
            if response.status_code in [400, 405]:  # These indicate the endpoint exists
                available_endpoints.append(endpoint)
                print(f"    ^^^ This endpoint appears to be available")
        except Exception as e:
            print(f"  {endpoint}: Error - {e}")

    if available_endpoints:
        print(f"\nAvailable standard endpoints: {available_endpoints}")
    else:
        print("\nNo standard FireCrawl endpoints detected")

    # Test POST to scrape endpoint
    print("\nTesting POST to scrape endpoint...")
    try:
        response = requests.post(
            f"{firecrawl_url}/scrape",
            json={"url": "https://example.com"},
            timeout=10
        )
        print(f"POST /scrape status: {response.status_code}")
        if response.status_code == 200:
            print(f"POST /scrape response: {response.text[:200]}...")
        else:
            print(f"POST /scrape error: {response.text[:200]}...")
    except Exception as e:
        print(f"Error with POST /scrape: {e}")

if __name__ == "__main__":
    test_firecrawl_endpoints()

