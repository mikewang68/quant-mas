#!/usr/bin/env python3

import requests
import re

def check_index_page():
    # Router configuration
    ROUTER_IP = "192.168.1.1"
    base_url = f"http://{ROUTER_IP}"

    # Create a session
    session = requests.Session()

    # Set headers to mimic a browser
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': f'{base_url}/webpages/login.html',
    })

    print("=== Checking index page for authentication clues ===")
    try:
        # Try to access the index page directly (should redirect to login if not authenticated)
        index_response = session.get(f"{base_url}/webpages/index.html", timeout=10)
        print(f"Index page status code: {index_response.status_code}")
        print(f"Index page URL after redirects: {index_response.url}")

        if index_response.status_code == 200:
            content = index_response.text
            print(f"Index page content length: {len(content)}")

            # Look for stok in the index page
            stok_matches = re.findall(r'[&?]stok=([a-zA-Z0-9]+)', content)
            print(f"stok values found in index page: {stok_matches}")

            # Look for stok in JavaScript variables
            js_stok_matches = re.findall(r'stok["\s]*[=:]["\s]*["\']([a-zA-Z0-9]+)["\']', content)
            print(f"stok values in JavaScript: {js_stok_matches}")

            # Look for any API endpoints in the index page
            api_endpoints = re.findall(r'["\'](\/[^\s"\']*api[^\s"\']*)["\']', content)
            print(f"API endpoints found: {list(set(api_endpoints))}")

            # Look for any references to WAN or network status
            wan_refs = re.findall(r'wan[0-9]*|network|status', content, re.IGNORECASE)
            print(f"WAN/network references found: {len(wan_refs)}")

        else:
            print(f"Failed to access index page: {index_response.status_code}")

    except Exception as e:
        print(f"Error checking index page: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_index_page()

