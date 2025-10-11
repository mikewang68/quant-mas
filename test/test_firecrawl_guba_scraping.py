#!/usr/bin/env python3
"""
Test FireCrawl scraping functionality for specific Eastmoney Guba URLs with custom requirements
"""

import sys
import os
import requests
import json
from datetime import datetime
import re

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.enhanced_public_opinion_analysis_strategy_v2 import EnhancedPublicOpinionAnalysisStrategyV2

def extract_date_from_content(content):
    """Extract date information from content if available"""
    if not content:
        return None

    # Look for common date patterns in Chinese financial content
    date_patterns = [
        r'(\d{4}-\d{2}-\d{2})',
        r'(\d{4}/\d{2}/\d{2})',
        r'(\d{4}年\d{1,2}月\d{1,2}日)'
    ]

    for pattern in date_patterns:
        matches = re.findall(pattern, content)
        if matches:
            return matches[0]
    return None

def filter_content_by_date(content, days=5):
    """Filter content to only include items from the last N days"""
    if not content:
        return None

    # This is a simplified implementation - in practice, you would need to parse
    # the actual HTML structure of the Guba pages to extract dates
    return content  # For now, return all content

def test_specific_firecrawl_requirements():
    """Test FireCrawl scraping with specific requirements from the task"""
    print("Testing FireCrawl scraping with specific requirements")
    print("=" * 60)

    # Initialize strategy to get FireCrawl configuration
    # EnhancedPublicOpinionAnalysisStrategyV2 requires name and params arguments
    strategy = EnhancedPublicOpinionAnalysisStrategyV2(
        name="test_enhanced_public_opinion_analysis_strategy_v2",
        params={}
    )

    # Get FireCrawl configuration
    api_url = strategy.firecrawl_config.get("api_url")
    timeout = strategy.firecrawl_config.get("timeout", 30)
    api_key = strategy.firecrawl_config.get("api_key", "")

    print(f"FireCrawl API URL: {api_url}")
    print(f"API Key available: {'Yes' if api_key else 'No'}")

    # URLs to test with specific requirements
    urls_to_test = [
        {
            "url": "https://guba.eastmoney.com/list,300339,1,f.html",
            "description": "Consultation section, 5 days data",
            "requirement": "5_days"
        },
        {
            "url": "https://guba.eastmoney.com/list,300339,2,f.html",
            "description": "Research reports section, first 5 items",
            "requirement": "5_items"
        },
        {
            "url": "https://guba.eastmoney.com/list,300339,3,f.html",
            "description": "Announcements section, 5 days data",
            "requirement": "5_days"
        },
        {
            "url": "https://guba.eastmoney.com/list,300339,99.html",
            "description": "Hot posts section, 5 days data",
            "requirement": "5_days"
        },
        {
            "url": "https://guba.eastmoney.com/list,300339.html",
            "description": "Main page, first 10 items",
            "requirement": "10_items"
        }
    ]

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    results = {}

    for i, test_item in enumerate(urls_to_test, 1):
        url = test_item["url"]
        description = test_item["description"]
        requirement = test_item["requirement"]

        print(f"\n{i}. Testing URL: {url}")
        print(f"   Description: {description}")
        print(f"   Requirement: {requirement}")

        try:
            # Prepare payload for scrape endpoint
            payload = {
                "url": url
            }

            # Send request to FireCrawl scrape API
            response = requests.post(
                f"{api_url}/scrape",
                headers=headers,
                json=payload,
                timeout=timeout,
            )

            print(f"   Status code: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                success = result.get('success', False)
                print(f"   Success: {success}")

                if success:
                    data = result.get('data', {})
                    content = data.get('content', '')
                    title = data.get('title', 'N/A')

                    print(f"   Title: {title}")
                    print(f"   Content length: {len(content)} characters")

                    # Apply specific filtering based on requirements
                    if requirement == "5_days":
                        # In a real implementation, we would filter content by date here
                        filtered_content = filter_content_by_date(content, 5)
                        print(f"   Note: Would filter for last 5 days (not implemented in this test)")
                    elif requirement == "5_items":
                        # In a real implementation, we would limit to first 5 items
                        print(f"   Note: Would limit to first 5 items (not implemented in this test)")
                    elif requirement == "10_items":
                        # In a real implementation, we would limit to first 10 items
                        print(f"   Note: Would limit to first 10 items (not implemented in this test)")

                    # Show content preview
                    if content:
                        content_preview = content[:300] + "..." if len(content) > 300 else content
                        print(f"   Content preview: {content_preview}")

                    results[url] = {
                        "status": "success",
                        "title": title,
                        "content_length": len(content),
                        "requirement": requirement
                    }
                else:
                    error_msg = result.get('error', 'Unknown error')
                    print(f"   Error: {error_msg}")
                    results[url] = {
                        "status": "failed",
                        "error": error_msg,
                        "requirement": requirement
                    }
            else:
                error_text = response.text[:300] + "..." if len(response.text) > 300 else response.text
                print(f"   Error response: {error_text}")
                results[url] = {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {error_text}",
                    "requirement": requirement
                }
        except Exception as e:
            print(f"   Exception: {e}")
            results[url] = {
                "status": "exception",
                "error": str(e),
                "requirement": requirement
            }

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY OF TEST RESULTS")
    print("=" * 60)

    success_count = sum(1 for r in results.values() if r["status"] == "success")
    print(f"Successful scrapes: {success_count}/{len(urls_to_test)}")

    for url, result in results.items():
        # Get short URL for display
        short_url = url.replace("https://guba.eastmoney.com/", "")
        print(f"\n{short_url}")
        print(f"  Status: {result['status'].upper()}")
        print(f"  Requirement: {result['requirement']}")
        if result["status"] == "success":
            print(f"  Title: {result['title']}")
            print(f"  Content length: {result['content_length']} characters")
        else:
            print(f"  Error: {result['error']}")

    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"firecrawl_guba_custom_test_results_{timestamp}.json"

    output_data = {
        "test_timestamp": timestamp,
        "test_description": "Custom FireCrawl Guba scraping test with specific requirements",
        "firecrawl_api_url": api_url,
        "test_results": results
    }

    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"\nResults saved to: {results_file}")
    except Exception as e:
        print(f"\nFailed to save results: {e}")

    return success_count > 0

