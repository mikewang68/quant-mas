#!/usr/bin/env python3
"""
Test the scrape_guba_posts() function from test_firecrawl.py
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the function directly from test_firecrawl.py
from test.test_firecrawl import scrape_guba_posts

def main():
    """Main test function"""
    print("Testing scrape_guba_posts() function")
    print("=" * 50)

    try:
        # Call the function
        results = scrape_guba_posts()

        print(f"\nFunction returned {len(results)} results")

        # Display results
        if results:
            print("\nResults:")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result}")
        else:
            print("No results returned")

    except Exception as e:
        print(f"Error running scrape_guba_posts(): {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

