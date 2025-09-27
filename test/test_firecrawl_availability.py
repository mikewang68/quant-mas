#!/usr/bin/env python3
"""
Test script to check FireCrawl availability and configuration
"""

import sys
import os
import requests

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2

def test_firecrawl_availability():
    """Test FireCrawl availability"""
    print("Testing FireCrawl availability...")

    # Initialize strategy
    strategy = EnhancedPublicOpinionAnalysisStrategyV2()

    # Get FireCrawl configuration
    api_url = strategy.firecrawl_config.get("api_url", "http://192.168.1.2:8080/v1")
    timeout = strategy.firecrawl_config.get("timeout", 30)

    print(f"FireCrawl API URL: {api_url}")
    print(f"Timeout: {timeout}")

    # Extract base URL for testing
    from urllib.parse import urlparse
    parsed = urlparse(api_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    print(f"Base URL (for testing): {base_url}")

    # Test base URL accessibility
    try:
        print("\n1. Testing base URL accessibility...")
        response = requests.get(base_url, timeout=timeout)
        print(f"   Status code: {response.status_code}")
        print(f"   Response text preview: {response.text[:100]}")

        if "SCRAPERS-JS" in response.text:
            print("   Detected custom FireCrawl deployment (SCRAPERS-JS)")
        else:
            print("   Standard deployment detected")

    except Exception as e:
        print(f"   Error accessing base URL: {e}")
        return False

    # Test scrape endpoint
    try:
        print("\n2. Testing scrape endpoint...")
        scrape_url = f"{base_url}/v1/scrape"
        # Test with POST request like the strategy does
        response = requests.post(scrape_url,
                               json={"url": "https://example.com"},
                               timeout=timeout)
        print(f"   Status code: {response.status_code}")
        print(f"   Response text preview: {str(response.json())[:100] if response.status_code == 200 else response.text[:100]}")

        if response.status_code == 200:
            print("   Scrape endpoint is available and working")
            return True
        elif response.status_code in [400, 405]:
            print("   Scrape endpoint is available (standard FireCrawl)")
            return True
        elif response.status_code == 404:
            print("   Scrape endpoint not found")
        else:
            print("   Unexpected response from scrape endpoint")

    except Exception as e:
        print(f"   Error accessing scrape endpoint: {e}")

    return False

def test_strategy_firecrawl_check():
    """Test the strategy's FireCrawl availability check"""
    print("\n3. Testing strategy's FireCrawl availability check...")

    strategy = EnhancedPublicOpinionAnalysisStrategyV2()

    api_url = strategy.firecrawl_config.get("api_url", "http://192.168.1.2:8080/v1")
    timeout = strategy.firecrawl_config.get("timeout", 30)

    is_available = strategy._is_firecrawl_available(api_url, timeout)
    print(f"   Strategy reports FireCrawl available: {is_available}")

    return is_available

def main():
    """Main test function"""
    print("FireCrawl Availability Test")
    print("=" * 40)

    # Test FireCrawl availability
    available = test_firecrawl_availability()

    # Test strategy's check
    strategy_check = test_strategy_firecrawl_check()

    print("\n" + "=" * 40)
    print("Summary:")
    print(f"  Manual check: {'Available' if available else 'Not available'}")
    print(f"  Strategy check: {'Available' if strategy_check else 'Not available'}")

    if not available and not strategy_check:
        print("\nFireCrawl is not available for this strategy.")
        print("This is normal if you're using a custom deployment that doesn't support standard endpoints.")

if __name__ == "__main__":
    main()

