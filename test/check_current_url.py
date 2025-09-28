#!/usr/bin/env python3

import requests
import re

def check_current_url():
    # Router configuration
    ROUTER_IP = "192.168.1.1"
    base_url = f"http://{ROUTER_IP}"

    # Create a session
    session = requests.Session()

    # Set headers to mimic a browser
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    })

    print("=== Checking current URL and redirects ===")
    try:
        # Get the index page and check the final URL
        index_response = session.get(f"{base_url}/webpages/index.html", timeout=10)
        print(f"Requested URL: {base_url}/webpages/index.html")
        print(f"Final URL: {index_response.url}")
        print(f"Status code: {index_response.status_code}")

        # Check if there are any stok parameters in the URL
        stok_match = re.search(r'[&?]stok=([a-zA-Z0-9]+)', index_response.url)
        if stok_match:
            print(f"Found stok in URL: {stok_match.group(1)}")
        else:
            print("No stok found in URL")

        # Check the response content for any stok references
        content = index_response.text

        # Look for stok in JavaScript more carefully
        stok_patterns = [
            r'stok["\s]*[=:]["\s]*["\']([a-zA-Z0-9]+)["\']',
            r'["\']stok["\']\s*[:,]\s*["\']([a-zA-Z0-9]+)["\']',
            r'stok\s*=\s*["\']([a-zA-Z0-9]+)["\']'
        ]

        for pattern in stok_patterns:
            matches = re.findall(pattern, content)
            if matches:
                print(f"stok matches for pattern '{pattern}': {matches}")

        # Look for any URLs in the JavaScript that might contain stok
        js_urls = re.findall(r'url\s*:\s*["\']([^"\']*)["\']', content)
        stok_urls = [url for url in js_urls if 'stok' in url]
        print(f"URLs containing 'stok': {stok_urls}")

        # Try to access the page with a stok parameter
        print(f"\n--- Trying to access page with default stok ---")
        stok_url = f"{base_url}/webpages/index.html?stok=12345"
        stok_response = session.get(stok_url, timeout=10)
        print(f"URL with stok: {stok_response.url}")
        print(f"Status code: {stok_response.status_code}")

    except Exception as e:
        print(f"Error checking current URL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_current_url()

