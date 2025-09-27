#!/usr/bin/env python3
"""
Test FireCrawl batch functionality to verify if it's available in the local deployment
"""

import sys
import os
import requests

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_firecrawl_batch_functionality():
    """Test if FireCrawl batch functionality is available"""
    print("Testing FireCrawl batch functionality")
    print("=" * 50)

    # FireCrawl configuration
    firecrawl_url = "http://192.168.1.2:8080"

    # Test v1 batch scrape endpoint
    print("Testing v1 batch scrape endpoint...")
    try:
        response = requests.get(f"{firecrawl_url}/v1/batch/scrape", timeout=10)
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.text[:200]}...")
    except requests.exceptions.RequestException as e:
        print(f"  Error: {e}")

    # Test v1 root endpoint to see available endpoints
    print("\nTesting v1 root endpoint...")
    try:
        response = requests.get(f"{firecrawl_url}/v1", timeout=10)
        print(f"  Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.text}")
        else:
            print(f"  Error Response: {response.text[:200]}...")
    except requests.exceptions.RequestException as e:
        print(f"  Error: {e}")

    # Test base URL to see if it responds
    print("\nTesting base URL...")
    try:
        response = requests.get(firecrawl_url, timeout=10)
        print(f"  Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.text[:200]}...")
        else:
            print(f"  Error Response: {response.text[:200]}...")
    except requests.exceptions.RequestException as e:
        print(f"  Error: {e}")

    print("\nTest completed!")

if __name__ == "__main__":
    test_firecrawl_batch_functionality()

