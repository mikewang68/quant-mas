#!/usr/bin/env python3
"""
Test various FireCrawl endpoints to determine what's available in the local deployment
"""

import sys
import os
import requests

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_firecrawl_endpoints():
    """Test various FireCrawl endpoints"""
    print("Testing FireCrawl endpoints")
    print("=" * 50)

    # FireCrawl configuration
    firecrawl_url = "http://192.168.1.2:8080"

    # List of endpoints to test
    endpoints = [
        "/",  # Base endpoint
        "/v0",  # Some versions use v0
        "/v1",  # Standard v1
        "/v1/scrape",  # v1 scrape
        "/v1/crawl",   # v1 crawl
        "/v1/map",     # v1 map
        "/v1/batch/scrape",  # v1 batch scrape
        "/v2",  # v2
        "/v2/scrape",  # v2 scrape
        "/v2/crawl",   # v2 crawl
        "/v2/map",     # v2 map
        "/v2/batch/scrape",  # v2 batch scrape
        "/api/v0",  # API prefixed versions
        "/api/v1",
        "/api/v2",
        "/scrape",  # Direct scrape endpoint
        "/crawl",   # Direct crawl endpoint
        "/map",     # Direct map endpoint
        "/batch/scrape",  # Direct batch scrape
    ]

    # Test each endpoint
    for endpoint in endpoints:
        url = f"{firecrawl_url}{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            print(f"  {endpoint:<20} - Status: {response.status_code}")
            if response.status_code == 200 and len(response.text) < 200:
                print(f"                    - Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"  {endpoint:<20} - Error: {str(e)[:50]}")

    # Test POST to scrape endpoint
    print("\nTesting POST to scrape endpoint...")
    try:
        response = requests.post(
            f"{firecrawl_url}/scrape",
            json={"url": "https://example.com"},
            timeout=10
        )
        print(f"  POST /scrape - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"               - Response type: {type(response.json())}")
    except requests.exceptions.RequestException as e:
        print(f"  POST /scrape - Error: {str(e)[:50]}")

    # Test if it's a FireCrawl deployment
    print("\nChecking if it's a standard FireCrawl deployment...")
    try:
        # Test if base URL is accessible
        response = requests.get(firecrawl_url, timeout=5)
        if response.status_code == 200:
            if "SCRAPERS-JS" in response.text:
                print("  Detected custom FireCrawl deployment (SCRAPERS-JS)")
                print("  This deployment doesn't support standard API endpoints")
            else:
                print("  Detected standard FireCrawl deployment")
        else:
            print("  FireCrawl is not accessible")
    except requests.exceptions.RequestException as e:
        print(f"  Error checking FireCrawl deployment: {str(e)[:50]}")

    print("\nTest completed!")

if __name__ == "__main__":
    test_firecrawl_endpoints()