def test_strategy_methods_with_custom_filtering():
    """Test using the strategy's built-in methods with custom filtering"""
    print("\n" + "="*60)
    print("Testing strategy methods with custom filtering...")
    print("="*60)

    try:
        # Initialize strategy
        strategy = EnhancedPublicOpinionAnalysisStrategyV2(
            name="test_enhanced_public_opinion_analysis_strategy_v2",
            params={}
        )

        # Test detailed Guba data collection for stock 300339
        stock_code = "300339"
        print(f"Collecting detailed Guba data for {stock_code}...")

        # This will use the strategy's built-in methods which may already have
        # some filtering capabilities
        detailed_data = strategy.get_detailed_guba_data(stock_code)

        print("✓ Detailed Guba data collection completed")
        for key, value in detailed_data.items():
            print(f"  {key}: {len(value)} items")

            # Show first few items as examples
            if isinstance(value, list) and value:
                print(f"    Sample items (first 2):")
                for i, item in enumerate(value[:2]):
                    if isinstance(item, dict):
                        print(f"      {i+1}. {str(item)[:100]}...")
                    else:
                        print(f"      {i+1}. {str(item)[:100]}...")

    except Exception as e:
        print(f"Error in strategy methods: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("FireCrawl Guba Scraping Test with Custom Requirements")
    print("=" * 60)

    # Test with custom requirements
    success = test_specific_firecrawl_requirements()

    # Test with strategy methods
    test_strategy_methods_with_custom_filtering()

    print("\n" + "=" * 60)
    if success:
        print("🎉 Test completed with some successful scrapes!")
    else:
        print("❌ All scraping attempts failed!")
    print("=" * 60)

